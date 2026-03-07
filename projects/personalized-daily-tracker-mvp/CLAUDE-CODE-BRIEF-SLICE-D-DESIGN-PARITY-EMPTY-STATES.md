# Claude Code Brief — Slice D (Design Parity + Empty States)

## Context
You are implementing **Phase D** from Pencil design report for Life Tracker.

Repo:
- `~/Downloads/06 dev/life-tracker/app`

Design source of truth:
- `~/Downloads/06 dev/life-tracker/life.pen`
- Focus frames:
  - `1Gace` (Notes Empty)
  - `P32fQ` (Tasks Empty)
  - `y0SDp` (Recipes Empty)
  - plus parity refinements across Home/Notes/Tasks/Recipes screens

Current app already has Slice A/B/C implemented. This slice is **polish + parity + empty states** (no backend).

---

## Scope

## 1) Implement Empty States (3 screens/conditions)

### Notes Empty
On `/notes`, show dedicated empty state when:
- there are no notes at all (base empty), OR
- active filter/search yields zero and user has no data.

Design requirements:
- Keep existing header/search/chips layout.
- Centered empty block with icon container (muted fill), title, description, CTA.
- CTA label: `CREATE NOTE`
- CTA action: route to `/notes/new`
- Accent color: terracotta

### Tasks Empty
On `/tasks`, show dedicated empty state when no tasks exist.
- Icon + title + short description (mentioning task tracking/sync is okay)
- CTA label: `CREATE TASK`
- CTA action: open existing add-task modal/sheet
- Accent color: sage

### Recipes Empty
On `/recipes`, show dedicated empty state when no recipes exist.
- Keep existing header/search/filter row.
- Centered icon + title + description + CTA.
- CTA label: `ADD RECIPE`
- CTA action: route to `/recipes/new`
- Accent color: terracotta

---

## 2) Global Design Parity Fixes (from Phase D report)
Apply these across screens where relevant:

1. **Tab bar pill styling parity**
- Outer nav has 2px border
- Pill visual treatment with rounded tab items (active tab filled)
- Keep active route behavior intact

2. **Filter chips parity**
- Height 32px
- Uppercase labels
- Active filled accent, inactive outlined
- Consistent spacing/letter spacing

3. **Add-tag control style**
- Use dashed-border “Add tag” treatment in note/recipe forms as in design
- Keep existing add/remove tag functionality

4. **Section label consistency**
- Uppercase micro-label style (10–11px, letter spacing)
- Apply to Ingredients/Steps labels and form labels consistently

5. **Recipe detail bullets parity**
- Ingredients use dash-style bullets (em-dash visual); keep readable alignment
- Steps keep numbered `01/02/03` format

6. **Touch target parity**
- Ensure interactive controls stay >=40px (buttons/chips/inputs)

---

## 3) Optional but recommended parity refinements
- Keep `StatusBar` visual consistent but no need to make real clock.
- Keep no tab bar on push screens (`/notes/new`, `/recipes/new`, `/recipes/[id]`) as current design.
- Keep all corners sharp except components explicitly rounded in design system (e.g., checkbox or tab internals).

---

## 4) Non-goals (do NOT do in this slice)
- No backend/API integration
- No Google Tasks sync integration yet
- No real AI implementation (stubs remain)
- No auth/user system
- No image upload pipeline

---

## 5) Acceptance Criteria
1. Empty states exist and render correctly for notes/tasks/recipes when data is empty.
2. Empty state CTAs work (`CREATE NOTE`, `CREATE TASK`, `ADD RECIPE`).
3. Existing non-empty list flows are unaffected.
4. Tab bar/chips/add-tag styles are visibly aligned to Phase D design.
5. Recipe detail ingredients/steps styling matches report intent.
6. Existing features from Slices A/B/C are not regressed.
7. `npm run lint` passes (warnings allowed only if justified and listed).
8. `npm run build` passes.

---

## 6) Required Delivery Format
Return:
1. Changed files list
2. What was implemented per scope section
3. Screenshots:
   - `/notes` empty + non-empty
   - `/tasks` empty + non-empty
   - `/recipes` empty + non-empty
   - one sample form showing dashed add-tag control
4. Lint output + build output
5. Explicit known gaps vs `.pen`

---

## 7) Guardrails
- Keep TypeScript strict (no `any`).
- Reuse existing components where practical; avoid introducing heavy dependencies.
- Preserve current localStorage keys and data model.
- Keep code readable for non-dev review.
