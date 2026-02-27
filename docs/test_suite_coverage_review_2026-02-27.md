# Test Suite Coverage Review (2026-02-27)

## Scope
- Compare current tests to recent git activity and estimate coverage of newer features.
- Focus window: changes since 2026-01-01, with attention to the latest commits in February 2026.

## Key Findings
1. High: latest builder import work is currently untested.
   - Latest feature commit `5f536d0` (2026-02-26) changes import ordering, dedupe, timestamps, and import maps.
   - No new tests were added with this change.
   - Impacted modules:
     - `app/builder_import_pipeline.py`
     - `app/db_import_content.py`
     - `app/builder_import_source.py`
     - `app/builder_import_transform.py`
     - `app/builder_import_llm.py`
     - `app/db_import_map.py`

2. High: auth/magic-link/lobby/session flows have no direct endpoint coverage.
   - Large and recently changed route surface in `app/api_auth.py`.
   - Includes register/verify, lobby decisions, magic links, ledger, and session restore.

3. High: authorization/scoping is partially covered.
   - Covered: settings admin route behavior and project house filter/update.
   - Not covered: session-based project scoping for non-admin users, and API denial paths for summary/questions edits.

4. Medium: transcript + question regeneration + upload paths are untested.
   - No tests found for:
     - transcript analysis endpoint (`/projects/{id}/transcript`)
     - question regeneration start/status endpoints
     - transcription upload + chunk completion endpoints and size/MIME boundaries

5. Medium: several newer project endpoints still have no direct tests.
   - `/backup`
   - `/houses`
   - `/projects/{id}/items/order`
   - `/projects/{id}/goal`
   - `/projects/{id}/progress/history`

## Coverage Estimate
- Commit-level coupling signal (app commits that include same-commit test changes):
  - Since 2026-01-01: `3 / 114` app-touching commits (about `2.6%`).
  - Since 2026-02-19: `3 / 34` app-touching commits (about `8.8%`).
- Route-level signal:
  - Roughly `10 / 42` API routes are directly exercised by current tests (about `24%`).
- Practical estimate for "new stuff" coverage:
  - Core project CRUD/UI flows are covered.
  - Most high-churn recent features are not.
  - Estimated current coverage of recent/new functionality: **~25-35%**.
  - Latest import-all updates feature: **effectively 0% covered**.

## Existing Coverage Noted
- Projects API happy paths + house filter/update + create validation:
  - `tests/http/test_projects_api.py`
- Settings admin route access behavior:
  - `tests/test_settings_access_controls.py`
- Env sync parsing edge case:
  - `tests/test_env_sync.py`
- Core E2E project/dashboard/items/archive/theme/interview guide flows:
  - `tests/e2e/*.py`

## Recommended Additions (Priority Order)
1. `tests/http/test_builder_import_pipeline.py`
   - all-checkins ingestion
   - dedupe exact/near duplicate behavior
   - historical timestamp preservation
   - import map updates across reruns

2. `tests/http/test_auth_api.py`
   - magic link issue/list/revoke/bootstrap
   - register/verify/status
   - lobby approve/reject
   - session challenge/restore
   - user house admin update

3. `tests/http/test_project_authz_and_scoping.py`
   - non-admin denial for summary/questions endpoints
   - house scoping behavior by session

4. `tests/http/test_transcript_and_regeneration_api.py`
   - transcript analyze success + error paths
   - question regeneration start/status lifecycle and failure states

5. `tests/http/test_transcription_uploads_api.py`
   - MIME normalization
   - 35MB limit enforcement
   - chunk session create/upload/complete flow

6. Extend project endpoint coverage
   - reorder, goal, progress history, houses list, backup

## Notes
- `pytest` is not available in current PATH in this environment, so this review was based on file/code inspection and git history mapping.
