# Decision Rights & Approval Gates

Project: **personalized-daily-tracker-mvp**  
Owner: **Boss (final decision maker)**  
Operating mode: **No major step proceeds without explicit Boss approval**.

---

## 1) Decision Rights (who decides what)

## Boss (final authority)
- Scope and priorities
- UX direction and final design acceptance
- Tech stack and integration choices
- Launch/no-launch decisions
- Any timeline/scope tradeoff

## SpongeBot (main, Chief of Staff)
- Converts requests into clear work packages
- Coordinates agents and sequence of work
- Flags risks, options, and recommended decision
- Cannot override approval gates

## Sandy (Builder)
- Proposes implementation details
- Executes code and technical setup after approvals
- Provides demos + test evidence per slice

## GLaDOS (Data)
- Defines/validates data model and reporting logic
- Handles integration/data quality checks
- Provides data QA evidence

## Squid (Architect/QC)
- Reviews plan quality and technical risk
- Runs acceptance/QC checks before release
- Issues go/no-go recommendation (Boss decides)

---

## 2) Approval Gates (hard stops)

## Gate 0 — Scope Lock (Approval required)
Input:
- PRD + MVP boundaries + acceptance criteria
Output:
- Approved scope baseline

## Gate 1 — UX Lock (Approval required)
Input:
- Pencil.dev flows + key screens (Home with huge buttons, Notes, Tasks, Recipes)
Output:
- Approved design baseline for MVP

## Gate 2 — Technical Plan Lock (Approval required)
Input:
- Architecture, data model, API contracts, milestone plan
Output:
- Approved build plan

## Gate 3 — Slice Delivery (Approval required per slice)
Input:
- Demo + test evidence for each feature slice
Output:
- Approved to merge/deploy that slice

## Gate 4 — Release Go/No-Go (Approval required)
Input:
- QC report + known issues + rollback plan
Output:
- Approved production release (or hold)

---

## 3) Change Control Rules
- Any change to scope, data model, or timeline must be logged as **CHANGE REQUEST**.
- SpongeBot presents: impact, options, recommendation.
- Boss approves/rejects before implementation.

---

## 4) Communication Format (for non-dev clarity)
Every update should include:
1. What was done
2. What decision is needed (if any)
3. Risks/tradeoffs (blunt)
4. Next step proposal

Use explicit tags:
- `INFO` (no decision needed)
- `APPROVAL NEEDED` (blocked until Boss decides)
- `RISK` (potential issue)

---

## 5) Definition of “Done” (MVP)
A feature is done only when all are true:
- Meets approved acceptance criteria
- Passes test/QC checks
- Demo reviewed by Boss
- Boss explicitly approves

---

## 6) Current immediate next action
- **Start Gate 0 approval:** Boss confirms PRD scope and success criteria for MVP.

If approved, proceed to Gate 1 (Pencil.dev design lock).
