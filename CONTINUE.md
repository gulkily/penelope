# CONTINUE

## Branch
- `fix/e2e-test-suite-refresh`

## Goal
- Refresh the E2E suite to match current app behavior using `docs/e2e_test_suite_update_checklist_2026-03-05.md`.
- Work one failing test at a time until `./pnl test e2e` is green.

## Completed So Far
1. Added admin auth bootstrap for E2E:
   - `tests/e2e/conftest.py`
   - Injects signed `penelope_session` cookie for local `E2E_BASE_URL`.
2. Updated stale selectors/copy in core tests:
   - Resident creation now uses `Resident name` + `Add resident`.
   - Waits for house options to load before submit.
3. Updated progress assertions from percent text to `units / goal` format.
4. Stabilized interview-guide tests:
   - Added waits for dashboard interactivity before opening Add update dialog.
   - Made guide loading checks content-based.
   - Hardened mobile backdrop close interaction.
5. Updated checklist doc and annotated existing E2E test names.

## Commits On This Branch
- `581fb36` `test: add e2e admin session fixture`
- `df989fa` `test: align e2e selectors and assertions with current ui`
- `c7150a6` `docs: add e2e test suite update checklist`
- `e4cf4b4` `docs: annotate e2e checklist with existing test names`
- `aee1ed3` `test: stabilize interview guide e2e interactions`

## Next Steps
1. Run full suite and identify next failing test:
   - `./pnl test e2e`
2. Fix one failing spec at a time and commit per feature/fix.
3. After each fix:
   - rerun affected test file first
   - rerun `./pnl test e2e`
4. Continue checking off completed checklist items.

## Suggested Immediate Workflow
1. Run: `python3 -m pytest tests/e2e -q`
2. Share first failing traceback.
3. Fix + commit.
4. Repeat.

## Notes
- If local unrelated files reappear, keep them stashed unless explicitly needed for E2E.
- Checklist source of truth: `docs/e2e_test_suite_update_checklist_2026-03-05.md`.
