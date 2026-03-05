# Multi House Support - Step 3 Development Plan

1. Stage 1 - Add canonical house model to resident storage
- Goal: Persist one normalized house value per resident with safe defaults for existing rows.
- Dependencies: Existing `projects` storage and DB initialization/backfill flow.
- Expected changes: Conceptually add required `house` field to resident/project storage; ensure missing existing values backfill to `Unassigned`; centralize fixed allowed values (`Unassigned`, `Actioners`, `SF2`) and normalization rules.
- Planned signatures: `normalize_house(value: str) -> str`; `ALLOWED_HOUSES: tuple[str, ...]`.
- Verification approach: Open an existing DB and confirm every resident has a non-empty normalized house value.
- Risks/open questions:
  - Unknown historical values need deterministic mapping (`Unassigned` fallback).
  - Keep normalization behavior identical across API and UI.
- Shared components/API contracts: `app/db_init.py`, `app/db_projects.py`, shared constants module.

2. Stage 2 - Extend project list/detail APIs with house data and filtering
- Goal: Make house available and filterable in canonical resident APIs.
- Dependencies: Stage 1.
- Expected changes: Extend list/detail payloads to include `house`; add optional house filter on project listing while preserving existing sort/pagination behavior.
- Planned signatures: `list_projects(..., house: str | None = None, ...) -> tuple[list[dict], int]`; `GET /api/projects?house=<value>`.
- Verification approach: Call `/api/projects` with `All houses` behavior (no filter) and per-house filters; verify returned subsets and payload fields.
- Risks/open questions:
  - Preserve compatibility with current query params (`page`, `sort_key`, `sort_dir`, `include_archived`).
  - Define invalid-house query behavior (400 vs fallback).
- Shared components/API contracts: `GET /api/projects`, `GET /api/projects/{project_id}`.

3. Stage 3 - Add create/update house API contracts
- Goal: Enforce required house on create and support direct house edits.
- Dependencies: Stage 1.
- Expected changes: Extend create payload validation to require `house` from fixed list; add dedicated house update endpoint for resident management edits.
- Planned signatures: `ProjectCreate(name: str, house: str)`; `ProjectHouseUpdate(house: str)`; `PUT /api/projects/{project_id}/house`.
- Verification approach: Confirm create rejects missing/invalid house, accepts valid house, and update endpoint persists edits.
- Risks/open questions:
  - Existing clients that send only `name` must be updated in the same rollout.
  - Ensure normalization still applies for mixed-case inputs.
- Shared components/API contracts: `POST /api/projects`, `PUT /api/projects/{project_id}/house`, request schemas.

4. Stage 4 - Extend resident management page for house assignment and filtering
- Goal: Allow users to assign/edit houses and filter residents by house in `/projects`.
- Dependencies: Stage 2-3.
- Expected changes: Add house filter control, required house input on resident create form, and editable house column/control in the resident table; wire table/create/edit actions to API; keep URL query-state for house filter.
- Verification approach: Create resident with each allowed house, edit house inline, toggle house filter, refresh page, and confirm filter state and data persistence.
- Risks/open questions:
  - Keep pagination/sort behavior stable when house filter is active.
  - Avoid accidental reset of edited house on list refresh.
- Shared components/API contracts: `templates/manage_projects.html`, `static/js/manage-projects.js`, `GET /api/projects`, `POST /api/projects`, `PUT /api/projects/{project_id}/house`.

5. Stage 5 - Extend dashboard resident selector with house filter and persistence
- Goal: Scope selector options to active house filter in `/`.
- Dependencies: Stage 2.
- Expected changes: Add house filter control on dashboard; load residents by active house filter; ensure selector only shows matching residents; persist house filter in URL and remembered client state with default `All houses`.
- Verification approach: Switch house filters on dashboard and verify selector options update correctly; reload page and confirm filter persistence; verify existing resident detail load still works.
- Risks/open questions:
  - If selected resident is excluded by a new filter, define clear reset behavior.
  - Keep URL state compatible with existing `?project=` deep links.
- Shared components/API contracts: `templates/index.html`, `static/js/app.js`, `GET /api/projects`.

6. Stage 6 - Regression coverage and rollout checks
- Goal: Protect existing workflows while adding house behavior.
- Dependencies: Stage 1-5.
- Expected changes: Add/extend HTTP tests for create validation, house update, list filtering, and payload shape; update any affected UI smoke checks.
- Verification approach: Run focused HTTP tests plus manual smoke on dashboard and resident management for add/edit/archive/filter flows.
- Risks/open questions:
  - Ensure archived resident handling remains unchanged under house filters.
  - Confirm no regressions in project selection and progress update flows.
- Shared components/API contracts: `tests/http/test_projects_api.py`, existing dashboard/management API contracts.
