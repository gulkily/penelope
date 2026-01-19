# Resident Progress Tracking - Step 2 Feature Description

Problem: The dashboard currently frames North Star progress by project, but the team needs progress tracked by resident. The experience should speak in resident terms without disrupting existing data or workflows.

User stories:
- As a program lead, I want to select a resident and see their objective and progress so that I can track individual outcomes.
- As a coordinator, I want to update a resident's progress and notes so that the dashboard reflects the latest status.
- As a stakeholder, I want the dashboard labels to reference residents so that reports align with how we operate.

Core requirements:
- The main dashboard selection and labels use resident terminology.
- Selecting a resident shows their objective, progress, section items, and questions.
- Updates to objective, progress, items, and questions continue to autosave as they do today.
- The management view supports creating, renaming, and archiving residents using resident labels.
- Existing records remain visible and intact under the resident framing.

Shared component inventory:
- Dashboard selector in `templates/index.html`: reuse the existing dropdown, relabel to residents.
- Objective input and progress slider in `templates/index.html`: reuse as the resident objective/progress editors.
- Section lists and inline-add controls in `templates/index.html`: reuse for resident summary, challenges, opportunities, and milestones.
- Questions textarea in `templates/index.html`: reuse for resident questions.
- Management view in `templates/manage_projects.html`: extend existing layout with resident terminology rather than building a new screen.
- Project API surfaces in `app/api.py`: reuse the existing list, detail, and update endpoints as the resident data surfaces.

Simple user flow:
1. Open the North Star dashboard.
2. Select a resident from the dropdown.
3. Review the resident's objective, progress, and sections.
4. Update progress or add items as needed.
5. Changes autosave and remain visible on reload.

Success criteria:
- User-facing labels reference residents in the dashboard and management view.
- Selecting a resident loads the correct data and updates persist across refresh.
- Section actions and questions behave the same way they do today.
- Existing data remains accessible under the resident framing.
