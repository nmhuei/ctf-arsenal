# USTH Academic Digital Learning V4 Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the existing USTH V3 visual system with the approved V4 shell, dense student-app surfaces, aligned auxiliary pages, and verified desktop/mobile rendered output while preserving all current behavior and real-data constraints.

**Architecture:** Treat V4 as a design-system convergence layer rather than a route rewrite. First update Figma foundations/components and directly rebuild the existing V3 frames, then mirror the same tokens/shell/components in the current Next.js/legacy frontend with minimal markup changes and targeted CSS cleanup. Preserve backend/API contracts and existing JavaScript behavior; the redesign only changes structure when necessary to support the approved layout.

**Tech Stack:** Figma Design + Plugin API, Next.js 16.2.10, React/TypeScript, existing legacy JavaScript/CSS, Playwright E2E/visual capture, Node-based unit tests.

## Global Constraints
- Edit existing Figma V3 frames directly; do not create a separate V4 page.
- Do not invent unsupported backend data or metrics.
- Preserve Concept Card 880×520 core geometry.
- Dashboard and Forum primary workflows should fit approximately within 1440×900.
- Desktop sidebar target width is approximately 232px.
- Profile is top-right; Settings is pinned bottom-left in the desktop sidebar.
- Every navigation item has a visible consistent SVG icon.
- Mobile navigation icons must remain visible and horizontal overflow must be absent.
- Do not change dependencies or lockfiles merely to work around package-manager environment issues.
- Before editing Next.js code, read the relevant Next.js 16.2.10 docs shipped under `node_modules/next/dist/docs` as required by `frontend/AGENTS.md`.

---

### Task 1: Record and verify the approved V4 baseline

**Files:**
- Create: `docs/superpowers/specs/2026-08-11-usth-figma-v4-redesign-design.md`
- Create: `docs/superpowers/plans/2026-08-11-usth-figma-v4-redesign-plan.md`

**Interfaces:**
- Consumes: approved V4 design direction and existing V3 frame inventory.
- Produces: immutable design/implementation baseline used by all later tasks.

- [ ] **Step 1: Add the approved design spec**

Copy the exact design specification into `docs/superpowers/specs/2026-08-11-usth-figma-v4-redesign-design.md`.

- [ ] **Step 2: Add this implementation plan**

Copy this file into `docs/superpowers/plans/2026-08-11-usth-figma-v4-redesign-plan.md`.

- [ ] **Step 3: Scan both documents for unresolved placeholders**

Run:
```bash
grep -RniE 'T[B]D|T[O]DO|implement[[:space:]]+later|fill[[:space:]]+in[[:space:]]+details' docs/superpowers/specs/2026-08-11-usth-figma-v4-redesign-design.md docs/superpowers/plans/2026-08-11-usth-figma-v4-redesign-plan.md
```
Expected: no output.

- [ ] **Step 4: Commit the baseline**

```bash
git add docs/superpowers/specs/2026-08-11-usth-figma-v4-redesign-design.md docs/superpowers/plans/2026-08-11-usth-figma-v4-redesign-plan.md
git commit -m "docs: specify USTH Figma V4 redesign"
```

### Task 2: Audit current Figma foundations and reusable assets

**Files:**
- No code files modified.
- Maintain Figma state ledger at `/tmp/design-system-state-usth-v4.json`.

**Interfaces:**
- Consumes: Figma file `9TFyTC2ZIEQWvXFO5aCXsJ`, existing V3 pages and frames.
- Produces: resolved token/component/style map and node IDs for direct V3 edits.

- [ ] **Step 1: Inspect Figma pages, existing local variables, fonts, components, and styles**

Use read-only Figma inspection on pages `01 — Foundations`, `02 — Components`, and `05 — Student App`; record exact node IDs and existing conventions in the state ledger.

- [ ] **Step 2: Inspect existing student-app component instances and library links**

Resolve reusable navigation, button, input, card, avatar, badge, and icon patterns from existing screens before using library search.

- [ ] **Step 3: Inspect design libraries and search unresolved assets**

Run `get_libraries` followed by scoped `search_design_system` only for assets not resolved from existing screens.

- [ ] **Step 4: Record the gap analysis**

The ledger must explicitly identify: existing V3 tokens/components that can be retained, V4 tokens/components that need updates, and conflicts between existing code/Figma conventions and the approved V4 spec.

### Task 3: Update Figma foundations and components for V4

**Files:**
- Figma pages: `01 — Foundations`, `02 — Components`.

**Interfaces:**
- Consumes: Task 2 token/component map.
- Produces: V4 token styles/variables and reusable component primitives for screen rebuilds.

- [ ] **Step 1: Update color/spacing/radius/effect foundations**

Apply the approved V4 palette and density scale while preserving useful existing local variables/styles. Use scoped variables and semantic aliases where the file structure supports them.

- [ ] **Step 2: Normalize typography styles**

Resolve the actual product font first, then update page/section/card/body/metadata/navigation type styles to the approved hierarchy.

- [ ] **Step 3: Build or normalize shell primitives**

Create/update reusable SidebarNavItem, ProfileChip, IconButton, SearchField, SegmentedFilter, FilterChip, SortControl, Avatar, Badge, ProgressBar, EmptyState and button patterns.

- [ ] **Step 4: Build or normalize product cards/composers**

Create/update CourseCard, MetricCard, DiscussionComposer, DiscussionItem and SettingsRow patterns with auto-layout and V4 token bindings.

- [ ] **Step 5: Validate components**

For each changed component family, inspect metadata and screenshots; verify no clipped text, invalid variant matrix, inconsistent icon sizing, or missing token binding.

### Task 4: Rebuild existing Student App V3 frames directly as V4

**Files:**
- Figma page: `05 — Student App`.
- Existing frames: Dashboard `2:2`, Courses `2:50`, Roadmap `2:101`, Skills `2:131`, Forum `2:177`, Profile `2:207`, Settings `2:240`, Questionnaire `10:2`, Concept Card `10:28`, Chatbot `10:44`, Interface `10:60`.

**Interfaces:**
- Consumes: V4 foundations/components from Task 3.
- Produces: direct V4 replacements of existing V3 frames without creating a parallel V4 page.

- [ ] **Step 1: Rebuild the shared shell in Dashboard and validate**

Apply 232px deep-navy sidebar, clear USTH branding, visible icons, bottom-pinned Settings, compact header and top-right Profile chip. Capture the Dashboard frame and verify shell geometry before reusing it.

- [ ] **Step 2: Rebuild Dashboard content**

Implement dense Continue Learning + high-emphasis weekly/streak row, compact in-progress courses, and data-backed summary cards. Verify primary content is useful within 1440×900.

- [ ] **Step 3: Rebuild Courses**

Merge search/enrollment/sort into one toolbar, compact secondary filters, and reduce course-card dead space.

- [ ] **Step 4: Rebuild Forum**

Create unified top controls, large white discussion workspace, compact personal composer, dense discussion list, and only data-safe contextual content.

- [ ] **Step 5: Rebuild Roadmap, Skills, Profile and Settings**

Apply the same shell/density hierarchy while preserving current information and data semantics.

- [ ] **Step 6: Rebuild Questionnaire, Concept Card, Chatbot and Interface**

Preserve Concept Card 880×520; keep questionnaire and chatbot compact; align auxiliary surfaces to V4.

- [ ] **Step 7: Capture and inspect all changed Student App frames**

Use Figma screenshots at sufficient resolution and correct any visible clipping, alignment, inconsistent padding, missing icons or excessive whitespace before leaving the page.

### Task 5: Rebuild remaining Figma pages directly

**Files:**
- Figma pages: `03 — Landing`, `04 — Auth`, `06 — Course`, `07 — Lesson`, `08 — Admin`, `09 — Mobile`.

**Interfaces:**
- Consumes: shared V4 foundations/components and approved shell rules.
- Produces: visually consistent V4 coverage across all existing product surfaces.

- [ ] **Step 1: Update Landing**

Retain more breathing room than the app shell but apply USTH identity, V4 colors, existing imagery, and stronger academic hierarchy.

- [ ] **Step 2: Update Login/Register**

Apply strong USTH branding and compact professional forms without unsupported decorative behavior.

- [ ] **Step 3: Update Course Detail and Lesson**

Preserve learning content dominance, module/lesson structure, progress, and current actions.

- [ ] **Step 4: Update Admin**

Use dense table-friendly V4 styling and restrained status colors.

- [ ] **Step 5: Update Mobile frames**

Use top mobile header, visible icon+label bottom nav, 16px page padding, compact controls, and zero horizontal overflow.

- [ ] **Step 6: Final Figma QA**

Capture every updated frame and correct inconsistent shell widths, page headers, radii, icon sizes, clipped text, missing assets, dead space, and viewport-density problems.

### Task 6: Audit frontend source before implementation

**Files:**
- Read: `frontend/AGENTS.md`
- Read: relevant `frontend/node_modules/next/dist/docs/**`
- Read: `frontend/src/app/(base)/dashboard/page.tsx`
- Read: `frontend/src/components/StudentNavigation.tsx`
- Read: `frontend/src/components/Topbar.tsx`
- Read: `frontend/src/components/UsthBrand.tsx`
- Read: `frontend/public/static/css/usth/tokens.css`
- Read: `frontend/public/static/css/usth/shell.css`
- Read: dashboard/forum/course/auth/admin CSS and legacy JS used by the affected routes.

**Interfaces:**
- Consumes: final approved Figma V4 frames.
- Produces: exact source-to-design mapping and the smallest safe set of code edits.

- [ ] **Step 1: Read repository guidance and relevant Next.js 16.2.10 docs**

Document the applicable routing/client-component constraints before editing React code.

- [ ] **Step 2: Call Figma `get_design_context` for the implemented V4 reference frames**

At minimum collect design context for Dashboard, Courses and Forum, plus any frame whose markup structure must change.

- [ ] **Step 3: Audit existing data sources before adding visual fields**

Trace dashboard streak/summary, course filters/progress, forum metadata and profile/settings data through current frontend/backend calls. Mark unsupported metrics as hidden/empty-state only.

### Task 7: Implement V4 tokens and shared shell in the frontend

**Files:**
- Modify: `frontend/public/static/css/usth/tokens.css`
- Modify: `frontend/public/static/css/usth/shell.css`
- Modify: `frontend/src/components/StudentNavigation.tsx`
- Modify: `frontend/src/components/Topbar.tsx`
- Modify: `frontend/src/components/UsthBrand.tsx` only if required to surface the existing USTH asset correctly.
- Test: existing Playwright student navigation/shell coverage under `frontend/e2e/`.

**Interfaces:**
- Consumes: final V4 Figma shell/tokens.
- Produces: reusable CSS variables and shell behavior consumed by all student pages.

- [ ] **Step 1: Add a failing shell regression test**

Assert desktop sidebar width near 232px, visible navigation SVGs, Settings positioned in the sidebar footer region, and Profile visible in the top-right utility region.

- [ ] **Step 2: Run the shell regression test and confirm it fails on V3**

Run the focused Playwright spec with `./node_modules/.bin/playwright test <spec> --project=chromium` from `frontend`.

- [ ] **Step 3: Update V4 tokens and shell CSS**

Replace V3 shell colors/density with approved V4 variables and remove rules that hide navigation icons or the top utility profile.

- [ ] **Step 4: Adjust navigation/topbar markup only where CSS cannot express the approved structure**

Keep existing navigation callbacks and route behavior unchanged; separate Settings from primary nav and surface the existing profile utility.

- [ ] **Step 5: Re-run the shell regression test**

Expected: pass with no horizontal overflow at desktop and mobile shell targets.

- [ ] **Step 6: Commit shell convergence**

```bash
git add frontend/public/static/css/usth/tokens.css frontend/public/static/css/usth/shell.css frontend/src/components/StudentNavigation.tsx frontend/src/components/Topbar.tsx frontend/src/components/UsthBrand.tsx frontend/e2e
git commit -m "feat: converge student shell on Figma V4"
```

### Task 8: Implement Dashboard, Courses and Forum V4 layouts

**Files:**
- Modify: `frontend/src/app/(base)/dashboard/page.tsx`
- Modify: affected V4 dashboard/course/forum CSS under `frontend/public/static/css/usth/`.
- Modify: existing forum/dashboard legacy JS only when layout requires stable hooks; preserve API behavior.
- Test: focused Playwright specs under `frontend/e2e/`.

**Interfaces:**
- Consumes: shared shell/tokens from Task 7 and existing API data.
- Produces: dense V4 Dashboard/Courses/Forum student surfaces.

- [ ] **Step 1: Write viewport-density regressions**

Assert Dashboard primary sections and Forum controls/composer/first discussion items are visible within the 1440×900 reference viewport when mock data is populated; assert no page-level horizontal overflow.

- [ ] **Step 2: Run the regressions and confirm V3 failures**

Expected: current spacing/ordering causes at least one density or layout assertion to fail.

- [ ] **Step 3: Implement Dashboard V4 structure**

Use current data hooks for continue-learning, weekly/streak and metrics; compact or hide unsupported empty blocks instead of adding fake values.

- [ ] **Step 4: Implement Courses compact toolbar and cards**

Keep current search/filter/sort behavior and IDs/hooks while restructuring presentation into the approved compact toolbar.

- [ ] **Step 5: Implement Forum V4 workspace**

Remove geometry hacks such as large forced search margins; keep current forum search/filter/sort/composer/list behavior while composing them into the unified control bar and discussion frame.

- [ ] **Step 6: Re-run focused tests**

Expected: density, controls, posting behavior, and overflow tests pass.

- [ ] **Step 7: Run the forum XSS regression**

```bash
node e2e/unit/forum-xss.test.mjs
```
Expected: pass.

- [ ] **Step 8: Commit primary student surfaces**

```bash
git add frontend/src/app/'(base)'/dashboard/page.tsx frontend/public/static/css/usth frontend/e2e
git commit -m "feat: rebuild dashboard courses and forum for V4"
```

### Task 9: Implement remaining student and auxiliary V4 surfaces

**Files:**
- Modify: existing Roadmap/Skills/Profile/Settings components and related CSS.
- Modify: existing Questionnaire, Concept Card, Interface and Chatbot components/CSS.
- Test: relevant existing Playwright specs.

**Interfaces:**
- Consumes: V4 shared shell/tokens.
- Produces: consistent remaining student/auxiliary surfaces with current behavior preserved.

- [ ] **Step 1: Add/extend regressions for mobile icons, Settings placement, Concept Card geometry and auxiliary overflow**

- [ ] **Step 2: Run focused tests and confirm failures where V3 differs**

- [ ] **Step 3: Implement Roadmap/Skills/Profile/Settings V4 styling and minimal markup changes**

- [ ] **Step 4: Implement Questionnaire/Concept Card/Interface/Chatbot V4 styling**

Keep Concept Card at 880×520 and avoid introducing scroll/overflow regressions.

- [ ] **Step 5: Re-run focused tests and commit**

```bash
git add frontend/src frontend/public/static/css/usth frontend/e2e
git commit -m "feat: align student auxiliary surfaces with V4"
```

### Task 10: Implement Landing, Auth, Course, Lesson and Admin V4 convergence

**Files:**
- Modify: existing landing components/CSS.
- Modify: existing login/register pages/CSS.
- Modify: course detail and lesson pages/CSS.
- Modify: admin page/components/CSS.
- Test: existing Playwright route specs.

**Interfaces:**
- Consumes: V4 foundations and Figma references.
- Produces: full product-scope V4 visual convergence.

- [ ] **Step 1: Add route-level visual/overflow regressions for affected surfaces**

- [ ] **Step 2: Run focused regressions and establish V3 baseline failures**

- [ ] **Step 3: Implement Landing/Auth convergence**

Reuse existing USTH assets and form behavior.

- [ ] **Step 4: Implement Course/Lesson convergence**

Keep learning content and module navigation behavior unchanged.

- [ ] **Step 5: Implement Admin convergence**

Keep tables/actions/status behavior unchanged.

- [ ] **Step 6: Re-run focused tests and commit**

```bash
git add frontend/src frontend/public/static/css frontend/e2e
git commit -m "feat: finish Figma V4 surface convergence"
```

### Task 11: Full verification, rendered capture and visual QA

**Files:**
- Create/update evidence under `frontend/.visual-qa/figma-v4/final/`.
- Modify only files required by verified QA defects.

**Interfaces:**
- Consumes: all implemented V4 surfaces.
- Produces: final passing build/test set and screenshot evidence with documented visual inspection.

- [ ] **Step 1: Run TypeScript and unit verification**

From `frontend`:
```bash
./node_modules/.bin/tsc --noEmit
node e2e/unit/forum-xss.test.mjs
```
Expected: both pass.

- [ ] **Step 2: Run the full Playwright suite**

```bash
./node_modules/.bin/playwright test
```
Expected: all tests pass.

- [ ] **Step 3: Run production build without changing the package manager or lockfile**

```bash
./node_modules/.bin/next build
```
Expected: successful Next.js production build.

- [ ] **Step 4: Capture desktop and mobile screenshots**

Capture Landing, Dashboard, Courses, Roadmap, Skills, Forum, Profile, Settings, Login, Register, Admin, Course Detail, Lesson, Questionnaire, Concept Card, Interface and Chatbot at their reference desktop/mobile sizes into `frontend/.visual-qa/figma-v4/final/`.

- [ ] **Step 5: Run automated geometry checks**

For each capture route, assert: `document.documentElement.scrollWidth <= window.innerWidth`, no broken `img` elements, expected navigation SVG count > 0, no unexpected console/page errors, and target first-view sections have bounding boxes intersecting the reference viewport.

- [ ] **Step 6: Perform manual visual inspection against the final Figma V4 frames**

Inspect alignment, page padding, missing/broken assets, icon presence/consistency, clipping, excessive whitespace, excessive scrolling, color monotony, competing accents, card density, forum composition, dashboard streak composition, and mobile wrapping.

- [ ] **Step 7: Fix every confirmed QA defect and repeat Steps 1–6**

Do not close the task with known visual regressions.

- [ ] **Step 8: Commit final QA fixes/evidence metadata**

```bash
git add frontend docs/superpowers
git commit -m "test: verify USTH Figma V4 visual convergence"
```
