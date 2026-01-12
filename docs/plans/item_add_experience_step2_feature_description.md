# Item Add Experience - Step 2 Feature Description

Problem: Adding list items currently uses a prompt dialog, which interrupts flow and feels dated.

User stories:
- As a project mentor, I want to add items inline so that I can capture updates without leaving context.
- As a contributor, I want add controls to be clear and easy to use with keyboard or mouse.
- As a team member, I want the add and edit textboxes to expand so that longer updates are readable.

Core requirements:
- Replace prompt dialogs with inline add rows inside each section card.
- Inline add inputs are always visible and support keyboard submission.
- Edit inputs should use the same expandable behavior as add inputs.
- Adding an item persists and refreshes the list immediately.
- Use the existing FastAPI + vanilla frontend stack (no new frameworks).

Shared component inventory:
- Reuse existing section cards and list rendering.
- Reuse the item creation API (`POST /api/projects/{project_id}/items`).
- Reuse the inline edit flow for items and extend it with expandable inputs.

Simple user flow:
1. Select a project.
2. Type a new item into the inline add input within a section.
3. Press Enter or click Add to submit.
4. See the new item appear immediately.
5. Edit an item; the input expands to show the full text.

Success criteria:
- Users can add items without a modal prompt.
- Inline add controls work with keyboard and mouse.
- Add and edit inputs expand for longer text.
- Items persist after refresh or reselect.
