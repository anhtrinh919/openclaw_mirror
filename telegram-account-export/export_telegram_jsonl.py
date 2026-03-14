from __future__ import annotations

import asyncio
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

ROOT = Path(__file__).resolve().parent
STATE_DIR = ROOT / "state"
OUTPUT_DIR = ROOT / "output"

load_dotenv(ROOT / ".env")

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]


def sanitize(value: str) -> str:
    value = value.strip() or "unnamed"
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value)[:120]


async def ensure_login(client: TelegramClient) -> None:
    await client.connect()
    if await client.is_user_authorized():
        return

    phone = input("Telegram phone number: ").strip()
    await client.send_code_request(phone)
    code = input("Telegram login code: ").strip()

    try:
        await client.sign_in(phone=phone, code=code)
    except SessionPasswordNeededError:
        password = input("Telegram 2FA password: ")
        await client.sign_in(password=password)


async def main() -> None:
    since = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    day = since.strftime("%Y-%m-%d")

    out_dir = OUTPUT_DIR / day
    out_dir.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    client = TelegramClient(str(STATE_DIR / "telethon"), API_ID, API_HASH)

    async with client:
        await ensure_login(client)

        manifest = {"day": day, "files": []}

        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            name = dialog.name or getattr(entity, "username", None) or str(getattr(entity, "id", "unknown"))
            path = out_dir / f"{sanitize(name)}__{getattr(entity, 'id', 'unknown')}.jsonl"

            count = 0
            with path.open("w", encoding="utf-8") as fh:
                async for m in client.iter_messages(entity, reverse=True):
                    if not m.date:
                        continue

                    dt = m.date.astimezone(timezone.utc)
                    if dt < since:
                        continue

                    record = {
                        "chat_id": getattr(entity, "id", None),
                        "chat_name": name,
                        "message_id": m.id,
                        "timestamp_utc": dt.isoformat(),
                        "sender_id": m.sender_id,
                        "text": m.message,
                        "out": m.out,
                    }
                    fh.write(json.dumps(record, ensure_ascii=False) + "\n")
                    count += 1

            manifest["files"].append({
                "path": str(path),
                "message_count": count,
            })

        (out_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        print(f"Done: {out_dir}")


if __name__ == "__main__":
    asyncio.run(main())
