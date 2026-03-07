# Decision Guide: Cron vs Heartbeat

## Quick Decision Table

| Scenario | Tool | Why |
|----------|------|-----|
| "Remind me in 20 minutes" | Cron (`at`) | Exact one-shot |
| "Send report at 9 AM daily" | Cron (`cron`) | Exact time |
| "Check inbox every 30 min" | Heartbeat | Loose timing, context-aware |
| "Weekly analysis every Monday" | Cron (`cron`) | Standalone task |
| "Monitor calendar for events" | Heartbeat | Context-aware batching |
| "Ping me when task done" | Neither (immediate) | Event-driven |

## Cron: Use When

1. **Exact timing required** - "9:00 AM sharp", not "around 9"
2. **One-shot reminders** - "Remind me in 20 minutes"
3. **Standalone tasks** - Doesn't need conversation context
4. **Different model** - Heavy task needs smarter/cheaper model
5. **Noisy output** - Would clutter main session history
6. **External delivery** - Output goes to specific channel/person

## Heartbeat: Use When

1. **Multiple periodic checks** - Inbox + calendar + weather in one turn
2. **Context-aware decisions** - Need recent conversation history
3. **Loose timing OK** - 30 min drift is fine
4. **Smart suppression** - Only alert when something matters
5. **Cost efficient** - One agent turn vs multiple cron jobs

## Session Target Decision

### Main Session (`sessionTarget: "main"`)

**Use when:**
- Need main session context
- Want reminder in conversation flow
- Task is simple system event

**Requirements:**
- `payload.kind: "systemEvent"`
- `payload.text: "..."`

### Isolated Session (`sessionTarget: "isolated"`)

**Use when:**
- Standalone task, no context needed
- Different model/thinking needed
- Output should go elsewhere
- Task might be noisy

**Requirements:**
- `payload.kind: "agentTurn"`
- `payload.message: "..."`
- Optional: `delivery` config

## Timezone Conversion

User usually speaks in local time. Convert to UTC for cron.

**Vietnam (UTC+7):**
- 12:00 PM VN = 05:00 UTC
- 9:00 AM VN = 02:00 UTC
- 7:00 PM VN = 12:00 UTC

**Formula:** `UTC = Local - Offset`
- Vietnam: `UTC = VN - 7`

**In JSON:**
```json
{
  "schedule": {
    "kind": "cron",
    "expr": "0 5 * * *",
    "tz": "Asia/Ho_Chi_Minh"
  }
}
```

Or use explicit UTC:
```json
{
  "schedule": {
    "kind": "at",
    "at": "2026-02-25T05:15:00Z"
  }
}
```

## Delivery Decision

| Delivery Mode | Use When |
|---------------|----------|
| `none` | Silent execution, agent handles output |
| `announce` | Send summary to specific channel/person |
| `webhook` | POST to external service |

## Common Mistakes

1. ❌ Using heartbeat for "exactly 9:00 AM"
2. ❌ Using cron for "check stuff periodically"
3. ❌ Main session with agentTurn payload
4. ❌ Isolated session with systemEvent payload
5. ❌ Forgetting timezone conversion
6. ❌ Missing required JSON fields

## Example Scenarios

### "Remind me to call mom at 7 PM"

→ **Cron, one-shot, main session**

```json
{
  "name": "call-mom",
  "schedule": { "kind": "at", "at": "2026-02-25T12:00:00Z" },
  "sessionTarget": "main",
  "payload": { "kind": "systemEvent", "text": "Time to call mom!" }
}
```

### "Send a test message to group at 12:15"

→ **Cron, one-shot, isolated with message tool**

```json
{
  "name": "test-msg",
  "schedule": { "kind": "at", "at": "2026-02-25T05:15:00Z" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Use message tool: action=send, channel=telegram, to=-5187233312, message='Test!'"
  }
}
```

### "Check my inbox every morning"

→ **Cron, recurring, isolated, announce**

```json
{
  "name": "inbox-check",
  "schedule": { "kind": "cron", "expr": "0 7 * * *", "tz": "Asia/Ho_Chi_Minh" },
  "sessionTarget": "isolated",
  "payload": { "kind": "agentTurn", "message": "Check inbox, summarize urgent items." },
  "delivery": { "mode": "announce", "channel": "telegram", "to": "171900099" }
}
```

### "Monitor my calendar and inbox throughout the day"

→ **Heartbeat (add to HEARTBEAT.md)**

```markdown
# HEARTBEAT.md
- Check calendar for events in next 2h
- Check inbox for urgent emails
- Alert if anything needs attention
```
