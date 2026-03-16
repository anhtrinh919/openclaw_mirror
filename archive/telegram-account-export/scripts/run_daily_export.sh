#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d .venv ]]; then
  echo "missing virtualenv: $ROOT_DIR/.venv" >&2
  exit 1
fi

if [[ ! -f .env ]]; then
  echo "missing env file: $ROOT_DIR/.env" >&2
  exit 1
fi

mkdir -p logs output state

LOCK_DIR="$ROOT_DIR/state/export.lock"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "export already running; lock exists at $LOCK_DIR" >&2
  exit 1
fi
trap 'rmdir "$LOCK_DIR"' EXIT

SINCE="${SINCE:-}"
UNTIL="${UNTIL:-}"

if [[ -z "$SINCE" || -z "$UNTIL" ]]; then
  YDAY="$(date -u -d 'yesterday' +%F)"
  TODAY="$(date -u +%F)"
  SINCE="${SINCE:-${YDAY}T00:00:00Z}"
  UNTIL="${UNTIL:-${TODAY}T00:00:00Z}"
fi

source .venv/bin/activate
export PYTHONUNBUFFERED=1

python scripts/export_telegram_jsonl.py --since "$SINCE" --until "$UNTIL" "$@"
