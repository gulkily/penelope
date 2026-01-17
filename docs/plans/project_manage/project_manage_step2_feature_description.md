# Project Management (Add/Archive) - Step 2 Feature Description

Problem: Users need a dedicated management page to add new projects and archive existing ones without cluttering the main dashboard.

User stories:
- As a user, I want to add a new project so that it appears in the dashboard selector.
- As a user, I want to mark projects as archived so that inactive work is hidden from daily views.
- As a user, I want to click a project in the management table to jump to its dashboard details.

Core requirements:
- Provide a separate management page with a table of all projects.
- Each row includes an archive checkbox to toggle archived state.
- Include an add project form on the same page.
- Project names link to the main dashboard with the project preselected.
- Archived projects are clearly indicated in the table.

Shared component inventory:
- Reuse the project list API used by the dashboard selector.
- Reuse the project selection URL pattern (`?project=`) for table links.
- Extend the project data to include an archived state.

Simple user flow:
1. Open the Project Management page.
2. Add a new project via the form.
3. Toggle the archive checkbox for an old project.
4. Click a project name to open its dashboard view.

Success criteria:
- New projects appear in the dashboard selector after creation.
- Archive toggles persist and are reflected in the management table.
- Project links open the dashboard with the correct project selected.
