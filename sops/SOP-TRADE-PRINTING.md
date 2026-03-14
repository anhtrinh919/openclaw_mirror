# SOP-TRADE-PRINTING — Quy Trình Xử Lý Đơn Hàng In Ấn

(Extracted from legacy `/data/workspace/SOP.md`. One SOP per file.)

---

# SOP Trade - Quy Trình Xử Lý Đơn Hàng In Ấn

## Tổng Quan

Quy trình xử lý đơn hàng in ấn từ file Excel/screenshot → tổng hợp vào Google Sheet.

---

## Hard Trigger Rule

This SOP should be treated as a **hard route**, not a soft suggestion, in the highest-confidence case below.

### Immediate hard trigger
If trusted inbound metadata shows:
- `chat_id = telegram:-5194157539`, and
- the message includes an Excel attachment (`.xlsx` / spreadsheet file)

then the assistant must:
1. immediately open and follow this SOP,
2. reply with a short acknowledgment that processing has started,
3. process the order without waiting for extra keywords or clarification.

Do **not** require phrases like “đơn in”, “lên sheet”, or other natural-language hints when that attachment rule is already satisfied.

### Workflow continuity rule
After this SOP is triggered for a given order/thread, keep treating subsequent related follow-up turns as part of the same printing workflow until one of these happens:
- the order is fully processed,
- the user clearly changes topic,
- or the user explicitly says to stop/cancel.

So follow-up shorthand like:
- “up lên sheet giúp mình với”
- “cái Google Sheet mà cậu vẫn hay đẩy lên ấy”
- “xong chưa”
- “check lại giúp mình”

should stay inside this SOP context rather than falling back to generic chat behavior.

---

## Luồng Chính

```
User gửi file Excel/screenshot
    ↓
Main: Thông báo "đã nhận, đang xử lý..."
    ↓
Spawn sub-agent (GPT-5.2) để xử lý
    ↓
Sub-agent: Đọc file → Tổng hợp → Ghi GSheet → Quality check
    ↓
Main: Thông báo "đã xong" cho user
```

---

## Chi Tiết Các Bước

### Bước 1: Nhận File & Thông Báo

**Trigger:**
- Hard trigger: trusted inbound `chat_id = telegram:-5194157539` + Excel attachment (`.xlsx` / spreadsheet file)
- Or: user `6402311566` gửi tin nhắn DM chứa file Excel / screenshot đơn in
- Or: group `-5194157539` gửi screenshot có bảng kê đơn hàng

**Quy tắc:** 1 file/bảng = 1 đơn hàng

**Action của Main:**
1. Thông báo ngắn: "Đã nhận thông tin, đang xử lý..."
2. Spawn sub-agent (model: `openai-codex/gpt-5.2`) để làm task

---

### Bước 2: Đọc File Excel & Tổng Hợp

**Cấu trúc file Excel:**
- **A1:** `NCC: [Tên nhà cung cấp]`
- **A2:** `CT: [Tên chương trình]`
- **A5 trở đi:** Data (header ở row 3)

| Cột | Nội dung |
|-----|----------|
| A | Tên hạng mục |
| B | STT |
| C | Siêu Thị |
| D | Code |
| E | Số lượng |
| F | Chất liệu |
| G | Đơn giá |
| H | Dài |
| I | Rộng |
| J | Thành Tiền |

**Logic tổng hợp:**
1. Group data theo: `(Tên hạng mục + Chất liệu + Đơn giá + Dài + Rộng)`
2. Tính tổng SL = SUM(Số lượng) cho mỗi group
3. Tính tổng thành tiền = SUM(Thành Tiền) cho mỗi group
4. Map SL từng siêu thị vào cột tương ứng

---

### Bước 3: Ghi Vào Google Sheet

**GSheet:** `https://docs.google.com/spreadsheets/d/1cHzgteJN6LfhrQdiZI8IABp_rJ17Xr-RoAqOoTCCBWc`
**Sheet:** `Tổng hợp`

**Cấu trúc GSheet:**
- Row 1: Title
- Row 2: Header
- Row 3+: Data (append mới, không đè)

**Mapping cột:**

| GSheet | Nội dung | Source |
|--------|----------|--------|
| A | Thời gian | Ngày nhận file (dd/mm/yyyy) |
| B | CT | Từ A2 file Excel |
| C | Tên hạng mục | Từ cột A file Excel |
| D | Chất liệu | Từ cột F file Excel |
| E | Rộng | Từ cột I file Excel |
| F | Dài | Từ cột H file Excel |
| G | Đơn giá | Từ cột G file Excel |
| H | Thành tiền | Tổng thành tiền của hạng mục |
| I | Số lượng | Tổng SL của hạng mục |
| J-AH | SL theo siêu thị | Map theo Code (xem bảng dưới) |
| AI | NCC | Theo rule NCC theo Chất liệu (xem dưới) |

**Map Code → Cột GSheet:**

| Code | Cột | Code | Cột | Code | Cột |
|------|-----|------|-----|------|-----|
| BVI | J | LQU | N | TTH | Y |
| CNG | K | PXU | O | VYE | Z |
| HDI | L | XKH | P | TDI | AA |
| CSO | M | DAN | Q | PHY | AB |
| | | TTI | R | GTH | AC |
| | | XMA | S | DTR | AD |
| | | PYE | T | QYE | AE |
| | | TNG | U | DVA | AF |
| | | CLI | V | LNH | AG |
| | | KMO | W | VP | AH |
| | | TNU | X | HNA | **AG (gộp vào LNH)** |

> **Note (Boss update):** `HNA` và `LNH` dùng **chung 1 cột** → ghi `HNA` vào **cột LNH (AG)**.

**Rule NCC theo Chất liệu (Trâm Anh update):**
- Nếu **Chất liệu** là **“Bạt in phun hiflex 720”** hoặc **“Bạt in phun hiflex 720 2da”** → **NCC = Hoàng Việt**
- Các **chất liệu còn lại** → **NCC = Đối tác vàng**

---

### Bước 4: Quality Check

**Check 1: Tổng Số Lượng**
- Tổng SL ở cột I phải bằng tổng SL ở các cột J-AH

**Check 2: Tổng Thành Tiền**
- Thành tiền trong GSheet phải bằng tổng thành tiền từ file Excel

**Kết quả:**
- ✅ Nếu pass → Thông báo "đã xong"
- ❌ Nếu fail → Sửa lỗi (thử tối đa 2 lần)

---

## Quy Tắc Spawn Sub-Agent

### Khi Nào Spawn?
- **LUÔN** spawn sub-agent cho task xử lý file Excel/GSheet
- Sub-agent dùng model: `openai-codex/gpt-5.2`

### Kiến Thức Cần Truyền Cho Sub-Agent:
1. Cách cài pandas/openpyxl (nếu chưa có)
2. Cấu trúc file Excel (A1, A2, header row 3, data từ row 5)
3. Cách group & tổng hợp data
4. Cấu trúc GSheet & mapping cột
5. Với bất kỳ bước Google auth / restore nào, đọc và follow `/data/workspace/sops/SOP-GOG-AUTH.md` (đặc biệt Step 0)
6. Cách quality check

### Communication:
- ❌ Sub-agent KHÔNG communicate với user/group
- ✅ Sub-agent chỉ announce về main session
- ✅ Main session communicate với user

---

## Quy Tắc Xử Lý Lỗi

### Lỗi Hệ Thống (API error, spawn failed, model unresponsive)
1. Tự spawn lại 1 lần nữa
2. Nếu spawn 2 lần vẫn fail → Báo về Boss (Telegram: 171900099)

### Lỗi Thực Hiện (sub-agent spawn ok nhưng thao tác lỗi)
1. Tự tìm cách sửa lỗi (thử tối đa 2 lần)
2. Nếu vẫn fail → Báo về Boss với chi tiết lỗi

---

## Xử Lý Screenshot

Nếu user gửi screenshot thay vì Excel:
1. Dùng OCR hoặc browser tool để đọc bảng
2. Extract data theo cấu trúc tương tự Excel
3. Process như bình thường

---

## File Liên Quan

- **Google Sheet:** `1cHzgteJN6LfhrQdiZI8IABp_rJ17Xr-RoAqOoTCCBWc`
- **Google auth SOP:** `/data/workspace/sops/SOP-GOG-AUTH.md`
- **Gog Auth Backup:** `/data/workspace/gog_auth_backup.json`
- **Gog Client Secret:** `/data/workspace/gog_client_secret.json`
- **Keyring Password:** `openclaw_secure_2026`
- **Account:** `tuananhtrinh919@gmail.com`

---

## Ví Dụ Thực Tế

**File Excel:**
```
A1: NCC: Đối tác vàng
A2: CT: Trang trí khu bán thùng
A5-J28: Fomex 1 (24 siêu thị, mỗi nơi SL=2)
A29-J52: Fomex 2 (24 siêu thị, mỗi nơi SL=5)
A53-J76: Fomex 3 (24 siêu thị, mỗi nơi SL=1)
```

---

**Cập nhật:** 2026-03-13
**Tác giả:** SpongeBot 🫧
