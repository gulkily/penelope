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

## Stage 4 - Extend resident management page for house assignment and filtering
- Changes:
  - Updated `templates/manage_projects.html` to add required house selection in the create form, house filter control, and a house column in the resident table.
  - Extended `static/js/manage-projects.js` to:
    - send required `house` on resident creation,
    - support inline house editing via `PUT /api/projects/{project_id}/house`,
    - apply house filtering through `/api/projects?house=...`,
    - persist house filter in URL and local storage (`houseFilter` key).
  - Added management-page styling for new form/filter/table controls in `static/css/main.css`.
- Verification:
  - Ran `node --check static/js/manage-projects.js`.
- Notes:
  - Existing pagination/sort behavior is retained while filtering by house.

## Stage 5 - Extend dashboard resident selector with house filter and persistence
- Changes:
  - Added house filter control to the dashboard header in `templates/index.html`.
  - Extended `static/js/app.js` to:
    - read/write house filter from URL query param (`house`) and local storage (`houseFilter`),
    - request `/api/projects` with the active house filter,
    - repopulate resident selector options to only show residents matching the active house filter.
  - Updated dashboard header layout in `static/css/main.css` to wrap cleanly with the extra filter control.
- Verification:
  - Ran `node --check static/js/app.js`.
  - Ran `node --check static/js/manage-projects.js`.
- Notes:
  - Existing `?project=` deep-link behavior is preserved while applying house-filter scoping.

## Stage 6 - Regression coverage and rollout checks
- Changes:
  - Adjusted `init_db` ordering in `app/db_init.py` so project house backfill runs after seed insertion, ensuring seeded residents are normalized to canonical house values.
  - Updated `tests/http/test_projects_api.py` to:
    - send required `house` in project creation flows,
    - validate `/api/projects?house=...` filtering,
    - validate `PUT /api/projects/{project_id}/house`,
    - validate invalid/missing house create behavior.
- Verification:
  - Ran `python -m py_compile app/house.py app/db_init.py app/db_projects.py app/db.py app/schemas.py app/api.py tests/http/test_projects_api.py`.
- Notes:
  - Did not run `pytest tests/http` because these tests require a separately running app server in this environment.
