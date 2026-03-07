#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="/data/backups"

latest_state() {
  ls -1t "$BACKUP_DIR"/openclaw-state-*.tgz 2>/dev/null | head -n 1
}

latest_workspace() {
  ls -1t "$BACKUP_DIR"/workspace-core-*.tgz 2>/dev/null | head -n 1
}

STATE_TGZ="${1:-$(latest_state)}"
WORKSPACE_TGZ="${2:-$(latest_workspace)}"

if [[ -z "${STATE_TGZ:-}" || ! -f "$STATE_TGZ" ]]; then
  echo "❌ No openclaw-state backup found in $BACKUP_DIR"
  exit 1
fi
if [[ -z "${WORKSPACE_TGZ:-}" || ! -f "$WORKSPACE_TGZ" ]]; then
  echo "❌ No workspace-core backup found in $BACKUP_DIR"
  exit 1
fi

echo "Using:"
echo "- STATE: $STATE_TGZ"
echo "- WORKSPACE: $WORKSPACE_TGZ"

echo "Stopping gateway..."
openclaw gateway stop || true

echo "Restoring /data/.openclaw ..."
tar -C /data -xzf "$STATE_TGZ"

echo "Restoring /data/workspace core ..."
tar -C /data/workspace -xzf "$WORKSPACE_TGZ"

echo "Fixing ownership..."
chown -R openclaw:openclaw /data/.openclaw /data/workspace || true

echo "Starting gateway..."
openclaw gateway start

echo "✅ Restore complete"
openclaw gateway status || true
