# Item Edit/Delete - Step 2 Feature Description

Problem: Mentors need a way to edit and remove list items so project updates stay accurate and current without re-adding entries.

User stories:
- As a project mentor, I want to edit an item so that I can correct or refine updates.
- As a project mentor, I want to delete an item so that outdated or incorrect updates are removed.
- As a team member, I want changes to appear immediately so that the list reflects the latest status.

Core requirements:
- Provide edit and delete actions for items in Summary, Challenges, Opportunities, and Milestones.
- Actions are discoverable on hover and accessible via keyboard focus.
- Edits persist per project and update the UI immediately.
- Deletes remove items from the UI and persistence layer.
- Use the existing FastAPI + vanilla frontend stack (no new frameworks).

Shared component inventory:
- Reuse the existing section list rendering and project selection flow.
- Extend the item API to support update and delete operations.
- Reuse the list item markup; add action affordances without creating new pages.

Simple user flow:
1. Open the North Star dashboard and select a project.
2. Hover or focus a list item to reveal actions.
3. Choose edit, update the text, and save.
4. Choose delete and confirm removal.
5. See the list update immediately.

Success criteria:
- Items can be edited and deleted using both mouse and keyboard.
- Updated items persist after refresh or reselect.
- Deleted items no longer appear in the list or API responses.
