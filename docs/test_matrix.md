# Test Matrix

This matrix maps key frontend flows to current automated coverage.

| Flow | E2E test | HTTP test | Notes |
| --- | --- | --- | --- |
| Dashboard loads | tests/e2e/test_smoke.py | — | Basic page load + title check. |
| Create project (UI) | tests/e2e/test_dashboard_flow.py | — | Creates project via Manage Projects UI. |
| Select project (UI) | tests/e2e/test_dashboard_flow.py | — | Navigates from project list to dashboard. |
| Update objective (UI) | tests/e2e/test_dashboard_flow.py | — | Verifies autosave via network response + reload. |
| Update progress (UI) | tests/e2e/test_dashboard_flow.py | — | Sets slider to 50% and checks label. |
| Questions autosave (UI) | tests/e2e/test_questions_autosave.py | — | Verifies autosave persistence after reload. |
| Item add/edit/delete (UI) | tests/e2e/test_items_flow.py | — | Covers Summary item CRUD flow. |
| Archive/unarchive project (UI) | tests/e2e/test_archive_project.py | — | Toggles archive checkbox in Manage Projects. |
| Theme toggle (UI) | tests/e2e/test_theme_toggle.py | — | Cycles theme preferences and checks attributes. |
| Project create + updates (API) | — | tests/http/test_projects_api.py | Covers create + objective/progress via API. |

## Gaps
- None noted for the current flow list.
