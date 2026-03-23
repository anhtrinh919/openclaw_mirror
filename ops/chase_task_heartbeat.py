#!/usr/bin/env python3
import json
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

API_URL = 'https://life-tracker-production-17cb.up.railway.app/api/mcp'
KEY_PATH = '/data/workspace/.chase_api_key'
VN = ZoneInfo('Asia/Ho_Chi_Minh')


def mcp_call(method, params=None, req_id=1):
    key = open(KEY_PATH, 'r', encoding='utf-8').read().strip()
    body = {'jsonrpc': '2.0', 'id': req_id, 'method': method}
    if params is not None:
        body['params'] = params
    req = urllib.request.Request(API_URL, data=json.dumps(body).encode(), method='POST')
    req.add_header('Authorization', f'Bearer {key}')
    req.add_header('X-API-Key', key)
    req.add_header('Accept', 'application/json, text/event-stream')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, timeout=25) as r:
        payload = json.loads(r.read().decode())
    if 'error' in payload:
        raise RuntimeError(payload['error'])
    return payload.get('result', {})


def parse_tool_text(result):
    content = result.get('content') or []
    if not content:
        return None
    text = content[0].get('text')
    return json.loads(text) if text else None


def fmt_task(t):
    title = t.get('title', 'Untitled')
    due = t.get('due_date') or 'no due'
    return f'{title} ({due})'


def main():
    try:
        mcp_call('initialize', {
            'protocolVersion': '2025-03-26',
            'capabilities': {},
            'clientInfo': {'name': 'SpongeBot Chase Heartbeat', 'version': '1.0'}
        }, req_id=1)
        dashboard = parse_tool_text(mcp_call('tools/call', {'name': 'get_dashboard', 'arguments': {}}, req_id=2)) or {}
        chase_view = parse_tool_text(mcp_call('tools/call', {'name': 'get_chase_view', 'arguments': {}}, req_id=3)) or []
    except Exception as e:
        print(f'⚠️ Chase MCP alert: connection failed — {type(e).__name__}: {e}')
        return 0

    now_vn = datetime.now(timezone.utc).astimezone(VN)
    tasks_by_status = dashboard.get('tasks_by_status', {})
    backlog = int(tasks_by_status.get('backlog', 0) or 0)
    in_progress = int(tasks_by_status.get('in-progress', 0) or 0)
    critical = int((dashboard.get('tasks_by_priority') or {}).get('critical', 0) or 0)
    this_week = dashboard.get('this_week_tasks') or []
    past_due = dashboard.get('past_due_tasks') or []

    chase_contacts = []
    for row in chase_view:
        contact = row.get('contact') or {}
        name = contact.get('name', 'Unknown')
        overdue = row.get('past_due') or []
        week = row.get('this_week') or []
        other = row.get('other') or []
        total = len(overdue) + len(week) + len(other)
        if total:
            chase_contacts.append((name, len(overdue), len(week), len(other), overdue, week, other))

    parts = [f'🫧 Chase check {now_vn.strftime("%H:%M VN")}: {backlog} backlog, {in_progress} in progress, {len(past_due)} overdue, {len(this_week)} due this week']
    if critical:
        parts.append(f'{critical} critical')

    highlights = []
    if past_due:
        highlights.append('Overdue: ' + '; '.join(fmt_task(t) for t in past_due[:3]))
    elif this_week:
        highlights.append('Due soon: ' + '; '.join(fmt_task(t) for t in this_week[:3]))

    if chase_contacts:
        contact_lines = []
        for name, od, wk, ot, overdue, week, other in chase_contacts[:3]:
            if od:
                sample = fmt_task(overdue[0])
            elif wk:
                sample = fmt_task(week[0])
            else:
                sample = fmt_task(other[0])
            contact_lines.append(f'{name}: {od} overdue, {wk} this week, {ot} other — next {sample}')
        highlights.append('To chase: ' + ' | '.join(contact_lines))

    if not highlights:
        highlights.append('No urgent pending or chase items right now.')

    print('. '.join(parts) + '. ' + ' '.join(highlights))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
