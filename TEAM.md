# TEAM.md — Quick Team Index

Canonical master doc: `/data/workspace/multi-agent.md`

Use this file for a quick overview; use `multi-agent.md` for full operating policy.

---

## Team summary

- **main (SpongeBot)** — Chief of Staff / orchestrator
  - owns task framing, delegation, integration, final delivery
- **sandy** — Builder / Dev / Sysadmin
  - implementation, tests, execution artifacts
- **glados** — Data / Reporting / Decks
  - analysis, data QA, xlsx/pptx/report artifacts
- **squid** — Architect / Planner / QC gate
  - plan review, QC verdicts, structured quality gate

---

## Standard flow (short)
1) Boss asks `main`
2) `main` writes TASK_BRIEF + SUCCESS
3) `main` assigns to sandy/glados
4) worker produces artifacts
5) `squid` reviews with QC verdict
6) `main` delivers final to Boss

---

## Trigger
- `@team` → start team-mode orchestration for the current task.
- Proactive delegation is allowed when `main` judges a task as too complex/time-consuming/risky for single-agent execution.

---

## Key links
- Master operating instructions: `/data/workspace/multi-agent.md`
- Deliverables root: `/data/workspace/deliverables/`
- Shared templates: `/data/workspace/shared/templates/`
- Ops helpers: `/data/workspace/ops/multi-agent-v1/`
