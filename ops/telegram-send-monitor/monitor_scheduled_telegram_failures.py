#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path('/data/workspace/ops/telegram-send-monitor')
STATE_PATH = ROOT / 'state.json'
INCIDENTS_PATH = ROOT / 'incidents.jsonl'
VN_TZ = ZoneInfo('Asia/Ho_Chi_Minh')
SEND_SCRIPT = '/data/workspace/ops/send_telegram_verified.sh'
DEFAULT_LOOKBACK_HOURS = 72
DEFAULT_RUN_LIMIT = 8


@dataclass
class Incident:
    key: str
    job_id: str
    job_name: str
    run_at_ms: int
    status: str
    reason: str
    target: str | None
    summary: str | None
    error: str | None
    session_key: str | None
    delivery_status: str | None

    def to_json(self) -> dict[str, Any]:
        return {
            'key': self.key,
            'jobId': self.job_id,
            'jobName': self.job_name,
            'runAtMs': self.run_at_ms,
            'runAtUtc': iso_utc(self.run_at_ms),
            'runAtVn': iso_vn(self.run_at_ms),
            'status': self.status,
            'reason': self.reason,
            'target': self.target,
            'summary': self.summary,
            'error': self.error,
            'sessionKey': self.session_key,
            'deliveryStatus': self.delivery_status,
            'detectedAtUtc': datetime.now(timezone.utc).isoformat(),
        }


def iso_utc(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


def iso_vn(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=VN_TZ).isoformat()


def run_json(cmd: list[str]) -> Any:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr.strip() or proc.stdout.strip()}")
    text = proc.stdout.strip()
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or end < start:
        raise RuntimeError(f"no JSON object found from: {' '.join(cmd)}")
    return json.loads(text[start:end + 1])


def load_state() -> dict[str, Any]:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    return {
        'version': 1,
        'bootstrappedAtMs': None,
        'lastCheckedAtMs': None,
        'seenRunKeys': [],
        'recentIncidentKeys': [],
    }


def save_state(state: dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    state['seenRunKeys'] = sorted(set(state.get('seenRunKeys', [])))[-2000:]
    state['recentIncidentKeys'] = sorted(set(state.get('recentIncidentKeys', [])))[-500:]
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')


def append_incidents(incidents: list[Incident]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    with INCIDENTS_PATH.open('a', encoding='utf-8') as f:
        for incident in incidents:
            f.write(json.dumps(incident.to_json(), ensure_ascii=False) + '\n')


def parse_target_from_message(message: str) -> str | None:
    m = re.search(r"/data/workspace/ops/send_telegram_verified\.sh\s+([^\s'\"]+)", message)
    if m:
        return m.group(1)
    return None


def is_direct_verified_sender_job(job: dict[str, Any]) -> bool:
    payload = job.get('payload') or {}
    message = (payload.get('message') or '') + '\n' + (payload.get('text') or '')
    if SEND_SCRIPT not in message:
        return False
    scheduler_markers = [
        'Create a one-shot cron job',
        'You schedule a random check-in message',
        'message is exactly:',
    ]
    return not any(marker in message for marker in scheduler_markers)


def is_telegram_delivery_job(job: dict[str, Any]) -> bool:
    delivery = job.get('delivery') or {}
    if (delivery.get('channel') or '').lower() == 'telegram':
        return True
    if is_direct_verified_sender_job(job):
        return True
    return False


def incident_from_run(job: dict[str, Any], entry: dict[str, Any]) -> Incident | None:
    payload = job.get('payload') or {}
    message = (payload.get('message') or '') + '\n' + (payload.get('text') or '')
    direct_verified = is_direct_verified_sender_job(job)
    delivery_telegram = ((job.get('delivery') or {}).get('channel') or '').lower() == 'telegram'

    status = entry.get('status') or 'unknown'
    summary = entry.get('summary')
    error = entry.get('error')
    delivery_status = entry.get('deliveryStatus')
    run_at_ms = int(entry.get('runAtMs') or 0)
    if run_at_ms <= 0:
        return None

    reason = None
    if status == 'error':
        reason = error or 'job failed'
    elif isinstance(summary, str) and summary.startswith('SEND_FAILED'):
        reason = summary
    elif direct_verified:
        normalized = (summary or '').strip()
        if normalized not in {'SENT_OK', 'SKIPPED'}:
            reason = f"unexpected success summary: {normalized or '<empty>'}"
    elif delivery_telegram:
        delivered = entry.get('delivered')
        if delivered is False or delivery_status in {'not-delivered', 'failed'}:
            reason = f"telegram delivery not confirmed ({delivery_status or 'unknown'})"

    if not reason:
        return None

    key = f"{job.get('id')}:{run_at_ms}"
    return Incident(
        key=key,
        job_id=str(job.get('id') or ''),
        job_name=str(job.get('name') or ''),
        run_at_ms=run_at_ms,
        status=status,
        reason=reason,
        target=parse_target_from_message(message) or ((job.get('delivery') or {}).get('to')),
        summary=summary,
        error=error,
        session_key=entry.get('sessionKey'),
        delivery_status=delivery_status,
    )


def collect_new_incidents(lookback_hours: int, run_limit: int, bootstrap_alerts: bool) -> tuple[list[Incident], dict[str, Any], bool]:
    now_ms = int(time.time() * 1000)
    cutoff_ms = now_ms - lookback_hours * 3600 * 1000
    state = load_state()
    seen_run_keys = set(state.get('seenRunKeys', []))
    recent_incident_keys = set(state.get('recentIncidentKeys', []))
    bootstrapped = bool(state.get('bootstrappedAtMs'))

    jobs_obj = run_json(['openclaw', 'cron', 'list', '--json'])
    jobs = jobs_obj.get('jobs', [])

    all_seen_this_pass: set[str] = set()
    new_incidents: list[Incident] = []

    for job in jobs:
        if not is_telegram_delivery_job(job):
            continue
        runs_obj = run_json(['openclaw', 'cron', 'runs', '--id', str(job['id']), '--limit', str(run_limit)])
        for entry in runs_obj.get('entries', []):
            run_at_ms = int(entry.get('runAtMs') or 0)
            if run_at_ms <= 0 or run_at_ms < cutoff_ms:
                continue
            run_key = f"{job.get('id')}:{run_at_ms}"
            all_seen_this_pass.add(run_key)
            incident = incident_from_run(job, entry)
            if not incident:
                continue
            if run_key in recent_incident_keys:
                continue
            if (not bootstrapped) and (not bootstrap_alerts):
                continue
            if run_key in seen_run_keys:
                continue
            new_incidents.append(incident)

    if not bootstrapped:
        state['bootstrappedAtMs'] = now_ms

    seen_run_keys.update(all_seen_this_pass)
    recent_incident_keys.update(i.key for i in new_incidents)
    state['lastCheckedAtMs'] = now_ms
    state['seenRunKeys'] = sorted(seen_run_keys)
    state['recentIncidentKeys'] = sorted(recent_incident_keys)
    return sorted(new_incidents, key=lambda x: x.run_at_ms), state, bootstrapped


def render_alert(incidents: list[Incident]) -> str:
    if not incidents:
        return ''
    lines = ['🚨 Scheduled Telegram send failure detected:']
    for incident in incidents[:10]:
        target = f" → {incident.target}" if incident.target else ''
        lines.append(
            f"• {incident.job_name}{target} at {iso_vn(incident.run_at_ms)} — {incident.reason}"
        )
    if len(incidents) > 10:
        lines.append(f"• ...and {len(incidents) - 10} more")
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Detect failed scheduled Telegram sends and emit a deduped alert string for heartbeats.')
    parser.add_argument('--print-alert', action='store_true', help='print alert text only when there are new incidents')
    parser.add_argument('--bootstrap-alerts', action='store_true', help='on first run, alert for already-seen incidents inside lookback instead of silently baselining')
    parser.add_argument('--lookback-hours', type=int, default=DEFAULT_LOOKBACK_HOURS)
    parser.add_argument('--run-limit', type=int, default=DEFAULT_RUN_LIMIT)
    args = parser.parse_args()

    try:
        incidents, state, _bootstrapped = collect_new_incidents(
            lookback_hours=args.lookback_hours,
            run_limit=args.run_limit,
            bootstrap_alerts=args.bootstrap_alerts,
        )
        if incidents:
            append_incidents(incidents)
        save_state(state)
        if args.print_alert:
            text = render_alert(incidents)
            if text:
                print(text)
        else:
            print(json.dumps({
                'ok': True,
                'newIncidentCount': len(incidents),
                'incidentsPath': str(INCIDENTS_PATH),
                'statePath': str(STATE_PATH),
            }, ensure_ascii=False))
        return 0
    except Exception as e:
        print(f"MONITOR_ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
