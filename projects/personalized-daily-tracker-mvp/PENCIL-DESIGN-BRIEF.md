# Pencil.dev Design Brief — Personalized Daily Tracker (MVP)

## 0) Objective
Design a sleek, mobile-first personal web app with a very clear entry point and minimal friction for daily use.

MVP modules:
1. Quick Capture Notes
2. Tasks
3. Recipes

---

## 1) Product Personality
- Calm, modern, premium utility
- Feels personal, not corporate
- Fast, intentional, uncluttered

Tone words: **clean / confident / warm / focused**

---

## 2) Primary UX Principle
"Capture in seconds, organize later."

Everything should optimize for:
- quick entry
- low cognitive load
- easy return navigation

---

## 3) Information Architecture (MVP)

Top level:
- Home (launcher)
- Notes
- Tasks
- Recipes
- Settings (minimal)

Home = primary daily entry.

---

## 4) Critical Requirement — First Screen
The first screen must have **3 huge buttons/cards** above the fold:
1. **Quick Capture Notes**
2. **Tasks**
3. **Recipes**

### Layout requirements
- Mobile first (390x844 reference)
- Each button/card should be highly tappable (min 56px height, ideally larger)
- Full-width stacked cards on mobile
- Distinct icon + label + one-line helper text
- Strong visual hierarchy; no competing elements above cards

### Microcopy suggestion
- Quick Capture Notes — “Save ideas, reminders, and thoughts fast”
- Tasks — “See and update today’s priorities”
- Recipes — “Save and find your favorite recipes”

---

## 5) Screen List to Design

## 5.1 Home / Launcher
- Greeting + date (lightweight)
- 3 giant cards/buttons (notes/tasks/recipes)
- Optional tiny quick-add FAB anchored bottom-right

## 5.2 Notes
- Notes list: search bar, filter chips (All, Reminder, Archived)
- Note card: title/body preview, tags, reminder badge
- Add/Edit note sheet/modal
- Empty state with action CTA

## 5.3 Tasks
- Task list grouped by status (To do, Doing, Done)
- Quick add task input
- Task row with checkbox, due date, source badge (e.g., synced)
- Filters: Today / Upcoming / Done

## 5.4 Recipes
- Recipe list: search + tag chips + favorites toggle
- Recipe card: title, source badge/url, tags, favorite icon
- Add/Edit recipe form
- Recipe detail screen (ingredients + steps)

## 5.5 Shared Components
- Bottom navigation (Home/Notes/Tasks/Recipes)
- Universal search pattern
- Empty states and skeleton loaders
- Toast/inline confirmations

---

## 6) Interaction Details
- Tap card -> instant transition (<250ms perceived)
- Quick add actions should open lightweight bottom sheet on mobile
- Use autosave drafts for long text entries
- Confirm destructive actions with simple modal
- Keep back-navigation obvious and thumb-friendly

---

## 7) Visual Design Direction

## 7.1 Style
- Minimal surfaces
- Rounded corners (12–16px)
- Soft shadow/elevation
- Strong typography scale
- Plenty of whitespace

## 7.2 Color
- Neutral base + one accent color
- Ensure excellent contrast for outdoor/mobile reading
- Support dark mode in design system tokens (even if not built in v1)

## 7.3 Typography
- Highly legible sans-serif
- Prioritize readability over decorative style
- Scale should make card labels immediately scan-able

---

## 8) Responsive Rules
- Mobile-first as primary target
- Tablet/desktop can switch from stacked cards to 2-column layouts where suitable
- Maintain the same IA and interaction language across breakpoints

---

## 9) Accessibility
- Touch targets >=44x44 px minimum (prefer >56 for primary actions)
- Contrast ratio WCAG AA
- Clear focus states
- Avoid icon-only critical actions

---

## 10) AI UX Surfaces (MVP-ready placeholders)
Include visual placeholders for future AI actions:
- “Suggest tags” button in notes/recipes
- “Summarize” action for long note/recipe text
- “Organize suggestions” panel (non-blocking)

Important: AI should appear as assistive, not intrusive.

---

## 11) Deliverables Needed from Pencil.dev
1. High-fidelity mobile screens (primary)
2. Desktop adaptations (key screens)
3. Clickable prototype for core flows
4. Component library spec (buttons/cards/forms/tags/chips/nav)
5. Spacing/type/color tokens
6. Export-ready assets/icons

---

## 12) Priority Flow to Prototype First
1. Open app -> Home launcher
2. Tap Quick Capture Notes -> create note with reminder -> save
3. Back to Home -> Tasks -> mark task done
4. Back to Home -> Recipes -> add recipe from URL + tags

This is the baseline journey the MVP must nail.
