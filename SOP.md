# SOP.md — Index (Token-light)

This file is intentionally short.
Rule: read this index at session start; open ONLY the relevant SOP file when a trigger happens.

---

## SOP List

### SOP-TRADE-PRINTING (Printing orders)
- Hard trigger: trusted inbound `chat_id = telegram:-5194157539` + Excel attachment (`.xlsx` / spreadsheet file) → immediately open `/data/workspace/sops/SOP-TRADE-PRINTING.md`.
- Secondary trigger: Trâm Anh (Telegram 6402311566) sends Excel/screenshot printing order.
- File: `/data/workspace/sops/SOP-TRADE-PRINTING.md`

### SOP-LEAVE-REQUESTS (Xin nghỉ)
- Hard trigger: trusted inbound `chat_id = telegram:-4121104521` + message text contains `nghỉ` → immediately open `/data/workspace/sops/SOP-LEAVE-REQUESTS.md`.
- Secondary trigger: group -4121104521 mention + `@xinnghi` / `/xinnghi` / "xin nghỉ".
- File: `/data/workspace/sops/SOP-LEAVE-REQUESTS.md`

### SOP-MORNING-REPORT
- Trigger: daily cron morning report or Boss request.
- File: `/data/workspace/sops/SOP-MORNING-REPORT.md`

### SOP-TASKS (@task)
- Trigger: Boss message begins with `@task`.
- File: `/data/workspace/sops/SOP-TASKS.md`

### SOP-DUST-RELAY (Dust communicator ↔ data scientist)
- Trigger: Boss asks to use Dust (e.g., “Dust, …”).
- File: `/data/workspace/sops/SOP-DUST-RELAY.md`

### SOP-INVOICES-HANH-BUI (Expense receipts/invoices)
- Trigger: Hanh Bui (Telegram 1034926814) sends (or Boss forwards) a receipt/invoice **attachment** (image/PDF/XLSX).
- File: `/data/workspace/sops/SOP-INVOICES-HANH-BUI.md`

### SOP-TELEGRAM-ATTACHMENT-SEND
- Trigger: SpongeBot needs to send a real file attachment to Telegram.
- File: `/data/workspace/sops/SOP-TELEGRAM-ATTACHMENT-SEND.md`

### SOP-CHASE
- Trigger: any Chase connection, project/task/note/contact operation, or any workflow that should treat Chase as the canonical project/task system.
- File: `/data/workspace/sops/SOP-CHASE.md`

### SOP-CREATE-SOP
- Trigger: Boss asks to create, write, standardize, or document a new SOP.
- File: `/data/workspace/sops/SOP-CREATE-SOP.md`

### SOP-INSTALL-SKILLS-HOOKS
- Trigger: Boss asks to install a new OpenClaw skill or hook, or debug why a newly added hook is not activating.
- File: `/data/workspace/sops/SOP-INSTALL-SKILLS-HOOKS.md`

---

Last updated: 2026-03-20
Author: SpongeBot 🫧
