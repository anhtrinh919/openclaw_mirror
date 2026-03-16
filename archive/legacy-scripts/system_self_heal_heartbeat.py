#!/usr/bin/env python3
import json, pathlib, subprocess, time, hashlib

SEND = '/data/workspace/ops/send_telegram_verified.sh'
RESTORE = '/data/workspace/ops/gog_restore.sh'
BOSS = '171900099'
STATE = pathlib.Path('/data/workspace/watchers/system_self_heal_heartbeat_state.json')
TASK_SYNC_JOB = '671497b7-ebbb-4c5a-be46-a32b22ec550e'
WATCHDOG_NAMES = {
    'telegram-delivery-watchdog-workhours',
    'google-auth-health-heartbeat-twice-daily',
    'task-system-sync-watchdog-workhours',
}
GOG_PROBES = [
    ['bash','-lc',"GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog gmail search 'is:unread' --account tuananhtrinh919@gmail.com --max 1 --json --no-input >/dev/null"],
    ['bash','-lc',"GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog calendar events --today --account tuananhtrinh919@gmail.com --json --no-input >/dev/null"],
    ['bash','-lc',"GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog sheets get 1-O_B27mSDqfEZemD27bPNmWtfnV3cW51LeClBmSwB6c 'Sheet1!A1:Z3' --account tuananhtrinh919@gmail.com --json --no-input >/dev/null"],
    ['bash','-lc',"GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog tasks list '@default' --account tuananhtrinh919@gmail.com --json --no-input --all --show-hidden --show-completed >/dev/null"],
]


def run(cmd, check=True):
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            pass
    return {}


def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


actions = []
issues = []

# 1) Auto-heal Gog auth
restore = run([RESTORE], check=False)
if restore.returncode != 0:
    issues.append('gog restore failed')
else:
    probe_fail = []
    for p in GOG_PROBES:
        r = run(p, check=False)
        if r.returncode != 0:
            probe_fail.append((p[2] if len(p) > 2 else p[-1])[:80])
    if probe_fail:
        issues.append('gog probes failing after restore')
    else:
        actions.append('gog auth restore+probes OK')

# 2) Inspect cron health
cron = json.loads(run(['openclaw','cron','list','--json']).stdout)['jobs']
by_name = {j['name']: j for j in cron}
by_id = {j['id']: j for j in cron}

# 3) Ensure watchdog jobs exist and are enabled
for name in WATCHDOG_NAMES:
    j = by_name.get(name)
    if not j:
        issues.append(f'missing watchdog job: {name}')
    elif not j.get('enabled'):
        issues.append(f'watchdog disabled: {name}')

# 4) Ensure Telegram-sending crons use verified sender pattern
for j in cron:
    payload = j.get('payload') or {}
    msg = (payload.get('message') or '') + '\n' + (payload.get('text') or '')
    if '/data/workspace/ops/send_telegram_verified.sh' in msg:
        if 'SENT_OK' not in msg or 'Do not run exec more than once' not in msg:
            issues.append(f'telegram cron missing terminal guard: {j["name"]}')
        if (j.get('delivery') or {}).get('mode') != 'none':
            issues.append(f'telegram cron delivery mode not none: {j["name"]}')

# 5) Auto-heal task sync if stale or last run failed
sync = by_id.get(TASK_SYNC_JOB)
if not sync:
    issues.append('task sync cron missing')
else:
    state = sync.get('state') or {}
    now_ms = int(time.time() * 1000)
    last_run = state.get('lastRunAtMs') or 0
    stale = (now_ms - last_run) > 30 * 3600 * 1000
    failed = state.get('lastRunStatus') not in (None, 'ok')
    if stale or failed:
        rerun = run(['openclaw','cron','run',TASK_SYNC_JOB,'--expect-final','--timeout','120000'], check=False)
        if rerun.returncode == 0:
            actions.append('re-ran task sync cron')
        else:
            issues.append('task sync rerun failed')

# 6) Alert only if unresolved issues remain or noteworthy healing happened
state = load_state()
fingerprint = hashlib.sha256(('\n'.join(issues) + '\n--\n' + '\n'.join(actions)).encode()).hexdigest() if (issues or actions) else ''
last = state.get('lastFingerprint', '')
if issues:
    msg = '🚨 Self-heal heartbeat found issues:\n'
    for x in issues[:12]:
        msg += f'• {x}\n'
    if actions:
        msg += '\n🛠️ Auto-heal actions performed:\n'
        for x in actions[:8]:
            msg += f'• {x}\n'
    if fingerprint != last:
        subprocess.check_output([SEND, BOSS, msg], text=True)
        state['lastFingerprint'] = fingerprint
        save_state(state)
    print('ALERT_SENT')
elif actions:
    # stay quiet unless it changed materially; still record for dedupe
    state['lastFingerprint'] = fingerprint
    save_state(state)
    print('HEALED_OK')
else:
    state['lastFingerprint'] = ''
    save_state(state)
    print('OK')
