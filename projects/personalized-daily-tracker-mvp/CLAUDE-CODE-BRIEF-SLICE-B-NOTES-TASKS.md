# Claude Code Brief — Slice B (3 Screens): Notes + Tasks

## Project + Workspace
- Canon repo path: `~/Downloads/06 dev/life-tracker/app`
- Design sources:
  - `~/Downloads/06 dev/life-tracker/life.pen` (primary)
  - `~/Downloads/06 dev/life-tracker/Tasks List.png`
  - `~/Downloads/06 dev/life-tracker/Tasks List-1.png`
  - `~/Downloads/06 dev/life-tracker/Tasks List-2.png`

## Scope (exactly 3 screens)
1. **Notes List** (`/notes`)
2. **Add Note** (`/notes/new`)
3. **Tasks List** (`/tasks`)

Keep Home screen as-is except shared component reuse needed by these screens.

---

## Hard Requirements

## 1) Visual Fidelity
Implement these 3 screens to match `.pen` layout and style system:
- 402x874 mobile canvas intent
- Existing token palette (`bg-page`, `accent-terracotta`, `accent-sage`, etc.)
- Existing typography style (DM Sans)
- Existing nav/status bar language

Do **not** redesign. Follow `.pen`.

## 2) Notes List (`/notes`)
Include:
- Header title: `Notes`
- Search bar placeholder: `Search notes...`
- Filter chips: `ALL`, `IDEAS`, `REMINDERS`, `ARCHIVED`
- Note cards like design sample (title, relative time, body preview, tags, optional reminder badge)
- Bottom tab bar route-aware state (already implemented pattern)

Behavior:
- Search filters by title/body/tags (client-side)
- Chip filter works client-side
- Tapping note card opens `/notes/new?id=<noteId>` for edit
- Add button in header (if shown in design) routes to `/notes/new`

## 3) Add Note (`/notes/new`)
Fields from design:
- `TITLE (OPTIONAL)` input
- `NOTE` textarea
- `TAGS` area (existing tags + "Add tag")
- `REMINDER` picker/field with placeholder `Set reminder...`
- AI row label: `Suggest tags` (UI + stub action only)

Top bar:
- Back navigation
- `SAVE` button

Behavior:
- Create mode (no id): save new note
- Edit mode (`?id=`): load existing note and update
- Validate: note body required
- On save: persist and navigate back to `/notes`

## 4) Tasks List (`/tasks`)
Include:
- Header title: `Tasks`
- Add button (visual present; add flow can be minimal modal/sheet)
- Filter chips: `ALL`, `TO DO`, `DOING`, `DONE`
- Grouped sections as in design:
  - `DOING` + count
  - `TO DO` + count
- Task rows with:
  - checkbox/status control
  - title
  - due text (`Due today`, `Due tomorrow`, `Due Mar 10`, etc.)
  - optional source badge (`Google Tasks`, `Local`)

Behavior:
- Chip filtering works client-side
- Toggle status updates section placement immediately
- Add task (minimal): title + optional due date + default status `TO DO`

---

## Data + State (MVP local-first)
Use local persistence for now (no backend yet):
- `localStorage` keys:
  - `life.notes.v1`
  - `life.tasks.v1`

Create typed models in `src/lib/types.ts`:

```ts
export type NoteStatus = "active" | "archived";

export interface Note {
  id: string;
  title?: string;
  body: string;
  tags: string[];
  reminderAt?: string; // ISO
  status: NoteStatus;
  createdAt: string; // ISO
  updatedAt: string; // ISO
}

export type TaskStatus = "todo" | "doing" | "done";

export interface Task {
  id: string;
  title: string;
  status: TaskStatus;
  dueAt?: string; // ISO
  source?: "google_tasks" | "local";
  createdAt: string;
  updatedAt: string;
}
```

Seed initial mock data to match design copy if storage empty.

---

## Architecture/Code Expectations
- Keep App Router structure clean:
  - `src/app/notes/page.tsx`
  - `src/app/notes/new/page.tsx`
  - `src/app/tasks/page.tsx`
- Extract reusable UI where obvious:
  - chips, note card, task row, section header
- No heavy state library needed; React hooks + small lib helpers are enough
- No backend/API calls in this slice
- Keep strict TypeScript, no `any`

---

## Non-goals (do not implement now)
- Real AI classification (stub UI only)
- Google Tasks sync integration
- Drag-and-drop task sorting
- Rich text editor
- Auth/multi-user

---

## Acceptance Criteria (must pass)
1. All 3 screens exist and are navigable.
2. Notes CRUD (create + edit) works locally.
3. Notes search + chips filtering works.
4. Tasks list renders grouped sections with working filter chips.
5. Task status toggle moves items between groups correctly.
6. Local persistence survives page refresh.
7. `npm run lint` passes clean.
8. `npm run build` passes clean.
9. Styling is visually aligned with `.pen` for spacing/typography/colors.

---

## Required Delivery Format (from contractor)
Return:
1. Changed file list
2. Short implementation notes + tradeoffs
3. Screenshots of:
   - `/notes`
   - `/notes/new`
   - `/tasks`
4. Test evidence:
   - lint output
   - build output
5. Any known gaps vs `.pen` (explicit)

---

## Implementation Guardrails
- Preserve existing Home route behavior and current tab navigation behavior.
- Do not break previously accepted Slice A quality.
- Keep component names and file organization readable for non-dev review.
