# SOP-TASKS — Task Creation (@task)

(Extracted from legacy `/data/workspace/SOP.md`. One SOP per file.)

---

# SOP 4: Task Creation - @Task Trigger

## Tổng Quan
Quy trình xử lý `@task` trigger từ bất kỳ chat/group Telegram nào → Tạo task trong `task.md` theo bucket → (tuỳ chọn) tạo Google Tasks item cho Boss → Tạo reminder cron gửi Telegram lúc 12pm deadline đến chat gốc.

**Trigger patterns (bất kỳ chat Telegram):** 
- `@task [description] [PIC] [deadline]` (hoặc tương tự, parse tự động).
- Hoạt động ở DM/group (capture chat_id từ metadata).

**Required:** Description (nhiệm vụ), PIC (Person In Charge, e.g., "Trâm Anh" hoặc ID 6402311566), Deadline (dd/mm/yyyy hoặc relative như "tomorrow").

**Language:** English/Tiếng Việt based on user; keep consistent.

**Tracking file:** `/data/workspace/task.md` (buckets + log table).

**Integrations (current):**
- Canonical tracker Sheet (bot-managed): `/data/workspace/task_system.json` → `task_tracker_sheet`
- Boss on-demand view: Google Tasks list (Boss manages completion): `/data/workspace/task_system.json` → `google_tasks`

**Completion rule:** Boss marks tasks **done** in Google Tasks → bot syncs status back to Sheet **1x/day**.

---

## Luồng Chính
```
User: @task [description] [PIC] [deadline]
    ↓
Bot: Parse/ask missing info → Smart bucket sort
    ↓
Bot: Append task to task.md + log table
    ↓
Bot: (If PIC=Boss and Google Tasks enabled) create Google Tasks item
    ↓
Bot: Create cron reminder (12pm deadline, send to original chat_id)
    ↓
Bot: Reply "✅ Task created in [bucket]. Reminder set."
```

---

## Chi Tiết Các Bước

### Bước 1: Trigger Detection & Parsing
- **Patterns:** `@task` + text (parse description, PIC, deadline using keywords/natural lang).
- **Missing info:** Reply hỏi (e.g., "Cần PIC và deadline cho '[description]'!") → Wait user reply → Retry parse.
- **Deadline parse:** dd/mm/yyyy → Convert to ISO (YYYY-MM-DD). Relative (e.g., "3 days") → Add to today (Vietnam TZ).
- **PIC lookup:** Cross-check `contacts.md` for names/IDs; fallback to raw text.
- **Origin:** Store chat_id (e.g., "telegram:171900099" or group ID like "-5194157539").

### Bước 2: Smart Bucket Sorting
Logic tự động dựa trên description/PIC/keywords (priority order):
- **Personal:** PIC = "Boss", "Tuan Anh", "me" (nếu user=Boss) hoặc keywords: "personal", "errand", "reminder".
- **Staff:** PIC match contacts.md (e.g., "Trâm Anh" → 6402311566, "Chi Phan" → 82510296).
- **Critical:** Keywords: "urgent", "ASAP", "deadline", "critical", "fire", "emergency" HOẶC deadline < 3 ngày.
- **Other:** Default nếu không match trên.

### Bước 3: Append to task.md
- **Bucket sections:** Append bullet dưới bucket đúng:
  ```
  ### Personal
  - **TASK-20260228-01** | [Description] | PIC: Tuan Anh | Deadline: 2026-03-01 | Chat: telegram:171900099 | Reminder: cron-abc123 ✅
  ```
- **Log table:** Add row cuối bảng:
  | ID | Created | Description | PIC | Deadline | Bucket | Origin Chat | Reminder Set | Status |
  |----|---------|-------------|-----|----------|--------|-------------|--------------|--------|
  | TASK-20260228-01 | 2026-02-28T10:00:00Z | Review report | Trâm Anh | 2026-03-01 | staff | telegram:-5194157539 | ✅ cron-abc123 | pending |

- Update footer: **Last updated: YYYY-MM-DD by SpongeBot 🫧**

### Bước 3.5 (Optional): Create Google Tasks item for Boss
Only when:
- PIC is Boss ("Tuan Anh"/"me"), AND
- `/data/workspace/task_system.json` has `google_tasks.enabled=true` and a `tasklistId`.

Action:
- `gog tasks add <tasklistId> --title "[TASK-ID] — [description]" --due [YYYY-MM-DD] --notes "Canonical tracker: [sheet url]"`
Notes:
- Google Tasks due time may be ignored; include time in title/notes if needed (e.g., "(Wed 08:00 VN)").

### Bước 4: Create Reminder Cron
**Cron tool call (EXACT):**
```json
{
  "action": "add",
  "job": {
    "name": "task-reminder-TASK-YYYYMMDDNN",
    "schedule": { "kind": "at", "at": "[YYYY-MM-DD 12:00:00 Asia/Ho_Chi_Minh]" },
    "sessionTarget": "isolated",
    "payload": { "kind": "agentTurn", "message": "Send reminder: '🔥 Reminder: [Description] (PIC: [PIC], Deadline: [Date])' to Telegram chat [chat_id]. Use message(action=send, channel=telegram, to=[chat_id], message=...). Model: openrouter/anthropic/claude-sonnet-4.6, thinking=low." },
    "delivery": { "mode": "none" },
    "enabled": true
  }
}
```
- Capture cron ID từ response, update task.md (Reminder Set column).
- Timeout: 30s (simple send).
- TZ: ALWAYS Asia/Ho_Chi_Minh.

### Bước 5: Reply to User
```
✅ Task "[description]" created in "[bucket]" bucket (PIC: [PIC], Deadline: [date]).
Details logged in task.md.
Reminder set for 12pm [deadline date] in this chat/group.
```
- Nếu group: Mention user nếu có.

---

## Daily Sync: Google Tasks → Sheet
Boss wants: when he marks done in Google Tasks, bot updates Sheet automatically.

Implementation:
- Cron job runs **1x/day** (current: 18:00 Asia/Ho_Chi_Minh).
- It restores gog auth (keyring can disappear after container restart) before any API calls.
  - Correct restore command (important: `credentials set`):
    `GOG_KEYRING_PASSWORD=openclaw_secure_2026 gog auth credentials set /data/workspace/gog_client_secret.json --no-input && GOG_KEYRING_PASSWORD=openclaw_secure_2026 gog auth tokens import /data/workspace/gog_auth_backup.json --no-input`
- It reads `/data/workspace/task_system.json` for `tasklistId` + `spreadsheetId`.
- It fetches Google Tasks **including completed** + **all pages**:
  - `gog tasks list <tasklistId> --all --show-hidden --show-completed ...`
- It maps tasks by title prefix `TASK-YYYYMMDD-NN` and updates Sheet column **E (Status)**.

---

## Quy Tắc Xử Lý Lỗi
- **Parse fail:** Ask once, then fallback to "other" bucket.
- **task.md write fail:** Fixed ✅ (retry write); if permanent ❌, alert Boss.
- **Cron fail:** Retry once; if fail, "❌ Manual reminder needed—logged in task.md".
- **Google Tasks fail:** Log in task.md Notes; proceed without blocking.
- **Cross-chat:** Reminders only Telegram (if origin non-Telegram, send to Boss DM 171900099).

---

## File Liên Quan
- **Master list:** `/data/workspace/task.md`
- **System config:** `/data/workspace/task_system.json`
- **Canonical sheet:** see `/data/workspace/task_system.json` → `task_tracker_sheet`
- **Cron sync job:** `tasks-sync-google-tasks-to-sheet-daily`
- **Contacts for PIC:** `/data/workspace/contacts.md`

---

**Cập nhật:** 2026-03-03  
**Tác giả:** SpongeBot 🫧
