#!/usr/bin/env python3
import json, pathlib, re, subprocess, time, hashlib

SEND = '/data/workspace/ops/send_telegram_verified.sh'
RESTORE = '/data/workspace/ops/gog_restore.sh'
BOSS = '171900099'
STATE = pathlib.Path('/data/workspace/watchers/task_system_sync_watchdog_state.json')
TASK_MD = pathlib.Path('/data/workspace/task.md')
SYS = json.loads(pathlib.Path('/data/workspace/task_system.json').read_text())

subprocess.check_call([RESTORE])

acct = SYS['account']
tasklist = SYS['google_tasks']['tasklistId']
sheet = SYS['task_tracker_sheet']['spreadsheetId']

def out(cmd):
    return subprocess.check_output(cmd, text=True)

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

# Google Tasks
raw_tasks = json.loads(out(['bash','-lc', f"GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog tasks list '{tasklist}' --account {acct} --json --no-input --all --show-hidden --show-completed"]))
gmap = {}
for t in raw_tasks.get('tasks', []):
    m = re.search(r'TASK-\d{{8}}-\d{{2}}', t.get('title',''))
    if m:
        gmap[m.group(0)] = 'done ✅' if t.get('status') == 'completed' else 'pending'

# Sheet
raw_sheet = json.loads(out(['bash','-lc', f"GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog sheets get {sheet} 'Tasks!A2:K1000' --account {acct} --json --no-input"]))
values = raw_sheet.get('values') or []
smap = {}
for row in values:
    if not row or not row[0].strip():
        continue
    tid = row[0].strip()
    status = row[4].strip() if len(row) > 4 else ''
    smap[tid] = status

# task.md
text = TASK_MD.read_text().splitlines()
mdmap = {}
reminders = {}
for line in text:
    m = re.search(r'(TASK-\d{8}-\d{2}).*?Reminder:\s*([^|]+).*?Status:\s*([^|]+)', line)
    if m:
        tid, rem, status = m.group(1), m.group(2).strip(), m.group(3).strip()
        mdmap[tid] = status
        reminders[tid] = rem

# active cron ids
cron_jobs = json.loads(out(['openclaw','cron','list','--json']))['jobs']
active_ids = {j['id'] for j in cron_jobs if j.get('enabled')}

issues = []
for tid, gstatus in sorted(gmap.items()):
    sstatus = smap.get(tid)
    mstatus = mdmap.get(tid)
    if sstatus and sstatus != gstatus:
        issues.append(f"{tid}: sheet={sstatus} vs google={gstatus}")
    if mstatus and mstatus != gstatus:
        issues.append(f"{tid}: task.md={mstatus} vs google={gstatus}")
    rem = reminders.get(tid, '')
    if gstatus == 'done ✅':
        ids = re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', rem)
        active = [x for x in ids if x in active_ids]
        if active:
            issues.append(f"{tid}: done in Google Tasks but active reminder cron(s) still enabled: {', '.join(active)}")

fingerprint = hashlib.sha256('\n'.join(issues).encode()).hexdigest() if issues else ''
state = load_state()
if issues and state.get('lastFingerprint') != fingerprint:
    msg = '🚨 Task system sync watchdog found drift:\n' + '\n'.join(f'• {x}' for x in issues[:15])
    if len(issues) > 15:
        msg += f"\n• ...and {len(issues)-15} more"
    subprocess.check_output([SEND, BOSS, msg], text=True)
    state['lastFingerprint'] = fingerprint
    state['lastAlertAt'] = int(time.time())
    save_state(state)
    print('ALERT_SENT')
elif issues:
    print('ALREADY_ALERTED')
else:
    if state.get('lastFingerprint'):
        state['lastFingerprint'] = ''
        save_state(state)
    print('OK')
