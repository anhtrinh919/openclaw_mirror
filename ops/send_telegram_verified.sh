#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "usage: $0 <telegram_chat_id> <message>" >&2
  exit 2
fi

target="$1"
shift
message="$*"

resp="$(openclaw message send --channel telegram --target "$target" --message "$message" --json)"

RESP="$resp" python3 - "$target" <<'PY'
import json, os, sys
expected = str(sys.argv[1])
raw = os.environ.get('RESP', '')
start = raw.find('{')
end = raw.rfind('}')
if start == -1 or end == -1 or end < start:
    print(f"NO_JSON_OBJECT_FOUND:\n{raw}", file=sys.stderr)
    raise SystemExit(1)
blob = raw[start:end+1]
try:
    data = json.loads(blob)
except Exception as e:
    print(f"INVALID_JSON: {e}\nBLOB={blob}\nRAW={raw}", file=sys.stderr)
    raise SystemExit(1)
payload = data.get('payload') or {}
chat_id = str(payload.get('chatId', ''))
message_id = str(payload.get('messageId', ''))
ok = payload.get('ok') is True
if not ok:
    print(f"SEND_NOT_OK: {blob}", file=sys.stderr)
    raise SystemExit(1)
if chat_id != expected:
    print(f"CHAT_ID_MISMATCH: expected {expected} got {chat_id}", file=sys.stderr)
    raise SystemExit(1)
if not message_id:
    print(f"MISSING_MESSAGE_ID: {blob}", file=sys.stderr)
    raise SystemExit(1)
print(json.dumps({"ok": True, "chatId": chat_id, "messageId": message_id}, ensure_ascii=False))
PY
