# Recommended JSONL Schema: All Chats Export

Each line in `all-chats.jsonl` is one normalized Telegram message event.

## JSONL line example

```json
{
  "schema_version": "tg-message-event.v1",
  "message_uid": "tgacct:boss-main:chat:123456789:msg:44192",
  "account_id": "boss-main",
  "export_date": "2026-03-13",
  "ingested_at": "2026-03-13T06:30:21Z",
  "source": {
    "platform": "telegram",
    "account_type": "personal",
    "export_batch_id": "2026-03-13T06-30-00Z",
    "source_file": "all-chats.jsonl",
    "line_number": 1821
  },
  "chat": {
    "chat_id": "123456789",
    "chat_key": "dm-alice",
    "chat_type": "direct",
    "chat_title": "Alice Nguyen",
    "username": "alice_ng",
    "folder": "main",
    "is_archived": false
  },
  "message": {
    "message_id": 44192,
    "thread_id": null,
    "grouped_id": null,
    "date": "2026-03-13T04:11:02Z",
    "edit_date": null,
    "reply_to_message_id": 44180,
    "forwarded": false,
    "via_bot": null,
    "service_action": null,
    "deleted": false
  },
  "sender": {
    "sender_id": "99887766",
    "sender_type": "user",
    "display_name": "Tuan Anh",
    "username": null,
    "is_self": true
  },
  "direction": "outbound",
  "text": {
    "raw": "I’ll send you the revised deck before 5pm.",
    "normalized": "i will send you the revised deck before 5pm",
    "language_hint": "en",
    "has_urls": false,
    "has_mentions": false,
    "entity_spans": []
  },
  "attachments": [],
  "reactions": [],
  "derived": {
    "conversation_partner_ids": ["55443322"],
    "is_question": false,
    "contains_commitment": true,
    "contains_time_reference": true,
    "contains_followup_signal": false,
    "priority_hint": "normal"
  }
}
```

## Field-by-field recommendation

### Top-level identity

- `schema_version` — string, pinned to a version like `tg-message-event.v1`
- `message_uid` — deterministic global key: `tgacct:<account_id>:chat:<chat_id>:msg:<message_id>`
- `account_id` — stable internal account label, not a phone number
- `export_date` — the export partition date, `YYYY-MM-DD`
- `ingested_at` — timestamp when OpenClaw normalized the event

### `source`

Tracks how the line got into the lake.

- `platform` — always `telegram`
- `account_type` — `personal`
- `export_batch_id` — unique run ID for the export job
- `source_file` — source filename
- `line_number` — original line number for debugging

### `chat`

- `chat_id` — Telegram chat ID as string
- `chat_key` — filesystem-safe stable slug for per-chat exports
- `chat_type` — `direct`, `group`, `supergroup`, `channel`, `bot`
- `chat_title` — title or best display label
- `username` — chat username if present
- `folder` — optional logical bucket: `main`, `archive`, custom folder name
- `is_archived` — boolean

### `message`

- `message_id` — Telegram message ID within the chat
- `thread_id` — topic/thread identifier if present
- `grouped_id` — album/media group ID if present
- `date` — message timestamp in UTC ISO-8601
- `edit_date` — edit timestamp if present
- `reply_to_message_id` — parent message ID if this is a reply
- `forwarded` — boolean
- `via_bot` — bot username or ID if applicable
- `service_action` — service event label if not a normal text/media message
- `deleted` — boolean if exporter knows the message was deleted later

### `sender`

- `sender_id` — Telegram user/channel/bot ID as string
- `sender_type` — `user`, `channel`, `bot`, `system`
- `display_name` — best display name at export time
- `username` — sender username if known
- `is_self` — whether the message was sent by the account owner

### `direction`

One of:
- `outbound`
- `inbound`
- `system`

This is critical for follow-through logic. `sender.is_self` may be enough for some cases, but `direction` makes downstream rules simpler and more robust.

### `text`

- `raw` — original message text/caption as exported
- `normalized` — lowercased, whitespace-normalized, punctuation-light text for heuristics/search
- `language_hint` — optional language guess
- `has_urls` — boolean
- `has_mentions` — boolean
- `entity_spans` — extracted entities if available

Recommended `entity_spans` item:

```json
{
  "type": "url",
  "offset": 12,
  "length": 18,
  "value": "https://example.com"
}
```

### `attachments`

Array of zero or more attachment metadata objects.

Recommended attachment item:

```json
{
  "attachment_id": "att_01HQ...",
  "kind": "document",
  "mime_type": "application/pdf",
  "file_name": "proposal.pdf",
  "file_size": 820331,
  "attachment_key": "a1/b2/proposal_820331.pdf",
  "caption": null,
  "duration_seconds": null,
  "width": null,
  "height": null
}
```

Store binaries outside JSONL. Keep only metadata and a retrievable key/path.

### `reactions`

Optional summary array for reaction-rich chats.

Recommended reaction item:

```json
{
  "emoji": "👍",
  "count": 2,
  "chosen_by_self": false
}
```

### `derived`

This is the only optional section I still recommend strongly, because it dramatically lowers later AI/token cost.

Suggested booleans:
- `conversation_partner_ids`
- `is_question`
- `contains_commitment`
- `contains_time_reference`
- `contains_followup_signal`
- `priority_hint`

These can be heuristic-only at first.

## Required vs optional

### Required for v1

- `schema_version`
- `message_uid`
- `account_id`
- `export_date`
- `ingested_at`
- `chat.chat_id`
- `chat.chat_type`
- `message.message_id`
- `message.date`
- `sender.sender_id` or `sender.is_self`
- `sender.is_self`
- `direction`
- `text.raw` or `attachments`

### Strongly recommended

- `chat.chat_key`
- `chat.chat_title`
- `message.reply_to_message_id`
- `message.edit_date`
- `text.normalized`
- `derived.contains_commitment`
- `derived.contains_time_reference`
- `derived.is_question`

## Rules for normalization

- Serialize all Telegram IDs as **strings** except `message_id`, which may stay numeric.
- Use **UTC ISO-8601** timestamps everywhere.
- Normalize blank strings to `null` for usernames and optional labels.
- Keep `raw` text untouched except safe decoding.
- Put heuristic enrichments under `derived`, not inside Telegram-native structures.

## Why this is the best canonical grain

One line per message event gives OpenClaw everything it needs for:
- daily summaries
- unanswered inbound tracking
- commitment/follow-through detection
- people-level memory building
- chat-level reconstruction when needed

Chat snapshots are useful as derived artifacts, but they are worse as the source of truth because they are harder to de-duplicate and harder to incrementally reprocess.
