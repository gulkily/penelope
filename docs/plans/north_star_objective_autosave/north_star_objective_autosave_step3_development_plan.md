# North Star Objective Autosave - Step 3 Development Plan

1. Update dashboard UI for objective editing
   - Goal: Remove the manual save affordance so the objective relies on autosave only.
   - Dependencies: Existing dashboard template in `templates/index.html`.
   - Expected changes: Remove the "Save objective" button markup and any related hooks; keep the objective input unchanged.
   - Verification: Load the dashboard and confirm the button no longer renders.
   - Risks/open questions: None.
   - Shared components/API contracts touched: Objective input in `templates/index.html`.

2. Add objective autosave behavior in the dashboard script
   - Goal: Persist objective edits automatically after a short idle period.
   - Dependencies: Existing autosave patterns for progress/questions in `static/js/app.js` and `PUT /api/projects/{project_id}/objective`.
   - Expected changes: Replace the click handler with an input-based timer (e.g., `scheduleObjectiveSave`), add/clear a new timer in state, and keep the objective update request payload the same.
   - Verification: Edit the objective, pause typing, then refresh/reselect the project to confirm the value persisted.
   - Risks/open questions: Ensure autosave does not fire when no project is selected.
   - Shared components/API contracts touched: `static/js/app.js` autosave flow, objective update endpoint.

3. Align interactivity toggles with the removed button
   - Goal: Ensure the UI enable/disable flow reflects the absence of the save button.
   - Dependencies: `setInteractivity` and related state management in `static/js/app.js`.
   - Expected changes: Remove objective save button references in `setInteractivity` and DOM lookups; keep objective input enabling intact.
   - Verification: Switch between no project and a selected project and confirm the objective field toggles correctly without errors.
   - Risks/open questions: Watch for null references after removing the button.
   - Shared components/API contracts touched: `static/js/app.js` interactivity helpers.
