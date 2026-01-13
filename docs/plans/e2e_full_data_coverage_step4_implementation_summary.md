## Stage 1 – Add comprehensive E2E data population test
- Changes: Added an E2E test that fills objective, progress, questions, and all section items in a new project.
- Verification: Manual smoke test suggested (run `pytest tests/e2e/test_full_data_coverage.py`; not run here).
- Notes: The test creates a new project and writes to the active database.
