# Claude Code Brief — Slice C (3 Screens): Recipes

## Project + Workspace
- Canon repo path: `~/Downloads/06 dev/life-tracker/app`
- Design source of truth: `~/Downloads/06 dev/life-tracker/life.pen`
- Target recipe frames in `.pen`:
  1. `Recipes List`
  2. `Recipe Detail`
  3. `Add Recipe`

## Scope (exactly 3 recipe screens)
1. **Recipes List** (`/recipes`)
2. **Recipe Detail** (`/recipes/[id]`)
3. **Add Recipe** (`/recipes/new`)

Keep Home + Notes + Tasks behavior intact.

---

## Hard Requirements

## 1) Visual fidelity to `.pen`
Implement these screens to match the `.pen` structure and style:
- mobile-first 402x874 intent
- current token system (colors/spacing/typography)
- same component language as existing app (status bar, tab bar)
- do not redesign

## 2) Recipes List (`/recipes`)
Include:
- Header: `Recipes` + add button (40x40 style)
- Search bar placeholder: `Search recipes...`
- Filter chips: `ALL`, `DINNER`, `QUICK`, `VEGGIE`
- Favorite toggle chip/button (heart icon) as shown in `.pen` row
- Recipe cards with:
  - title
  - source domain (e.g., `seriouseats.com`)
  - tags
- Bottom tab bar with route-aware active state

Behavior:
- Search by title/source/tags (client-side)
- Chip filtering by tag (client-side)
- Favorite toggle filtering (show favorites only)
- Card click routes to `/recipes/[id]`
- Add button routes to `/recipes/new`

## 3) Recipe Detail (`/recipes/[id]`)
Include:
- Top area with `BACK`
- Hero image block (use placeholder image if no image URL)
- Title + source link text
- Tag row
- Ingredients section (`INGREDIENTS`) with bullet list
- Steps section (`STEPS`) with numbered lines (`01`, `02`, ...)
- AI actions row/buttons:
  - `Summarize recipe`
  - `Suggest tags`

Behavior:
- Load recipe by route id
- If missing id -> show clean not-found state with back link
- AI actions are UI stubs only (no real AI call yet)

## 4) Add Recipe (`/recipes/new`)
Top bar:
- Back
- `SAVE`

Fields (from `.pen` labels):
- `TITLE`
- `SOURCE URL` (placeholder: `Paste URL to auto-fill...`)
- `INGREDIENTS` (multiline, one per line)
- `STEPS` (multiline)
- `TAGS` (+ add tag)
- AI row:
  - `Extract from URL`
  - `Suggest tags`

Behavior:
- Validate title required
- Save creates new recipe and returns to `/recipes`
- `Extract from URL` is stub UI for now (e.g., toast/alert + TODO note)
- `Suggest tags` is stub UI for now

---

## Data + State (local-first)
Extend local storage with recipes:
- key: `life.recipes.v1`

Add model(s) in `src/lib/types.ts`:

```ts
export interface Recipe {
  id: string;
  title: string;
  sourceUrl?: string;
  sourceDomain?: string;
  ingredients: string[];
  steps: string[];
  tags: string[];
  favorite: boolean;
  imageUrl?: string;
  createdAt: string;
  updatedAt: string;
}
```

In `src/lib/store.ts` add:
- `getRecipes()`
- `getRecipe(id)`
- `saveRecipe(recipe)`
- `deleteRecipe(id)` (optional but helpful)
- `toggleRecipeFavorite(id)`

Seed initial recipes matching `.pen` copy (at least):
- `Spicy Miso Ramen` (seriouseats.com, tags dinner/japanese)
- `Lemon Herb Chicken` (bonappetit.com, tags dinner/quick)

Use realistic ingredient/step arrays to match detail screen sample.

---

## Routing + Files
Expected files (or equivalent):
- `src/app/recipes/page.tsx`
- `src/app/recipes/new/page.tsx`
- `src/app/recipes/[id]/page.tsx`

Optional reusable components (recommended):
- `RecipeCard`
- `TagChips` (if not reusing FilterChips)
- `SectionBlock` for ingredients/steps

---

## Non-goals (do NOT build now)
- real URL parser/extractor
- real AI summarization/tagging
- backend/API sync
- image upload pipeline

---

## Acceptance Criteria (must pass)
1. All 3 recipe screens are implemented and navigable.
2. Recipes list supports search + chip filtering + favorite filter.
3. Card opens detail route with correct data.
4. Add Recipe saves to localStorage and shows in list immediately.
5. Recipe detail renders title/source/tags/ingredients/steps/AI actions.
6. Existing Home/Notes/Tasks flows are not regressed.
7. `npm run lint` passes.
8. `npm run build` passes (routes include `/recipes/new` and `/recipes/[id]`).

---

## Required Delivery Format
Return:
1. Changed file list
2. Notes on implementation decisions/tradeoffs
3. Screenshots of:
   - `/recipes`
   - `/recipes/new`
   - `/recipes/<seed-id>` detail
4. Test evidence:
   - lint output
   - build output
5. Explicit known gaps vs `.pen`

---

## Guardrails
- Keep style consistent with accepted Slices A/B.
- Do not remove or break route-aware tab behavior.
- Keep TypeScript strict (no `any`).
- Preserve local-first architecture and clear code readability for non-dev review.
