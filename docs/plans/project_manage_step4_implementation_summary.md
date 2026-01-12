## Stage 1 - Extend data model for archived state
- Changes: Added archived flag to projects, added DB helpers in a split data layer to keep modules small, and seeded archived defaults.
- Verification: Not run yet; please start the server and confirm project payloads include `archived`.
- Notes: Existing records default to archived=false.

## Stage 2 - Add API endpoints for add/archive updates
- Changes: Added project creation and archive toggle endpoints plus request schemas; added `include_archived` flag to list projects.
- Verification: Not run yet; please `POST /api/projects` and `PUT /api/projects/{id}/archive`, then re-fetch the list.
- Notes: Archive toggles use boolean payloads.

## Stage 3 - Build the management page UI
- Changes: Added a dedicated project management page with an add form and projects table.
- Verification: Not run yet; please load `/projects` and confirm the layout renders.
- Notes: Project names link to the dashboard with `?project=` query param.

## Stage 4 - Wire UI actions to the API
- Changes: Added JS to load projects, create new projects, toggle archive checkboxes, and sync dashboard selection via URL params.
- Verification: Not run yet; please add a project, toggle archived, and click a project link to open the dashboard.
- Notes: Project links use `?project=`; archived projects are still accessible via direct link.
