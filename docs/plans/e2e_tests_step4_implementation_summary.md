## Stage 1 – Establish Python Playwright baseline
- Changes: Added Python Playwright dependencies, created initial E2E smoke test, and updated gitignore for pytest cache.
- Verification: Manual smoke test suggested (start the app and run `pytest tests/e2e`; not run here).
- Notes: Tests expect the app to be running locally.

## Stage 2 – Add core UI E2E coverage
- Changes: Added a Playwright test that creates a project and updates objective/progress through the UI.
- Verification: Manual smoke test suggested (run `pytest tests/e2e`; not run here).
- Notes: The test writes to the active database.

## Stage 3 – Add HTTP-level integration tests
- Changes: Added Playwright API tests that create a project and verify objective/progress updates.
- Verification: Manual smoke test suggested (run `pytest tests/http`; not run here).
- Notes: The test writes to the active database.

## Stage 4 – Document test workflows and npm policy
- Changes: Documented Python-based test commands in README and AGENTS, and added a no-npm instruction.
- Verification: Manual smoke test suggested (follow README steps to run tests; not run here).
- Notes: Set `E2E_BASE_URL` to target a non-default server.
