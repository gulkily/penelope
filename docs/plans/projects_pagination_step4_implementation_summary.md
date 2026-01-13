## Stage 1 – Add paginated list support in the API
- Changes: Added page support to `GET /api/projects`, returning `total` plus page metadata and updating `app/db_projects.list_projects` to support limit/offset.
- Verification: Not run here (requires running the server and requesting paged results).
- Notes: Default (no page) response remains backward compatible with full lists.
