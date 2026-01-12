## Stage 1 – Establish E2E tooling baseline
- Changes: Added Playwright configuration, scripts, and a basic smoke test; updated gitignore for Playwright artifacts.
- Verification: Manual smoke test suggested (start the app and run `npm run test:e2e`; not run here).
- Notes: Tests expect the app to be running locally.

## Stage 2 – Add core UI E2E coverage
- Changes: Added a Playwright test that creates a project and updates objective/progress through the UI.
- Verification: Manual smoke test suggested (run `npm run test:e2e`; not run here).
- Notes: The test writes to the active database.

## Stage 3 – Add HTTP-level integration tests
- Changes: Added Playwright API tests that create a project and verify objective/progress updates.
- Verification: Manual smoke test suggested (run `npm run test:api`; not run here).
- Notes: The test writes to the active database.
