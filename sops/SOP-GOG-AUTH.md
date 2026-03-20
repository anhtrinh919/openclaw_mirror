# SOP-GOG-AUTH — Canonical Google Workspace Auth for `gog`

Use this as the **single source of truth** for all `gog` auth handling.

If any workflow needs Gmail / Calendar / Sheets / Drive / Tasks / other Google Workspace access, it should **reference this SOP** instead of duplicating auth commands.

---

## Purpose

This SOP exists because `gog` auth can drift or break in 3 common ways:
- container restart wipes keyring state
- stale backup token gets re-imported
- refresh token gets expired/revoked

This SOP standardizes:
1. restore after restart
2. full re-auth
3. backup export
4. verification

---

## Current Workspace Auth Facts

- **Account:** `tuananhtrinh919@gmail.com`
- **Client secret:** `/data/workspace/gog_client_secret.json`
- **Backup token:** `/data/workspace/gog_auth_backup.json`
- **Keyring dir:** `/home/openclaw/.config/gogcli/keyring/`
- **Password env:** `GOG_KEYRING_PASSWORD=openclaw_secure_2026`
- **Canonical binary:** `/home/linuxbrew/.linuxbrew/bin/gog`
- **Fallback binary:** `gog`

Current intended service set:
- `gmail`
- `calendar`
- `drive`
- `sheets`
- `tasks`
- `contacts`
- `docs`
- `slides`
- `people`
- `forms`
- `appscript`

---

## Rule Zero

**Do not duplicate raw restore commands across SOPs or cron prompts.**

Instead, point to:
- `/data/workspace/sops/SOP-GOG-AUTH.md`

If a job needs Google access, instruct it to:
1. read this SOP first
2. run **Step 0** before API calls

---

## Step 0 — Restore Gog Auth (standard pre-flight)

Run this before any `gog` API usage in automations, cron jobs, or isolated sessions:

```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog auth credentials set /data/workspace/gog_client_secret.json --no-input && \
GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog auth tokens import /data/workspace/gog_auth_backup.json --force --no-input
```

If `/home/linuxbrew/.linuxbrew/bin/gog` is unavailable, fallback to `gog`.

Retry once if restore fails.

---

## Step 1 — Quick Health Check

After restore, verify with at least one lightweight live probe for the services you need.

Recommended probes:

### Gmail
```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog gmail search \"is:unread\" --account tuananhtrinh919@gmail.com --max 1 --json --no-input
```

### Calendar
```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog calendar events --today --account tuananhtrinh919@gmail.com --json --no-input
```

### Sheets
```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog sheets get 1-O_B27mSDqfEZemD27bPNmWtfnV3cW51LeClBmSwB6c \"Sheet1!A1:Z3\" --account tuananhtrinh919@gmail.com --json --no-input
```

### Tasks
```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog tasks list '@default' --account tuananhtrinh919@gmail.com --json --no-input --all --show-hidden --show-completed
```

---

## Step 2 — Full Re-Auth (agent-driven)

**Agents only:** On `invalid_grant`/expired token:

1. `exec(pty=true)`: `GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog auth add tuananhtrinh919@gmail.com --manual --services gmail,calendar,drive,sheets,tasks,contacts,docs,slides,people,forms,appscript --force-consent --timeout 15m`

2. `process.log` → extract/print auth URL to user.

3. Message user: Open URL, authorize, paste full redirect `http://127.0.0.1:...` back.

4. On paste: `process.write(full-redirect-url)` to session.

5. `process.poll/log` until `gog auth list` shows full services.

Success: `email tuananhtrinh919@gmail.com services appscript,calendar,...`

---

## Step 3 — Export Fresh Backup Immediately

After re-auth:

```bash
rm -f /data/workspace/gog_auth_backup.json && \
GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog auth tokens export tuananhtrinh919@gmail.com --out /data/workspace/gog_auth_backup.json --force --no-input
```

(Uses `rm` to overwrite; verifies `exported true`.)

---

## Step 4 — Verify Cemented Fix

Confirm:
1. `gog auth list --json --no-input` → full services.
2. `/data/workspace/gog_auth_backup.json` → fresh scopes.
3. Gmail/Calendar/Sheets/Tasks probes pass.

---

## Failure Modes

- `invalid_grant` → Steps 2-3.
- Cron fails post-auth → Step 3 missing.
- Narrow scopes → Step 2 full bundle.

## Operational Rule

Cron/SOPs: \"Read SOP-GOG-AUTH.md; Step 0 then probes.\"

**Cập nhật:** 2026-03-20 (agent-driven re-auth)
**Tác giả:** SpongeBot 🫧
