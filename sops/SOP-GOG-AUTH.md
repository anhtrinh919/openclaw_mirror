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
GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog gmail search "is:unread" --account tuananhtrinh919@gmail.com --max 1 --json --no-input
```

### Calendar
```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog calendar events --today --account tuananhtrinh919@gmail.com --json --no-input
```

### Sheets
```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog sheets get 1-O_B27mSDqfEZemD27bPNmWtfnV3cW51LeClBmSwB6c "Sheet1!A1:Z3" --account tuananhtrinh919@gmail.com --json --no-input
```

### Tasks
```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog tasks list '@default' --account tuananhtrinh919@gmail.com --json --no-input --all --show-hidden --show-completed
```

---

## Step 2 — Full Re-Auth (when token is revoked / invalid_grant)

Use this when:
- API calls return `invalid_grant`
- token is expired/revoked
- required scopes are missing
- backup token was stale or downgraded

### Start a live manual auth session

```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog auth add tuananhtrinh919@gmail.com \
  --manual \
  --services gmail,calendar,drive,sheets,tasks,contacts,docs,slides,people,forms,appscript \
  --force-consent \
  --timeout 15m
```

Important:
- keep the auth process/session alive while the user approves
- user opens the Google URL
- user pastes back the final `http://127.0.0.1:...` redirect URL
- feed that redirect URL back into the waiting `gog` process

On success, `gog auth list --json --no-input` should show the expanded service set.

---

## Step 3 — Export Fresh Backup Immediately

After successful re-auth, **always** refresh the persistent backup token file.

```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog auth tokens export tuananhtrinh919@gmail.com --out /tmp/gog_auth_backup_fresh.json --force --no-input && \
cp /tmp/gog_auth_backup_fresh.json /data/workspace/gog_auth_backup.json
```

Reason:
- cron restore depends on `/data/workspace/gog_auth_backup.json`
- if this file is stale, future runs can re-break even after a successful manual re-auth

---

## Step 4 — Verify Cemented Fix

After export, confirm all of these:

1. `gog auth list --json --no-input` shows the expected service set
2. `/data/workspace/gog_auth_backup.json` contains the expected expanded `services` / `scopes`
3. live Gmail probe passes
4. live Calendar probe passes
5. live Sheets probe passes
6. live Tasks probe passes

If all six pass, the fix is considered real.

---

## Failure Modes

### `invalid_grant`
Meaning:
- refresh token expired or revoked

Action:
- do **Step 2** full re-auth
- then do **Step 3** export fresh backup

### Auth looks fine in one session, but cron still fails later
Meaning:
- backup file was not refreshed
- cron imported stale token from `/data/workspace/gog_auth_backup.json`

Action:
- do **Step 3** immediately after re-auth

### Missing service scopes
Meaning:
- auth exists, but token was created with too narrow a service set

Action:
- full re-auth with the canonical service bundle from this SOP

### `requested scopes invalid`
Meaning:
- auth request included unsupported scopes/services for this client/runtime

Action:
- use the canonical service bundle from this SOP, not ad-hoc “everything” scope requests

---

## Operational Rule for Other SOPs / Cron Jobs

Allowed pattern:
- “Read `/data/workspace/sops/SOP-GOG-AUTH.md` and follow Step 0 before using `gog`.”

Avoid pattern:
- embedding raw restore commands directly in every SOP or cron prompt

---

**Cập nhật:** 2026-03-13
**Tác giả:** SpongeBot 🫧
