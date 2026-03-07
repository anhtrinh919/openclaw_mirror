# OpenClaw Multi‑Agent Operating Spec (v1)
Owner: Boss (Tuan Anh)
Goal: 4 isolated main agents (Pattern B) + optional sub-agents (Pattern C), with strict success criteria + rigorous QC without endless loops.

## 0) Agent roster (branding locked)
| agentId | Name | Role | User-facing? | Primary output |
|---|---|---|---|---|
| main | SpongeBot | Chief of Staff / Orchestrator | Yes (Boss DM) | TASK_BRIEF + integration + final delivery |
| sandy | Sandy | Builder / Dev / Sysadmin | Yes (Boss DM) | code changes + tests + implementation artifacts |
| glados | GLaDOS | Data / Reporting / Decks | Yes (Boss DM) | reports + xlsx + pptx + analysis artifacts |
| squid | Squidward | Architect / Planner / QC Gate | Optional (usually internal) | PLAN rubric + QC_REPORT + verdict |

**Comms default:** Boss can DM main/sandy/glados directly. squid is mainly internal QC.
**Coordination:** main + squid can talk to all agents. sandy/glados report back to main and request QC from squid.

---

## 1) Workspace / files
### 1.1 Isolation rules
- Each agent has its **own workspace** (persona/memory/private docs are isolated).
- A single **shared mount** exists for reusable code/templates: `/shared`
  - Recommended: read-only for `squid`, usually read-only for `main`
  - `sandy` is the primary writer to `/shared`
  - `glados` writes to `/shared` only for reusable reporting templates (explicitly requested)

### 1.2 Deliverables (single source of truth)
All tasks create a folder:
`/deliverables/<YYYY-MM-DD>_<short-name>/`

Inside each task folder:
- `STATUS.md` (single-line current state + next checkpoint)
- `TASK_BRIEF.md` (written by main)
- `PLAN.md` (worker plan, or squid plan for architecture)
- `WORKLOG.md` (append-only)
- `RESULT.md`
- `OPEN_QUESTIONS.md` (only if blocked)
- Optional evidence:
  - `TEST_REPORT.md`
  - `DATA_QUALITY_REPORT.md`
  - `QC_REPORT.md`
  - `BACKLOG_IMPROVEMENTS.md` (non-blocking only)

Global index:
- `/deliverables/DASHBOARD.md` (maintained by main)

---

## 2) Responsibilities & permissions (policy)
### 2.1 Responsibility boundaries (hard)
- **main:** spec → assign → heartbeat → integrate → deliver
- **sandy:** implement + run tests + operational changes
- **glados:** data QA + analysis + xlsx/pptx + visuals
- **squid:** plan/QC gate; blocks only for meaningful issues (see P0/P1/P2)

### 2.2 Permissions matrix (recommended)
| Capability | main | sandy | glados | squid |
|---|---:|---:|---:|---:|
| Cross-agent sessions_send / sessions_spawn | ✅ (all) | ⚠️ (only to main, if needed) | ⚠️ (only to main, if needed) | ✅ (all) |
| Write `/deliverables/*` | ✅ | ✅ | ✅ | ✅ (QC + plan docs only) |
| Write `/shared/*` | ⚠️ limited | ✅ primary | ⚠️ templates only | ❌ |
| Shell/exec | ⚠️ minimal | ✅ | ⚠️ limited | ❌ (default) |
| Outbound messaging to Boss | ✅ | ✅ (own DM only) | ✅ (own DM only) | ⚠️ usually no |
| GitHub ops | ⚠️ review | ✅ owner | ⚠️ optional | ❌ |
| ClawHub skill mgmt | ❌ | ✅ (explicit approval) | ❌ | ❌ |
| Dust API / relay ops | ⚠️ oversight | ⚠️ as needed | ✅ owner | ❌ |

**Shadow-work prevention rule:** if Boss DMs `sandy` or `glados`, they must send a short CC packet to `main` (template in §9).

---

## 3) Definition of Success (most important invariant)
Every task must carry an explicit, testable “SUCCESS block” that propagates through all artifacts.

### 3.1 SUCCESS block (required in TASK_BRIEF.md)
**SUCCESS =**
- **ACCEPTANCE (testable):** bullet list
- **EVIDENCE REQUIRED:** which files/logs/screenshots prove it
- **CONSTRAINTS:** time, tools, safety, non-destructive rules
- **NON‑GOALS:** explicitly excluded scope

**No agent may claim “done” without matching EVIDENCE.**

---

## 4) Standard templates (copy/paste)
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
### NON‑GOALS
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

### 4.2 PLAN.md (worker or squid)
```md
## Approach
## Assumptions
## Risks + mitigations
## Rollback (if applicable)
## Work breakdown
## Verification plan (maps to SUCCESS acceptance items)
```

### 4.3 STATUS.md (single source for state)
```md
STATE: <queued|in_progress|ready_for_review|changes_requested|approved|delivered|blocked>
NEXT_CHECKPOINT_UTC: <timestamp>
OWNER: <agentId>
BLOCKERS: <none|...>
```

### 4.4 WORKLOG.md (append-only)
```md
- <timestamp> <agentId>: <what changed / commands run / key decision>
- <timestamp> ...
```

### 4.5 RESULT.md (must include verify)
```md
## Outcome
## How to verify (step-by-step)
## Notes / limitations
## Links to evidence artifacts
```

---

## 5) Inter-agent workflow (default)
### 5.1 Normal execution path
1) Boss → `main`: request
2) `main` → create `/deliverables/<task>/` + write TASK_BRIEF (with SUCCESS)
3) Optional: `main` → `squid`: quick plan alignment (if architecture-heavy)
4) `main` → assign to `sandy` and/or `glados`
5) Worker executes, maintains artifacts, updates STATUS
6) Worker → `main`: “ready_for_review” + pointers
7) `main` → `squid`: REVIEW_REQUEST
8) `squid` → QC_REPORT + verdict
9) If approved: `main` → Boss final delivery (with verification + paths)
10) If changes requested: worker updates artifacts; max 2 cycles (see §7)

### 5.2 No Builder↔Data direct cross-agent (default)
- `sandy` and `glados` do **not** coordinate directly across agents by default.
- All coordination routes through `main` (and QC through `squid`).

---

## 6) Heartbeat / check-ins (main’s control loop)
### 6.1 When to use heartbeat
Any task expected to take >15 minutes or involving multiple steps.

### 6.2 Heartbeat cadence
- Default cadence: every **20 minutes**
- Faster cadence (10 min) if the task is high-risk or blocking another task.

### 6.3 Check-in message format (max 8 lines)
```text
STATUS: <blocked|in_progress|ready_for_review>
DONE: <1-3 bullets>
NEXT: <1-3 bullets>
BLOCKERS: <none|...>
ETA: <time>
ARTIFACTS: </deliverables/... paths>
```

### 6.4 “No-progress escalation”
If 2 consecutive check-ins show no tangible progress:
- main must choose one:
  - de-scope
  - spawn helper (sub-agent) for a narrow chunk
  - stop + request Boss decision

---

## 7) QC gate policy (squid) — rigorous without infinite nitpicks
### 7.1 Severity levels
- **P0 (Blocker):** violates SUCCESS acceptance; incorrect results; security/privacy risk; data integrity risk; cannot verify.
- **P1 (Important):** materially reduces operational risk; significant maintainability issue; major clarity gap.
- **P2 (Nice-to-have):** style, minor refactors, micro-optimizations, “tighten up wording”.

**Blocking rule:** squid may block only on **P0**. P1 is “should fix” but must justify risk reduction. P2 is never blocking.

### 7.2 Review cycle cap
- Maximum **2** changes-requested cycles.
- On cycle 3, squid must either:
  - APPROVE with known issues + add them to BACKLOG_IMPROVEMENTS, or
  - ESCALATE to Boss with scope/time tradeoff options.

### 7.3 QC interaction is structured (no debate threads)
Worker sends:

**REVIEW_REQUEST**
- Task folder:
- What changed:
- Evidence run (tests/data checks):
- Questions (max 3):

squid replies:

**QC_VERDICT**
VERDICT: APPROVED | CHANGES_REQUESTED
P0 FIXES (required):
1) ...
P1 (recommended, justify):
1) ...
P2 (backlog only):
1) ...
RE-VERIFY CHECKLIST (maps to SUCCESS items):
- [ ] ...

---

## 8) Token & context discipline (“avoid token boom”)
### 8.1 Artifact-first rule
Workers do details in files; messages contain only:
- a short delta
- and **paths** to artifacts

### 8.2 Handoff compression
After any long execution:
- worker creates `SUMMARY_FOR_HANDOFF.md` (≤ 200 lines)
- future coordination references the summary + artifacts, not chat history

### 8.3 “Context packet” limit
main sends to workers:
- TASK_BRIEF + at most 5 bullets of extra context
Everything else is “read from task folder”.

---

## 9) Direct Boss↔Agent DMs (required CC behavior)
If Boss Dms `sandy` or `glados` directly, they must CC `main` with:

**BOSS_DM_CC**
- Boss asked:
- My interpretation:
- SUCCESS (draft, if not provided):
- I will deliver:
- Where artifacts will be:
- ETA / blockers:

---

## 10) Setup checklist (OpenClaw config intent)
(High-level; implementation specifics can follow.)
- 4 agentIds: `main`, `sandy`, `glados`, `squid`
- Bind 3 Discord bots → `main`, `sandy`, `glados` (Boss can DM each)
- Enable cross-agent only for `main` + `squid` (tight allowlist)
- Set agent-to-agent ping-pong turns low; prefer structured messages + artifact links.

---

## 11) Skill focus (by agent)
- main: orchestration + dashboard + messaging; minimal tooling
- sandy: github + clawhub + exec + infra + implementation
- glados: Dust API/relay + python + xlsx + pptx + charts/visuals; future BI
- squid: planning + QC rubric enforcement; minimal tools; writes QC artifacts only
