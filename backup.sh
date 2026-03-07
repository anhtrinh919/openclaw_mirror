#!/usr/bin/env bash
set -euo pipefail

TS="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="/data/backups"
mkdir -p "$BACKUP_DIR"

STATE_TGZ="$BACKUP_DIR/openclaw-state-$TS.tgz"
WORKSPACE_TGZ="$BACKUP_DIR/workspace-core-$TS.tgz"

tar -C /data -czf "$STATE_TGZ" .openclaw

tar -C /data/workspace -czf "$WORKSPACE_TGZ" \
  AGENTS.md SOUL.md USER.md MEMORY.md contacts.md SOP.md SKILLS.md \
  memory sops task.md task_system.json leave_requests.json news_watch_state.json 2>/dev/null || true

echo "✅ Backup complete"
echo "- $STATE_TGZ"
echo "- $WORKSPACE_TGZ"
