# TEAM-ROUTING.md — Real Team Routing Map

This file documents what team routing is **actually** live right now, by surface.

---

## Current truth

### Telegram

**Direct named-agent chats on Telegram are NOT currently live** with the current single Telegram bot/account setup.

What works on Telegram right now:
- Boss DMs **main** (`SpongeBot`)
- `main` can delegate internally to named agents using `sessions_send`
- canonical internal team session keys:
  - `agent:sandy:main`
  - `agent:glados:main`
  - `agent:squid:main`

So Telegram team mode should work as:
- **user-facing route:** Boss → `main`
- **internal route:** `main` → named agents via `sessions_send`
- **delivery route:** `main` integrates results and replies back to Boss on Telegram

This is the canonical Telegram team path.

### Discord

**Direct named-agent routing is live on Discord.**

Current bindings:
- `main` ↔ Discord `accountId=main`
- `sandy` ↔ Discord `accountId=sandy`
- `glados` ↔ Discord `accountId=glados`

Observed direct Discord sessions already exist for Boss:
- `agent:main:discord:direct:556701373681631291`
- `agent:sandy:discord:direct:556701373681631291`
- `agent:glados:discord:direct:556701373681631291`

So Boss can talk directly to those agents on Discord.

---

## Recommended operating model

### For Telegram
- Boss asks `main`
- `main` delegates to:
  - `agent:sandy:main`
  - `agent:glados:main`
  - `agent:squid:main`
- `main` returns the integrated result to Telegram

### For Discord
- Boss can DM:
  - `main`
  - `sandy`
  - `glados`
- Workers must still follow team coordination rules from `/data/workspace/multi-agent.md`

---

## Why direct named-agent Telegram is not live yet

With current setup, Telegram routing is documented cleanly for:
- one Telegram bot/account per agent, OR
- Telegram forum topic routing with `agentId` per topic

Current system only has the default Telegram account bound to `main`.
There are no live Telegram account bindings for:
- `sandy`
- `glados`
- `squid`

So Boss cannot directly DM those named agents on Telegram yet.

---

## What would be required to make direct named-agent Telegram work

### Option A — one Telegram bot per agent
Need:
- one BotFather bot token for each agent
- config bindings like:

```json5
{
  "bindings": [
    { "agentId": "main",   "match": { "channel": "telegram", "accountId": "default" } },
    { "agentId": "sandy",  "match": { "channel": "telegram", "accountId": "sandy" } },
    { "agentId": "glados", "match": { "channel": "telegram", "accountId": "glados" } }
  ],
  "channels": {
    "telegram": {
      "accounts": {
        "default": { "botToken": "<MAIN_BOT_TOKEN>" },
        "sandy":   { "botToken": "<SANDY_BOT_TOKEN>" },
        "glados":  { "botToken": "<GLADOS_BOT_TOKEN>" }
      }
    }
  }
}
```

Pros:
- clean direct DMs per agent
- user-visible separate identities

Cons:
- needs config changes
- needs more bots/tokens
- needs gateway reload/restart handled by Boss

### Option B — Telegram forum topic routing
Need:
- a Telegram forum supergroup
- one topic per agent
- topic config with `agentId`

Best for structured team channels, not direct DM.

---

## Canonical instruction for `main`

When on Telegram, and team delegation is needed:
- do **not** rely on `sessions_spawn(agentId=...)` for named teammates
- use `sessions_send` to the persistent named sessions instead:
  - `agent:sandy:main`
  - `agent:glados:main`
  - `agent:squid:main`

This avoids the broken/unsupported named-spawn path in this surface.

---

Last updated: 2026-03-13 by SpongeBot 🫧
