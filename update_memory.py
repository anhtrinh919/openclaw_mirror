#!/usr/bin/env python3
import sys

MEMORY_PATH = "/data/workspace/MEMORY.md"

with open(MEMORY_PATH, "r") as f:
    data = f.read()

# Find the triggers section (be tolerant to date changes)
before = data.find("- **Triggers (Updated")
if before == -1:
    print("Triggers not found")
    sys.exit(1)

# Find the start of New User Onboarding
after = data.find("**New User Onboarding (WhatsApp)")
if after == -1:
    print("New User Onboarding not found")
    sys.exit(1)

new_triggers = '''- **Triggers (Updated 2026-03-01):**
- `@think`: Spawn **openai-codex/gpt-5.3-codex** for reasoning. Also apply the 3-step memory approach: persist to files → pass Context Pack → self-load (read MEMORY/daily/SOP + sessions_history with passed sessionKey).
- `@deepthink`: Spawn **openai-codex/gpt-5.3-codex** for extra-deep reasoning / hard problems. Same 3-step memory approach as `@think`.
- `@think + @do`: @do with sub-agent **openai-codex/gpt-5.3-codex** (autonomous deep tasks).
- `@qc`: Spawn **openai-codex/gpt-5.2** to review work as a quality gate and report issues/fixes.
- `@memory`: Commit in main (no spawn).
- `@do`: Autonomous in main (no spawn unless +@think).
- `@doc`: Docs dive in main.
- `@schedule`: Cron in main (no spawn).
- `@task`: Create task in task.md with PIC, deadline, auto-bucket sorting (personal/staff/critical/other). Create reminder cron for deadline date at 12pm Vietnam time to original chat. Required: description, PIC, deadline. Ask if missing. See SOP.md for details.
See AGENTS.md for table.

'''

result = data[:before] + new_triggers + data[after:]

with open(MEMORY_PATH, "w") as f:
    f.write(result)

print("Updated MEMORY.md triggers successfully")
