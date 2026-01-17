# Test Matrix Gaps - Step 1 Solution Assessment

Problem statement: Several critical UI flows are not covered by automated tests, leaving gaps in frontend confidence.

Option A: Expand the existing Playwright E2E suite to cover missing flows
- Pros: Real UI coverage, validates end-to-end behavior, aligns with current test stack.
- Cons: Slower runs, potential flakiness around autosave and async UI.

Option B: Add focused HTTP-level tests for missing flows where possible
- Pros: Fast, reliable, lower maintenance.
- Cons: Does not validate UI behavior or regressions.

Option C: Add a mix of E2E for UI-critical flows and HTTP tests for pure API behavior
- Pros: Balanced coverage and speed, focuses E2E on highest-risk UI paths.
- Cons: Requires prioritization and test taxonomy discipline.

Recommendation: Option C, using E2E for UI-critical flows (questions autosave, item add/edit/delete, archive/unarchive, theme toggle) and HTTP tests only when UI coverage is not needed.
