## Stage 1 - Add canonical house model to resident storage
- Changes:
  - Added `app/house.py` with canonical house constants and normalization helpers (`normalize_house`, `normalize_house_filter`).
  - Extended `projects` schema initialization in `app/db_init.py` with required `house` column defaulting to `Unassigned`.
  - Added DB backfill logic to normalize existing `projects.house` values and fall back to `Unassigned` for missing/invalid values.
- Verification:
  - Ran `python -m py_compile app/house.py app/db_init.py`.
- Notes:
  - House values are now normalized centrally and ready to be wired into API/UI stages.

## Stage 2 - Extend project list/detail APIs with house data and filtering
- Changes:
  - Extended `list_projects` in `app/db_projects.py` to return `house` and accept optional house filtering.
  - Added house filtering support to `/api/projects` query handling in `app/api.py`.
  - Extended project detail payloads from `get_project` to include resident `house`.
- Verification:
  - Ran `python -m py_compile app/db_projects.py app/api.py`.
- Notes:
  - Existing list sort/pagination behavior was preserved while adding optional `house` filtering.

## Stage 3 - Add create/update house API contracts
- Changes:
  - Updated project creation contracts to require `house` (`ProjectCreate`) and normalized the value in `db.create_project`.
  - Added `ProjectHouseUpdate` schema and new endpoint `PUT /api/projects/{project_id}/house`.
  - Added `db.update_project_house` and exported it via `app/db.py`.
- Verification:
  - Ran `python -m py_compile app/db_projects.py app/db.py app/schemas.py app/api.py`.
- Notes:
  - Invalid or missing house values now return HTTP 400 from API contracts.
