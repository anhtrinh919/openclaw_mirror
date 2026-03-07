# SOP_trade_order.md - Quy Trình Quản Lý Đơn In Ấn

**Google Sheets Created on 2026-02-25:** ID: 1-O_B27mSDqfEZemD27bPNmWtfnV3cW51LeClBmSwB6c | URL: https://docs.google.com/spreadsheets/d/1-O_B27mSDqfEZemD27bPNmWtfnV3cW51LeClBmSwB6c/edit

## Mục Tiêu
Hỗ trợ user 6402311566 (Trâm Anh) quản lý đơn in ấn qua Telegram DM. Tất cả giao tiếp bằng tiếng Việt.

## Database
- Google Sheet: \"Printing Orders Database\" (ID: 1-O_B27mSDqfEZemD27bPNmWtfnV3cW51LeClBmSwB6c).
- Fallback: CSV tại /data/workspace/printing_orders.csv (migrate khi có new data).
- Cột: date (YYYY-MM-DD), supplier, item name, dimension 1, dimension 2, quantity (số), note.

## Protocol Xử Lý Tin Nhắn
1. Detect sender ID == 6402311566 → Switch to Vietnamese.
2. Parse tin nhắn (ví dụ: \"In 100 tờ từ ABC, 21x29.7\"): Extract fields (default date = today).
3. Nếu thiếu: Hỏi clarify (e.g., \"Chị ơi, số lượng bao nhiêu ạ?\").
4. Verify max 2 lần; nếu không reply, default (e.g., qty=1, note=\"unclear\").
5. Log: Append row vào Sheet via API (curl with access_token) or CSV fallback.
6. Confirm: \"Đã ghi đơn in: [tóm tắt]. Cảm ơn chị!\"

## Báo Cáo
- Hàng ngày 5pm VN: Tổng hợp logs, gửi Boss qua main session.

## Skills/Tools
- API direct (curl).
- edit/write: CSV.
- memory_search: Convo recall.

## Edge Cases
- Lỗi parse: Hỏi lại.
- Token expire: Auto refresh.
- Non-order msg: Ignore.

**Setup Complete:** Sheet + API ready. User DM testing.