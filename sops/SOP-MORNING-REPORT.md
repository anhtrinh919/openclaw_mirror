# SOP-MORNING-REPORT — Quy Trình Báo Cáo Sáng

(Extracted from legacy `/data/workspace/SOP.md`. One SOP per file.)

---

# SOP Daily Morning Report - Quy Trình Báo Cáo Sáng

## ⭐ APPROVED PERFECT TEMPLATE (2026-02-28, Boss confirmed)

```
🫧 DAILY REPORT — [Weekday, DD Mon YYYY] 🫧

━━━━━━━━━━━━━━━━━━━━

📧 EMAIL ACTIONS REQUIRED ([N] unread)

🔥 Priority:
• [Sender]: [Subject] — [Action needed]
• [Sender]: [Subject] — [Action needed]

📋 Review:
• [Sender]: [Subject] — [Impact/notes]
• [Sender]: [Subject] — [Impact/notes]

━━━━━━━━━━━━━━━━━━━━

🤖 AGENT WORK RECAP (Last 24h)

✅ Completed Tasks:
• 📊 [Task] — [Details]
• 📝 [Task] — [Details]
• 🗓️ [Task] — [Details]

📈 Sessions Active:
• [N] session(s) ([channels]) — [N]k tokens processed
• Key activities: [summary]

⚠️ Issues Resolved:
• [Issue] → [Fix applied]

━━━━━━━━━━━━━━━━━━━━

🏪 VN RETAIL NEWS (Last 7 days)

📈 Key Updates:
• [Chain] — [Update]
• [Chain] — [Update]
• [Context] — [Notable event]

🎯 Action: [Urgent item or "No urgent items — market stable"]

━━━━━━━━━━━━━━━━━━━━

📅 TODAY'S SCHEDULE ([Weekday, DD Mon])

🕘 [Time slot]:
• [HH:MM] — [Event]: [Person/Details] 🔥

📋 [Category] ([N] people/items):
• [Person/Item] — [Status/detail]
• [Person/Item] — [Status/detail]

🖨️ [Category]:
• [N] [items] total — [brief description]
• Latest: [item] ([quantity])

━━━━━━━━━━━━━━━━━━━━

✨ ACTION ITEMS FOR BOSS:

🔥 Urgent:
• [HH:MM] [Event] — [Person/context]

📋 Review:
• [Item] — [Why it matters]
• [Item] — [Why it matters]

📊 Monitor:
• [Item] — [What to watch]
• [Item] — [What to watch]

━━━━━━━━━━━━━━━━━━━━

🎯 Quality Gate Status: ✅ All checks passed
📝 Syntax Fixes: ✅ [Status or "None needed"]

Ready for the day, Boss! 🫧
```

---

## Config

**Cron Job ID:** `1ecc6e06-c111-44bb-8167-b4c517750d0d`
**Schedule:** `0 6 * * *` (6:00 AM daily, Asia/Ho_Chi_Minh)
**Session Target:** `isolated`
**Model:** `openai-codex/gpt-5.2`
**Delivery:** Telegram DM → Boss (171900099)

---

## Step 0: Pre-Flight (ALWAYS FIRST)

```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 gog auth credentials /data/workspace/gog_client_secret.json && \
GOG_KEYRING_PASSWORD=openclaw_secure_2026 gog auth tokens import /data/workspace/gog_auth_backup.json
```

**Quality gate rules:**
- Test EACH tool before compiling
- Fail → retry ONCE with corrected syntax
- Still fail → mark section `❌ Failed: [error]`
- NEVER send report without all sections (or explicit ❌ acknowledgment)

---

## Step 1: Email Recap

**Command (EXACT):**
```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 gog gmail search "is:unread OR is:important" --account tuananhtrinh919@gmail.com --max 10
```

**Output target:**
- 🔥 Priority: action-required emails (updates, invoices, deadlines)
- 📋 Review: informational emails (reports, pricing, announcements)
- Skip: pure promotions unless notable

---

## Step 2: Agent Work Recap (ALL sessions, last 24h)

**Commands (EXACT):**
```typescript
// Step A: Get all sessions
sessions_list({ activeMinutes: 1440, limit: 20 })

// Step B: For EACH session found, get history
sessions_history({ sessionKey: "[key]", limit: 50 })
```

**Coverage:** ALL channels — Telegram, Discord, WhatsApp, UI
**Output target:**
- ✅ Completed Tasks: what was done (with emoji context 📊📝🗓️⚙️🧪)
- 📈 Sessions Active: count + channel + tokens processed
- ⚠️ Issues Resolved: errors fixed (with → arrow showing fix)

---

## Step 3: VN Retail News

**Commands (EXACT):**
```typescript
web_search({ query: "Vietnam retail news WinMart Big C Lotte Mart 2026", country: "ALL", count: 5 })
web_search({ query: "Vietnam supermarket Aeon Co.opmart Circle K GS25 FamilyMart 7-Eleven news 2026", country: "ALL", count: 3 })
```

⚠️ `country: "ALL"` — NEVER use "VN" (invalid, causes error)

**Output target:**
- 📈 Key Updates: 2-4 notable items across all chains
- 🎯 Action: "No urgent items — market stable" OR specific action if needed

---

## Step 4: Today's Schedule

**Command (EXACT):**
```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 gog calendar events --today --account tuananhtrinh919@gmail.com
```

⚠️ Use `events --today` NOT `events list --tz`

**Output target:**
- Group by time slot (Morning / Afternoon / Evening)
- 🔥 on time-sensitive/interview items
- Include leave requests from `/data/workspace/leave_requests.json`
- Include printing orders from sheets

**Printing Sheet command:**
```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 gog sheets get 1-O_B27mSDqfEZemD27bPNmWtfnV3cW51LeClBmSwB6c "Sheet1!A1:Z10" --account tuananhtrinh919@gmail.com
```

---

## Step 5: Action Items for Boss

Synthesize from all sections above into 3 buckets:
- 🔥 **Urgent:** Time-sensitive today (interviews, deadlines, approvals)
- 📋 **Review:** Items needing Boss attention but not urgent
- 📊 **Monitor:** Background items to watch

---

## Step 6: Delivery

```typescript
message({
  action: "send",
  channel: "telegram",
  to: "171900099",
  message: "[compiled report using APPROVED TEMPLATE above]"
})
```

---

## Formatting Rules (STRICT)

| Rule | Detail |
|------|--------|
| Dividers | `━━━━━━━━━━━━━━━━━━━━` between sections |
| Urgency | 🔥 for time-sensitive items |
| Bullets | `•` not `-` |
| Sections | 📧 🤖 🏪 📅 ✨ |
| Length | < 500 words (avoid truncation) |
| Footer | Always end: `Ready for the day, Boss! 🫧` |

---

## Fallback

```
⚠️ Morning report errors:
❌ [Section]: [Error detail]
Boss please check manually.
```

---

## Common Errors Reference

| Error | Cause | Fix |
|------|-------|-----|
| `expected "<query>"` | Gmail missing query | Add `"is:unread OR is:important"` |
| `unknown flag --tz` | Wrong calendar flag | Use `--today` not `--tz` |
| `expected "<range>"` | Sheets missing range | Add `"Sheet1!A1:Z10"` |
| `'VN' invalid country` | Wrong Brave param | Use `country: "ALL"` |
| `no TTY for keyring` | Missing env var | Add `GOG_KEYRING_PASSWORD=openclaw_secure_2026` |
| Report truncated | Too verbose output | Reduce words; keep template + <500 words |

---

**Cập nhật:** 2026-02-28
**Tác giả:** SpongeBot 🫧
