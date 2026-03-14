# Optional Per-Chat Split Scheme

Use per-chat files as a **derived convenience layer**, not the source of truth.

## Recommendation

Keep one canonical file:

```text
exports/telegram-account/daily/2026-03-13/all-chats.jsonl
```

Then optionally write chat-specific projections:

```text
exports/telegram-account/daily/2026-03-13/derived/per-chat/
  dm-alice.jsonl
  group-family.jsonl
  project-opensea.jsonl
```

## Why split per chat at all

- Faster chat-specific prompts
- Easier debugging and manual review
- Simpler long-lived memory building per relationship/project
- Cheap input for heartbeats like “who am I waiting on?” or “who did I promise something to?”

## Naming scheme

Use `chat.chat_key` as the filename stem.

Recommended pattern:

```text
<chat_type>-<slug>.jsonl
```

Examples:
- `direct-alice-nguyen.jsonl`
- `group-family.jsonl`
- `supergroup-lcm-marketing.jsonl`

If a reliable slug is not available, fall back to:

```text
<chat_type>-<chat_id>.jsonl
```

## Contents of each per-chat file

Each line should remain the **same event object** as the canonical schema. Do not invent a second schema for per-chat files.

That means a per-chat file is just a filtered projection of `all-chats.jsonl`.

## Companion per-chat manifest

Optional but useful:

```json
{
  "chat_id": "123456789",
  "chat_key": "direct-alice-nguyen",
  "chat_type": "direct",
  "chat_title": "Alice Nguyen",
  "export_date": "2026-03-13",
  "message_count": 42,
  "first_message_at": "2026-03-13T01:12:00Z",
  "last_message_at": "2026-03-13T13:51:00Z",
  "inbound_count": 18,
  "outbound_count": 24,
  "has_unanswered_inbound": true,
  "contains_commitments": true
}
```

## Trade-off

Per-chat files create duplicated storage. That is fine here because:
- message metadata is small
- daily export volume is manageable
- the speed and prompt simplicity gains are worth it

If volume grows later, keep the canonical JSONL only and generate per-chat files on demand.

## Best rule

- **Must have:** daily `all-chats.jsonl`
- **Nice to have:** `derived/per-chat/*.jsonl`
- **Never do first:** per-chat only, without a canonical all-chat export
