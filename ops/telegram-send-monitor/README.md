# Telegram Scheduled-Send Heartbeat Monitor

Purpose: alert Boss only when a **scheduled outbound Telegram send** actually fails.

## What it watches

It inspects OpenClaw cron jobs and recent cron run history, then flags only jobs that are Telegram send jobs:

- direct verified sender pattern: `/data/workspace/ops/send_telegram_verified.sh ...`
- explicit cron delivery channel `telegram`

A run is treated as a failure when any of these happens:

- cron run status is `error`
- cron run summary starts with `SEND_FAILED`
- a verified-sender job returns an unexpected non-terminal summary instead of `SENT_OK` or `SKIPPED`
- a Telegram delivery job finishes but delivery is not confirmed

## Low-noise behavior

- Dedupes by `jobId:runAtMs`
- Logs new incidents to `incidents.jsonl`
- Persists dedupe/baseline state in `state.json`
- First run is **quiet by default**: it establishes baseline and does not page Boss for older failures already in history
- Later runs only emit alert text for **new** failures

## Files

- `monitor_scheduled_telegram_failures.py` — detector for heartbeat use
- `state.json` — dedupe + baseline state
- `incidents.jsonl` — append-only incident log

## Manual test

Quiet baseline run:

```bash
python3 /data/workspace/ops/telegram-send-monitor/monitor_scheduled_telegram_failures.py --print-alert
```

Force first-run historical alerts too:

```bash
python3 /data/workspace/ops/telegram-send-monitor/monitor_scheduled_telegram_failures.py --print-alert --bootstrap-alerts
```

Structured output:

```bash
python3 /data/workspace/ops/telegram-send-monitor/monitor_scheduled_telegram_failures.py
```

## Heartbeat wiring

Heartbeat should run this command:

```bash
python3 /data/workspace/ops/telegram-send-monitor/monitor_scheduled_telegram_failures.py --print-alert
```

Expected behavior:

- empty stdout => no new failures
- non-empty stdout => send exactly that text to Boss Telegram DM

## Notes

- This is heartbeat-based monitoring, not a separate cron watchdog.
- It relies on real cron metadata from `openclaw cron list --json` and `openclaw cron runs --id ...`.
- Recommended heartbeat cadence: `10m` or `15m`.
