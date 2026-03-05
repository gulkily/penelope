# North Star Objective Autosave - Step 2 Feature Description

Problem: Editing the North Star objective requires a manual save, which breaks the autosave pattern used elsewhere and can leave changes unsaved.

User stories:
- As a project lead, I want objective edits to save automatically so that I do not lose changes when I move away.
- As a contributor, I want the objective to persist without a separate save step so that updates feel consistent with the rest of the dashboard.
- As a stakeholder, I want the latest objective to appear after refresh so that I trust the dashboard as the source of truth.

Core requirements:
- Save objective edits automatically after the user updates the field.
- Remove the dedicated "Save objective" button from the dashboard UI.
- Preserve the existing objective display and editing location on the dashboard.
- Persist objective changes per project with the current project data flow.
- Do not autosave when no project is selected.

Shared component inventory:
- Dashboard objective field (`templates/index.html`) reuses the existing input and removes the save action; no new UI surface.
- Project detail API (`GET /api/projects/{project_id}`) already returns `objective`; continue using it to populate the field.
- Objective update API (`PUT /api/projects/{project_id}/objective`) remains the single write endpoint for autosave.
- Existing autosave behavior for progress and questions in `static/js/app.js` provides the canonical autosave interaction to extend.

Simple user flow:
1. Open the North Star dashboard and select a project.
2. Review the current objective in the objective field.
3. Edit the objective text.
4. Pause typing; the objective saves automatically.
5. Refresh or reselect the project and see the updated objective.

Success criteria:
- Objective edits persist without clicking a save button.
- The "Save objective" button no longer appears in the dashboard.
- Selecting or reloading a project shows the latest saved objective.
- Autosave does not fire when no project is selected.
