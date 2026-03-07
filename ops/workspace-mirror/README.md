# Workspace Mirror (Option 1)

This mirrors `/data/workspace` into a clean git repo (`/data/workspace-mirror`) and pushes to a **private GitHub repo**.

## What this gives you
- Visual browsing in GitHub UI (files, search, history, diffs)
- On-demand snapshots (run whenever you want)
- No Railway volume dismount/remount

## Safety defaults
- Excludes secrets + runtime internals (see `mirror-excludes.txt`)
- Uses token only in push command (not persisted in git remote config)

## 1) Create private GitHub repo
Create an empty private repo, e.g.:
- `tuananhtrinh919/openclaw-workspace-mirror`

## 2) Add Railway env vars (OpenClaw service)
Set these variables:
- `MIRROR_REPO=https://github.com/<owner>/<repo>.git`
- `GITHUB_TOKEN=<github_pat_with_repo_write>`
- Optional:
  - `MIRROR_BRANCH=main`
  - `MIRROR_GIT_NAME=SpongeBot Mirror`
  - `MIRROR_GIT_EMAIL=spongebot-mirror@local`

## 3) First dry run (no push)
```bash
cd /data/workspace
chmod +x /data/workspace/ops/workspace-mirror/sync-workspace-mirror.sh
PUSH=0 /data/workspace/ops/workspace-mirror/sync-workspace-mirror.sh
```

## 4) Push snapshot
```bash
cd /data/workspace
/data/workspace/ops/workspace-mirror/sync-workspace-mirror.sh
```

## 5) On-demand usage
Whenever you want fresh files visible in GitHub, run:
```bash
/data/workspace/ops/workspace-mirror/sync-workspace-mirror.sh
```

## 6) Optional: periodic auto-sync (every 30 min)
Use Railway Cron or OpenClaw cron to run:
```bash
/data/workspace/ops/workspace-mirror/sync-workspace-mirror.sh
```

## Notes
- Mirror mode uses `--delete`: deleted local files are deleted in mirror repo next sync.
- If you want less aggressive behavior, ask to switch to append-only mode.
