# Setup: Telegram Account Export via Telethon

This setup produces a real local session that cron can reuse without re-entering login details every day.

## Preconditions

- Linux host with Python 3.10+
- A personal Telegram account you are allowed to use for export
- Access to `https://my.telegram.org` to create API credentials
- Enough local disk for JSONL output

## Manual auth checkpoints

These are the exact human-in-the-loop steps you should expect.

1. **Create Telegram API credentials manually**
   - Open `https://my.telegram.org`
   - Log in with the phone number of the Telegram account
   - Go to **API development tools**
   - Create an application if you do not already have one
   - Copy the resulting **api_id** and **api_hash** into `.env`

2. **First interactive login on this Linux host**
   - Run the exporter manually once
   - Telethon will prompt for the account phone number
   - Telethon will prompt for the login code received in Telegram/SMS
   - If the account has 2FA enabled, Telethon will prompt for the password
   - On success, Telethon writes a reusable session file under `state/`

3. **Checkpoint after successful auth**
   - Confirm `state/telethon.session` exists
   - Confirm a test export writes JSONL into `output/YYYY-MM-DD/`
   - Only after this should cron be enabled

## Install

```bash
cd /data/workspace/telegram-account-export
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p state logs output
cp .env.example .env
```

Edit `.env` and fill in real values.

If you want to limit exports to selected chats:

```bash
cp config/export_targets.example.txt config/export_targets.txt
```

Then edit `config/export_targets.txt`.

## First auth + smoke test

Run a small export for one day window:

```bash
cd /data/workspace/telegram-account-export
source .venv/bin/activate
python scripts/export_telegram_jsonl.py \
  --since 2026-03-12T00:00:00Z \
  --until 2026-03-13T00:00:00Z \
  --verbose
```

Expected behavior on first run:

- prompts for phone number
- prompts for login code
- prompts for 2FA password if enabled
- creates `state/telethon.session`
- writes JSONL files under `output/2026-03-12/`

## Cron example

This runs daily at 01:15 UTC and exports the previous UTC day.

```cron
15 1 * * * cd /data/workspace/telegram-account-export && /bin/bash scripts/run_daily_export.sh >> logs/cron.log 2>&1
```

## Notes and boundaries

- Telegram exports only what the authenticated account can access.
- Some large histories may take a long time; start with a limited target list.
- Keep the `state/` directory private. It contains the reusable login session.
- Do not commit `.env`, `state/`, `logs/`, or `output/`.
