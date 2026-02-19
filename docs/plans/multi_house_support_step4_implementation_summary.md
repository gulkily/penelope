## Stage 1 - Add canonical house model to resident storage
- Changes:
  - Added `app/house.py` with canonical house constants and normalization helpers (`normalize_house`, `normalize_house_filter`).
  - Extended `projects` schema initialization in `app/db_init.py` with required `house` column defaulting to `Unassigned`.
  - Added DB backfill logic to normalize existing `projects.house` values and fall back to `Unassigned` for missing/invalid values.
- Verification:
  - Ran `python -m py_compile app/house.py app/db_init.py`.
- Notes:
  - House values are now normalized centrally and ready to be wired into API/UI stages.
