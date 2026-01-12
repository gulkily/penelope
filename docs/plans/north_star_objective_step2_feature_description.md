# North Star Objective - Step 2 Feature Description

Problem: Project teams need to define and view a single, explicit North Star objective per project to keep progress aligned with a clear target.

User stories:
- As a project lead, I want to set a North Star objective so that the team shares a clear outcome to aim for.
- As a contributor, I want to see the current objective while reviewing progress so that my updates stay aligned.
- As a stakeholder, I want to view the objective alongside status details so that I can quickly understand what success means.

Core requirements:
- Allow a single objective to be saved per project.
- Display the objective prominently in the dashboard when a project is selected.
- Keep the objective editable for authorized users (same scope as current add-item interactions).
- Persist the objective per project so it remains across sessions.
- Use the existing FastAPI + vanilla frontend stack (no new frameworks).

Shared component inventory:
- Reuse the existing project selector and project detail loading flow.
- Extend the current project detail API payload to include the objective.
- Reuse the dashboard layout area for a new objective display; no separate new page.

Simple user flow:
1. Open the North Star dashboard.
2. Select a project from the dropdown.
3. Review the current objective near the top of the dashboard.
4. Update the objective and save changes.
5. Confirm the new objective appears on refresh or reselect.

Success criteria:
- Selecting a project shows its saved objective immediately.
- Updating the objective persists and is visible on subsequent loads.
- The objective is visually clear and does not conflict with existing sections.
