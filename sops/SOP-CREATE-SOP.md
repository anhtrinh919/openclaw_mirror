# SOP-CREATE-SOP

Use this SOP whenever Boss asks to create a new SOP.

## Goal
Create SOPs that are short, reusable, trigger-driven, and easy to execute under pressure.

## Naming rule
Use this filename format:
- `/data/workspace/sops/SOP-<TOPIC>.md`
- Topic should be uppercase with hyphens.
- Examples:
  - `SOP-INSTALL-SKILLS-HOOKS.md`
  - `SOP-CREATE-SOP.md`

## When to create a new SOP
Create a new SOP when at least one is true:
1. the task is recurring
2. the task has a clear trigger
3. the task has failure-prone steps
4. the task depends on exact commands, exact paths, or exact success criteria
5. Boss wants the process standardized

## When not to create a new SOP
Do **not** create a new SOP when:
- it is a one-off task
- it is just a note, not a procedure
- the process belongs inside an existing SOP

In that case, update the existing SOP instead.

## Required structure
Each SOP should usually contain:
1. **Title**
2. **Use this when...** or trigger line
3. **Goal** or **Purpose**
4. **Rules** / canonical constraints
5. **Exact steps**
6. **Success proof**
7. **Common failure modes**
8. **Notes** / verification date if useful

## Writing rules
- Lead with the trigger.
- Prefer exact commands over vague guidance.
- Prefer exact paths over generic placeholders when known.
- State the canonical system if one exists.
- Include hard rules like **do not use X** when needed.
- Include success criteria so future runs can verify completion.
- Keep it short; remove theory.
- If the SOP changes routing behavior, update `/data/workspace/SOP.md`.

## Creation workflow
1. Check `/data/workspace/SOP.md` to confirm no existing SOP already covers it.
2. If a related SOP exists, decide whether to extend it or create a new one.
3. Draft the new SOP in `/data/workspace/sops/`.
4. Add the trigger + file path to `/data/workspace/SOP.md`.
5. If the SOP depends on a proven command or path, include the verified command exactly.
6. If the SOP contains operational claims, prefer claims already verified in this workspace.

## Minimal template
```md
# SOP-<TOPIC>

Use this SOP when <trigger>.

## Goal
<what this SOP standardizes>

## Rules
- <canonical rule>
- <hard constraint>

## Exact steps
1. <step>
2. <step>
3. <step>

## Success proof
- <observable success condition>

## Failure modes
- <common failure>
- <how to recover>
```

## Index update rule
After creating a new SOP, add it to `/data/workspace/SOP.md` with:
- SOP name
- plain-English trigger
- exact file path

## Quality bar
A good SOP should let future SpongeBot do the task correctly with minimal guesswork.
