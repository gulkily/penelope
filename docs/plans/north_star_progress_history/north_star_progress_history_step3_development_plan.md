# North Star Progress History - Step 3 Development Plan

1. Add progress history storage and data access helpers
- Goal: Persist each progress update as a timestamped history entry per resident.
- Dependencies: Existing SQLite initialization and DB connection helpers.
- Expected changes: Conceptually add a `progress_history` table with resident/project ID, progress value, and recorded timestamp; add DB helpers to insert and list history entries; expose the helpers via `app/db.py`; document the new table in `docs/postgres_migration.md`.
- Planned signatures: `log_progress_history(project_id: int, progress: int, recorded_at: str) -> None`, `list_progress_history(project_id: int, limit: int | None = None) -> list[dict]`.
- Verification approach: Restart the app and confirm the history table exists; run a quick insert via the helper and confirm it can be read back.
- Risks/open questions: Confirm the timestamp format (UTC ISO) stays consistent with other stored timestamps.
- Shared components/API contracts: Database schema bootstrap (`app/db_init.py`), DB helper exports (`app/db.py`).

2. Log history entries on every progress update
- Goal: Ensure all progress changes are recorded without altering the current dashboard behavior.
- Dependencies: Stage 1 helpers for history insertions.
- Expected changes: Update the progress update path to write a history entry alongside the existing progress update; keep the `PUT /api/projects/{project_id}/progress` response unchanged.
- Verification approach: Update progress via the existing API or UI, then confirm a new history entry exists for the resident.
- Risks/open questions: The slider can emit frequent updates; confirm history growth is acceptable or consider future throttling.
- Shared components/API contracts: Progress update API contract, `app/db_projects.py` update helper.

3. Provide a read endpoint for progress history
- Goal: Allow the backend to return a resident’s history for future graphing.
- Dependencies: Stages 1–2 data helpers.
- Expected changes: Add a `GET /api/projects/{project_id}/progress/history` endpoint; add response schema(s) for history entries; ensure entries are returned in a predictable order (newest or oldest first).
- Planned signatures: `GET /api/projects/{project_id}/progress/history`.
- Verification approach: Call the new endpoint after multiple updates and confirm the response contains distinct timestamped entries.
- Risks/open questions: Decide if pagination/limits are needed now or deferred until graphing work.
- Shared components/API contracts: `app/api.py` router, `app/schemas.py` response models.

4. Add coverage for history logging and retrieval
- Goal: Prevent regressions around history insertion and retrieval.
- Dependencies: Stages 1–3.
- Expected changes: Add an HTTP-level test that updates progress multiple times and verifies the history endpoint returns matching entries.
- Verification approach: Run `pytest tests/http` against a running server and ensure the new test passes.
- Risks/open questions: Ensure tests remain stable with existing seed data.
- Shared components/API contracts: HTTP tests for `/api/projects/{project_id}/progress` and the new history endpoint.
