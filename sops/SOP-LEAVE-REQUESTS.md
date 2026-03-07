# SOP-LEAVE-REQUESTS — Quy Trình Xin Nghỉ

(Extracted from legacy `/data/workspace/SOP.md`. One SOP per file.)

---

# SOP Leave Request - Quy Trình Xin Nghỉ

## Tổng Quan

Quy trình xử lý yêu cầu xin nghỉ từ nhân viên trong group Telegram -4121104521 → Boss approval → Tạo calendar event.

---

## Config

**Group:** `-4121104521` (requireMention: true, groupPolicy: open)
**Language:** Tiếng Việt (luôn respond bằng tiếng Việt trong group này)
**Pending limit:** 1 request tại một thời điểm
**Tracking file:** `/data/workspace/leave_requests.json`

---

## Luồng Chính

```
User mention + trigger (@xinnghi / /xinnghi / "xin nghỉ")
    ↓
Bot: Parse ngày nghỉ + lý do (hoặc hỏi lại)
    ↓
Bot: Lưu pending request → Reply "Đã nhận. Chờ duyệt"
    ↓
Bot: DM Boss → Gửi request details → Chờ approval
    ↓
Boss reply "duyệt" hoặc "từ chối"
    ↓
If approved:
    - Bot: Reply group "@user Đã duyệt"
    - Bot: Tạo calendar event (restore gog auth trước)
If rejected:
    - Bot: Reply group "@user Đã từ chối"
```

---

## Chi Tiết Các Bước

### Bước 1: Trigger Detection

**Trigger patterns** (trong group -4121104521):
- Mention bot + `@xinnghi`
- Mention bot + `/xinnghi`
- Mention bot + "xin nghỉ"

**Language:** Bot LUÔN respond bằng tiếng Việt trong group này.

---

### Bước 2: Parse Ngày Nghỉ & Lý Do

**Input formats:**
- 1 ngày: "nghỉ ngày 28/2", "nghỉ 28/02", "nghỉ thứ 6"
- Range: "28/2 - 2/3", "từ 28/2 đến 2/3"
- Relative: "nghỉ 3 ngày tới", "nghỉ tuần sau"
- Half-day: "nghỉ sáng", "nghỉ chiều", "1/2 ngày"

---

### Bước 3: Save Pending Request

**File:** `/data/workspace/leave_requests.json`

```json
{
  "pending": {
    "id": "LR-YYYYMMDDNN",
    "userId": 123456789,
    "userName": "Nguyễn Văn A",
    "dates": { "start": "2026-02-28", "end": "2026-03-02" },
    "reason": "Đi đám cưới",
    "status": "pending",
    "createdAt": "2026-02-27T08:00:00Z"
  },
  "history": []
}
```

---

### Bước 4: DM Boss

```
📋 Yêu cầu xin nghỉ:

👤 Người yêu cầu: [Tên] (user ID: [ID])
📅 Ngày nghỉ: [Ngày] ([Số ngày])
📝 Lý do: [Lý do]

Reply "duyệt" để approve hoặc "từ chối" để reject.
```

---

### Bước 5 & 6: Approval + Calendar Event

**Boss reply:** "duyệt" → Approved | "từ chối" → Rejected

#### Pre-flight (auth restore)
```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 gog auth credentials /data/workspace/gog_client_secret.json && \
GOG_KEYRING_PASSWORD=openclaw_secure_2026 gog auth tokens import /data/workspace/gog_auth_backup.json
```

#### Calendar creation

**A) Full-day leave (nghỉ cả ngày / nhiều ngày):**
```bash
GOG_KEYRING_PASSWORD=openclaw_secure_2026 gog calendar create tuananhtrinh919@gmail.com \
  --account tuananhtrinh919@gmail.com \
  --summary "[Tên user] - [Lý do]" \
  --from "YYYY-MM-DD" \
  --to "YYYY-MM-DD" \
  --all-day
```

**B) Half-day leave (nghỉ sáng/chiều):**
- Nghỉ sáng (VN): `08:00–12:00`
- Nghỉ chiều (VN): `13:00–17:00`

Use RFC3339 (UTC) to avoid timezone ambiguity:
```bash
# Example: nghỉ sáng 05/03/2026 (VN) = 01:00–05:00 UTC
GOG_KEYRING_PASSWORD=openclaw_secure_2026 gog calendar create tuananhtrinh919@gmail.com \
  --account tuananhtrinh919@gmail.com \
  --summary "[Tên user] - Nghỉ sáng ([Lý do])" \
  --from "2026-03-05T01:00:00Z" \
  --to   "2026-03-05T05:00:00Z" \
  --reminder "popup:30m"
```

---

**Cập nhật:** 2026-03-04
**Tác giả:** SpongeBot 🫧
