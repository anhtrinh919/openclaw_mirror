# MEMORY.md - Long-Term Memory

This is my curated long-term memory: key events, setups, lessons, and decisions. Updated periodically from daily notes.

---

## Key Setups

### gog
- **Gog Auth - 2026-02-25:** Tokens stored in keyring at `/home/openclaw/.config/gogcli/keyring/` (NOT a flat file — disappears on container restart!). Client secret at `/data/workspace/gog_client_secret.json`. Backup token (with `email` field): `/data/workspace/gog_auth_backup.json`. Account: `tuananhtrinh919@gmail.com`. Services: calendar, drive, gmail, sheets. Use `GOG_KEYRING_PASSWORD=openclaw_secure_2026`.
- Container restarts wipe the gog keyring → must re-import tokens manually.
- **⚠️ RESTORE AFTER RESTART:** `GOG_KEYRING_PASSWORD=openclaw_secure_2026 gog auth credentials /data/workspace/gog_client_secret.json && GOG_KEYRING_PASSWORD=openclaw_secure_2026 gog auth tokens import /data/workspace/gog_auth_backup.json`

---

## Critical Lessons

**Timezone:** ALWAYS use Vietnam time (UTC+7, Asia/Ho_Chi_Minh) for all schedules unless specified otherwise.

**Config & Gateway:**
- ⚠️ NEVER self-edit config or restart gateway - Boss handles this

**Cron Schema:** Quick reference:
- `sessionTarget: \"main\"` → `payload.kind: \"systemEvent\"`
- `sessionTarget: \"isolated\"` → `payload.kind: \"agentTurn\"`
- All 4 fields required: `name`, `schedule`, `sessionTarget`, `payload`

**Railway/Container:**
- Railway doesn't support direct SSH; gateway is behind wss:// proxy on port 443.
- Node connections use WebSocket, not raw SSH.
- **Session transcripts:** Stored at `/data/.openclaw/agents/main/sessions/*.jsonl` (JSONL format). Use for cross-channel session analysis in cron jobs.