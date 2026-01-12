# Test Matrix Gaps - Step 2 Feature Description

Problem: Several key frontend flows (questions autosave, item edits, archive actions, theme toggle) are not covered by automated tests, reducing confidence in UI changes.

User stories:
- As a project lead, I want critical UI flows covered so that releases are less risky.
- As a developer, I want clear automated checks for common dashboard interactions.
- As a stakeholder, I want visibility into which flows are protected by tests.

Core requirements:
- Add automated coverage for the gap list in `docs/test_matrix.md`.
- Prioritize UI-critical flows for E2E coverage.
- Keep tests stable and avoid flaky timing assumptions.
- Update the test matrix to reflect new coverage.
- Do not introduce npm-based tooling.

Shared component inventory:
- Reuse Playwright + pytest stack in `tests/e2e`.
- Reuse current UI selectors and flows in `templates/` and `static/js/`.
- Update `docs/test_matrix.md` as the source of truth for coverage.

Simple user flow:
1. Run the E2E test suite.
2. See the added flows covered by automated checks.
3. Review the updated test matrix for coverage status.

Success criteria:
- All listed gaps in the test matrix have corresponding tests.
- The test matrix reflects the new coverage.
- Tests pass reliably on a local run.
