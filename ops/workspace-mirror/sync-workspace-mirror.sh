#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${SOURCE_DIR:-/data/workspace}"
MIRROR_DIR="${MIRROR_DIR:-/data/workspace-mirror}"
BRANCH="main"
EXCLUDES_FILE="${EXCLUDES_FILE:-/data/workspace/ops/workspace-mirror/mirror-excludes.txt}"
REPO_URL="${MIRROR_REPO:-}"
PUSH="${PUSH:-1}"
TS="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

mkdir -p "$MIRROR_DIR"

if [[ ! -d "$MIRROR_DIR/.git" ]]; then
  git -C "$MIRROR_DIR" init -b "$BRANCH"
fi

git -C "$MIRROR_DIR" config user.name "${MIRROR_GIT_NAME:-SpongeBot Mirror}"
git -C "$MIRROR_DIR" config user.email "${MIRROR_GIT_EMAIL:-spongebot-mirror@local}"

# Sync snapshot with deletion for true mirror behavior.
# Uses Python so it works even when rsync is unavailable.
python3 - "$SOURCE_DIR" "$MIRROR_DIR" "$EXCLUDES_FILE" <<'PY'
import fnmatch
import os
import shutil
import sys
from pathlib import Path

source = Path(sys.argv[1]).resolve()
mirror = Path(sys.argv[2]).resolve()
ex_file = Path(sys.argv[3]).resolve()

patterns = []
for line in ex_file.read_text(encoding='utf-8').splitlines():
    s = line.strip()
    if not s or s.startswith('#'):
        continue
    patterns.append(s)

# Always protect mirror git internals
patterns.append('.git/')

def is_excluded(rel: str, is_dir: bool=False) -> bool:
    rel = rel.replace('\\', '/')
    if rel.startswith('./'):
        rel = rel[2:]
    for p in patterns:
        pp = p.strip()
        dir_only = pp.endswith('/')
        pp = pp[:-1] if dir_only else pp
        if dir_only and not is_dir:
            continue
        if fnmatch.fnmatch(rel, pp) or fnmatch.fnmatch('/' + rel, pp):
            return True
        # match directory prefixes like tmp/
        if dir_only and (rel == pp or rel.startswith(pp + '/')):
            return True
    return False

# Build allowed file + dir sets from source
allowed_files = set()
allowed_dirs = {''}

for root, dirs, files in os.walk(source):
    root_p = Path(root)
    rel_root = '' if root_p == source else str(root_p.relative_to(source)).replace('\\','/')

    # filter dirs in-place
    keep_dirs = []
    for d in dirs:
        rel_d = f"{rel_root}/{d}".strip('/')
        if is_excluded(rel_d, is_dir=True):
            continue
        keep_dirs.append(d)
        allowed_dirs.add(rel_d)
    dirs[:] = keep_dirs

    for f in files:
        rel_f = f"{rel_root}/{f}".strip('/')
        if is_excluded(rel_f, is_dir=False):
            continue
        allowed_files.add(rel_f)
        allowed_dirs.add(str(Path(rel_f).parent).replace('\\','/').strip('.'))

# Copy/update files
for rel_f in sorted(allowed_files):
    src_f = source / rel_f
    dst_f = mirror / rel_f
    dst_f.parent.mkdir(parents=True, exist_ok=True)
    if (not dst_f.exists() or src_f.stat().st_size != dst_f.stat().st_size or int(src_f.stat().st_mtime) != int(dst_f.stat().st_mtime)):
        shutil.copy2(src_f, dst_f)

# Delete files/dirs in mirror not in allowed set (except .git)
for root, dirs, files in os.walk(mirror, topdown=False):
    root_p = Path(root)
    rel_root = '' if root_p == mirror else str(root_p.relative_to(mirror)).replace('\\','/')

    for f in files:
        rel_f = f"{rel_root}/{f}".strip('/')
        if rel_f.startswith('.git/'):
            continue
        if rel_f not in allowed_files:
            (mirror / rel_f).unlink(missing_ok=True)

    for d in dirs:
        rel_d = f"{rel_root}/{d}".strip('/')
        if rel_d == '.git' or rel_d.startswith('.git/'):
            continue
        dir_p = mirror / rel_d
        if rel_d not in allowed_dirs:
            try:
                dir_p.rmdir()
            except OSError:
                pass
PY

# Keep a copy of mirror policy inside the mirror repo.
mkdir -p "$MIRROR_DIR/.mirror"
cp "$EXCLUDES_FILE" "$MIRROR_DIR/.mirror/mirror-excludes.txt"

git -C "$MIRROR_DIR" add -A

if git -C "$MIRROR_DIR" diff --cached --quiet; then
  echo "No changes to commit."
else
  git -C "$MIRROR_DIR" commit -m "mirror: workspace snapshot $TS"
  echo "Committed mirror snapshot at $TS"
fi

if [[ "$PUSH" == "1" ]]; then
  if [[ -z "$REPO_URL" ]]; then
    echo "PUSH=1 but MIRROR_REPO is empty. Skipping push."
    exit 0
  fi

  # Use ephemeral tokenized URL so token is not stored in git config.
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    CLEAN_URL="${REPO_URL#https://}"
    PUSH_URL="https://x-access-token:${GITHUB_TOKEN}@${CLEAN_URL}"
  else
    PUSH_URL="$REPO_URL"
  fi

  git -C "$MIRROR_DIR" push "$PUSH_URL" "HEAD:${BRANCH}" --force
  echo "Pushed mirror to ${REPO_URL} (${BRANCH})"
fi
