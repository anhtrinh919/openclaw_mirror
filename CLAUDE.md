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

- `IDENTITY.md` / `SOUL.md` — Agent persona and communication rules (ultra-concise, sub-20-word, lead with answer)
- `USER.md` — Boss profile (Vietnam UTC+7, English, blunt style)
- `AGENTS.md` — 8 core workspace rules including startup checklist order
- `MEMORY.md` — Long-term memory index
- `contacts.md` — Single source of truth for identity mapping, language, tone
- `task.md` — Master tasklist (Personal/Staff/Critical/Other buckets)
- `SOP.md` — SOP index (token-light; open individual SOPs only when triggered)
- `SKILLS.md` — Skill index (agent-browser, excel-xlsx, scheduler-expert, gog, etc.)
- `TOOLS.md` — Local tool setup notes and secret paths
- `TEAM-ROUTING.md` — Live routing: Telegram → main; Discord → direct named-agent chats
- `multi-agent.md` — Master operating doc (10 sections: roster, workflow, QC policy, token discipline)

## Directory Layout

- `ops/` — Operational scripts: backup/restore, Telegram send/monitor, heartbeat, workspace mirror sync
- `sops/` — One SOP per file, trigger-activated (trade printing, leave requests, morning report, tasks, invoices, etc.)
- `skills/` — Workspace-custom skills (agent-browser, excel-xlsx, scheduler-expert, pptx, vn-meal-coach)
- `memory/` — Dated daily notes (69+ files, Feb–Mar 2026)
- `deliverables/` — Task output folders with standard artifacts (STATUS/TASK_BRIEF/PLAN/WORKLOG/RESULT)
- `shared/` — Reusable templates (Sandy primary writer; main/squid read-only)
- `projects/` — Active project folders
- `archive/` — Legacy docs and scripts
- `telegram-account-export/` — Telegram conversation export tooling (JSONL format)

## Scripts

- `backup.sh` — Creates timestamped tarballs of `.openclaw` state + workspace core files to `/data/backups/`
- `restore.sh` — Restores from latest backups, stops/restarts gateway, runs sanity checks
- `dust_relay.py` — Python SSE client for Dust agent API with reconnection and auto-approve logic
- `ops/send_telegram_verified.sh` — Verified Telegram send with JSON validation (requires `payload.ok=true`)

## Critical Operational Rules

1. **Session startup order:** SOUL → USER → contacts → MEMORY → today's memory note → SOP index → SKILLS → TEAM
2. **Telegram send:** `sessions_send` to groups is unreliable; use `openclaw message send --channel telegram --target <chatId>`
3. **Language:** Vietnamese default; Boss stays English
4. **Team triggers:** `@think`, `@plan`, `@qc`, `@do`, `@doc`, `@task`, `@team`, `@f5`
5. **Hard-routed SOPs:** Trade printing (chat -5194157539 + Excel), Leave requests (chat -4121104521 + "nghỉ")
6. **QC policy:** Block only P0 issues; max 2 change cycles
7. **Token discipline:** Artifact-first, SUMMARY_FOR_HANDOFF ≤200 lines

## Credentials (paths only)

- GOG auth: `gog_auth_backup.json`, `gog_client_secret.json`
- Gemini API key: `.gemini_api_key` (chmod 600)
- GOG binary: `/home/linuxbrew/.linuxbrew/bin/gog`
- Keyring: `/home/openclaw/.config/gogcli/keyring/`
