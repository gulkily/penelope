## Stage 1 – Add Questions autosave coverage
- Changes: Added an E2E test that fills the Questions textarea and verifies autosave persistence.
- Verification: Manual smoke test suggested (run `pytest tests/e2e/test_questions_autosave.py`; not run here).
- Notes: The test creates a new project and writes to the active database.

## Stage 2 – Add item add/edit/delete coverage
- Changes: Added an E2E test that adds, edits, and deletes a Summary item.
- Verification: Manual smoke test suggested (run `pytest tests/e2e/test_items_flow.py`; not run here).
- Notes: The test creates a new project and writes to the active database.
