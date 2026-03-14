#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import Channel, Chat, User


ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
DEFAULT_ENV_PATH = ROOT / ".env"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Telegram dialogs/messages to JSONL")
    parser.add_argument("--since", required=True, help="Inclusive ISO timestamp, e.g. 2026-03-12T00:00:00Z")
    parser.add_argument("--until", required=True, help="Exclusive ISO timestamp, e.g. 2026-03-13T00:00:00Z")
    parser.add_argument("--target", action="append", default=[], help="Chat selector; may repeat")
    parser.add_argument("--targets-file", default=None, help="Optional newline-delimited target file")
    parser.add_argument("--output-root", default=None, help="Override export root")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def parse_iso_utc(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError(f"timestamp must include timezone: {value}")
    return dt.astimezone(timezone.utc)


def sanitize_name(value: str) -> str:
    value = value.strip() or "unnamed"
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    return value[:120]


def load_targets(explicit_targets: list[str], targets_file: str | None) -> list[str]:
    targets: list[str] = []
    targets.extend(t for t in explicit_targets if t and t.strip())
    if targets_file:
        path = Path(targets_file)
        if not path.is_absolute():
            path = ROOT / path
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    targets.append(line)
    deduped: list[str] = []
    seen: set[str] = set()
    for item in targets:
        key = item.strip()
        if key not in seen:
            seen.add(key)
            deduped.append(key)
    return deduped


@dataclass
class ExportConfig:
    api_id: int
    api_hash: str
    session_name: str
    output_root: Path
    targets: list[str]
    verbose: bool


def load_config(args: argparse.Namespace) -> ExportConfig:
    load_dotenv(DEFAULT_ENV_PATH)
    api_id_raw = os.getenv("TELEGRAM_API_ID", "").strip()
    api_hash = os.getenv("TELEGRAM_API_HASH", "").strip()
    session_name = os.getenv("TELEGRAM_SESSION_NAME", "telethon").strip() or "telethon"
    output_root_raw = args.output_root or os.getenv("EXPORT_ROOT", "./output")
    targets_file = args.targets_file or os.getenv("EXPORT_TARGETS_FILE", "").strip() or None

    if not api_id_raw or not api_hash:
        raise SystemExit("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in .env")

    output_root = Path(output_root_raw)
    if not output_root.is_absolute():
        output_root = ROOT / output_root

    return ExportConfig(
        api_id=int(api_id_raw),
        api_hash=api_hash,
        session_name=session_name,
        output_root=output_root,
        targets=load_targets(args.target, targets_file),
        verbose=args.verbose,
    )


def session_path(session_name: str) -> str:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    return str(STATE_DIR / session_name)


def dialog_label(dialog) -> str:
    entity = dialog.entity
    if getattr(dialog, "name", None):
        return dialog.name
    if isinstance(entity, User):
        parts = [entity.first_name or "", entity.last_name or ""]
        return " ".join(p for p in parts if p).strip() or str(entity.id)
    return str(getattr(entity, "title", None) or getattr(entity, "username", None) or getattr(entity, "id", "unknown"))


def dialog_identifiers(dialog) -> set[str]:
    entity = dialog.entity
    values = {
        str(getattr(entity, "id", "")),
        dialog_label(dialog),
        getattr(entity, "username", "") or "",
        f"@{getattr(entity, 'username', '')}" if getattr(entity, "username", None) else "",
    }
    return {v.strip() for v in values if v and v.strip()}


def message_to_record(message, dialog) -> dict:
    sender = message.sender_id
    media = None
    if message.media:
        media = type(message.media).__name__
    return {
        "dialog_id": getattr(dialog.entity, "id", None),
        "dialog_name": dialog_label(dialog),
        "message_id": message.id,
        "date_utc": message.date.astimezone(timezone.utc).isoformat(),
        "sender_id": sender,
        "text": message.message,
        "raw_text": getattr(message, "raw_text", None),
        "reply_to_msg_id": getattr(getattr(message, "reply_to", None), "reply_to_msg_id", None),
        "post": getattr(message, "post", None),
        "out": getattr(message, "out", None),
        "mentioned": getattr(message, "mentioned", None),
        "media_type": media,
    }


async def ensure_login(client: TelegramClient) -> None:
    await client.connect()
    if await client.is_user_authorized():
        return
    phone = input("Telegram phone number (international format): ").strip()
    await client.send_code_request(phone)
    code = input("Telegram login code: ").strip()
    try:
        await client.sign_in(phone=phone, code=code)
    except SessionPasswordNeededError:
        password = input("Telegram 2FA password: ")
        await client.sign_in(password=password)


async def iter_selected_dialogs(client: TelegramClient, targets: list[str], verbose: bool):
    selected = []
    async for dialog in client.iter_dialogs():
        ids = dialog_identifiers(dialog)
        if not targets or any(target in ids for target in targets):
            selected.append(dialog)
            if verbose:
                print(f"selected dialog: {dialog_label(dialog)} :: {sorted(ids)}")
    return selected


async def export_dialog(dialog, client: TelegramClient, since: datetime, until: datetime, output_dir: Path, verbose: bool) -> tuple[Path, int]:
    entity = dialog.entity
    name = dialog_label(dialog)
    output_path = output_dir / f"{sanitize_name(name)}__{getattr(entity, 'id', 'unknown')}.jsonl"
    count = 0
    with output_path.open("w", encoding="utf-8") as fh:
        async for message in client.iter_messages(entity, offset_date=until, reverse=True):
            if message.date is None:
                continue
            msg_dt = message.date.astimezone(timezone.utc)
            if msg_dt < since:
                continue
            if msg_dt >= until:
                continue
            fh.write(json.dumps(message_to_record(message, dialog), ensure_ascii=False) + "\n")
            count += 1
    if verbose:
        print(f"wrote {count} messages -> {output_path}")
    return output_path, count


async def main() -> None:
    args = parse_args()
    since = parse_iso_utc(args.since)
    until = parse_iso_utc(args.until)
    if since >= until:
        raise SystemExit("--since must be earlier than --until")

    config = load_config(args)
    day_folder = since.strftime("%Y-%m-%d")
    output_dir = config.output_root / day_folder
    output_dir.mkdir(parents=True, exist_ok=True)

    client = TelegramClient(session_path(config.session_name), config.api_id, config.api_hash)
    async with client:
        await ensure_login(client)
        dialogs = await iter_selected_dialogs(client, config.targets, config.verbose)
        if not dialogs:
            print("no dialogs matched selection")
            return
        manifest = {
            "since": since.isoformat(),
            "until": until.isoformat(),
            "dialog_count": len(dialogs),
            "targets": config.targets,
            "files": [],
        }
        for dialog in dialogs:
            path, count = await export_dialog(dialog, client, since, until, output_dir, config.verbose)
            manifest["files"].append({
                "dialog_name": dialog_label(dialog),
                "dialog_id": getattr(dialog.entity, "id", None),
                "path": str(path),
                "message_count": count,
            })
        manifest_path = output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"ok": True, "manifest": str(manifest_path), "dialog_count": len(dialogs)}))


if __name__ == "__main__":
    asyncio.run(main())
