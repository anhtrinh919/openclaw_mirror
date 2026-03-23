# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

This is a **mirror** of the OpenClaw multi-agent AI assistant workspace running on Railway. The live system orchestrates 4 specialized agents (main/sandy/glados/squid) serving Tuan Anh ("Boss") via Telegram and Discord. This repo is a document-first backup — not runnable locally.

## Agent Team

| Agent | Handle | Role |
|-------|--------|------|
| **main** (SpongeBot) | Chief of Staff | Orchestrator, Boss-facing, task briefs, final delivery |
| **sandy** | Builder | Code, tests, sysadmin, artifacts |
| **glados** | Data/Reporting | Reports, Excel, PowerPoint, analysis |
| **squid** | Architect/QC | Plans, rubrics, quality control verdicts |

Standard flow: Boss → main → (optional squid plan) → sandy/glados execute → squid QC → main delivers.

## Key Files

- `SOUL.md` — Agent persona and response rules (sub-40-word, lead with answer, root cause always)
- `USER.md` — Boss profile (UTC+7, English, blunt; when to redirect to Claude Code)
- `AGENTS.md` — Startup sequence, hard routes, trigger map, delegation + skill routing
- `MEMORY.md` — Long-term facts: key setups, critical lessons, Boss profile
- `contacts.md` — Per-person identity, language, tone (SOUL.md is style authority)
- `SOP.md` — Token-light SOP index; open individual SOPs only when triggered
- `SKILLS.md` — Skill index (agent-browser, excel-xlsx, scheduler-expert, gog, etc.)
- `TOOLS.md` — Local tool setup notes and secret paths
- `TEAM-ROUTING.md` — Live routing: Telegram → main; Discord → direct named-agent chats
- `multi-agent.md` — Master operating doc (roster, workflow, QC policy, token discipline)

## Directory Layout

- `ops/` — Operational scripts: backup/restore, Telegram send/monitor, heartbeat, workspace mirror sync
- `sops/` — One SOP per file, trigger-activated (trade printing, leave requests, tasks, invoices, etc.)
- `skills/` — Workspace-custom skills (agent-browser, excel-xlsx, scheduler-expert, pptx, vn-meal-coach)
- `memory/` — Dated daily notes
- `deliverables/` — Task output folders with standard artifacts (STATUS/TASK_BRIEF/PLAN/WORKLOG/RESULT)
- `shared/` — Reusable templates (Sandy primary writer; main/squid read-only)
- `projects/` — Active project folders
- `archive/` — Legacy docs and scripts

## Critical Operational Rules

1. **Session startup:** SOUL.md, USER.md, IDENTITY.md, MEMORY.md are auto-injected. Read manually: `contacts.md`, then today's + yesterday's memory note. Read on-demand: `SOP.md`, `SKILLS.md`, `TEAM.md`.
2. **Telegram send:** `sessions_send` to groups is unreliable; use `openclaw message send --channel telegram --target <chatId>`. Require `payload.ok=true` proof.
3. **Language:** Vietnamese default; Boss stays English.
4. **Task management:** Chase is the canonical PM tool — use `sops/SOP-TASKS.md` for any create/track/remind intent.
5. **Hard-routed SOPs:** Trade printing (chat `-5194157539` + Excel), Leave requests (chat `-4121104521` + "nghỉ"), SOP creation (Boss asks to write/standardize a SOP).
6. **Triggers:** `@think`, `@plan`, `@qc`, `@do`, `@doc`, `@task`, `@team`, `@f5`
7. **QC policy:** Block only P0 issues; max 2 change cycles.
8. **Token discipline:** Artifact-first, SUMMARY_FOR_HANDOFF ≤200 lines.
9. **NEVER self-edit config or restart gateway.**

## Credentials (paths only)

- GOG auth: `gog_auth_backup.json`, `gog_client_secret.json`
- Gemini API key: `.gemini_api_key` (chmod 600)
- GOG binary: `/home/linuxbrew/.linuxbrew/bin/gog`
- Keyring: `/home/openclaw/.config/gogcli/keyring/`
