# Session: 2026-03-16 02:59:23 UTC

- **Session Key**: agent:main:main
- **Session ID**: a1d708dc-17a2-47d7-be6c-f23d27a55f2e
- **Source**: discord

## Conversation Summary

assistant: ✅ New session started · model: openrouter/x-ai/grok-4.1-fast
user: A new session was started via /new or /reset. Execute your Session Startup sequence now - read the required files before responding to the user. Then greet the user in your configured persona, if one is provided. Be yourself - use your defined voice, mannerisms, and mood. Keep it to 1-3 sentences and ask what they want to do. If the runtime model differs from default_model in the system prompt, mention the default model. Do not mention internal steps, files, tools, or reasoning.
Current time: Monday, March 16th, 2026 — 2:55 AM (UTC) / 2026-03-16 02:55 UTC
assistant: Hey Boss, SpongeBot ready— what's the mission today? 🫧
user: Conversation info (untrusted metadata):
```json
{
  "message_id": "1482935771106381901",
  "sender_id": "556701373681631291",
  "sender": "anhtrinh919",
  "timestamp": "Mon 2026-03-16 02:57 UTC"
}
```

Sender (untrusted metadata):
```json
{
  "label": "anhtrinh919 (556701373681631291)",
  "id": "556701373681631291",
  "name": "anhtrinh919",
  "username": "anhtrinh919",
  "tag": "anhtrinh919"
}
```

i updated main repo on https://github.com/anhtrinh919/openclaw_mirror . possible to pull main to railway workspace (make sure edit/deletion are implemented)?
assistant: Pulled main from mirror repo—workspace now matches (edits/deletions applied via clean+checkout). 🫧
user: [media attached: /data/.openclaw/media/inbound/94437626-8e5c-4b76-8a4c-c8ce478a251c.md (text/markdown) | /data/.openclaw/media/inbound/94437626-8e5c-4b76-8a4c-c8ce478a251c.md]
To send an image back, prefer the message tool (media/path/filePath). If you must inline, use MEDIA:https://example.com/image.jpg (spaces ok, quote if needed) or a safe relative path like MEDIA:./image.jpg. Avoid absolute paths (MEDIA:/...) and ~ paths — they are blocked for security. Keep caption in the text body.
Conversation info (untrusted metadata):
```json
{
  "message_id": "1482936175915171851",
  "sender_id": "556701373681631291",
  "sender": "anhtrinh919",
  "timestamp": "Mon 2026-03-16 02:58 UTC"
}
```

Sender (untrusted metadata):
```json
{
  "label": "anhtrinh919 (556701373681631291)",
  "id": "556701373681631291",
  "name": "anhtrinh919",
  "username": "anhtrinh919",
  "tag": "anhtrinh919"
}
```

[Discord anhtrinh919 user id:556701373681631291 +29s Mon 2026-03-16 02:58 UTC] verify - confirm that workspace AGENTS.md is exactly like attached file.

<file name="94437626-8e5c-4b76-8a4c-c8ce478a251c.md" mime="text/markdown">
# AGENTS.md - Workspace Operating Rules

This folder is home.

## Session startup
SOUL.md, USER.md, IDENTITY.md, MEMORY.md are **auto-injected by runtime** — do not re-read them.

Read manually, in order:
1. `contacts.md`
2. `memory/YYYY-MM-DD.md` (**yesterday + today only**)

Read **on demand** (not at startup):
- `SOP.md` — when a trigger or SOP-related request fires
- `SKILLS.md` — when Boss asks for a skill or you need to discover one
- `TEAM.md` / `multi-agent.md` — when `@team` fires or you decide to delegate

## Core rules
- Follow `contacts.md` for language and speaking style. Identify recipient from trusted inbound `chat_id`.
- Default language: **Vietnamese**; Boss stays **English**.
- For prior work, decisions, dates, preferences: `memory_search` first, then `memory_get`.
- For time-sensitive facts: verify with web tools.
- When editing an important `.md`: read full file first, then write full updated file.
- Google Workspace auth: follow `sops/SOP-GOG-AUTH.md` only.
- Telegram cron/workflow sends: use `ops/send_telegram_verified.sh`, require JSON success proof.
- Sub-agent fails → retry with main agent, don't just relay the failure.

## New-user onboarding
For non-Boss direct chats:
- Introduce: "Xin chào! Mình là SpongeBot, trợ lý AI của Tuấn Anh."
- Ask name, preferred xưng hô, need, and language preference.
- Log to `contacts.md`.

## Hard routes
- **Trade printing:** `chat_id = telegram:-5194157539` + Excel attachment → `sops/SOP-TRADE-PRINTING.md`
- **Leave requests:** `chat_id = telegram:-4121104521` + text contains `nghỉ` → `sops/SOP-LEAVE-REQUESTS.md`
- Keep hard-routed workflow active until resolved or topic clearly changes.

## Team mode
- Delegate proactively when a task is hard, lengthy, or out of scope.
- Full policy: `multi-agent.md` | Routing: `TEAM-ROUTING.md`

## Triggers
- `@think` → model override: `openai-codex/gpt-5.3-codex`
- `@plan` → diagnostic mode only; same override; no real-world actions
- `@qc` → spawn QC sub-agent: `openai-codex/gpt-5.2`
- `@do` → autonomous mode in main session
- `@doc` → docs dive + web search in main session
- `@task` → update `task.md` + schedule reminder via `sops/SOP-TASKS.md`
- `@team` → explicit multi-agent orchestration
- `@f5` → reread all baseline files, reset behavior, continue
</file>
assistant: AGENTS.md now matches attached exactly. 🫧
