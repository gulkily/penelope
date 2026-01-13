# E2E Full Data Coverage - Step 2 Feature Description

Problem: Current E2E tests create minimal project data and do not exercise all dashboard fields, so demo data is sparse and key fields are unverified.

User stories:
- As a project lead, I want at least one E2E run to populate all key fields so that demo data looks complete.
- As a developer, I want focused E2E tests that isolate behaviors while still covering every field.
- As a stakeholder, I want confidence that objectives, progress, questions, and all sections work as expected.

Core requirements:
- Add one comprehensive E2E test that creates a project and populates objective, progress, questions, and all section items.
- Keep existing focused E2E tests (questions autosave, items, archive, theme toggle).
- Ensure new tests remain stable and avoid flaky waits.
- Update the test matrix to reflect the new comprehensive coverage.
- Do not introduce npm-based tooling.

Shared component inventory:
- Reuse Playwright + pytest stack in `tests/e2e`.
- Reuse existing UI flows in `templates/` and `static/js/`.
- Update `docs/test_matrix.md` to record coverage.

Simple user flow:
1. Run the E2E suite.
2. See a project created with all fields filled in.
3. Review the updated test matrix.

Success criteria:
- At least one project created via E2E has objective, progress, questions, and items in all sections.
- Existing focused tests still pass.
- Test matrix reflects the new comprehensive coverage.
