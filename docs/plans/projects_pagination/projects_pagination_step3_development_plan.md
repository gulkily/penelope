# Projects Pagination - Step 3 Development Plan

1. Stage 1 - Add paginated list support in the API
   - Goal: Allow `/api/projects` to return a paginated slice with a fixed 100-item page size.
   - Dependencies: Existing `app/api.py` list endpoint and `app/db_projects.list_projects` data access.
   - Expected changes: Extend `list_projects` to accept pagination parameters (page or offset) while preserving `include_archived`; include total count in the response for page controls.
   - Planned signatures: `list_projects(include_archived: bool = False, limit: int = 100, offset: int = 0) -> tuple[list[dict], int]` or similar; `GET /api/projects?page={n}&include_archived=1`.
   - Verification: With the server running, request two pages and confirm counts and project IDs differ appropriately.
   - Risks/open questions: Decide on default page index (1-based vs 0-based) and ensure backward compatibility for non-paginated callers.
   - Shared components/API contracts touched: `app/api.py` `GET /api/projects`, `app/db_projects.list_projects`.

2. Stage 2 - Update management page pagination UI
   - Goal: Add pagination controls to the projects management page.
   - Dependencies: Stage 1 API response with total count.
   - Expected changes: Extend `templates/manage_projects.html` with pagination controls (next/previous, page indicator); update `static/js/manage-projects.js` to track current page and total pages.
   - Verification: Load the management page and confirm pagination controls appear and update as pages change.
   - Risks/open questions: Decide on control layout for small screens and whether to disable buttons at boundaries.
   - Shared components/API contracts touched: `templates/manage_projects.html`, `static/js/manage-projects.js`.

3. Stage 3 - Preserve sorting and actions with pagination
   - Goal: Ensure sorting and archive/add behaviors work correctly on paginated data.
   - Dependencies: Stage 2.
   - Expected changes: Reapply sorting to fetched page results; when archiving or adding, reload the current page (or reset to page 1) while keeping controls in sync.
   - Verification: Sort by each column, archive a project, add a project, and confirm the page updates without breaking pagination state.
   - Risks/open questions: Decide whether to keep users on the same page after add/archive or reset to the first page for clarity.
   - Shared components/API contracts touched: `static/js/manage-projects.js`, `GET /api/projects` paging parameters.

4. Stage 4 - Document pagination behavior
   - Goal: Make the new pagination expectations discoverable.
   - Dependencies: Stage 1–3.
   - Expected changes: Update `README.md` (and `AGENTS.md` if needed) to note pagination on the management page and the 100-item page size.
   - Verification: Review the docs for accuracy after the feature ships.
   - Risks/open questions: Ensure doc language matches the actual paging defaults and behavior.
   - Shared components/API contracts touched: `README.md`, `AGENTS.md`.
