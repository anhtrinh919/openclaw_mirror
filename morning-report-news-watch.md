# morning-report-news-watch.md

Purpose: Reference file for the morning report cron job.

Use this file before generating the report.

## A) Vietnam Modern Trade Watchlist (official sites)

### Hypermarket / Supermarket chains
- WinMart / WinMart+ — https://winmart.vn/
- Co.opmart (Saigon Co.op) — https://www.co-opmart.com.vn/
- GO! / Big C (Central Retail) — https://www.go-vietnam.vn/
- MM Mega Market Vietnam — https://mmvietnam.com/
- LOTTE Mart Vietnam — https://www.lottemart.com.vn/
- AEON Vietnam / AEON Mall — https://aeon.com.vn/ | https://aeonmall-vietnam.com/
- Emart Vietnam — https://emartvn.com.vn/
- BRGMart — https://brgmart.vn/
- Satrafoods — https://satrafoods.com.vn/
- Bach Hoa Xanh — https://www.bachhoaxanh.com/

### Convenience chains
- Circle K Vietnam — https://www.circlek.com.vn/
- FamilyMart Vietnam — https://www.familymart.vn/
- GS25 Vietnam — https://gs25.com.vn/
- 7-Eleven Vietnam — https://www.7-eleven.vn/
- Ministop Vietnam — https://www.ministop.vn/

## B) Retail news collection rules (STRICT)

1) Time window = previous day only (Vietnam time, Asia/Ho_Chi_Minh).
2) Build date range as `YYYY-MM-DDtoYYYY-MM-DD` where both ends are yesterday date.
3) Search only for items published on previous day.
4) If no previous-day item found across the retailer list, output exactly: `No update`.
5) Keep retail section concise (max 3 bullets if updates exist).

Suggested search patterns:
- "Vietnam retail [chain] news"
- "[chain] Vietnam update"
- "[chain] khai trương OR mở rộng OR doanh thu OR khuyến mãi"

## C) AI Watch (merged into morning report)

This replaces separate AI watch task. Check previous day only.

### Required topics
1) OpenClaw
   - Official docs: https://docs.openclaw.ai
   - GitHub releases: https://github.com/openclaw/openclaw/releases
   - Repo: https://github.com/openclaw/openclaw

2) pencil.dev
   - Site: https://pencil.dev
   - Any official changelog/update/blog pages on pencil.dev

3) New AI applications (task-focused)
   - Browser agents
   - Coding/dev tools
   - Spreadsheet/data tools
   - Design/video/content tools
   - Sales/support/ops automation tools

### AI watch rules (STRICT)
1) Previous day only (Asia/Ho_Chi_Minh), same date-range rule as retail.
2) Only include credible sources (official product blogs/docs/repos or reputable tech media).
3) If no previous-day updates found across all AI topics, output exactly: `No update`.
4) If updates exist, keep to max 3 bullets total (high signal only):
   - product/source
   - what changed
   - why it matters (one short phrase)

## D) Output style constraints
- Prioritize facts over hype.
- No speculation.
- No stale news beyond previous day.
- If uncertain publication date, exclude the item.