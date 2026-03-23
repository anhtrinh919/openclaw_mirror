# SOP-INSTALL-SKILLS-HOOKS

Use this SOP when Boss asks to install a new skill or a new hook in OpenClaw.

## Goal
Standardize skill and hook installation so OpenClaw discovers them correctly.

## Canonical rules
- For **skills**, install under `/data/workspace/skills/<skill-name>`.
- For **hooks**, use the OpenClaw CLI install path.
- Do **not** assume manual hook folder copy is enough.
- After hook install, restart the gateway.

## Skill install workflow
### 1. Prefer the official installer first
If the registry/CLI supports it, try the skill CLI install first.

### 2. If CLI install fails, identify the real cause
Common causes:
- wrong slug format
- registry limitation
- rate limit
- skill exists only as GitHub source

### 3. Manual skill install fallback
Clone or copy the skill into:
- `/data/workspace/skills/<skill-name>`

Example:
```bash
git clone https://github.com/peterskoett/self-improving-agent.git /data/workspace/skills/self-improving-agent
```

### 4. Verify skill files
At minimum confirm:
- `SKILL.md` exists
- referenced supporting files/directories exist if required

## Hook install workflow
### Canonical method
Install hooks with:
```bash
openclaw hooks install <path-to-hook-dir>
```

Example:
```bash
openclaw hooks install /data/workspace/skills/self-improving-agent/hooks/openclaw
```

### Important lesson
Manual copy into `~/.openclaw/hooks/...` may leave files present but still **not discoverable** by `openclaw hooks enable`.
Use `openclaw hooks install` instead.

### What successful hook install does
- installs into the OpenClaw managed hooks area
- updates OpenClaw config
- registers the installed hook id

## Required restart after hook install
After successful hook install:
```bash
openclaw gateway restart
```

The hook is not considered active until the gateway has restarted.

## Success proof
### Skill success proof
Treat the skill as installed only if:
- the target folder exists in `/data/workspace/skills/`
- `SKILL.md` exists

### Hook success proof
Treat the hook as installed only if:
- `openclaw hooks install ...` succeeds
- output reports installed hooks
- gateway restart is completed

## Known failure mode already seen
### Case: self-improvement hook
This failed approach:
- copy hook files manually into `/home/openclaw/.openclaw/hooks/self-improvement`
- run `openclaw hooks enable self-improvement`

Observed result:
- files existed
- CLI still returned `Hook "self-improvement" not found`

Working fix:
```bash
openclaw hooks install /data/workspace/skills/self-improving-agent/hooks/openclaw
openclaw gateway restart
```

## Notes
- Skill page URLs may use `author/skill` format while CLI expects a plain slug.
- For hooks, installation method matters more than file placement.
- If install commands require approval, preserve the exact command for approval.

Last verified: 2026-03-23
Verified example: `self-improvement` skill + hook
