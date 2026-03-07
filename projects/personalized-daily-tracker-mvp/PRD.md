# PRD — Personalized Daily Tracker (MVP)

## 1) Product Summary
A sleek, persistent personal web app that centralizes daily life inputs currently scattered across apps/sites:
- Quick capture notes/ideas/reminders
- Tasks visibility + lightweight task actions
- Recipe saving and retrieval

This MVP is designed to be mobile-first and fast to use in under 10 seconds for common actions.

---

## 2) Goals
1. Reduce context switching across tools.
2. Make daily capture frictionless.
3. Provide one home screen with large, clear navigation.
4. Establish architecture for future health modules (gym + calorie tracking).

### Non-goals (MVP)
- Full nutrition engine
- Full workout programming logic
- Multi-user collaboration
- Advanced AI auto-agents running continuously in background

---

## 3) Target User
Primary: Boss (single user), using phone + desktop.

---

## 4) Core MVP Scope

## 4.1 First Screen (Hard requirement)
Landing screen has **3 huge buttons/cards** (full-width on mobile):
1. **Quick Capture Notes**
2. **Tasks**
3. **Recipes**

Design intent:
- one-tap entry
- high contrast
- large touch targets (>=56px height)
- no clutter above the fold

## 4.2 Quick Capture Notes
- Add note in one field (title optional, body required)
- Optional tags
- Optional reminder datetime
- Inbox list + search
- Mark as archived

## 4.3 Tasks (MVP integration mode)
- Show tasks from existing task system (Google Tasks / tracker flow)
- Basic actions: create task, mark done, set due date, filter by status
- Preserve existing SOP workflow (do not break current automation)

## 4.4 Recipes
- Save recipe with: title, source URL, ingredients (free text), steps (free text), tags
- Quick add from pasted URL (manual extraction first; AI extraction optional)
- List + search + tag filter + favorite

---

## 5) AI-Powered Organization (Feasibility)

## 5.1 What AI will do in MVP (practical)
- Suggest tags for notes/tasks/recipes
- Suggest category/folder placement
- Generate concise summaries for long notes/recipes
- Deduplicate similar items (suggest, not auto-delete)

## 5.2 Claude Max vs API reality
- **Claude Max subscription itself is not a stable backend API for app integration.**
- For production app behavior, use:
  - Option A: Anthropic API key
  - Option B: OpenRouter API (accepted fallback)

Recommendation:
- Build AI provider abstraction from day 1 (`AIProvider` interface)
- Default to OpenRouter initially for flexibility
- Keep provider switchable without UI changes

## 5.3 AI Safety/Control
- AI actions are suggestion-first (user approves)
- Keep full edit history for AI-changed metadata
- Never auto-delete user content

---

## 6) UX Requirements
- Mobile-first
- App shell + PWA installable
- Fast startup (<2.5s on average mobile connection)
- Offline-first draft capture (sync when online)
- Consistent command bar / quick add CTA available globally

---

## 7) Data Model (MVP-level)

### Note
- id, title, body, tags[], reminderAt, status(active|archived), createdAt, updatedAt

### Task
- id, title, description, status(todo|doing|done), dueAt, source(google_tasks|local), createdAt, updatedAt

### Recipe
- id, title, sourceUrl, ingredientsText, stepsText, tags[], favorite(bool), createdAt, updatedAt

### AI Metadata (shared)
- aiTags[], aiSummary, aiCategory, aiConfidence, lastClassifiedAt

---

## 8) Technical Architecture (high-level)
- Frontend: modern React/Next.js app (PWA)
- Backend: API routes + background jobs
- DB: Postgres (or Supabase Postgres)
- Auth: single-user secure auth (email magic link or OAuth)
- Storage: object storage for future media (image calories)
- Integrations:
  - Google Tasks sync adapter
  - Optional OpenRouter/Anthropic adapter

---

## 9) Success Metrics (MVP)
- >=80% daily captures done inside app (vs scattered tools)
- Time-to-capture <=10 seconds median
- >=1 daily session on 70%+ days after launch month
- At least 50 recipes + 100 notes migrated/created in first 30 days

---

## 10) Milestones

### Milestone 1 (Week 1)
- App shell, auth, landing screen with huge buttons
- Note CRUD + reminder field

### Milestone 2 (Week 2)
- Task list view + create/complete + basic sync adapter

### Milestone 3 (Week 3)
- Recipe CRUD + tags/favorites + search
- AI tag/summarize suggestions (provider abstraction)

### Milestone 4 (Week 4, stabilization)
- polish, bug fixes, perf, deployment, analytics events

---

## 11) Future Extensions (post-MVP)
1. Gym planner + progression charts
2. Image-based calorie tracking (photo upload + AI estimate + manual correction)
3. Daily briefing screen (aggregated from notes/tasks/recipes/health)

---

## 12) Risks & Mitigations
- Risk: scope creep -> Mitigation: freeze MVP to 3 modules only.
- Risk: AI misclassification -> Mitigation: suggestion-only, one-tap undo.
- Risk: task sync edge cases -> Mitigation: source-of-truth rules + conflict logs.
- Risk: mobile UX complexity -> Mitigation: large-button minimal IA first.
