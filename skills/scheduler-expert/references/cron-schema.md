# Cron JSON Schema Reference

All field names are case-sensitive. Use exact strings.

## Required Fields (ALL jobs)

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique identifier for the job |
| `schedule` | object | When to run (see schedule kinds) |
| `sessionTarget` | string | `"main"` or `"isolated"` |
| `payload` | object | What to run (see payload kinds) |

## Schedule Kinds

### Kind: `at` (one-shot)

```json
{
  "kind": "at",
  "at": "2026-02-25T12:15:00Z"
}
```

- ISO 8601 timestamp
- No timezone = treated as UTC
- Auto-deletes after success (set `deleteAfterRun: false` to keep)

### Kind: `every` (interval)

```json
{
  "kind": "every",
  "everyMs": 3600000
}
```

- `everyMs` in milliseconds
- 60000 = 1 min, 3600000 = 1 hour, 86400000 = 1 day

### Kind: `cron` (expression)

```json
{
  "kind": "cron",
  "expr": "0 7 * * *",
  "tz": "Asia/Ho_Chi_Minh"
}
```

- 5-field cron: `MIN HOUR DOM MONTH DOW`
- `tz` is optional (defaults to host TZ)
- Examples:
  - `"0 7 * * *"` = daily at 7:00
  - `"0 9 * * 1"` = every Monday at 9:00
  - `"*/15 * * * *"` = every 15 minutes

## Payload Kinds

### Kind: `systemEvent` (main session ONLY)

```json
{
  "kind": "systemEvent",
  "text": "Reminder: do the thing"
}
```

- MUST use with `sessionTarget: "main"`
- Injects text as system event into main session
- Agent sees it during next heartbeat

### Kind: `agentTurn` (isolated session ONLY)

```json
{
  "kind": "agentTurn",
  "message": "Check inbox and summarize urgent emails.",
  "model": "openrouter/z-ai/glm-5",
  "thinking": "off",
  "timeoutSeconds": 120
}
```

- MUST use with `sessionTarget: "isolated"`
- `message` (required): Prompt for the agent
- `model` (optional): Model override
- `thinking` (optional): `"off"`, `"low"`, `"medium"`, `"high"`
- `timeoutSeconds` (optional): Max run time

## Delivery Config (isolated jobs)

```json
{
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "to": "-5187233312",
    "bestEffort": true
  }
}
```

| Field | Values | Description |
|-------|--------|-------------|
| `mode` | `"none"`, `"announce"`, `"webhook"` | How to deliver output |
| `channel` | `"telegram"`, `"whatsapp"`, `"discord"`, `"slack"`, `"signal"`, `"last"` | Target channel |
| `to` | string | Chat/user ID or webhook URL |
| `bestEffort` | boolean | Don't fail job if delivery fails |

### Delivery Modes

- **`none`**: Silent run, no delivery
- **`announce`**: Send summary to channel (isolated only)
- **`webhook`**: POST to URL (main or isolated)

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `true` | Job active state |
| `deleteAfterRun` | boolean | `true` for `at` | Delete after success |
| `wakeMode` | string | `"now"` | `"now"` or `"next-heartbeat"` |
| `agentId` | string | - | Bind to specific agent |

## Full Examples

### Simple Reminder (main session)

```json
{
  "name": "standup-reminder",
  "schedule": { "kind": "at", "at": "2026-02-25T09:55:00Z" },
  "sessionTarget": "main",
  "payload": { "kind": "systemEvent", "text": "Standup in 5 minutes!" },
  "wakeMode": "now",
  "deleteAfterRun": true
}
```

### Daily Briefing (isolated)

```json
{
  "name": "daily-brief",
  "schedule": { "kind": "cron", "expr": "0 7 * * *", "tz": "Asia/Ho_Chi_Minh" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Generate morning briefing: calendar, inbox, weather. Send summary to telegram.",
    "timeoutSeconds": 180
  },
  "delivery": { "mode": "announce", "channel": "telegram", "to": "171900099" }
}
```

### Telegram Message Send (isolated with message tool)

```json
{
  "name": "send-telegram-msg",
  "schedule": { "kind": "at", "at": "2026-02-25T05:15:00Z" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Use the message tool: action=send, channel=telegram, to=-5187233312, message='Scheduled message from SpongeBot! 🫧'"
  },
  "delivery": { "mode": "none" }
}
```

### Interval Check (every 2 hours)

```json
{
  "name": "inbox-check",
  "schedule": { "kind": "every", "everyMs": 7200000 },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Check inbox for urgent emails. Announce if any found."
  },
  "delivery": { "mode": "announce", "channel": "telegram", "to": "171900099" }
}
```
