#!/usr/bin/env python3
import json, subprocess, time, os, pathlib

BOSS_CHAT = '171900099'
SEND = '/data/workspace/ops/send_telegram_verified.sh'
STATE = pathlib.Path('/data/workspace/watchers/telegram_delivery_watchdog_state.json')
LOOKBACK_SEC = 2 * 3600 + 15 * 60


def run(cmd):
    return subprocess.check_output(cmd, text=True)


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            pass
    return {"alerted": []}


def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    # keep only recent keys
    state['alerted'] = state.get('alerted', [])[-200:]
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


now_ms = int(time.time() * 1000)
cutoff_ms = now_ms - LOOKBACK_SEC * 1000
jobs = json.loads(run(['openclaw', 'cron', 'list', '--json']))['jobs']
state = load_state()
alerted = set(state.get('alerted', []))
new_keys = []
issues = []

for job in jobs:
    payload = job.get('payload') or {}
    msg = (payload.get('message') or '') + '\n' + (payload.get('text') or '')
    is_telegram_sender = ('/data/workspace/ops/send_telegram_verified.sh' in msg) or (job.get('delivery') or {}).get('channel') == 'telegram'
    if not is_telegram_sender:
        continue
    runs = json.loads(run(['openclaw', 'cron', 'runs', '--id', job['id'], '--limit', '5']))['entries']
    for e in runs:
        run_at = e.get('runAtMs') or 0
        if run_at < cutoff_ms:
            continue
        key = f"{job['id']}:{run_at}"
        if key in alerted:
            continue
        summary = e.get('summary', '') or ''
        status = e.get('status')
        bad = False
        reason = None
        if status == 'error':
            bad = True
            reason = e.get('error', 'cron error')
        elif summary.startswith('SEND_FAILED'):
            bad = True
            reason = summary
        elif '/data/workspace/ops/send_telegram_verified.sh' in msg and status == 'ok' and summary not in ('SENT_OK', 'SKIPPED'):
            bad = True
            reason = f"unexpected summary: {summary[:120] or '<empty>'}"
        elif (job.get('delivery') or {}).get('channel') == 'telegram' and status == 'ok' and job['name'] == 'morning-report' and e.get('delivered') is not True:
            bad = True
            reason = f"delivery not confirmed ({e.get('deliveryStatus')})"
        if bad:
            issues.append({
                'key': key,
                'name': job['name'],
                'runAtMs': run_at,
                'reason': reason,
            })
            new_keys.append(key)

if issues:
    lines = ['🚨 Telegram delivery watchdog detected issues in the last ~2h:']
    for x in issues[:10]:
        lines.append(f"• {x['name']} — {x['reason']}")
    if len(issues) > 10:
        lines.append(f"• ...and {len(issues)-10} more")
    subprocess.check_output([SEND, BOSS_CHAT, '\n'.join(lines)], text=True)
    alerted.update(new_keys)
    state['alerted'] = sorted(alerted)
    save_state(state)
    print('ALERT_SENT')
else:
    print('OK')
