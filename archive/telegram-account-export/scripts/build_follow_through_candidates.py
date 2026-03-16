#!/usr/bin/env python3
"""Extract follow-through candidates from all-chats.jsonl.

Usage:
  python build_follow_through_candidates.py /path/to/all-chats.jsonl > follow-through-candidates.json
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

COMMITMENT_PATTERNS = [
    r"\bi['’]?ll\b",
    r"\bi will\b",
    r"\blet me\b",
    r"\bget back to you\b",
    r"\bwill send\b",
    r"\bwill update\b",
    r"\bmình sẽ\b",
    r"\bđể mình\b",
    r"\bem sẽ\b",
    r"\banh sẽ\b",
    r"\bmai\b",
    r"\bngày mai\b",
]
TIME_PATTERNS = [
    r"\btoday\b",
    r"\btomorrow\b",
    r"\btonight\b",
    r"\bthis afternoon\b",
    r"\bbefore \d{1,2}(:\d{2})?\s?(am|pm)?\b",
    r"\bmai\b",
    r"\bngày mai\b",
    r"\bchiều nay\b",
    r"\btối nay\b",
]
QUESTION_PATTERNS = [
    r"\?",
    r"\bcan you\b",
    r"\bwhen\b",
    r"\bđược không\b",
    r"\bbao giờ\b",
    r"\bgửi\b",
]
RESOLUTION_HINTS = [
    r"\bsent\b",
    r"\bhere is\b",
    r"\battached\b",
    r"\bđây nhé\b",
    r"\bgửi bạn\b",
    r"\bxong rồi\b",
]


def load_events(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def text_for_event(event) -> str:
    text = event.get("text", {}).get("normalized") or event.get("text", {}).get("raw") or ""
    return " ".join(text.lower().split())


def trim_text(value: str | None, limit: int = 220) -> str | None:
    if not value:
        return value
    value = " ".join(value.split())
    return value if len(value) <= limit else value[: limit - 1] + "…"


def matches_any(patterns, text: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def classify_candidate(event):
    direction = event.get("direction")
    derived = event.get("derived", {})
    text = text_for_event(event)

    has_commitment = derived.get("contains_commitment")
    if has_commitment is None:
        has_commitment = matches_any(COMMITMENT_PATTERNS, text)

    has_time = derived.get("contains_time_reference")
    if has_time is None:
        has_time = matches_any(TIME_PATTERNS, text)

    is_question = derived.get("is_question")
    if is_question is None:
        is_question = matches_any(QUESTION_PATTERNS, text)

    if has_commitment and direction == "outbound":
        return "you_owe", has_time, is_question
    if has_commitment and direction == "inbound":
        return "others_owe_you", has_time, is_question
    if direction == "inbound" and is_question:
        return "unanswered_inbound", has_time, is_question
    return None, has_time, is_question


def resolved_by_later_outbound(candidate, later_events):
    for later in later_events:
        if later.get("direction") != "outbound":
            continue
        text = text_for_event(later)
        if later.get("attachments"):
            return True
        if matches_any(RESOLUTION_HINTS, text):
            return True
    return False


def event_sort_key(event):
    return (
        event.get("chat", {}).get("chat_id") or "",
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
        print(json.dumps({"date": None, "you_owe": [], "others_owe_you": [], "unanswered_inbound": []}, ensure_ascii=False, indent=2))
        return 0

    buckets = defaultdict(list)
    for event in events:
        buckets[event.get("chat", {}).get("chat_id")].append(event)

    result = {
        "date": events[0].get("export_date"),
        "source_file": str(path),
        "you_owe": [],
        "others_owe_you": [],
        "unanswered_inbound": [],
    }

    for chat_id, bucket in buckets.items():
        bucket.sort(key=lambda e: (e.get("message", {}).get("date") or "", e.get("message", {}).get("message_id") or 0))
        for idx, event in enumerate(bucket):
            candidate_type, has_time, is_question = classify_candidate(event)
            if not candidate_type:
                continue
            later_events = bucket[idx + 1 :]
            if candidate_type in {"you_owe", "unanswered_inbound"} and resolved_by_later_outbound(event, later_events):
                continue

            result[candidate_type].append({
                "chat_id": chat_id,
                "chat_key": event.get("chat", {}).get("chat_key"),
                "chat_title": event.get("chat", {}).get("chat_title"),
                "message_uid": event.get("message_uid"),
                "message_date": event.get("message", {}).get("date"),
                "direction": event.get("direction"),
                "from": event.get("sender", {}).get("display_name"),
                "text": trim_text(event.get("text", {}).get("raw")),
                "has_time_reference": has_time,
                "is_question": is_question,
                "reason": candidate_type,
            })

    for key in ("you_owe", "others_owe_you", "unanswered_inbound"):
        result[key].sort(key=lambda item: (item.get("message_date") or "", item.get("chat_key") or ""))

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
