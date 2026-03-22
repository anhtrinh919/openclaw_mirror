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
- **Protocol:** tools/call (see SOP-CHASE)
- Connection/permission policy: `/data/workspace/sops/SOP-CHASE.md`

---

[... rest unchanged ...]

## Error Handling

### If Chase MCP is unavailable
1. say Chase is temporarily unavailable
2. do not pretend task creation succeeded
3. if needed, save a temporary local fallback note in `/data/workspace/task.md`
4. **Retry:** Cron **10-15min** or on MCP up (`tools/list`)

[... rest unchanged ...]