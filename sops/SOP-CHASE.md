# SOP-CHASE — Canonical Chase Connection + Usage Policy

Use this as the **single source of truth** for all Chase access and all Chase task / project / note operations.

If any workflow needs project management, task management, notes, or contact lookup, it should **treat Chase as the canonical system of record** and follow this SOP.

---

## Purpose

This SOP standardizes:
1. how SpongeBot connects to Chase
2. when Chase should be used by default
3. what actions are allowed automatically
4. what actions require Boss approval
5. how ownership and project scope are interpreted
6. how to operate safely across human + agent workflows

---

## Canonical Platform Rule

**Chase is the canonical project / task management platform for both humans and agents.**

Default rule:
- new projects should be created in Chase
- new tasks should be created in Chase
- task updates should be written back to Chase
- project status should be read from Chase first
- notes relevant to project execution should live in Chase when possible

Do not treat local markdown task lists, transient chat memory, or agent scratchpads as the source of truth when Chase is available.

---

## Current Connection Facts

- **Base app URL:** `https://life-tracker-production-17cb.up.railway.app`
- **MCP docs URL:** `https://life-tracker-production-17cb.up.railway.app/mcp-docs`
- **MCP endpoint:** `https://life-tracker-production-17cb.up.railway.app/api/mcp`
- **Observed behavior:** docs page redirects to login, but `/api/mcp` is live and behaves like an MCP endpoint
- **Auth method:** API key

### Secret handling rule

**Do not hardcode the raw Chase API key into SOPs, prompts, cron payloads, or chat replies.**

If Chase access is needed in a reusable workflow, reference a secret source instead of pasting the key again.

Canonical secret storage:
- `/data/workspace/.chase_api_key` with `chmod 600`

Optional future alternative:
- a gateway/env secret such as `CHASE_API_KEY`

Current rule:
- use `/data/workspace/.chase_api_key` as the default secret source for Chase access
- do not paste the raw key into SOPs, prompts, cron payloads, or chat replies

---

## MCP Protocol 🔌

**JSON-RPC 2.0** via POST `/api/mcp`

### Headers
```
Authorization: Bearer $(cat /data/workspace/.chase_api_key)
Content-Type: application/json
Accept: application/json,text/event-stream
```

### Introspect tools
```json
{\"jsonrpc\":\"2.0\",\"method\":\"tools/list\",\"params\":{},\"id\":1}
```

### Call tool
```json
{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"list_tasks\",\"arguments\":{\"q\":\"PLL\",\"limit\":10}},\"id\":2}
```

**Tools:** list_tasks, get_task, create_task, update_task, delete_task, search_tasks, list_projects, create_project, list_contacts, get_dashboard, get_chase_view, etc.

---

## Standard Connection Rule

When connecting programmatically:
- use the Chase MCP endpoint at `/api/mcp`
- authenticate with the Chase API key
- prefer MCP-native operations over browser automation
- use browser UI only if MCP cannot perform the needed action

If the docs page redirects to login, that does **not** mean MCP is down.
The real health check is whether `/api/mcp` responds as an MCP server.

---

## Operating Model

Every Chase project has a unique ID.

Default project targeting rule:
- when Boss names a project and the unique ID is known, act on that project directly
- when the project name is ambiguous, resolve ambiguity before editing
- when a project cannot be matched confidently, ask once for clarification

Default task behavior:
- if a request implies action tracking, create or update a Chase task
- if work is completed, reflect completion in Chase
- if priorities/statuses/dates change, update Chase rather than only mentioning it in chat

---

## Permission Policy

Two modes exist: **auto** and **approval-required**.

### 1) Allowed without approval

SpongeBot may do these automatically:

#### Tasks
- create tasks
- edit tasks
- delete tasks
- move tasks between statuses or projects
- assign or re-prioritize tasks
- update due dates, titles, descriptions, tags, or metadata

Constraint:
- only inside **projects SpongeBot manages**

#### Notes
- create notes
- edit notes **created by SpongeBot / agent-side workflows**
- delete notes **created by SpongeBot / agent-side workflows**

#### Contacts
- view contacts

#### Projects
- create projects
- edit/manage projects **created by SpongeBot**

Examples of allowed project management:
- rename project
- update description
- update status
- archive/unarchive if clearly part of normal project maintenance
- add or reorganize project tasks or internal structure

### 2) Requires approval

SpongeBot must get Boss approval before doing these:

#### Contacts
- create contacts
- edit contacts
- delete contacts
- merge contacts
- reclassify contacts in ways that change meaning or ownership

#### Notes
- edit notes not created by SpongeBot
- delete notes not created by SpongeBot

#### Projects
- edit/manage projects not created by SpongeBot
- delete or archive projects not created by SpongeBot unless Boss explicitly approved that specific action
- materially restructure projects not created by SpongeBot

Approval must be explicit in the current conversation, not inferred from tone.

---

## Ownership Rules

Use the `sb-...` naming convention as the durable ownership marker.

### A. SpongeBot-created objects
A project or note is considered SpongeBot-created if its canonical identifier, slug, title prefix, or other durable Chase-visible marker starts with `sb-`.

Examples:
- `sb-opensea-launch`
- `sb-marketing-agency-pipeline`
- `sb-weekly-review-note`

### B. “Project SpongeBot manages” means
A project is auto-managed if **at least one** of these is true:
- it has an `sb-` durable marker
- it was explicitly assigned by Boss to SpongeBot for management
- Boss explicitly said SpongeBot manages it

If none of those are true, treat the project as **not automatically managed** and require approval for structural edits.

### C. “Notes you created” means
A note is considered SpongeBot-created if **at least one** of these is true:
- it has an `sb-` durable marker
- Chase metadata clearly shows it was created by SpongeBot/agent workflow

If neither is true, treat the note as not SpongeBot-created.

### D. Naming rule
When SpongeBot creates a new project or note in Chase, default to an `sb-` prefix where the product/UI supports it.

### E. When ownership is unclear
If ownership cannot be determined confidently:
- read first
- do not mutate
- ask Boss for approval or confirmation

---

## Approval Standard

Approval is valid when Boss clearly says something like:
- `approved`
- `go ahead`
- `do it`
- `yes, update/delete/create it`
- any direct instruction naming the object/action

Approval should be interpreted narrowly:
- approval to edit one contact is not blanket approval for all contacts
- approval to change one external project is not blanket approval for all non-SpongeBot projects

When a mutation is destructive or hard to reverse, prefer a brief confirmation even if approval seems implied.

---

## Deletion Rules

Deletion is allowed automatically only when the object falls inside the auto-permitted categories above.

Before deletion:
- verify the target object identity
- prefer soft-delete/archive if Chase supports it and the user did not request hard delete
- avoid deleting on fuzzy name matches

If a deletion would affect human-created content outside SpongeBot-owned scope, require approval.

---

## Contact Rules

Contacts are higher-sensitivity records.

Default behavior:
- viewing contacts is allowed
- any contact mutation requires approval

This includes:
- create
- edit
- delete
- merge
- status/category changes
- relationship or ownership changes

---

## Project Rules

### Auto-manage allowed for SpongeBot-created projects
For projects created by SpongeBot, SpongeBot may:
- rename
- update metadata
- reorganize
- add/remove internal tasks
- maintain status
- archive/unarchive when operationally appropriate

### Approval required for externally created projects
For projects not created by SpongeBot, require approval before:
- editing project fields
- changing membership/ownership
- deleting/archiving
- materially changing structure

### Project creation rule
When Boss asks for a new initiative, plan, tracker, or workspace, create a Chase project unless Boss says otherwise.

---

## Task Rules

Inside projects SpongeBot manages, task CRUD is fully allowed without approval.

Default task hygiene:
- titles should be short and actionable
- descriptions should preserve decision-relevant context
- due dates should use the user-intended timezone when relevant
- status changes should reflect real execution state
- avoid duplicate tasks when updating an existing one is better

If a task belongs to a project outside SpongeBot-managed scope and the requested change is ambiguous, ask once.

---

## Note Rules

Notes should be used for:
- project context
- execution logs
- decision summaries
- brief structured research relevant to work

Auto-permitted:
- create notes
- edit/delete notes created by SpongeBot

Approval-required:
- edit/delete notes not created by SpongeBot

When in doubt, create a new linked note instead of altering someone else’s note.

---

## Read-First / Write-Second Rule

Before mutating Chase records:
1. identify the target object confidently
2. read the current state when feasible
3. perform the smallest correct mutation
4. avoid broad or multi-object writes unless explicitly requested

For bulk operations:
- prefer one well-scoped batch over many tiny writes
- avoid tight mutation loops when rate limits may apply
- serialize sensitive updates when order matters

---

## Conflict Resolution

If Chase conflicts with chat memory, local notes, or agent scratchpads:
- treat Chase as canonical for project/task state
- treat chat as the user’s latest instruction source
- if the user’s instruction conflicts with Chase state, update Chase after confirming intent when needed

---

## Safe Fallbacks

If Chase MCP is unavailable:
1. say Chase is temporarily unavailable
2. avoid pretending the write succeeded
3. keep a temporary local record only if needed to avoid losing intent
4. **Retry:** Cron **10-15min** or on MCP up (check `tools/list`)

Temporary local notes are a fallback, not the source of truth.

---

## Recommended Future Improvements

These are not blockers:
- optionally mirror the Chase API key into an env secret such as `CHASE_API_KEY`
- define archive vs hard-delete behavior explicitly for each object type
- expose a stable permission/role model for agents

---

## Operational Summary

### Auto
- task CRUD in SpongeBot-managed projects
- note create + edit/delete for SpongeBot-created notes
- contact view
- project create + manage for SpongeBot-created projects

### Approval required
- all contact mutations
- edit/delete notes not created by SpongeBot
- create/edit/manage/delete/archive non-SpongeBot projects

---

**Updated:** 2026-03-22 (MCP tools/call format)  
**Author:** SpongeBot 🫧