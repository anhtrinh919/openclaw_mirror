# Telegram Account Export (Option A)

Daily Telegram export scaffold using a **personal Telegram account** via **Telethon**.

This avoids OpenClaw native Telegram changes and is practical on this Linux host.

## Recommended architecture

- **Client library:** Python + Telethon
- **Auth model:** one-time interactive login on this machine to create a local `.session` file
- **Config model:** environment variables loaded from `.env`
- **Export model:** one JSONL file per chat per day window
- **Schedule model:** cron calls a bash wrapper, wrapper calls the Python exporter
- **Safety model:** lock file, UTC date windows, no secret values committed, output folders kept local

## Data flow

1. Manual setup creates Python venv and installs dependencies.
2. Manual auth run creates `state/telethon.session`.
3. Cron runs `scripts/run_daily_export.sh` once per day.
4. Wrapper computes yesterday's UTC date range unless explicitly provided.
5. `scripts/export_telegram_jsonl.py` logs in using the saved session.
6. Exporter lists dialogs, filters them, fetches messages for the date window, and writes JSONL.
7. Logs go to `logs/`; exported data goes to `output/YYYY-MM-DD/`.

## File layout

```text
telegram-account-export/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── config/
│   └── export_targets.example.txt
├── docs/
│   └── SETUP.md
├── logs/
├── output/
├── scripts/
│   ├── export_telegram_jsonl.py
│   └── run_daily_export.sh
└── state/
```

Create `state/` locally before first auth; it is intentionally ignored by git.

## Quick start

See `docs/SETUP.md`.
