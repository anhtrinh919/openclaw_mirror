# OpenClaw Railway Fork Migration Plan

Date: 2026-03-23
Owner: Boss
Scope: Migrate the current Railway-hosted OpenClaw instance to a Railway deployment built from Boss’s own OpenClaw fork, while preserving config, workspace Markdown files, SOP behavior, and cron continuity with the smallest possible interruption.

---

## 1) Executive summary

This migration is feasible.

The safe path is **state-first migration**, not image-first migration:
- preserve or export the existing OpenClaw state
- deploy the forked build on Railway
- attach restored/preserved state at `/data`
- keep only **one active cron scheduler** at cutover time
- verify channels, workspace, SOP-critical files, and cron ownership before final switch

Hard truth:
- **true zero interruption is not realistic** on a single active gateway unless the fork already supports safe multi-instance scheduler handoff
- **near-zero interruption is realistic** with a short controlled cutover window

Recommended approach:
- **parallel warm-up + controlled cutover**
- old instance remains source of truth until final switch
- new instance is prepared and validated before cron/channel ownership moves

---

## 2) Feasibility by requirement

### A. Deploy Railway from Boss’s own OpenClaw fork
**Status:** Feasible

Conditions:
- Railway service must build from the forked repo/branch
- fork must remain compatible with current OpenClaw state/config format, or include explicit migration support

Main risk:
- fork introduces schema, storage, or runtime behavior changes

### B. Keep all configs intact
**Status:** Feasible

Conditions:
- preserve existing OpenClaw state directory or restore a backup into the new deployment
- do not hand-recreate config manually unless forced

Main risk:
- config schema drift between current instance and forked build

### C. Keep workspace `.md` files intact
**Status:** Feasible

Conditions:
- keep `OPENCLAW_WORKSPACE_DIR=/data/workspace`
- copy or restore the existing workspace into the new deployment volume

Main risk:
- mounting the wrong volume path, or booting the new service against an empty `/data`

### D. Keep all SOPs running
**Status:** Mostly feasible

Conditions:
- SOP files/scripts must remain present in workspace
- fork must not break tool availability, paths, or config fields those SOPs assume

Main risk:
- hidden dependency breakage: auth location, CLI behavior, environment vars, plugin naming, or path assumptions

### E. Keep all crons running
**Status:** Feasible with care

Conditions:
- cron store must move intact
- only one gateway should own active cron execution at a time
- post-cutover verification must confirm jobs, next-run state, and recent run history

Main risk:
- duplicate runs if both old and new gateways execute the same jobs
- missed runs if cutover overlaps a due time without scheduler ownership

### F. Keep everything running without interruption
**Status:** Not fully feasible as stated

Realistic interpretation:
- **near-zero interruption** is feasible
- **hard zero interruption** is not safely guaranteed on a single scheduler design

Why:
- channels and cron ownership must move from one gateway process to another
- overlapping both can duplicate work; pausing one before the other creates a brief handoff gap

---

## 3) Ground truths and constraints

### 3.1 State is the real system
The container image is replaceable.
The persistent state is not.

Critical assets to preserve:
- OpenClaw config/state under `/data/.openclaw`
- workspace under `/data/workspace`
- cron store and run history under OpenClaw state
- credentials/tokens stored inside state or workspace-backed files

### 3.2 Cron is the most dangerous part of cutover
Cron runs inside the Gateway scheduler.

Implications:
- one active instance is safe
- two active instances with the same cron state can create duplicate executions
- a gap between active schedulers can miss jobs near cutover time

### 3.3 SOP continuity depends on compatibility, not just file copy
Even if every `.md` file survives, SOPs can still fail if the fork changes:
- config schema
- tool names/availability
- plugin behavior
- auth locations
- environment variables
- working directory assumptions

### 3.4 Railway persistence decides success
If `/data` persistence is wrong, the migration fails regardless of app correctness.

---

## 4) Recommended migration strategy

## Strategy: Parallel warm-up, then controlled cutover

This gives the best balance of safety and continuity.

### Phase 1 — Audit current production state
Goal: know exactly what must survive.

Capture:
- current OpenClaw version/commit
- fork target version/commit
- current config schema compatibility risk
- current env vars in Railway
- mounted volume path(s)
- workspace path
- cron job list and recent run history
- channel/account bindings currently active
- any local secrets referenced from workspace files
- any SOP scripts that rely on absolute paths

Outputs:
- inventory checklist
- compatibility notes
- rollback prerequisites

### Phase 2 — Create portable backup
Goal: create a restore point before any cutover work.

Backup should include:
- OpenClaw state
- workspace
- config
- cron definitions/history if included by OpenClaw backup

Also capture separately for fast validation:
- snapshot of `/data/workspace`
- snapshot/listing of cron jobs
- critical env vars from Railway service settings

Rule:
- do not rely on memory or manual recreation

### Phase 3 — Build and stage new Railway service from fork
Goal: get the new service bootable without touching production traffic.

Requirements:
- build from Boss’s fork/target branch
- mount a volume at `/data`
- set the same key path variables:
  - `OPENCLAW_GATEWAY_PORT=8080`
  - `OPENCLAW_STATE_DIR=/data/.openclaw`
  - `OPENCLAW_WORKSPACE_DIR=/data/workspace`
- mirror required env/config values from production
- keep public access controlled during staging

Important:
- do **not** let the staged instance become the active production scheduler too early

### Phase 4 — Restore state into staging and validate offline behavior
Goal: prove the fork can read the real state safely.

Validate:
- config loads without schema errors
- workspace files appear intact
- agent boots successfully
- channels/config parse correctly
- cron store loads correctly
- no unexpected migrations or destructive rewrites occur

If the fork auto-migrates state on first boot:
- stop immediately
- decide whether migration is reversible
- require a rollback-safe snapshot before proceeding

### Phase 5 — SOP compatibility test
Goal: verify business-critical behavior before switch.

Test categories:
- workspace file access
- markdown-based routing/instruction reads
- critical scripts referenced by SOPs
- Google/Telegram/auth-dependent flows that are known to matter
- cron-monitor script paths and state files

Minimum acceptance:
- no missing paths
- no schema breakage
- no auth-path regressions
- no changed tool names for critical workflows

### Phase 6 — Cutover planning window
Goal: reduce interruption and avoid duplicate cron execution.

Best practice:
- choose a low-traffic window
- avoid known cron-heavy minutes
- avoid top-of-hour if recurring jobs cluster there
- freeze config/cron edits during cutover

Pre-cutover checks:
- backup completed and restorable
- staging validated
- rollback deployment ready
- exact switch time chosen
- operator checklist prepared

### Phase 7 — Controlled cutover
Goal: transfer ownership from old gateway to new gateway with minimal gap.

Order:
1. Confirm no critical cron job is due in the next few minutes.
2. Freeze manual config/cron changes.
3. Take final backup/snapshot.
4. Stop old instance from being active scheduler/channel owner.
5. Start/promote new forked instance with restored production state.
6. Verify it claims state, boots cleanly, and exposes Control UI.
7. Verify channels reconnect.
8. Verify cron jobs are present and next runs look sane.
9. Run smoke tests.

Key principle:
- never allow both instances to actively own production cron execution unless the scheduler is proven leader-safe

### Phase 8 — Post-cutover verification
Goal: prove continuity, not just process uptime.

Verify:
- direct chat still works
- current workspace files are intact
- cron list matches baseline
- next scheduled jobs still exist
- recent run history remains visible where expected
- SOP-critical scripts and docs still resolve correctly
- any channel-specific health indicators look normal

### Phase 9 — Rollback window
Goal: restore service fast if the fork misbehaves.

Rollback trigger examples:
- config schema rejection
- broken channel auth/session behavior
- cron corruption or duplicate execution risk
- missing workspace state
- SOP-critical path breakage

Rollback action:
- stop new instance
- restore previous production deployment/state snapshot
- re-enable old instance as sole active scheduler/channel owner
- verify chat + cron health

---

## 5) Detailed requirement mapping

### Requirement: keep config intact
Plan control:
- preserve `.openclaw` state or restore from backup
- do not rewrite config manually except as a last resort
- validate schema compatibility before cutover

Pass criteria:
- config loads without validation failure
- current behaviors match production expectations

### Requirement: keep workspace Markdown intact
Plan control:
- preserve `/data/workspace`
- verify presence of key files after restore:
  - `AGENTS.md`
  - `SOUL.md`
  - `USER.md`
  - `IDENTITY.md`
  - `MEMORY.md`
  - `contacts.md`
  - `memory/` daily files
  - `sops/` files
  - `ops/` scripts

Pass criteria:
- file tree and timestamps/sizes look expected
- no empty workspace boot

### Requirement: keep SOPs running
Plan control:
- test highest-risk SOP dependencies before cutover
- verify referenced scripts, auth files, and binary paths

Pass criteria:
- no missing files
- no broken auth paths
- no incompatible CLI assumptions

### Requirement: keep crons running
Plan control:
- baseline the cron inventory before migration
- avoid dual active schedulers
- validate after cutover

Pass criteria:
- job count matches baseline
- schedules match baseline
- next-run timing remains sane
- no duplicate runs observed

---

## 6) Risks and mitigations

### Risk 1 — Empty or wrong Railway volume mount
Impact:
- appears as a successful deploy but with missing state/workspace

Mitigation:
- explicitly mount `/data`
- verify expected directories before promoting new service
- do not cut over if `/data/.openclaw` and `/data/workspace` are not present

### Risk 2 — Fork/config schema incompatibility
Impact:
- new service refuses to boot or mutates config/state unexpectedly

Mitigation:
- validate in staging first
- compare current version against fork target
- keep rollback snapshot ready

### Risk 3 — Duplicate cron execution
Impact:
- duplicate reminders, duplicate automation, possible user-facing damage

Mitigation:
- one active scheduler at a time
- avoid overlapping old/new production execution
- choose cutover away from dense cron windows

### Risk 4 — Missed cron during handoff
Impact:
- silent skipped automation during cutover minute

Mitigation:
- cut over in low-traffic window
- review next due times beforehand
- keep handoff short and explicit

### Risk 5 — Channel reconnection delay
Impact:
- brief messaging interruption after switch

Mitigation:
- validate channel config in staging where possible
- keep old deployment rollback-ready
- perform immediate chat smoke test after cutover

### Risk 6 — Hidden SOP dependency on old runtime behavior
Impact:
- specific workflows break after migration even if base chat works

Mitigation:
- identify critical SOPs up front
- test path-sensitive and auth-sensitive flows first
- do not assume file presence alone equals working SOPs

---

## 7) Acceptance criteria

Migration is successful only if all are true:
- new Railway deployment runs from Boss’s fork
- config is preserved and valid
- workspace Markdown files are intact
- SOP-critical files/scripts/auth paths still work
- cron inventory matches baseline
- no duplicate cron execution occurs
- direct chat works after cutover
- rollback is no longer needed after stable observation window

---

## 8) Explicit non-goals

This plan does **not** assume:
- hard zero downtime
- simultaneous dual-scheduler safety
- automatic compatibility between upstream OpenClaw and the fork
- manual config recreation as primary strategy

---

## 9) Operator runbook

### Preflight checklist
- [ ] Record current production version/commit
- [ ] Record target fork version/commit
- [ ] Confirm current Railway volume mount is `/data`
- [ ] Confirm production uses `/data/.openclaw` and `/data/workspace`
- [ ] Export/create OpenClaw backup
- [ ] Capture cron inventory and recent run history
- [ ] Capture key Railway env vars
- [ ] Identify top 3–5 critical SOPs to validate
- [ ] Build staged Railway service from fork
- [ ] Restore/copy state into staging
- [ ] Validate config loads cleanly
- [ ] Validate workspace contents
- [ ] Validate cron store loads
- [ ] Validate critical SOP dependencies
- [ ] Pick low-risk cutover window
- [ ] Freeze config/cron edits before cutover

### Cutover checklist
- [ ] Confirm no critical cron due in next few minutes
- [ ] Take final backup/snapshot
- [ ] Disable/stop old production instance
- [ ] Promote/start new forked instance on production state
- [ ] Confirm Control UI/gateway health
- [ ] Confirm direct messaging works
- [ ] Confirm cron inventory matches baseline
- [ ] Confirm next-run times look sane
- [ ] Run smoke tests for critical SOP paths

### Rollback checklist
- [ ] Stop new instance
- [ ] Restore old deployment/state snapshot
- [ ] Re-enable old instance as sole active scheduler
- [ ] Confirm messaging recovery
- [ ] Confirm cron recovery
- [ ] Log root cause before retry

---

## 10) Recommended decision

Proceed only if Boss accepts this exact tradeoff:

> We can preserve config, workspace, SOPs, and cron state with high confidence, but the safe promise is **near-zero interruption**, not absolute zero, because cron/channel ownership must be handed from one Railway gateway process to another.

If Boss wants maximum safety, use:
- staged validation
- full backup
- controlled cutover
- immediate rollback path

If Boss wants maximum speed instead, risk rises sharply around:
- config compatibility
- duplicate cron execution
- missed scheduled jobs

---

## 11) Sources used for the plan

External docs reviewed:
- OpenClaw Railway docs: persistent `/data` volume, recommended `OPENCLAW_STATE_DIR=/data/.openclaw`, `OPENCLAW_WORKSPACE_DIR=/data/workspace`
- OpenClaw cron docs: cron persists on gateway host; scheduler ownership matters across restarts and jobs persist independently of model turns
- OpenClaw config docs: config is schema-validated and boot can fail on incompatibility

Memory checked:
- `MEMORY.md` notes that Railway/container setup uses WebSocket connectivity and stores session transcripts under `/data/.openclaw/...`
- `MEMORY.md` quick reference confirms cron schema expectations

---

## 12) Next document if needed

If Boss wants execution next, the follow-up doc should be:
- `openclaw-railway-fork-migration-execution-checklist.md`

That version should contain:
- exact commands
- exact Railway settings to mirror
- exact pre/post verification commands
- exact rollback commands
