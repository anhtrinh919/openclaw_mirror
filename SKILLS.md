# SKILLS.md — Active Skills & How to Use Them

This file is a **human-friendly index** of the skills currently available in this OpenClaw workspace, plus quick examples for how you (Boss) can request them.

> Note: Skills are installed as folders containing `SKILL.md` + optional scripts/docs under:
> - Built-in (system): `/usr/local/lib/node_modules/openclaw/skills/<skill>/`
> - Workspace (custom/installed): `/data/workspace/skills/<skill>/`

---

## Slides / Presentations

### agent-browser (workspace)
- **Purpose:** Structured browser automation (navigate/click/type/snapshot) for web apps without APIs.
- **Where:** `/data/workspace/skills/agent-browser/SKILL.md`
- **Example asks:**
  - “Use agent-browser to log into X site and download the latest report.”
  - “Use agent-browser to update this web form daily.”

---

## Security / Safety

### arc-security-audit (workspace)
- **Purpose:** Audit the agent’s skill stack and basic risk posture; highlights suspicious skills/config.
- **Where:** `/data/workspace/skills/arc-security-audit/SKILL.md`
- **Example asks:**
  - “Run arc-security-audit and summarize the findings.”
  - “Audit newly installed skills before we enable them.”

---

## Spreadsheets / Excel

### excel-xlsx (workspace)
- **Purpose:** Read/write/generate Excel with correct types/dates/formulas; fewer parsing quirks.
- **Where:** `/data/workspace/skills/excel-xlsx/SKILL.md`
- **Example asks:**
  - “Use excel-xlsx to extract these tabs and build a summary table.”
  - “Write this forecast back into an XLSX template.”

### gog (system)
- **Purpose:** Google Workspace CLI (Gmail/Calendar/Drive/Sheets/Docs/Contacts).
- **Where:** `/usr/local/lib/node_modules/openclaw/skills/gog/SKILL.md`
- **Example asks:**
  - “Append these rows to the task tracker sheet.”
  - “List my calendar today.”

---

## Scheduling

### scheduler-expert (workspace)
- **Purpose:** Create/update OpenClaw cron jobs and reminders correctly.
- **Where:** `/data/workspace/skills/scheduler-expert/SKILL.md`
- **Example asks:**
  - “Set a daily reminder at 09:15 VN time.”
  - “Change cron X from 16:30 to 16:00 starting tomorrow.”

---

## GitHub

### github / gh-issues (system)
- **Purpose:** `gh`-powered PR/issue ops; and a workflow skill for issue→fix→PR.
- **Where:**
  - `/usr/local/lib/node_modules/openclaw/skills/github/SKILL.md`
  - `/usr/local/lib/node_modules/openclaw/skills/gh-issues/SKILL.md`

---

## Messaging

### discord (system)
- **Purpose:** Discord ops via `message` tool (`channel=discord`).
- **Where:** `/usr/local/lib/node_modules/openclaw/skills/discord/SKILL.md`

---

## Notes / Next improvements

- This index is **manual** (kept intentionally short). If you want, I can add:
  - an “Installed skills list” section (auto-generated)
  - recommended usage patterns for your workflows (PLL forecast / P&L decks / reminders)
