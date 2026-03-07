# SOP-DUST-RELAY — Dust (dust.tt) ↔ OpenClaw (“Communicator ↔ Data Scientist”)

(Extracted from legacy `/data/workspace/SOP.md`. One SOP per file.)

---

# SOP Dust (dust.tt) ↔ OpenClaw — “Communicator ↔ Data Scientist” Workflow

## Mục tiêu
OpenClaw đóng vai trò **communicator**: gửi câu hỏi cho Dust agent như một "data scientist", chờ Dust chạy **tất cả tools/dữ liệu** nó có, lấy **FULL reply**, sau đó OpenClaw chỉ **tóm tắt key figures + key facts** cho Boss.

**Nguyên tắc:**
- ✅ Dust trả lời đầy đủ + có số liệu/bằng chứng (nếu có)
- ✅ OpenClaw chỉ tóm tắt (không tự bịa số)
- ✅ Chấp nhận Dust có thể mất **tới 10 phút**

---

## Quy tắc “Clarify” (cập nhật)
**Mặc định: KHÔNG hỏi lại user để clarify.**
- Nếu user đã dùng format kiểu **“Dust, …”** → **pass thẳng** câu hỏi sang Dust.
- OpenClaw chỉ hỏi lại user **khi và chỉ khi** Dust phản hồi rằng **thiếu thông tin / cần làm rõ** (ví dụ: ngày nào, scope nào, store nào, division definition nào).

Mục tiêu là tránh làm gián đoạn user: Dust có đủ knowledge/context để tự suy ra/tra cứu phần lớn các thông tin.

---

## Config (hiện tại)
- **Dust base URL:** `https://dust.tt`
- **Workspace ID:** `Jb3tKIEjjE`
- **Agent:** `@lc-main`
- **Resolved agent configurationId (sId):** `7z5y4GH8Dz` (lookup qua `GET /assistant/agent_configurations`)

**Local files:**
- **API key file:** `/data/workspace/.dust_api_key` (chmod 600) — *KHÔNG ghi key vào SOP/MEMORY/log chat*
- **Profile:** `/data/workspace/dust_profile.json`
- **Relay script:** `/data/workspace/dust_relay.py`

---

## Luồng Chuẩn (1 query)
1) **Soạn prompt cho Dust**
   - (Theo rule Clarify ở trên) ưu tiên pass-through, chỉ thêm context tối thiểu nếu đã có.
   - Nói rõ ngày cần phân tích + ngày so sánh (nếu user yêu cầu)
   - Yêu cầu **chỉ trả 1 lần khi xong** (không gửi progress)
   - Yêu cầu cấu trúc output rõ: TL;DR → bảng số → root causes + evidence → actions

2) **Gọi Dust (đợi tối đa 10 phút)**
```bash
DUST_API_KEY="$(cat /data/workspace/.dust_api_key)" \
python3 /data/workspace/dust_relay.py \
  --workspace Jb3tKIEjjE \
  --agent-handle @lc-main \
  --prompt "[YOUR PROMPT HERE]"
```

3) **Nhận FULL Dust reply**
- Nếu nhận được đầy đủ: chuyển sang bước 4.
- Nếu rỗng/thiếu: xem Troubleshooting.

4) **OpenClaw tóm tắt cho Boss**
- Key figures
- Key facts
- Top 3 causes (kèm evidence)
- Top 5 actions

---

## Streaming / Độ tin cậy (đã fix)
**Vấn đề gặp phải (test đầu):** đôi khi SSE stream có thể kết thúc sớm hoặc không trả `agent_message_success` theo cách relay cũ bắt được → output rỗng.

**Fix (2026-03-02):** `dust_relay.py` đã:
- reconnect stream với `?lastEventId=`
- fallback `GET /assistant/conversations/{cId}` để lấy final agent message content

---

## Tool approvals (tự approve)
Nếu Dust yêu cầu approve tool execution (event `mcp_approve_execution`), relay sẽ auto-approve qua:
- `POST /assistant/conversations/{cId}/messages/{messageId}/validate-action`

---

## Lưu ý quyền truy cập (Dust)
- Một số **personal tools** (ví dụ Gmail cá nhân) có thể báo lỗi “Personal tools require the user to be authenticated” khi gọi bằng workspace API key.
- Các connector dữ liệu kiểu workspace (ví dụ BI/warehouse như BigQuery) có thể chạy OK.

---

## Bài test thành công (reference)
**Query:** “Doanh số hôm T7 sao thấp thế?” (T7=2026-02-28; so với T6=02-27 và T7 tuần trước=02-21)
- Dust chạy **8 queries** và trả báo cáo đầy đủ gồm bảng số + nguyên nhân + actions.
- OpenClaw tóm tắt key figures: Turnover ~5.09B VND; Orders & customer count giảm ~10% vs tuần trước; AOV tăng ~15%; GM% giảm ~3.2pp; promo weight tăng mạnh.

---

**Cập nhật:** 2026-03-03
**Tác giả:** SpongeBot 🫧
