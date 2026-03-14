# Heartbeat checklist

- Run: `python3 /data/workspace/ops/telegram-send-monitor/monitor_scheduled_telegram_failures.py --print-alert`
- If stdout is empty, reply `HEARTBEAT_OK`
- If stdout has text, send exactly that text and nothing else
- Do not alert for old incidents already baselined in `state.json`
- Keep this heartbeat focused on scheduled Telegram send failures only
