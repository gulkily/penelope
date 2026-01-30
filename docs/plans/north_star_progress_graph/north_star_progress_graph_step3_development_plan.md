# North Star Progress Graph - Step 3 Development Plan

1. Add residency date bounds to resident data
- Goal: Store per-resident residency start and end dates with safe defaults (Jan 1 / Jan 31).
- Dependencies: Existing SQLite initialization and project data access.
- Expected changes: Conceptually add `residency_start_date` and `residency_end_date` fields to resident storage with defaults; update project detail payload to include the bounds; update seed data to include defaults; update DB init migration helper to add fields for existing databases.
- Planned signatures: `update_residency_dates(project_id: int, start: str, end: str) -> None` (if updates are needed later).
- Verification approach: Load a resident and confirm the payload includes the default bounds.
- Risks/open questions: Confirm date format (UTC ISO date string) and future edit UI requirements.
- Shared components/API contracts: Project detail API response, DB initialization/migration logic.

2. Add expandable graph shell in the Objective section
- Goal: Provide a collapsible container that can show or hide the progress graph.
- Dependencies: Objective card markup and existing CSS patterns.
- Expected changes: Extend the Objective card in `templates/index.html` with a toggle control and graph container; add minimal CSS for expanded/collapsed states; no data wiring yet.
- Verification approach: Load the dashboard, toggle the graph visibility, and confirm layout stability.
- Risks/open questions: Ensure accessibility for the expand/collapse control (labels, focus).
- Shared components/API contracts: Objective card layout and existing form controls.

3. Render progress history into the graph with residency bounds
- Goal: Visualize progress history within the resident's configured residency start/end dates.
- Dependencies: Stage 1 bounds in the project payload and existing progress history API.
- Expected changes: Fetch progress history for the selected resident; filter series to the configured residency bounds; render the graph into the Objective section using the existing UI stack (no new framework).
- Planned signatures: `GET /api/projects/{project_id}/progress/history` (existing) plus client-side render helpers.
- Verification approach: Update progress multiple times, expand the graph, and confirm points render within the bounds.
- Risks/open questions: Decide on empty-state behavior when no history exists in the date range.
- Shared components/API contracts: Progress history API, Objective card graph container, project detail payload.

4. Add minimal copy/empty states for the graph
- Goal: Ensure the graph communicates clearly when data is missing or unavailable.
- Dependencies: Stage 2 container and Stage 3 data wiring.
- Expected changes: Add a short empty-state message in the graph container when there is no history to show.
- Verification approach: Select a resident with no updates and confirm the empty state is shown.
- Risks/open questions: Keep copy concise to avoid cluttering the Objective card.
- Shared components/API contracts: Objective card UI.
