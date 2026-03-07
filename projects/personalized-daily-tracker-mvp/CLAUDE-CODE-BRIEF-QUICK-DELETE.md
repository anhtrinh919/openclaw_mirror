# Claude Code Brief — Quick Delete (Notes, Tasks, Recipes)

Project path: `~/Downloads/06 dev/life-tracker/app`

## Goal
Add quick-delete controls so user can remove notes, tasks, and recipes directly from list views with minimal taps.

Keep current design language and do not break existing behaviors.

---

## Scope

## 1) Notes (`/notes`)
- Add a small delete icon button on each NoteCard (top-right area, near timestamp).
- On tap delete:
  - confirm prompt: `Delete this note?`
  - if confirmed -> delete from localStorage + update list immediately.
- Keep card tap-to-edit behavior unchanged.
- Ensure tapping delete does not trigger card navigation (`preventDefault`/`stopPropagation`).

## 2) Tasks (`/tasks`)
- Add delete icon on each TaskRow (right side).
- On tap delete:
  - confirm prompt: `Delete this task?`
  - if confirmed -> delete from localStorage + update grouped list immediately.
- Keep task status toggle behavior unchanged.

## 3) Recipes (`/recipes`)
- Add delete icon on each RecipeCard (same action row as heart is acceptable).
- On tap delete:
  - confirm prompt: `Delete this recipe?`
  - if confirmed -> delete from localStorage + update list immediately.
- Optional enhancement on detail page (`/recipes/[id]`):
  - add delete action in header area
  - on confirm delete -> navigate back to `/recipes`.

---

## Implementation Requirements
- Reuse existing store functions:
  - `deleteNote(id)`
  - `deleteTask(id)`
  - `deleteRecipe(id)`
- If missing in any path, wire them consistently.
- TypeScript strict, no `any`.
- Use existing icon set (Lucide, e.g. `Trash2`).
- Delete controls must be secondary visual priority (not stronger than primary actions).
- Keep touch targets >= 40px where practical.

---

## Acceptance Criteria
1. Notes/tasks/recipes can be deleted from list views.
2. UI updates immediately after delete.
3. No accidental navigation when pressing delete on cards.
4. Existing flows remain intact:
   - Notes search/filter/edit
   - Tasks filter/status/add
   - Recipes search/filter/favorite/detail/add
5. `npm run lint` passes (warnings only if pre-existing and documented).
6. `npm run build` passes.

---

## Required Delivery Format
1. Changed files list
2. What was implemented per entity (notes/tasks/recipes)
3. Screenshots showing each delete flow
4. Lint/build outputs
5. Known gaps (if any)
