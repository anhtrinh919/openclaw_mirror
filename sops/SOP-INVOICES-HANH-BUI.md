# SOP-INVOICES-HANH-BUI — Expense receipts/invoices (image/PDF/XLSX) → Google Sheet → Excel Export

## Purpose
Handle expense receipts/invoices originating from **Hanh Bui (Telegram: 1034926814)**.

Flow (canonical for image/PDF receipts):
1) **Classify**: check whether the attachment is an expense receipt/invoice.
2) Extract **ONLY** invoice **date** + **value** from the attachment.
3) Ask **(Q1)** for **description**.
4) Ask **(Q2)** for **Expense Account**.
5) Store to Google Sheet + Drive.
6) On request (e.g., “xuất báo cáo chi phí T3”), export filtered rows into the preset Excel template and send back in chat.

---

## Trigger (STRICT)
**Any attachment from Hanh Bui (Telegram: 1034926814)** MUST be handled as follows:
1) **First**: check if it is a **receipt/invoice**.
2) If **YES** → **start this SOP immediately**.
3) If **NO / unclear** → ask a 1-line clarification (see Classifier section) and stop.

This applies even if the file is sent as a Telegram “document”.

Also apply when:
- **Boss forwards** an attachment that originated from Hanh (forwarded context present or Boss explicitly says it’s from Hanh).

---

## Receipt/Invoice classifier (how to decide)
Goal: decide **“is this an expense receipt/invoice?”** quickly.

### Strong YES signals (any 1 may be enough)
- Contains words like: **HÓA ĐƠN / BIÊN LAI / RECEIPT / INVOICE / VAT**
- Contains an obvious **TOTAL / TỔNG / THÀNH TIỀN / SỐ TIỀN / AMOUNT PAID**
- Contains **date/time** + **payment method** (Cash/Card/QR/Bank) + a store/merchant header
- Has typical receipt structure: many lines + prices + subtotal/total

### Likely YES (need ≥2)
- Merchant/store name + currency (VND/THB/USD/KHR)
- “MST / Tax code / Số HĐ / Invoice No”
- “Cashier / POS / Terminal / Batch / Ref”

### Strong NO signals
- Personal photos/screenshots unrelated to purchase
- Chat images without totals/dates/merchant (memes, random screenshots)
- Non-expense files (e.g., portraits, scenery) unless user confirms

### If unclear
Ask exactly one short question:
- **“Chị ơi file này có phải hóa đơn/biên lai để em ghi chi phí không ạ?”**
If chị says **yes** → run SOP.
If **no** → ask what she wants done with the file.

---

## Communication protocol (ONLY for confirmed receipts/invoices)
When a receipt/invoice is confirmed (even without any question):
1) **Acknowledge**: “Em nhận được hóa đơn rồi ạ.”
2) **State next step**: “Em đang lấy **ngày** và **giá trị** trên hoá đơn.”
3) Then ask **Q1** + **Q2** as per workflow below.

(For Hanh Bui chat: use chị–em tone per SPEAKING-STYLES.)

### Hard rules (avoid past failure)
- ❌ Do **NOT** ask: “Chị muốn em làm gì với ảnh này?”
- ❌ Do **NOT** list line-items / split items / summarize products.
- ✅ This SOP is about **expense logging** (date + value + description + account).

---

## Data extraction rule (strict)
From the receipt/invoice attachment, extract and confirm **ONLY**:
1) **Invoice date**
2) **Invoice value (total paid)**

❌ Do not extract: vendor name, item list, phone numbers, membership IDs, etc.

(If the user includes vendor info later inside the **description**, you may store it in `vendor`, but do not OCR vendor from the image/PDF.)

---

## Canonical storage (Google Sheets)
- Spreadsheet: **SpongeBot — Invoices (Hanh Bui)**
- Sheet ID: `14x95k1XSJwrQpzx8NcLoCdWZC5ZBSyLexmWEq-9S6yE`
- URL: https://docs.google.com/spreadsheets/d/14x95k1XSJwrQpzx8NcLoCdWZC5ZBSyLexmWEq-9S6yE/edit
- Tab: `Invoices`

### Columns (GSheet reference; not all exported)
1) `invoice_date` — ISO `YYYY-MM-DD` (the date on invoice)
2) `added_date` — Asia/Ho_Chi_Minh `YYYY-MM-DD HH:MM:SS` (recorded timestamp)
3) `vendor` — optional (ONLY if user states it in description)
4) `value` — numeric (as on invoice)
5) `currency` — e.g., `VND`, `THB`, `USD`, `KHR`
6) `metadata` — JSON **string**
7) `exported` — `TRUE/FALSE` (whether this invoice has been exported to Excel)

### Metadata JSON (store as a STRING)
Include at least:
- `description` (user-provided)
- `expense_account` (normalized: vietnam|thailand|cambodia|laos|myanmar|other)
- `drive_file_id`, `drive_url` (uploaded attachment)
- `source` (telegram) + `chat_id`
- `extracted_invoice_date_raw`, `extracted_value_raw`
- (optional) `export_batch` (e.g., "2026-03-T3")

---

## Canonical Excel template
- Local template path: `/data/workspace/templates/Hanh_expense_template.xlsx`
- Template sheet/tab: `Month_Year`
- **Header row:** 4
- **Fill starts from:** row 5

### What to fill (ONLY these columns)
- **A**: Receipt No (1..N)
- **B**: Date = invoice date (NOT record date)
- **C**: Description = mô tả
- **D**: Account Code
- **E**: Exclusive GST = Amount in VND
- **F**: Receipt/Notes → **MUST BE LEFT BLANK**

### Account Code rules (from template)
- Read mapping from template cells **C45:D49** (do not hardcode if possible).
- Special rule: **Laos / Other → SEA → 8741-4101**.

### Currency conversion rules
- If `currency == VND`: put `value` directly into column **E**.
- If `currency != VND`: convert to VND using rates in:
  - `A55` (THB→VND)
  - `A56` (USD→VND)
  - `A57` (KHR→VND)
- Parse numeric rate from strings like `"1 THB = 840 VND"`.

### Do-not-touch (critical)
- Do **NOT** modify cells/rows that contain formulas / mapping in the template, especially **rows 45–50**.

---

## Excel integrity (critical)
This template contains **externalLink** parts. Some writers (notably `openpyxl`) may rewrite/destroy the external-link relationship metadata, causing Excel warning:
> “We found a problem with some content… Do you want us to recover…?”

### Safe approach
1) **Copy** the template `.xlsx` as the export output.
2) Use a library (e.g., openpyxl) to edit ONLY the target data cells (rows 5..N, cols A..F as defined).
3) If Excel still shows the repair prompt, patch the exported `.xlsx` by restoring external-link artifacts from the template:
   - `xl/externalLinks/externalLink1.xml`
   - `xl/externalLinks/_rels/externalLink1.xml.rels`

### Notes
- Do **NOT** overwrite `xl/sharedStrings.xml` after writing values (it can break description strings).
- Optionally ensure `[Content_Types].xml` and `xl/_rels/workbook.xml.rels` still contain the externalLink entries (merge if needed; do not blindly overwrite).
- Zip-test before sending (`python -m zipfile -t file.xlsx`).

---

## Workflow

### Step 0 — Receive attachment(s) from Hanh → classify
- If classifier says **YES** → continue to Step 1.
- If **unclear** → ask: “Chị ơi file này có phải hóa đơn/biên lai để em ghi chi phí không ạ?”
- If **NO** → ask what she wants done.

### Step 1 — Extract date + value (+ ask Q1 + inline buttons if single receipt)
Reply with extracted fields (and ASK to clarify if unclear; **do not guess**):
- **Ngày:** <dd/mm/yyyy>
- **Giá trị:** <amount + currency>

Ask **Q1** (description):
- “Chị cho em xin **mô tả chi phí** này là gì ạ?”

✅ If **this is ONE receipt/invoice**, include **inline buttons** for **Expense Account** in the SAME message so the user sees them immediately.

**Telegram inline buttons requirement:** must send using the **message tool** with `buttons`.

Suggested buttons (single receipt):
- Vietnam / Thailand / Cambodia / Laos / Myanmar / Other

Callback data suggestion:
- `expense_account:vietnam`
- `expense_account:thailand`
- `expense_account:cambodia`
- `expense_account:laos`
- `expense_account:myanmar`
- `expense_account:other`

If user taps a button first → acknowledge + still ask for Q1.
If user replies Q1 first → proceed (and still need Q2).

### Step 2 — Capture Q2 (Expense Account)
**Rule from Boss:**
- If user sends **ONE invoice** → **use inline buttons**.
- If user sends **MULTIPLE invoices at once** → **DO NOT use inline buttons** (slow + error-prone).
  - Ask user to **type** the expense account for each invoice in one message.

Allowed Expense Accounts (typed):
- Vietnam / Thailand / Cambodia / Laos / Myanmar / Other

Suggested prompt format for multiple invoices:
- “Reply theo format: `#1 Vietnam, #2 Cambodia, #3 Other`”

### Step 3 — Upload attachment(s) to Drive
- Upload original file(s) to Google Drive.
- File name suggestion: `invoice_<YYYY-MM-DD>_<value>.<ext>`.
- Store `drive_file_id` + `drive_url`.

### Step 4 — Append row(s) to Google Sheet
Append 1 row per invoice to `Invoices!A:G` with:
- invoice_date
- added_date
- vendor (optional; only if user said it in description)
- value
- currency
- metadata (JSON string)
- exported = `FALSE`

### Step 5 — Export to Excel (on request)
User examples:
- “xuất cho mình báo cáo chi phí **T3**”  → month = 3
- “xuất chi phí **tháng 3/2025**” → month=3 year=2025

Interpretation:
- `T3` / `tháng 3` = March.
- If year is not provided:
  - If invoices span multiple years: ask “T3 năm nào ạ?”
  - Otherwise default to the current year.

Filter:
- Select rows where `invoice_date` is within the requested month/year.

Export behavior:
- Fill template rows starting at row 5.
- For each invoice row:
  - A = receipt no
  - B = invoice_date
  - C = description
  - D = Account Code (per template mapping; Laos/Other→SEA)
  - E = amount in VND (convert if needed)
  - F = blank

After export:
- Send the `.xlsx` file back in chat.
- Update Google Sheet: set `exported=TRUE` for invoices included in the export.
  - (Optional) also add an `export_batch` identifier into metadata.

---

## Failure modes / how to respond
- If value or currency can’t be confidently extracted: ask user to confirm (do not guess).
- If date/value can’t be confidently extracted: ask user to confirm **only those fields**.
- If currency is unclear and conversion is needed: ask user to confirm the currency.
- If Drive/Sheets write fails: state status clearly (Fixed ✅ / Permanent ❌ — action required) and retry once.
- If Excel opens with repair prompt: treat as a bug; apply the Excel integrity patch step before sending.
