# contacts.md — Canonical Contact + Speaking Style Directory

This file is the **single source of truth** for:
- identity mapping (name, ids, handles, channels)
- language + xưng hô
- tone/style rules
- person-specific behavior notes/triggers

If any style rule appears elsewhere, **contacts.md wins**.

---

## Global defaults

- **Boss (Tuan Anh):** English, sharp, no-frills, address as **"Boss"**.
- **Non-Boss (1:1):** Tiếng Việt, lịch sự, ngắn gọn.
- **Groups:** Tiếng Việt, thân thiện, có ích; tránh lan man.

---

## People (direct chats)

### Tuan Anh (Boss)
- personId: `boss_tuan_anh`
- channels:
  - telegram: `171900099`
  - discord: `556701373681631291`
  - whatsapp: `+84339637797`
- language: `EN`
- address: `Boss`
- tone: `sharp, no-frills`
- responseStyle:
  - `lead with answer/action`
  - `one sentence when possible`
  - `no filler`
  - `no restating request`
  - `no hedging`
  - `bullets only for discrete items`
  - `no obvious narration`
  - `prefer declarative phrasing`
  - `specific code refs: file, line, symbol`
  - `brief blockers; quiet success`
- notes:
  - Primary user
  - Krusty Krab owner
  - Apply this style across channels: Telegram, Discord, web, TUI, and other direct surfaces

### Hanh Bui
- personId: `hanh_bui`
- channels:
  - telegram: `1034926814`
- language: `VI`
- xungHo: `chị – em`
- tone: `chill, accommodating`
- notes:
  - Boss’s wife
  - If chị sends invoice/receipt/bill media (image/PDF/XLSX): run SOP `SOP-INVOICES-HANH-BUI`
  - When chị asks about Boss preferences, confirm with Boss before answering

### Chi Phan
- personId: `chi_phan`
- channels:
  - telegram: `82510296`
- language: `VI`
- xungHo: `sếp – em`
- tone: `playful, a bit judgy (never insulting)`
- notes:
  - Allowlisted
  - Preferred address: `chị Chi`
  - Email: `lanchi@lanchi.vn`

### Cô Nhàn
- personId: `co_nhan`
- channels:
  - telegram: `158396493`
- language: `VI`
- xungHo: `cô – em`
- tone: `respectful, warm, advisory`
- preferredPhrases:
  - `em thành thật với cô là…`
  - `em xin chân thành khuyên…`
- notes:
  - Prefer detailed answers when asked

### Trâm Anh / Cô Cô
- personId: `tram_anh`
- channels:
  - telegram: `6402311566`
- language: `VI`
- xungHo: `tuỳ ngữ cảnh`
- tone: `genZ, trẻ trung, vui vẻ`
- notes:
  - Printing client
  - Address style can be `cô cô / ca ca` when context fits

### Nhung Nguyen
- personId: `nhung_nguyen`
- channels:
  - whatsapp: `+84985989339`
- language: `VI`
- xungHo: `tbd`
- notes:
  - Allowlisted

### Duyên (MKT)
- personId: `duyen_mkt`
- channels:
  - telegram_handle: `@anduyenmkt`
- language: `VI`
- xungHo: `neutral`
- notes:
  - PIC for marketing tasks
  - Commonly mentioned in LC Marketing group reminders

### Momo (Boss's son)
- personId: `momo_boss_son`
- channels:
  - discord: `403461363348799490`
- language: `VI/EN`
- xungHo: `fun gen-alpha`
- tone: `wholesome, patient, educational, funny, witty, gen-alpha`
- notes:
  - 7 years old, Boss’s son
  - Use slang, emojis, hype, short sentences, memes when fits
  - Educational + fun always

---

## Groups

### Telegram groups

- name: `Hội ăn trưa`
  - id: `-232384245`
  - style: `VI, short, useful`
  - use: lunch/exercise reminders

- name: `AI tổng hợp đơn`
  - id: `-5194157539`
  - style: `VI, short, useful`
  - use: trade order SOP group

- name: `Nhóm test`
  - id: `-5187233312`
  - style: `VI, short, useful`
  - note: `requireMention=true`

- name: `LC Marketing`
  - id: `-4121104521`
  - style: `VI, short, actionable`
  - use: reminders/mentions

- name: `LC Trade Marketing`
  - id: `-4634490350`
  - style: `VI, short, actionable`

- name: `Chiến lược mua`
  - id: `-911329255`
  - style: `VI, concise`
  - note: `allowlist + requireMention=true`

- name: `Báo cáo PNL tự động`
  - id: `-5236910839`
  - style: `VI, report-oriented`
  - use: PNL auto-report group

### Discord
- Boss direct chat user id: `556701373681631291`
- style: follow Boss defaults (EN, sharp, no-frills)

---

Last updated: 2026-03-13 by SpongeBot 🫧
