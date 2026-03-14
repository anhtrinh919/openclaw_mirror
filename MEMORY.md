# MEMORY.md - Long-Term Memory

This is my curated long-term memory: key events, setups, lessons, and decisions. Updated periodically from daily notes.

---

## Key Setups

### gog
- **Gog Auth - 2026-02-25 / refreshed 2026-03-13:** Tokens live in keyring at `/home/openclaw/.config/gogcli/keyring/` and the persistent backup token lives at `/data/workspace/gog_auth_backup.json`.
- **Client secret:** `/data/workspace/gog_client_secret.json`
- **Account:** `tuananhtrinh919@gmail.com`
- **Password env:** `GOG_KEYRING_PASSWORD=openclaw_secure_2026`
- **Canonical SOP:** `/data/workspace/sops/SOP-GOG-AUTH.md`
- **Canonical binary:** `/home/linuxbrew/.linuxbrew/bin/gog` (fallback: `gog`)
- **Current intended services:** gmail, calendar, drive, sheets, tasks, contacts, docs, slides, people, forms, appscript
- Container restarts can wipe the keyring state, so Google workflows should follow `SOP-GOG-AUTH.md` Step 0 before using `gog`.
- **Critical rule:** do not duplicate raw gog auth restore commands across SOPs or cron prompts; point them to `SOP-GOG-AUTH.md` instead.

### Telegram scheduled-send heartbeat monitor
- **Added 2026-03-14:** heartbeat-side monitor lives at `/data/workspace/ops/telegram-send-monitor/monitor_scheduled_telegram_failures.py`.
- **State:** `/data/workspace/ops/telegram-send-monitor/state.json`
- **Incidents log:** `/data/workspace/ops/telegram-send-monitor/incidents.jsonl`
- **Contract:** it should alert only on **new** failed scheduled Telegram sends by inspecting `openclaw cron list --json` and `openclaw cron runs --id ...`, then deduping by `jobId:runAtMs`.
- **Heartbeat wiring:** `HEARTBEAT.md` should run the script with `--print-alert`; empty stdout means no alert.

---

## Critical Lessons

**Timezone:** ALWAYS use Vietnam time (UTC+7, Asia/Ho_Chi_Minh) for all schedules unless specified otherwise.

**Config & Gateway:**
- ⚠️ NEVER self-edit config or restart gateway - Boss handles this

**Telegram send protocol - 2026-03-12:**
- ⚠️ `sessions_send` to a Telegram group session is **NOT** reliable for posting a real Telegram message.
- Group-session relay patterns can return `RELAY_OK` / show internal echoes while **nothing is actually posted** to Telegram.
- For real outbound Telegram messages, use the **direct send path**: `openclaw message send --channel telegram --target <chatId> --message '<text>' --json`
- Success proof must be the plugin send result with `payload.ok=true`, real `chatId`, and `messageId` (example: group `-232384245` succeeded with messageId `3222`).
- If needed, verify against gateway logs for `action: "send"` rather than session transcripts alone.

**Cron Schema:** Quick reference:
- `sessionTarget: "main"` → `payload.kind: "systemEvent"`
- `sessionTarget: "isolated"` → `payload.kind: "agentTurn"`
- All 4 fields required: `name`, `schedule`, `sessionTarget`, `payload`

**Railway/Container:**
- Railway doesn't support direct SSH; gateway is behind wss:// proxy on port 443.
- Node connections use WebSocket, not raw SSH.
- **Session transcripts:** Stored at `/data/.openclaw/agents/main/sessions/*.jsonl` (JSONL format). Use for cross-channel session analysis in cron jobs.

---

## Contacts / preferences (high-signal only)

### Tuan Anh (Boss) — gaming profile
- “Dad gamer” — played most popular games over the last ~25 years.
- Hardware/platforms: gaming PC, Switch, PS5, PSVR2; emulators on Android.
- Playstyle: ~99% single-player.
- Multiplayer exception: kid-friendly co-op / family games played with his son.

Last updated: 2026-03-14
