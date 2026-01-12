# Project URL State - Step 2 Feature Description

Problem: Users need shareable links that reflect the selected project, and selection should persist across reloads.

User stories:
- As a user, I want the URL to include the selected project so that I can share the view.
- As a user, I want the selected project to remain selected after reload so that I can continue where I left off.
- As a teammate, I want the link to open directly to the intended project so that reviews are efficient.

Core requirements:
- Encode the selected project ID in the URL (query string).
- On page load, preselect the project based on the URL if present.
- Update the URL when the selection changes.
- Invalid or missing project IDs should fall back to the empty state.
- Use the existing FastAPI + vanilla frontend stack (no new frameworks).

Shared component inventory:
- Reuse the existing project selector and data-fetch flow.
- Reuse the project detail API (`GET /api/projects/{project_id}`).
- No new pages or server routes required.

Simple user flow:
1. Open the dashboard with no query param; see the empty state.
2. Select a project; the URL updates with `?project={id}`.
3. Share or reload the URL.
4. The page loads with the same project selected.

Success criteria:
- The URL updates immediately when selection changes.
- Reloading a URL with a valid project parameter auto-selects it.
- Invalid project parameters do not break the UI and fall back to empty state.
