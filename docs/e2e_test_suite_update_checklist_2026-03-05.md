# E2E Test Suite Update Checklist (2026-03-05)

Current suite is in `tests/e2e`, but app behavior now depends on auth/session, role, and newer pages/features in `templates/index.html`, `templates/manage_projects.html`, `templates/lobby.html`, and `app/main.py`.

## Existing E2E Tests Already Written
- `tests/e2e/test_smoke.py::test_dashboard_loads`
- `tests/e2e/test_dashboard_flow.py::test_can_create_project_and_update_north_star`
- `tests/e2e/test_full_data_coverage.py::test_populates_all_fields`
- `tests/e2e/test_questions_autosave.py::test_questions_autosave`
- `tests/e2e/test_items_flow.py::test_item_add_edit_delete`
- `tests/e2e/test_archive_project.py::test_archive_unarchive_project`
- `tests/e2e/test_interview_guide.py::test_interview_guide_checklist_progress_updates`
- `tests/e2e/test_interview_guide.py::test_interview_guide_mobile_drawer_closes_on_backdrop`
- `tests/e2e/test_theme_toggle.py::test_theme_toggle_cycles_preferences`

## 1. Stabilize the test harness first
- [x] Add deterministic auth bootstrap fixture for admin session cookie injection.
- [ ] Add a deterministic auth bootstrap fixture (admin and non-admin).
- [ ] Add a deterministic DB strategy per test run (ephemeral DB or isolated test schema).
- [ ] Add fixture factories for account, resident, house, and seeded progress history.
- [ ] Add fixture helpers for URL param setup (`project`, `house`, pagination/sort params).
- [ ] Add route-mocking fixtures for LLM/transcription endpoints so tests do not depend on external APIs.
- [ ] Add helper to assert network request payloads for autosave/update endpoints.
- [ ] Standardize selectors strategy (`data-*` hooks) to avoid breakage from label/text copy changes.
- [ ] Add a fail-fast check that app is reachable and authenticated session is active before UI assertions.

## 2. Repair outdated existing tests
- [x] Update resident creation selectors (`Resident name`, `Add resident`, required house selection).
- [x] Update progress assertions from percent-only text to current unit format (`x / goal`).
- [x] Update project naming assumptions to resident naming.
- [ ] Remove duplicated create-resident helper logic into one shared helper.
- [ ] Verify all existing tests pass under current auth middleware and role rendering rules.

## 3. Add missing dashboard coverage (`/`)
- [ ] Authenticated load with no resident selected (empty state and disabled controls). Existing baseline page-load check: `test_dashboard_loads`.
- [ ] Resident selection by dropdown and by `?project=` URL parameter.
- [ ] Admin house filter behavior, including localStorage persistence and URL sync.
- [ ] Non-admin resident scoping by assigned house.
- [ ] Summary field editable for admin, read-only rendering for non-admin.
- [ ] Questions field editable for admin, read-only rendering for non-admin. Existing admin autosave test: `test_questions_autosave`.
- [ ] Objective autosave and persistence. Existing test: `test_can_create_project_and_update_north_star`.
- [ ] Goal autosave and slider max recalculation.
- [ ] Progress slider update + persistence + display correctness. Existing baseline test: `test_can_create_project_and_update_north_star`.
- [ ] Progress graph toggle and progress-history rendering.
- [ ] Inline add in all four sections (summary/challenges/opportunities/milestones). Existing broad add coverage: `test_populates_all_fields`.
- [ ] Item edit/save/cancel behavior. Existing summary-item flow: `test_item_add_edit_delete`.
- [ ] Item delete + undo toast restore path. Existing delete (without undo assertion): `test_item_add_edit_delete`.
- [ ] Item reorder via up/down buttons.
- [ ] Item reorder via keyboard (`ArrowUp`/`ArrowDown` on drag handle).
- [ ] Item reorder via pointer drag.
- [ ] Keyboard behavior (Enter submit, Shift+Enter newline, Escape cancel).

## 4. Add transcript/update-dialog coverage
- [ ] Open/close Add Update dialog. Existing dialog usage in interview-guide tests.
- [ ] Transcript draft autosave/restore/clear per resident.
- [ ] Interview guide load/toggle. Existing tests: `test_interview_guide_checklist_progress_updates`, `test_interview_guide_mobile_drawer_closes_on_backdrop`.
- [ ] Interview guide keyboard shortcut (`g`) behavior.
- [ ] Interview guide mobile drawer/backdrop close behavior. Existing test: `test_interview_guide_mobile_drawer_closes_on_backdrop`.
- [ ] Analyze transcript success path (mocked backend response).
- [ ] Analyze transcript offline/error/timeout states.
- [ ] Suggested updates render and selectable apply logic.
- [ ] Apply updates writes objective/goal/progress/items and refreshes resident view.
- [ ] Questions regeneration lifecycle after apply (`queued/running/completed/error`).
- [ ] Confetti trigger after successful apply.

## 5. Add audio upload/recording coverage
- [ ] File upload single-request path (small file).
- [ ] Chunked upload path (large file) with progress updates.
- [ ] Upload pause/resume messaging when offline.
- [ ] Upload failure handling and retry messaging.
- [ ] Recorder start/stop/reset UI behavior (if permissions are mocked).
- [ ] `RECORDER_ENABLED=false` hides/disables recorder UI appropriately.

## 6. Add resident management coverage (`/projects`)
- [ ] Create resident with house. Existing coverage in multiple tests including `test_can_create_project_and_update_north_star`.
- [ ] Archive/unarchive resident. Existing test: `test_archive_unarchive_project`.
- [ ] Change resident house inline.
- [ ] House filter on table.
- [ ] Sort by ID/name/archived.
- [ ] Pagination prev/next and status text.
- [ ] URL sync for page/sort/house and back/forward behavior.

## 7. Add auth/session flow coverage
- [ ] Unauthenticated access redirects to `/session/reset` with normalized `next`.
- [ ] `/session/reset` success restore redirects to requested route.
- [ ] `/session/reset` failure redirects to `/welcome`.
- [ ] `/welcome` unauthenticated rendering.
- [ ] `/welcome?token=...` lobby handoff behavior.
- [ ] `/lobby` rendering when lobby auth disabled.
- [ ] `/lobby?token=...` behavior when lobby auth disabled but token flow allowed.
- [ ] Logout button clears session and redirects to `/lobby`.

## 8. Add settings/admin-page coverage
- [ ] `/settings` admin-only access behavior.
- [ ] Backup download button success path and failure message.
- [ ] `/settings/magic-links` generate/copy/revoke flow.
- [ ] Magic-link house prefill from existing user.
- [ ] `/settings/users` list rendering and house reassignment.
- [ ] `/ledger` entries rendering, empty state, and failure fallback.
- [ ] Lobby badge indicator updates (pending request count).

## 9. Add global UI/state coverage
- [ ] Theme toggle cycle on each major page. Existing single-page baseline: `test_theme_toggle_cycles_preferences`.
- [ ] Theme localStorage persistence across reload/navigation.
- [ ] Navbar item visibility based on `NAVBAR_ENABLED_ITEMS`.
- [ ] Settings nav visibility only for admin.
- [ ] Session identity display in top nav.
- [ ] Build metadata visibility on settings page.

## 10. Reliability/maintainability updates
- [ ] Split specs by feature/page and tag smoke vs full coverage.
- [ ] Keep a fast PR smoke pack and a broader nightly pack.
- [ ] Add trace/screenshot/video artifacts on failure.
- [ ] Add flake tracking and quarantine policy for unstable tests.
- [ ] Remove hard waits; use event/state-driven waits only.
- [ ] Update `docs/test_matrix.md` to reflect real coverage and intentional gaps.

## Open Questions
1. Should E2E authenticate by injecting a session cookie fixture, or do you want full UI login/lobby flows exercised in regular runs?
2. Do you want external-dependent flows (LLM + transcription) fully mocked in E2E, or exercised against real services in some environment?
3. For PR gating, do you want only Chromium, or Chromium + Firefox/WebKit?
4. Should audio recording tests run in CI, or be nightly/manual only?
5. Is admin + non-admin role coverage required in E2E for every relevant dashboard/settings flow?
6. Can we add stable `data-testid`/`data-e2e` hooks to templates to reduce selector fragility?
7. Should we prioritize updating existing broken tests first, then add coverage, or do both together in one pass?
