# Item Edit/Delete - Step 3 Development Plan

1. Stage 1 - Extend backend API for item update and delete
   - Goal: Support editing and deleting items in the data layer.
   - Dependencies: Existing SQLite items table and API router.
   - Expected changes: Add DB helpers for update/delete; add `PUT /api/items/{item_id}` and `DELETE /api/items/{item_id}` endpoints; add request schema for item updates.
   - Planned signatures: `PUT /api/items/{item_id}`, `DELETE /api/items/{item_id}`.
   - Verification: Manually call update/delete endpoints and re-fetch the project items.
   - Risks/open questions: Ensure item IDs are scoped correctly to projects.
   - Shared components/API contracts: Reuse item payload shape (`id`, `section`, `text`).

2. Stage 2 - Add list item action affordances with keyboard access
   - Goal: Provide edit/delete controls that appear on hover and focus.
   - Dependencies: Stage 1 for API availability.
   - Expected changes: Update list item markup to include action buttons; ensure buttons are focusable and visible on `:focus-within`.
   - Verification: Tab through items and confirm controls appear and are usable.
   - Risks/open questions: Avoid clutter in dense lists.
   - Shared components/API contracts: Reuse list rendering with added action controls.

3. Stage 3 - Implement inline edit flow
   - Goal: Allow mentors to edit item text inline and save changes.
   - Dependencies: Stages 1–2.
   - Expected changes: Add JS to toggle edit mode, save updates, and refresh list.
   - Verification: Edit an item, save, refresh, and confirm persistence.
   - Risks/open questions: Decide on cancel behavior and validation.
   - Shared components/API contracts: Use item update endpoint.

4. Stage 4 - Implement delete flow with confirmation
   - Goal: Allow mentors to delete items safely.
   - Dependencies: Stage 1–2.
   - Expected changes: Add JS to confirm delete (e.g., confirm dialog) and refresh list.
   - Verification: Delete an item and confirm it is removed after refresh.
   - Risks/open questions: Confirm UX for accidental deletions.
   - Shared components/API contracts: Use item delete endpoint.

5. Stage 5 - Styling and UX polish
   - Goal: Keep actions subtle but discoverable.
   - Dependencies: Stages 2–4.
   - Expected changes: Add CSS for action buttons, hover/focus visibility, and edit state.
   - Verification: Visual check on desktop and mobile widths; keyboard focus highlights visible.
   - Risks/open questions: Ensure hover-only affordances have keyboard equivalents.
   - Shared components/API contracts: None.
