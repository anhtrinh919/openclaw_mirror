# revive.md — Full State Restore Runbook (Railway)

This runbook restores SpongeBot/OpenClaw from a “factory-setting” agent state using backups.

## Backup location
All backups are in:

```bash
/data/backups
```

Expected archive patterns:

- `openclaw-state-<timestamp>.tgz` → contains `/data/.openclaw` (sessions, config, credentials, plugins, runtime state)
- `workspace-core-<timestamp>.tgz` → contains critical files/folders from `/data/workspace`

Current host also has these files:

- `/data/backups/openclaw-state-.tgz`
- `/data/backups/workspace-core-.tgz`

(These names indicate `$ts` was empty when creating them; they are still valid tarballs.)

---

## What this restores

1. **OpenClaw state** (`/data/.openclaw`)
   - `openclaw.json`
   - session transcripts
   - memory index/runtime data
   - plugin install state
   - device/session metadata

2. **Workspace core** (`/data/workspace`)
   - `AGENTS.md`, `SOUL.md`, `USER.md`, `MEMORY.md`, `contacts.md`, `SOP.md`, `SKILLS.md`
   - `memory/`, `sops/`
   - `task.md`, `task_system.json`, `leave_requests.json`, `news_watch_state.json`

---

## Full restore steps

### 0) Pick the backup set
Use the newest archive for each type (or pick a matching timestamp pair):

```bash
ls -lt /data/backups/openclaw-state*.tgz
ls -lt /data/backups/workspace-core*.tgz
```

Set variables (example):

```bash
STATE_TGZ="/data/backups/openclaw-state-.tgz"
WORKSPACE_TGZ="/data/backups/workspace-core-.tgz"
```

### 1) Stop gateway

```bash
openclaw gateway stop
```

### 2) Restore OpenClaw runtime state

```bash
tar -C /data -xzf "$STATE_TGZ"
```

### 3) Restore workspace core

```bash
tar -C /data/workspace -xzf "$WORKSPACE_TGZ"
```

### 4) Fix ownership (important if backups were created as root)

```bash
chown -R openclaw:openclaw /data/.openclaw /data/workspace
```

### 5) Start gateway

```bash
openclaw gateway start
```

### 6) Quick sanity checks

```bash
openclaw gateway status
openclaw config get gateway.controlUi.allowedOrigins
ls -lah /data/workspace/memory | head
ls -lah /data/.openclaw/agents/main/sessions | head
```

---

## Critical note about Control UI origin
If UI becomes unreachable after restore/update, ensure this key includes both origins:

```bash
openclaw config set gateway.controlUi.allowedOrigins '["https://openclaw-production-47c1.up.railway.app","http://127.0.0.1:18789"]' --strict-json
```

---

## Recommended backup command format (to avoid empty timestamp)
Use:

```bash
ts="$(date +%Y%m%d-%H%M%S)"
```

before running tar commands.

Then create backups with:

```bash
tar -C /data -czf /data/backups/openclaw-state-$ts.tgz .openclaw

tar -C /data/workspace -czf /data/backups/workspace-core-$ts.tgz \
 AGENTS.md SOUL.md USER.md MEMORY.md contacts.md SOP.md SKILLS.md \
 memory sops task.md task_system.json leave_requests.json news_watch_state.json 2>/dev/null || true
```
