# North Star Unified Section - Step 2 Feature Description

Problem: The North Star objective and progress are separated in the dashboard, making it harder to scan and update the most important project context quickly.

User stories:
- As a project lead, I want the objective and progress together so that I can review North Star status at a glance.
- As a contributor, I want a single North Star area so that I can update the objective and progress in one place.
- As a stakeholder, I want a unified summary so that I can understand the target and progress in one view.

Core requirements:
- Combine the objective and progress into one dashboard section.
- Preserve the current ability to edit the objective and adjust progress.
- Keep the existing autosave behavior for objective and progress updates.
- Maintain responsive layout so the combined section works on desktop and mobile.
- Avoid saves when no project is selected.

Shared component inventory:
- Reuse the existing objective input and progress slider from `templates/index.html` in a single section.
- Continue using the existing project detail payload that includes `objective` and `progress`.
- Keep the current update endpoints for objective and progress as the write surfaces.
- Reuse the existing dashboard layout patterns and styling in `static/css/main.css`.

Simple user flow:
1. Open the North Star dashboard.
2. Select a project from the dropdown.
3. Review objective and progress together in the unified section.
4. Edit the objective and/or adjust progress.
5. Changes autosave and persist for the project.

Success criteria:
- Objective and progress appear together in a cohesive section.
- Editing either value persists without manual save actions.
- Reloading or reselecting the project shows the latest objective and progress.
- No errors occur when no project is selected.
