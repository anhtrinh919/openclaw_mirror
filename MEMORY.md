# MEMORY.md — Long-Term Memory

Curated: key setups, lessons, decisions. Updated periodically from daily notes.

---

## Key Setups

### gog (Google Workspace)
- Auth tokens: keyring at `/home/openclaw/.config/gogcli/keyring/`; backup token at `/data/workspace/gog_auth_backup.json`
- Client secret: `/data/workspace/gog_client_secret.json`
- Account: `tuananhtrinh919@gmail.com` · Password env: `GOG_KEYRING_PASSWORD=openclaw_secure_2026`
- Binary: `/home/linuxbrew/.linuxbrew/bin/gog` (fallback: `gog`)
- Services: gmail, calendar, drive, sheets, tasks, contacts, docs, slides, people, forms, appscript
- Container restarts wipe keyring → always run `SOP-GOG-AUTH.md` Step 0 before gog workflows.
- **Rule:** never duplicate raw gog auth commands across SOPs; point to `SOP-GOG-AUTH.md`.

### Telegram send monitor
- Script: `/data/workspace/ops/telegram-send-monitor/monitor_scheduled_telegram_failures.py`
- State: `/data/workspace/ops/telegram-send-monitor/state.json`
- Incidents: `/data/workspace/ops/telegram-send-monitor/incidents.jsonl`
- Contract: alerts on new failed scheduled sends only; deduped by `jobId:runAtMs`.
- Heartbeat: run with `--print-alert`; empty stdout = no alert.

---

## Critical Lessons

**Timezone:** Always Vietnam time (UTC+7) unless specified.

**Telegram sends (2026-03-12):**
- `sessions_send` to a group is unreliable — can return `RELAY_OK` while nothing posts.
- Use: `openclaw message send --channel telegram --target <chatId> --message '<text>' --json`
- Success proof: `payload.ok=true` + real `chatId` + `messageId`.

**Cron schema:**
- `sessionTarget: "main"` → `payload.kind: "systemEvent"`
- `sessionTarget: "isolated"` → `payload.kind: "agentTurn"`
- Required fields: `name`, `schedule`, `sessionTarget`, `payload`

**Railway/Container:**
- No direct SSH; gateway behind wss:// proxy on port 443.
- Session transcripts: `/data/.openclaw/agents/main/sessions/*.jsonl`

---

## Boss profile (high-signal)

### Gaming
- "Dad gamer" — 25 years of gaming history. Platforms: PC, Switch, PS5, PSVR2, Android emulators.
- ~99% single-player. Exception: kid-friendly co-op with his son.

Last updated: 2026-03-23
