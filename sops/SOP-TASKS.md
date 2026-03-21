# SOP-TASKS — Task Creation (@task)

Use this SOP whenever Boss sends `@task ...`.

Chase is now the **canonical PM system** for `@task`.

---

## Purpose

This SOP standardizes:
1. how `@task` is parsed
2. how tasks are created in Chase
3. how project assignment is chosen automatically
4. how notes, due dates, and Chase contacts are attached
5. when reminders are created
6. what to do if Chase MCP is unavailable

---

## Canonical Rule

**For `@task`, Chase is the source of truth.**

Do not use Google Tasks or Google Sheets as the canonical tracker.
Do not treat `/data/workspace/task.md` as canonical.
Use local files only as fallback if Chase is down.

Chase connection facts:
- MCP endpoint: `https://life-tracker-production-17cb.up.railway.app/api/mcp`
- API key file: `/data/workspace/.chase_api_key`
- Connection/permission policy: `/data/workspace/sops/SOP-CHASE.md`

---

## Trigger

**Pattern:** `@task [freeform task instruction]`

Examples:
- `@task send final OpenSea backlog to team - me - tomorrow 5pm`
- `@task follow up LanChi on PNL report - chị Chi - Monday`
- `@task create launch checklist for Opensea`

Default behavior:
- parse title
- infer or ask for project
- infer or ask for due date when needed
- infer or ask for contact when useful
- add notes if the message contains execution detail/context
- create the Chase task
- optionally create a reminder cron when the task has a due date

---

## Required / Optional Fields

### Required
- task title / actionable description

### Strongly preferred
- due date when timing matters
- contact when the task is about chasing/following up with someone

### Optional
- project
- notes/context
- priority

If essential fields are missing and the task cannot be created cleanly, ask once.

---

## Main Flow

```text
User: @task [instruction]
    ↓
Bot: Parse title, due date, contact, project, notes, priority
    ↓
Bot: Resolve Chase project smartly
    ↓
Bot: Resolve Chase contact smartly when relevant
    ↓
Bot: Create task in Chase with notes + due date + contact_id
    ↓
Bot: If due date exists, optionally create reminder cron to original chat
    ↓
Bot: Reply with created task summary
```

---

## Parsing Rules

From the user message, extract when possible:
- **title** → short action phrase
- **due_date** → ISO date if explicit or inferable
- **contact** → the person to chase / follow up with
- **project** → explicit project name/ID, or inferred project
- **notes** → extra context that should live in the task
- **priority** → `critical` only when urgency is explicit; else `normal`

### Due date handling
- Always interpret human dates in **Asia/Ho_Chi_Minh** unless Boss says otherwise.
- Store due date in Chase as `YYYY-MM-DD`.
- If user gives a time, preserve the time in task notes because Chase task schema uses `due_date` only.

### Notes handling
Put useful execution context into `notes`, such as:
- constraints
- success criteria
- links or references the user included
- follow-up details
- explicit time context like `5pm VN`

---

## Smart Project Assignment

When Boss provides a Chase project unique ID, use it directly.

Otherwise resolve project in this order:

### 1) Exact explicit project match
If Boss names a known Chase project clearly, use that project.

### 2) Strong keyword/domain match
Infer by context. Examples:
- `OpenSea`, `Opensea`, startup build work → `OpenSea`
- Lanchi / LanChi work → `LanChi`
- family/personal/home tasks → `Family`
- Chase product work → `Chase`
- OpenClaw / bot / agent infra work → `openclaw`

### 3) Existing project continuity
If the task is clearly a continuation of recent work already associated with a project, reuse that project.

### 4) Default fallback
Use the Chase default project only when no better fit exists.

### 5) Ask once when ambiguous
If 2+ projects are plausible and confidence is low, ask a brief clarifying question instead of guessing.

---

## Smart Contact Assignment

When the task is clearly about chasing, waiting on, following up with, or coordinating with a person:
- resolve that person against Chase contacts first
- attach `contact_id` when a confident match exists

Use contacts for examples like:
- `follow up with ...`
- `chase ...`
- `ask ...`
- `wait for ...`
- `remind ...`

If no Chase contact matches confidently:
- create the task without contact_id
- include the human name in notes
- do **not** mutate contacts without approval (see `SOP-CHASE`)

---

## Task Creation Rule

Create the Chase task with these defaults unless the user says otherwise:
- `status`: `backlog`
- `priority`: `normal` unless explicit urgency → `critical`
- `project_id`: resolved via Smart Project Assignment
- `notes`: concise but useful context
- `due_date`: if available
- `contact_id`: if confidently matched and relevant

When the task already exists and the user is clearly updating it, prefer updating the existing Chase task instead of creating a duplicate.

---

## Reminder Rule

If the task has a due date, create a reminder cron unless Boss clearly does not want reminders.

Default reminder behavior:
- send reminder to the original chat
- send at **12:00 Asia/Ho_Chi_Minh on the due date**
- if original surface is not Telegram, send to Boss Telegram DM `171900099`

For Telegram scheduled sends:
- use `/data/workspace/ops/send_telegram_verified.sh`
- do not rely on internal chat echoes as proof of delivery

Reminder message shape:
- `🔥 Chase reminder: [task title] — due today` 
- include project name, contact name, and time note when helpful

---

## Reply Format

Keep it short.

Example:
- `✅ Added to Chase: [title] — project: [project], due: [date], contact: [name/no contact]. Reminder set.`

If reminder not set:
- say so briefly

If project/contact was inferred:
- mention the chosen project only, not the whole reasoning

---

## Error Handling

### If Chase MCP is unavailable
1. say Chase is temporarily unavailable
2. do not pretend task creation succeeded
3. if needed, save a temporary local fallback note in `/data/workspace/task.md`
4. sync the task into Chase once access is restored

### If project resolution is ambiguous
- ask once

### If contact resolution is ambiguous
- create without contact_id unless the contact is critical to the task meaning

### If reminder creation fails
- task creation in Chase still stands
- tell Boss reminder was not set

---

## Heartbeat / Follow-up Monitoring

Chase heartbeat is handled separately from task creation.

Current rule:
- 4x/day, a scheduled Chase heartbeat checks pending tasks and chase/follow-up items
- it notifies Boss with pending work summary
- it alerts Boss if Chase MCP connectivity fails

---

## Files / Systems

- **Connection + permission policy:** `/data/workspace/sops/SOP-CHASE.md`
- **API key:** `/data/workspace/.chase_api_key`
- **Telegram verified sender:** `/data/workspace/ops/send_telegram_verified.sh`
- **Fallback scratch file only:** `/data/workspace/task.md`

---

**Cập nhật:** 2026-03-21  
**Tác giả:** SpongeBot 🫧
