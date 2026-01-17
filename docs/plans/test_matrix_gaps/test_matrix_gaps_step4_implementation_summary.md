## Stage 1 – Add Questions autosave coverage
- Changes: Added an E2E test that fills the Questions textarea and verifies autosave persistence.
- Verification: Manual smoke test suggested (run `pytest tests/e2e/test_questions_autosave.py`; not run here).
- Notes: The test creates a new project and writes to the active database.

## Stage 2 – Add item add/edit/delete coverage
- Changes: Added an E2E test that adds, edits, and deletes a Summary item.
- Verification: Manual smoke test suggested (run `pytest tests/e2e/test_items_flow.py`; not run here).
- Notes: The test creates a new project and writes to the active database.

## Stage 3 – Add archive/unarchive coverage
- Changes: Added an E2E test that archives and unarchives a project in the manage view.
- Verification: Manual smoke test suggested (run `pytest tests/e2e/test_archive_project.py`; not run here).
- Notes: The test creates a new project and writes to the active database.

## Stage 4 – Add theme toggle coverage
- Changes: Added an E2E test that cycles the theme toggle and verifies theme attributes.
- Verification: Manual smoke test suggested (run `pytest tests/e2e/test_theme_toggle.py`; not run here).
- Notes: The test expects a fresh localStorage state per test.

## Stage 5 – Update the test matrix
- Changes: Marked newly covered UI flows in the test matrix and cleared the gaps list.
- Verification: Manual smoke test suggested (review `docs/test_matrix.md`; not run here).
- Notes: None.
