# Multi-Agent Team Setup Pack (v1)

Prepared for spec:
- `main` = SpongeBot (orchestrator)
- `sandy` = builder/dev/sysadmin
- `glados` = data/reporting/decks
- `squid` = architect/QC

## What was done automatically
- Created isolated workspaces:
  - `/data/.openclaw/workspace-sandy`
  - `/data/.openclaw/workspace-glados`
  - `/data/.openclaw/workspace-squid`
- Added role-specific `SOUL.md` + `AGENTS.md` + `USER.md` in each workspace.
- Created shared and deliverables scaffolding:
  - `/data/workspace/shared/README.md`
  - `/data/workspace/deliverables/DASHBOARD.md`
  - `/data/workspace/deliverables/_template/*`
- Added task-folder bootstrap helper:
  - `/data/workspace/ops/multi-agent-v1/new-task.sh`

## Manual step 1 (required): apply config change
> This step is intentionally manual (per your instruction: no self-config change).

### 1) Create 2 new Discord bot tokens
- `sandy` bot token
- `glados` bot token

### 2) Run config patch script manually
```bash
cd /data/workspace
DISCORD_TOKEN_SANDY='paste_token_here' \
DISCORD_TOKEN_GLADOS='paste_token_here' \
node /data/workspace/ops/multi-agent-v1/apply-multi-agent-config.js
```

What this patch sets:
- `agents.list` for main/sandy/glados/squid with isolated workspaces and agent dirs
- `bindings` to route Discord account `main|sandy|glados` to corresponding agents
- `channels.discord.accounts.{main,sandy,glados}`
- `tools.agentToAgent.enabled=true`
- `tools.sessions.visibility='all'`
- `session.agentToAgent.maxPingPongTurns=2`

## Manual step 2 (required): restart gateway
> This step is intentionally manual (per your instruction: no self-gateway restart).

```bash
openclaw gateway restart
```

## Post-restart verification
```bash
openclaw agents list --bindings
openclaw channels status --probe
openclaw status --deep
```

Expected:
- 4 agents visible: main/sandy/glados/squid
- 3 Discord accounts visible: main/sandy/glados
- Bindings route each Discord account to its agent

## Notes on strict permission matrix
OpenClaw can strongly enforce tool-level permissions per agent. Exact “sandy/glados can only sessions_send to main but not others” is not natively granular by target agent in config today; this setup applies practical guardrails and process enforcement through artifact-first workflow + QC protocol.
