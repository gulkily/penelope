# Test Matrix

This matrix maps key frontend flows to current automated coverage.

| Flow | E2E test | HTTP test | Notes |
| --- | --- | --- | --- |
| Dashboard loads | tests/e2e/test_smoke.py | — | Basic page load + title check. |
| Create project (UI) | tests/e2e/test_dashboard_flow.py | — | Creates project via Manage Projects UI. |
| Select project (UI) | tests/e2e/test_dashboard_flow.py | — | Navigates from project list to dashboard. |
| Update objective (UI) | tests/e2e/test_dashboard_flow.py | — | Verifies autosave via network response + reload. |
| Update progress (UI) | tests/e2e/test_dashboard_flow.py | — | Sets slider to 50% and checks label. |
| Project create + updates (API) | — | tests/http/test_projects_api.py | Covers create + objective/progress via API. |

## Gaps
- Questions autosave (UI)
- Item add/edit/delete flows (UI)
- Archive/unarchive project (UI)
- Theme toggle (UI)
