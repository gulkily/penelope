# CONTINUE

## Branch
- `fix/e2e-test-suite-refresh`

## Session Rules (Persistent)
- Work unattended; do not pause for prompt-by-prompt confirmation.
- Continue until checklist completion and all work is committed by feature.
- Design tests to avoid stalling/hanging.
- Actually run tests locally after changes (do not leave as unverified).
- Keep these rules in this file for the duration of the session.

## Current Status
- Full E2E run is green after coverage expansion.
- Last full run command: `./pnl test e2e`
- Last result: `54 passed, 2 skipped in 46.57s`
- New coverage files added:
  - `tests/e2e/test_audio_upload_flows.py`
  - `tests/e2e/test_auth_and_settings_pages.py`
  - `tests/e2e/test_dashboard_graph_and_keyboard.py`
  - `tests/e2e/test_dashboard_house_filter.py`
  - `tests/e2e/test_dashboard_interactions.py`
  - `tests/e2e/test_dashboard_keyboard_inputs.py`
  - `tests/e2e/test_dashboard_role_visibility.py`
  - `tests/e2e/test_dashboard_selection_and_dialog.py`
  - `tests/e2e/test_manage_projects_controls.py`
  - `tests/e2e/test_magic_links_and_lobby_badge.py`
  - `tests/e2e/test_session_and_lobby_flows.py`
  - `tests/e2e/test_settings_subpages_and_theme.py`
  - `tests/e2e/test_transcript_dialog_flows.py`
  - `tests/e2e/helpers.py`

## Remaining Checklist Work
- Add deterministic DB isolation strategy for each test run.
- Add dedicated fixture factories/helpers (account/resident/house/progress history + URL-param helpers).
- Convert repeated route stubs into shared mocking fixtures.
- Add payload-assertion helper for autosave/update requests.
- Add pointer-drag reorder test coverage.
- Add upload pause/resume offline coverage.
- Add recorder mocked start/stop/reset coverage and `RECORDER_ENABLED=false` behavior coverage.
- Add lobby badge assertion in an environment where lobby nav badge is enabled.
- Add navbar visibility matrix coverage for `NAVBAR_ENABLED_ITEMS`.
- Complete reliability/maintainability tasks in section 10.

## Immediate Next Run
1. `./pnl test e2e`
2. Continue implementing unchecked checklist items.

## Execution Loop
1. Take first failing test only.
2. Patch only that failure.
3. Re-run that file.
4. Commit focused change.
5. Update checklist.

## Source Of Truth
- `docs/e2e_test_suite_update_checklist_2026-03-05.md`
