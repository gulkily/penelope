# E2E Tests - Step 3 Development Plan

1. Establish E2E tooling baseline
   - Goal: Add Playwright configuration and a basic test runner setup.
   - Dependencies: Project root tooling conventions and existing local startup flow.
   - Expected changes: Add Playwright config, a minimal sample spec, and document a single command to run E2E tests.
   - Verification: Run the sample E2E test against a locally running app.
   - Risks/open questions: Decide on browser target(s) and base URL handling.
   - Shared components/API contracts touched: None (tooling only).

2. Add core UI E2E coverage
   - Goal: Cover at least one critical user flow (e.g., select a project, update progress, update objective).
   - Dependencies: E2E tooling baseline and existing UI flows in `templates/` and `static/js/`.
   - Expected changes: Add focused Playwright specs that exercise the dashboard flow using stable selectors.
   - Verification: Run the UI tests locally and confirm they pass reliably.
   - Risks/open questions: Potential flakiness around async autosave timing.
   - Shared components/API contracts touched: UI selectors and routes used in Playwright specs.

3. Add lightweight HTTP-level integration tests
   - Goal: Validate core API behavior without a browser.
   - Dependencies: Existing API endpoints in `app/` and a test runner choice.
   - Expected changes: Add a small HTTP-level test suite that hits key endpoints (projects list, project detail, update objective/progress).
   - Verification: Run the integration tests against a locally running app or in-process test client.
   - Risks/open questions: Decide whether to use a real server or a test client; manage test data setup/cleanup.
   - Shared components/API contracts touched: API endpoints under `app/api.py`.

4. Document test workflows
   - Goal: Make it easy to run both suites locally.
   - Dependencies: Test runner commands from prior stages.
   - Expected changes: Update README or a dedicated docs section with run instructions and prerequisites.
   - Verification: Follow the documented steps to run the tests.
   - Risks/open questions: Ensure docs stay in sync as tooling evolves.
   - Shared components/API contracts touched: Documentation files in the repo root.
