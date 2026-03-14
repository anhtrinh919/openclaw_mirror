# Integration With the Current Telethon Exporter

This folder already has a working exporter at:

```text
scripts/export_telegram_jsonl.py
```

That exporter currently writes **one raw JSONL file per dialog per day** with records like:
- `dialog_id`
- `dialog_name`
- `message_id`
- `date_utc`
- `sender_id`
- `text`
- `raw_text`
- `reply_to_msg_id`
- `post`
- `out`
- `mentioned`
- `media_type`

## Best next step

Do **not** replace the exporter first.

Instead, add a normalization pass that reads the existing raw per-dialog files and produces:
- canonical `all-chats.jsonl`
- optional `derived/per-chat/*.jsonl`
- `derived/daily-summary-input.json`
- `derived/follow-through-candidates.json`

That gives OpenClaw the good schema without breaking the current working extraction path.

## Raw-to-normalized mapping

| Current raw field | Recommended normalized field |
|---|---|
| `dialog_id` | `chat.chat_id` |
| `dialog_name` | `chat.chat_title` |
| file stem / dialog metadata | `chat.chat_key`, `chat.chat_type` if derivable |
| `message_id` | `message.message_id` |
| `date_utc` | `message.date` |
| `sender_id` | `sender.sender_id` |
| `out` | `sender.is_self` and `direction` |
| `text` / `raw_text` | `text.raw` |
| normalized lowercased text | `text.normalized` |
| `reply_to_msg_id` | `message.reply_to_message_id` |
| `media_type` | `attachments[0].kind` or lightweight attachment placeholder |
| `post` | can help identify channel/broadcast semantics |
| `mentioned` | `text.has_mentions` |

## Minimal normalization rules for the existing exporter

### `direction`

```text
out=true  -> outbound
out=false -> inbound
post=true -> system or channel-style, depending on actual chat type
```

### `sender.is_self`

```text
sender.is_self = bool(out)
```

### `message_uid`

```text
tgacct:<account_id>:chat:<dialog_id>:msg:<message_id>
```

### `attachments`

The current exporter only records `media_type`, not file metadata. For now, represent it as lightweight metadata:

```json
[
  {
    "kind": "MessageMediaDocument",
    "attachment_key": "telegram-raw-media-not-exported"
  }
]
```

Later, if binary download is added, replace with real attachment metadata.

## Recommended implementation order

1. keep `scripts/export_telegram_jsonl.py` as-is
2. add a normalizer that merges raw per-dialog files into canonical `all-chats.jsonl`
3. run the two derived builders on the canonical file
4. optionally upgrade the exporter later to write the canonical schema directly

## Why this is safer

- no auth flow changes
- no extractor rewrite risk
- OpenClaw gets the schema it actually wants
- migration can happen incrementally
