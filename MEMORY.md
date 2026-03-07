# MEMORY.md - Long-Term Memory (Token-lean)

Curated, evergreen memory only.
Rule: **MEMORY.md stores pointers + IDs + non-obvious gotchas.** Detailed procedures live in SOPs under `/data/workspace/sops/`.

---

## Key Setups (must-know)

### Google Workspace (gog)
- Account: `tuananhtrinh919@gmail.com`
- **Keyring is ephemeral** (container restarts wipe it). Restore with:
  - `GOG_KEYRING_PASSWORD=openclaw_secure_2026 gog auth credentials set /data/workspace/gog_client_secret.json --no-input && GOG_KEYRING_PASSWORD=openclaw_secure_2026 gog auth tokens import /data/workspace/gog_auth_backup.json --no-input`
- Client secret: `/data/workspace/gog_client_secret.json`
- Token backup: `/data/workspace/gog_auth_backup.json`

### Telegram channel (gateway)
- Symptom: Telegram API calls fail with **401 Unauthorized** (e.g., `setMyCommands`, `deleteWebhook`, `deleteMyCommands`) → usually means **bot token mismatch/invalid**.
- Fix:
  1) Regenerate token in **@BotFather** (for the correct bot)
  2) Update `channels.telegram.botToken` (never paste token into chat)
  3) `openclaw gateway restart`
  4) Verify: `openclaw status --deep`

### Printing orders (Trâm Anh)
- Canon sheet: `1-O_B27mSDqfEZemD27bPNmWtfnV3cW51LeClBmSwB6c`
- SOP: `/data/workspace/sops/SOP-TRADE-PRINTING.md`

### Leave requests (LC Marketing)
- SOP: `/data/workspace/sops/SOP-LEAVE-REQUESTS.md`
- Tracking file: `/data/workspace/leave_requests.json`

### Task system (Sheet + Google Tasks)
- Canonical tracker sheet: **“SpongeBot — Task Tracker”**
  - SpreadsheetId: `1Q_MUiIcsogdJcTBh-Dfs8jNh_WLEBpFt4klwuFKh0Po`
- Boss view list: Google Tasks list **“Boss — SpongeBot”**
  - tasklistId: `UWJRX09xMVhsb1dubk9tOQ`
- Daily sync cron (Tasks → Sheet status): `tasks-sync-google-tasks-to-sheet-daily` (id `671497b7-ebbb-4c5a-be46-a32b22ec550e`) @ **18:00 Asia/Ho_Chi_Minh**
- SOP: `/data/workspace/sops/SOP-TASKS.md`

### Dust relay integration (dust.tt)
- SOP: `/data/workspace/sops/SOP-DUST-RELAY.md`
- Relay script: `/data/workspace/dust_relay.py`
- Profile: `/data/workspace/dust_profile.json`
- API key file: `/data/workspace/.dust_api_key` (chmod 600; never paste)
- Agent configId: `7z5y4GH8Dz` (Dust @lc-main workspace `Jb3tKIEjjE`)
- Known limitation: some *personal* connectors may not work via workspace API key; shared/workspace connectors usually OK.

### Multi-agent operating system (multi-agent-v1)
- Operating spec (v1): `/data/workspace/multi-agent-operating-spec-v1.md`
- Planned roster / agentIds:
  - `main` (SpongeBot, orchestrator)
  - `sandy` (Builder)
  - `glados` (Data)
  - `squid` (Architect/QC)
- Shared area: `/data/workspace/shared/` (templates in `/data/workspace/shared/templates/`)
- Deliverables root + templates: `/data/workspace/deliverables/` (templates in `/data/workspace/deliverables/_template/`)
- Ops helpers: `/data/workspace/ops/multi-agent-v1/` (`apply-multi-agent-config.js`, `new-task.sh`)
- Per-agent workspaces (seeded):
  - `/data/.openclaw/workspace-sandy`
  - `/data/.openclaw/workspace-glados`
  - `/data/.openclaw/workspace-squid`

---

## Recurring reports / reminders (pointers)

- Morning report SOP: `/data/workspace/sops/SOP-MORNING-REPORT.md`
- News watcher state: `/data/workspace/news_watch_state.json`

---

## Critical Lessons / Defaults

### Timezone
- Default timezone for schedules: **Asia/Ho_Chi_Minh (UTC+7)** unless specified otherwise.

### Runtime timeouts (OpenClaw config)
- Defaults were increased to **30 minutes**:
  - `agents.defaults.timeoutSeconds = 1800`
  - `tools.exec.timeoutSec = 1800`
- Note: config changes typically require a **gateway restart**.

### Web search tool (Brave) parameter gotchas
- `web_search.country` is a strict enum (e.g., `US`, `GB`, `ALL`). **`VN` is invalid**.
- `web_search.ui_lang` is also a strict enum (e.g., `en-US`). **`vi-VN` is invalid**.
- For Vietnamese content: set `search_lang: "vi"`, but keep `country/ui_lang` to supported values (often `ALL` + `en-US`).

### Plugins / extensions safety
- If `plugins.allow` is empty, non-bundled plugins may auto-load. Prefer an explicit allowlist.
- Known noisy issue seen: `zalouser` duplicate plugin id + failing load due to missing module `zca-js`.

### Session transcript access (tooling constraint)
- `sessions_history` visibility may be restricted to the **current session tree**.
- For cross-session review/debugging, use transcript files under:
  - `/data/.openclaw/agents/main/sessions/*.jsonl`

### Models
- ⚠️ GLM-5 (`openrouter/z-ai/glm-5`) is broken (errors).
- Preferred models:
  - `@think`, `@deepthink`, `@think + @do` → `openai-codex/gpt-5.3-codex`
  - `@qc` → `openai-codex/gpt-5.2`
- **Cron rule (Boss instruction):** future cron jobs default to **`openai-codex/gpt-5.2`**; use OpenRouter **only if Boss explicitly asks**.

### Cron schema (non-negotiable)
- `sessionTarget: "main"` → `payload.kind: "systemEvent"`
- `sessionTarget: "isolated"` → `payload.kind: "agentTurn"`
- Required fields: `name`, `schedule`, `sessionTarget`, `payload`

### Agent-first harness engineering (reference)
- Source article: OpenAI — *Harness engineering: leveraging Codex in an agent-first world*  
  https://openai.com/index/harness-engineering/
- Keep `AGENTS.md` as a concise map; put deep/volatile rules in structured docs with CI checks.
- Scale quality via enforced invariants + feedback loops, not ad-hoc prompt size.
- Prefer continuous cleanup (“garbage collection”) to prevent agent-generated code/process drift.
- Detailed notes snapshot: `/data/workspace/memory/2026-03-05.md`

---

## Contacts / preferences (high-signal only)

- Boss: Tuan Anh — Telegram `171900099`
  - Staycation prefs (when asked): **ăn uống ngon, view đẹp, ít người**; if **1-night trip** then prefer driving **≤ ~3h/way**.
  - Prefers **clear & direct tone**, especially for “No” answers: start with **“No — <short reason>.”** then the constraint + best alternative/next step; if relevant, explicitly confirm status (e.g., “Not timed out…”).
- Trâm Anh (printing): Telegram `6402311566`
- Cô Nhàn: Telegram `158396493`
  - Prefers **private reminders** (nhắc riêng)

---

## Where to look next

- SOP index: `/data/workspace/SOP.md`
- Contacts directory: `/data/workspace/contacts.md`
- Disaster recovery / restore runbook: `/data/workspace/revive.md`

---

Last updated: 2026-03-06
