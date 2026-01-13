# Projects Pagination - Step 2 Feature Description

Problem: The projects management page becomes hard to scan and slow with large lists, so it needs pagination at a fixed 100-item page size.

User stories:
- As a project lead, I want to browse projects in pages so that large lists stay readable.
- As an operator, I want to move between pages quickly so that I can find specific projects without scrolling.
- As a maintainer, I want existing project add/archive flows to keep working so that pagination does not break daily use.

Core requirements:
- The projects management page supports pagination with a fixed page size of 100 items.
- Pagination controls allow navigating across pages without leaving the management page.
- Existing sorting (ID, name, archived) remains available alongside pagination.
- Project add/archive actions continue to work with the paginated view.
- The main dashboard project selector remains unaffected by pagination changes.

Shared component inventory:
- `templates/manage_projects.html`: reuse the management table layout and extend it with pagination controls.
- `static/js/manage-projects.js`: reuse the data fetch, sorting logic, and table rendering; extend with pagination state.
- `app/api.py` `GET /api/projects`: reuse as the canonical list endpoint; extend for pagination support.
- `app/db_projects.list_projects`: reuse and extend to support paginated queries.
- `static/js/app.js` project selector: keep existing list behavior intact.

Simple user flow:
1. Open the project management page.
2. Review the first 100 projects and move to another page using pagination controls.
3. Sort or archive a project and confirm the list remains paginated.

Success criteria:
- The management table renders a maximum of 100 projects per page with clear navigation.
- Users can navigate between pages without errors or broken state.
- Sorting and archive actions continue to behave correctly on paginated data.
- The dashboard project selector continues to list non-archived projects as before.
