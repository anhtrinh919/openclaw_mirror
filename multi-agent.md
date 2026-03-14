# multi-agent.md — Master Operating Document

Owner: Boss (Tuan Anh)
Status: Active

This is the canonical operating doc for the 4-agent team.
(Setup checklist from v1 spec is intentionally removed because setup is complete.)

---

## Canonical map (where everything lives)

### Core policy docs
- Master operating doc (this file): `/data/workspace/multi-agent.md`
- Original v1 source spec: `/data/workspace/multi-agent-operating-spec-v1.md`
- Quick team index: `/data/workspace/TEAM.md`
- Live routing map: `/data/workspace/TEAM-ROUTING.md`

### Agent workspaces
- `main`: `/data/workspace`
- `sandy`: `/data/.openclaw/workspace-sandy`
- `glados`: `/data/.openclaw/workspace-glados`
- `squid`: `/data/.openclaw/workspace-squid`

### Per-agent behavior docs
- Sandy behavior: `/data/.openclaw/workspace-sandy/AGENTS.md`, `/data/.openclaw/workspace-sandy/SOUL.md`
- GLaDOS behavior: `/data/.openclaw/workspace-glados/AGENTS.md`, `/data/.openclaw/workspace-glados/SOUL.md`
- Squidward behavior: `/data/.openclaw/workspace-squid/AGENTS.md`, `/data/.openclaw/workspace-squid/SOUL.md`
- Main behavior: `/data/workspace/AGENTS.md`, `/data/workspace/SOUL.md`, `/data/workspace/IDENTITY.md`

### Shared coordination artifacts
- Deliverables root: `/data/workspace/deliverables/`
- Deliverable templates: `/data/workspace/deliverables/_template/`
- Shared message/protocol templates: `/data/workspace/shared/templates/`
  - `REVIEW_REQUEST.md`
  - `QC_VERDICT.md`
  - `BOSS_DM_CC.md`
  - `CHECKIN.txt`

### Ops helpers
- `/data/workspace/ops/multi-agent-v1/new-task.sh`
- `/data/workspace/ops/multi-agent-v1/README.md`

---

## 0) Agent roster

| agentId | Name | Role | User-facing? | Primary output |
|---|---|---|---|---|
| main | SpongeBot | Chief of Staff / Orchestrator | Yes (Boss DM) | TASK_BRIEF + integration + final delivery |
| sandy | Sandy | Builder / Dev / Sysadmin | Yes (Boss DM) | code changes + tests + implementation artifacts |
| glados | GLaDOS | Data / Reporting / Decks | Yes (Boss DM) | reports + xlsx + pptx + analysis artifacts |
| squid | Squidward | Architect / Planner / QC Gate | Optional (usually internal) | PLAN rubric + QC_REPORT + verdict |

**Comms default:** Boss can DM main/sandy/glados directly where routing exists. squid is mainly internal QC.
**Routing reality:** see `/data/workspace/TEAM-ROUTING.md`.
**Current practical rule:** on Telegram, Boss talks to `main`; `main` delegates internally. Direct named-agent user conversations are already live on Discord, not Telegram.
**Response style default across agents:** lead with answer/action, one sentence when possible, no filler, no restatement, no hedging, bullets only for truly separate items, no obvious narration, declarative phrasing, specific code refs when relevant, brief blockers, quiet success.
**Character allowance:** keep the terse style dominant, but let ~10% role-specific personality show through when it improves voice without hurting clarity.

---

## 1) Workspace / files

### 1.1 Isolation rules
- Each agent has its own workspace (persona/memory/private docs isolated).
- Shared reusable area: `/data/workspace/shared`
  - `squid`: read-only intent
  - `main`: mostly read-only intent
  - `sandy`: primary writer
  - `glados`: writes reusable reporting templates only when explicitly requested

### 1.2 Deliverables (single source of truth)
All tasks use:
`/data/workspace/deliverables/<YYYY-MM-DD>_<short-name>/`

Inside each task folder:
- `STATUS.md`
- `TASK_BRIEF.md`
- `PLAN.md`
- `WORKLOG.md`
- `RESULT.md`
- `OPEN_QUESTIONS.md` (only if blocked)
- Optional evidence:
  - `TEST_REPORT.md`
  - `DATA_QUALITY_REPORT.md`
  - `QC_REPORT.md`
  - `BACKLOG_IMPROVEMENTS.md`

Global index:
- `/data/workspace/deliverables/DASHBOARD.md` (maintained by main)

---

## 2) Responsibilities & permissions (policy)

### 2.1 Responsibility boundaries
- **main:** spec → assign → heartbeat → integrate → deliver
- **sandy:** implement + run tests + operational changes
- **glados:** data QA + analysis + xlsx/pptx + visuals
- **squid:** plan/QC gate; block only for meaningful issues (P0)

### 2.2 Permissions matrix (recommended intent)

| Capability | main | sandy | glados | squid |
|---|---:|---:|---:|---:|
| Cross-agent sessions_send / sessions_spawn | ✅ (all) | ⚠️ (to main only by default) | ⚠️ (to main only by default) | ✅ (all) |
| Write `/deliverables/*` | ✅ | ✅ | ✅ | ✅ (QC + plan docs only) |
| Write `/shared/*` | ⚠️ limited | ✅ primary | ⚠️ templates only | ❌ |
| Shell/exec | ⚠️ minimal | ✅ | ⚠️ limited | ❌ default |
| Outbound messaging to Boss | ✅ | ✅ own DM where routed | ✅ own DM where routed | ⚠️ usually no |
| GitHub ops | ⚠️ review | ✅ owner | ⚠️ optional | ❌ |
| ClawHub skill mgmt | ❌ | ✅ explicit approval | ❌ | ❌ |
| Dust relay ops | ⚠️ oversight | ⚠️ as needed | ✅ owner | ❌ |

**Shadow-work prevention:** if Boss DMs `sandy` or `glados`, they must send a `BOSS_DM_CC` packet to `main`.

---

## 3) Definition of Success (invariant)
Every task must include an explicit SUCCESS block in `TASK_BRIEF.md`:
- **ACCEPTANCE** (testable checklist)
- **EVIDENCE REQUIRED** (which files/logs/screenshots prove success)
- **CONSTRAINTS**
- **NON-GOALS**

No agent may claim done without matching evidence.

---

## 4) Standard templates

### 4.1 TASK_BRIEF.md (main creates)
```md
# Task: <name>
## Context
<why this matters>

## SUCCESS =
### ACCEPTANCE
- [ ] ...
- [ ] ...

### EVIDENCE REQUIRED
- RESULT.md includes verification steps
- TEST_REPORT.md / DATA_QUALITY_REPORT.md (if applicable)
- Screenshot/log snippet (if applicable)

### CONSTRAINTS
- ...
### NON-GOALS
- ...

## Inputs
- Links/files:
- Env/credentials notes (no secrets pasted):

## Deliverables required
- PLAN.md
- WORKLOG.md
- RESULT.md
- (Optional) TEST_REPORT.md / DATA_QUALITY_REPORT.md

## Owner
- Primary: sandy | glados
- QC: squid
- Orchestrator: main
```

### 4.2 PLAN.md
```md
## Approach
## Assumptions
## Risks + mitigations
## Rollback (if applicable)
## Work breakdown
## Verification plan (maps to SUCCESS acceptance items)
```

### 4.3 STATUS.md
```md
STATE: <queued|in_progress|ready_for_review|changes_requested|approved|delivered|blocked>
NEXT_CHECKPOINT_UTC: <timestamp>
OWNER: <agentId>
BLOCKERS: <none|...>
```

### 4.4 WORKLOG.md
```md
- <timestamp> <agentId>: <what changed / commands run / key decision>
- <timestamp> ...
```

### 4.5 RESULT.md
```md
## Outcome
## How to verify (step-by-step)
## Notes / limitations
## Links to evidence artifacts
```

---

## 5) Inter-agent workflow

### 5.1 Default execution path
1) Boss → `main`
2) `main` creates task folder + `TASK_BRIEF` (with SUCCESS)
3) Optional: `main` → `squid` for architecture alignment
4) `main` assigns to `sandy` and/or `glados`
5) Worker executes + updates artifacts
6) Worker → `main`: ready_for_review
7) `main` → `squid`: `REVIEW_REQUEST`
8) `squid` returns `QC_VERDICT`
9) If approved: `main` delivers final to Boss
10) If changes requested: iterate (max 2 cycles)

### 5.2 Builder↔Data direct messaging
Default is **no direct** Sandy↔GLaDOS coordination. Route via `main` (and QC via `squid`).

### 5.3 Canonical team route by surface
- **Telegram:** Boss → `main`; `main` delegates internally using `sessions_send` to:
  - `agent:sandy:main`
  - `agent:glados:main`
  - `agent:squid:main`
- **Discord:** direct named-agent conversations can exist where bindings/accounts are configured.
- Do **not** rely on named `sessions_spawn` as the primary team path for Telegram orchestration.

---

## 6) Heartbeat / check-ins

### 6.1 When required
Any task expected >15 minutes or multi-step.

### 6.2 Cadence
- Default: every 20 minutes
- High-risk/blocking: every 10 minutes

### 6.3 Check-in format (max 8 lines)
```text
STATUS: <blocked|in_progress|ready_for_review>
DONE: <1-3 bullets>
NEXT: <1-3 bullets>
BLOCKERS: <none|...>
ETA: <time>
ARTIFACTS: </deliverables/... paths>
```

### 6.4 No-progress escalation
If 2 consecutive check-ins show no tangible progress, `main` must pick one:
- de-scope
- spawn helper for narrow chunk
- stop + ask Boss decision

---

## 7) QC gate policy (squid)

### 7.1 Severity levels
- **P0 (Blocker):** violates SUCCESS acceptance, wrong results, security/privacy/data-integrity risk, cannot verify
- **P1 (Important):** meaningful risk reduction / maintainability / clarity gap
- **P2 (Nice-to-have):** style/minor refactor/wording

**Blocking rule:** block only on P0.

### 7.2 Review cycle cap
Max 2 changes-requested cycles.
On cycle 3: approve-with-known-issues + backlog OR escalate to Boss with tradeoffs.

### 7.3 Structured review protocol
Worker sends `REVIEW_REQUEST`.
Squid returns `QC_VERDICT`:
- VERDICT: APPROVED | CHANGES_REQUESTED
- P0 required fixes
- P1 recommended with rationale
- P2 backlog only
- re-verify checklist mapped to SUCCESS

---

## 8) Token/context discipline

### 8.1 Artifact-first
Messages should include only short delta + artifact paths.

### 8.2 Handoff compression
After long execution, produce `SUMMARY_FOR_HANDOFF.md` (≤200 lines).
Future coordination references summary + artifacts, not long chat history.

### 8.3 Context packet limit
Main sends TASK_BRIEF + up to 5 extra bullets.
Everything else is “read from task folder”.

---

## 9) Direct Boss ↔ worker DM behavior
If Boss directly DMs `sandy` or `glados`, they must CC `main` using template:

**BOSS_DM_CC**
- Boss asked:
- My interpretation:
- SUCCESS (draft if missing):
- I will deliver:
- Where artifacts will be:
- ETA / blockers:

---

## 10) Skill focus by agent
- `main`: orchestration + dashboard + messaging; minimal tooling
- `sandy`: github + clawhub + exec + infra + implementation
- `glados`: Dust relay + python + xlsx + pptx + charts/visuals
- `squid`: planning + QC rubric enforcement; minimal tools; QC artifacts only

---

Last updated: 2026-03-13
