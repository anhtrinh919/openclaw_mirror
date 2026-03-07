#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <short-name>"
  exit 1
fi

SHORT="$1"
DATE_UTC="$(date -u +%F)"
TASK_DIR="/data/workspace/deliverables/${DATE_UTC}_${SHORT}"
TEMPLATE_DIR="/data/workspace/deliverables/_template"

mkdir -p "$TASK_DIR"
cp "$TEMPLATE_DIR"/STATUS.md "$TASK_DIR"/
cp "$TEMPLATE_DIR"/TASK_BRIEF.md "$TASK_DIR"/
cp "$TEMPLATE_DIR"/PLAN.md "$TASK_DIR"/
cp "$TEMPLATE_DIR"/WORKLOG.md "$TASK_DIR"/
cp "$TEMPLATE_DIR"/RESULT.md "$TASK_DIR"/
cp "$TEMPLATE_DIR"/OPEN_QUESTIONS.md "$TASK_DIR"/

echo "Created: $TASK_DIR"
