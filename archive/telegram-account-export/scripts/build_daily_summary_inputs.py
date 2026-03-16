#!/usr/bin/env python3
"""Build a compact daily summary input from all-chats.jsonl.

Usage:
  python build_daily_summary_inputs.py /path/to/all-chats.jsonl > daily-summary-input.json
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def load_events(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def trim_text(value: str | None, limit: int = 280) -> str | None:
    if not value:
        return value
    value = " ".join(value.split())
    return value if len(value) <= limit else value[: limit - 1] + "…"


def event_sort_key(event):
    return (
        event.get("message", {}).get("date") or "",
        event.get("message", {}).get("message_id") or 0,
    )


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    events = sorted(load_events(path), key=event_sort_key)
    if not events:
        print(json.dumps({"date": None, "totals": {}, "top_chats": [], "open_threads": []}, ensure_ascii=False, indent=2))
        return 0

    export_date = events[0].get("export_date")
    chat_buckets = defaultdict(list)
    totals = Counter()
    sender_counter = Counter()
    commitments = []
    open_threads = []

    for event in events:
        chat = event.get("chat", {})
        sender = event.get("sender", {})
        derived = event.get("derived", {})
        text = event.get("text", {})
        attachments = event.get("attachments", [])
        direction = event.get("direction")
        chat_key = chat.get("chat_key") or f"{chat.get('chat_type', 'chat')}-{chat.get('chat_id', 'unknown')}"
        chat_buckets[chat_key].append(event)

        totals["messages"] += 1
        totals[direction or "unknown"] += 1
        if attachments:
            totals["messages_with_attachments"] += 1
        if derived.get("contains_commitment"):
            totals["commitments"] += 1
            commitments.append({
                "chat_key": chat_key,
                "chat_title": chat.get("chat_title"),
                "direction": direction,
                "sender": sender.get("display_name"),
                "message_uid": event.get("message_uid"),
                "text": trim_text(text.get("raw")),
                "date": event.get("message", {}).get("date"),
            })
        if direction == "inbound":
            sender_counter[sender.get("display_name") or sender.get("sender_id") or "unknown"] += 1

    top_chats = []
    for chat_key, bucket in chat_buckets.items():
        bucket = sorted(bucket, key=event_sort_key)
        inbound = sum(1 for e in bucket if e.get("direction") == "inbound")
        outbound = sum(1 for e in bucket if e.get("direction") == "outbound")
        last_event = bucket[-1]
        last_text = trim_text(last_event.get("text", {}).get("raw"))
        has_commitment = any(e.get("derived", {}).get("contains_commitment") for e in bucket)
        has_question = any(e.get("derived", {}).get("is_question") for e in bucket)
        unanswered_inbound = False
        for idx, e in enumerate(bucket):
            if e.get("direction") != "inbound":
                continue
            replied = any(later.get("direction") == "outbound" for later in bucket[idx + 1 :])
            if not replied:
                unanswered_inbound = True
                open_threads.append({
                    "chat_key": chat_key,
                    "chat_title": e.get("chat", {}).get("chat_title"),
                    "message_uid": e.get("message_uid"),
                    "message_date": e.get("message", {}).get("date"),
                    "from": e.get("sender", {}).get("display_name"),
                    "text": trim_text(e.get("text", {}).get("raw")),
                })
                break

        top_chats.append({
            "chat_key": chat_key,
            "chat_title": bucket[0].get("chat", {}).get("chat_title"),
            "chat_type": bucket[0].get("chat", {}).get("chat_type"),
            "message_count": len(bucket),
            "inbound_count": inbound,
            "outbound_count": outbound,
            "last_message_at": last_event.get("message", {}).get("date"),
            "last_message_preview": last_text,
            "has_commitment": has_commitment,
            "has_question": has_question,
            "unanswered_inbound": unanswered_inbound,
        })

    top_chats.sort(key=lambda item: (-item["message_count"], item["chat_key"]))
    open_threads.sort(key=lambda item: (item["message_date"] or "", item["chat_key"]))
    commitments.sort(key=lambda item: (item["date"] or "", item["chat_key"]))

    result = {
        "date": export_date,
        "source_file": str(path),
        "totals": dict(totals),
        "top_inbound_senders": [
            {"sender": sender, "message_count": count}
            for sender, count in sender_counter.most_common(10)
        ],
        "top_chats": top_chats[:25],
        "open_threads": open_threads[:50],
        "commitments": commitments[:50],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
