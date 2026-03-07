# Test Matrix

This matrix summarizes what our automated tests currently cover and how to run them.

## Run Commands
- Full E2E suite (Chromium): `python3 -m pytest tests/e2e -q`
- Full E2E suite (Firefox): `python3 -m pytest tests/e2e --browser firefox -q`
- Single E2E test with readable progress + skip reason: `python3 -m pytest tests/e2e/test_magic_links_and_lobby_badge.py::test_lobby_badge_indicator_updates_with_pending_count -v -rs --maxfail=1`
- HTTP tests: `python3 -m pytest tests/http -q`
- Task-runner shortcuts: `./pnl test e2e`, `./pnl test http`, `./pnl test`

## E2E Coverage By Feature

| Area | Test files | Key behaviors covered |
| --- | --- | --- |
| Smoke/auth bootstrap | `tests/e2e/test_smoke.py`, `tests/e2e/conftest.py` | App reachable, authenticated baseline session, fail-fast server health checks. |
| Dashboard core | `tests/e2e/test_dashboard_flow.py`, `tests/e2e/test_dashboard_selection_and_dialog.py`, `tests/e2e/test_dashboard_interactions.py` | Resident selection, objective/goal/progress autosave, empty state, undo delete, reorder persistence. |
| Dashboard keyboard/graph/filter/roles | `tests/e2e/test_dashboard_graph_and_keyboard.py`, `tests/e2e/test_dashboard_keyboard_inputs.py`, `tests/e2e/test_dashboard_house_filter.py`, `tests/e2e/test_dashboard_role_visibility.py` | Graph toggle, keyboard reorder/edit actions, house filter URL/localStorage sync, non-admin scoping and read-only fields. |
| Items/data population | `tests/e2e/test_items_flow.py`, `tests/e2e/test_full_data_coverage.py` | Item add/edit/delete, inline add across sections, persisted project data reload checks. |
| Interview guide + dialog | `tests/e2e/test_interview_guide.py`, `tests/e2e/test_transcript_dialog_flows.py` | Guide toggle/backdrop behavior, transcript draft restore, mocked analyze/apply flows, questions regeneration, timeout/offline/error states, confetti path. |
| Audio upload | `tests/e2e/test_audio_upload_flows.py` | Small-file single upload, large-file chunked upload, chunk retry, upload failure messaging. |
| Manage residents | `tests/e2e/test_manage_projects_controls.py`, `tests/e2e/test_archive_project.py` | House update/filter, id/name/archived sorting, pagination, URL/back-forward sync, archive/unarchive. |
| Settings/admin pages | `tests/e2e/test_auth_and_settings_pages.py`, `tests/e2e/test_settings_subpages_and_theme.py`, `tests/e2e/test_magic_links_and_lobby_badge.py` | Admin page access patterns, backup success/failure status, version/session metadata, magic-link house prefill, lobby badge indicator. |
| Session/lobby routes | `tests/e2e/test_session_and_lobby_flows.py` | `/session/reset` redirect/restore/failure flow, `/welcome` + token handoff, `/lobby` token handoff behavior. |
| Theme | `tests/e2e/test_theme_toggle.py`, `tests/e2e/test_settings_subpages_and_theme.py` | Theme cycle and cross-page persistence checks. |

## HTTP Coverage

| Area | Test files | Key behaviors covered |
| --- | --- | --- |
| Projects API | `tests/http/test_projects_api.py` | Project create/update flows and house filter/update API behavior. |

## Known Conditional Skips
- Admin-only pages (`/settings`, `/settings/magic-links`, `/settings/users`, `/ledger`) can skip if the current session is non-admin.
- Lobby badge test can skip if `lobby` is not enabled in `NAVBAR_ENABLED_ITEMS`.
- Some lobby/session tests depend on browser/runtime capabilities; use `-rs` to see exact skip reasons.

## Known Gaps
- Pointer drag reorder coverage.
- Recorder start/stop/reset mocked coverage and `RECORDER_ENABLED=false` UI assertions.
- Offline upload pause/resume path assertions.
- Navbar visibility matrix assertions for all `NAVBAR_ENABLED_ITEMS` combinations.
