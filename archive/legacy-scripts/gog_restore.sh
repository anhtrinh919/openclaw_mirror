#!/usr/bin/env bash
set -euo pipefail
GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog auth credentials set /data/workspace/gog_client_secret.json --no-input >/dev/null
GOG_KEYRING_PASSWORD=openclaw_secure_2026 /home/linuxbrew/.linuxbrew/bin/gog auth tokens import /data/workspace/gog_auth_backup.json --force --no-input >/dev/null
