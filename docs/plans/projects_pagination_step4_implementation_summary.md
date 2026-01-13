## Stage 1 – Add paginated list support in the API
- Changes: Added page support to `GET /api/projects`, returning `total` plus page metadata and updating `app/db_projects.list_projects` to support limit/offset and server-side sorting parameters.
- Verification: Not run here (requires running the server and requesting paged results).
- Notes: Default (no page) response remains backward compatible with full lists.

## Stage 2 – Update management page pagination UI
- Changes: Added pagination controls to `templates/manage_projects.html`, styled them in `static/css/main.css`, and introduced pagination state in `static/js/manage-projects.js`.
- Verification: Not run here (requires loading the management page in a browser).
- Notes: Pagination defaults to 100 items per page and uses API-provided totals.

## Stage 3 – Preserve sorting and actions with pagination
- Changes: Added server-side sorting when multiple pages exist, while keeping client-side sorting for single-page results and refreshing pagination status after sort interactions.
- Verification: Not run here (requires exercising sort, add, and archive flows in the UI).
- Notes: Sorting remains client-side on the current page; add/archive reloads the current page.

## Stage 4 – Document pagination behavior
- Changes: Documented the 100-item pagination behavior in `README.md`.
- Verification: Not run here (documentation update only).
- Notes: None.
