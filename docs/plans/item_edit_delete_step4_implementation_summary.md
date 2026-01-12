## Stage 1 - Extend backend API for item update and delete
- Changes: Added item update/delete helpers, request schema, and API endpoints.
- Verification: Not run yet; please `PUT /api/items/{id}` and `DELETE /api/items/{id}` to confirm persistence.
- Notes: Update returns the edited item payload.

## Stage 2 - Add list item action affordances with keyboard access
- Changes: Added edit/delete action buttons per item and ensured actions appear on hover or focus-within.
- Verification: Not run yet; please tab through list items and confirm action buttons appear.
- Notes: Actions are focusable without mouse input.

## Stage 3 - Implement inline edit flow
- Changes: Added inline edit mode with save/cancel actions and input focus handling.
- Verification: Not run yet; please edit an item, save, and refresh to confirm persistence.
- Notes: Cancel restores the original value without API calls.

## Stage 4 - Implement delete flow with confirmation
- Changes: Added delete action and refresh after removal.
- Verification: Not run yet; please delete an item and confirm it no longer appears after refresh.
- Notes: No confirmation dialog; deletion is immediate.

## Stage 5 - Styling and UX polish
- Changes: Styled action buttons, editing state, and input field to fit the card layout.
- Verification: Not run yet; please check hover/focus visibility and edit styling on desktop and mobile widths.
- Notes: Hover and keyboard focus reveal the same affordances.

## Stage 6 - Keyboard save/cancel shortcuts
- Changes: Enter saves and Escape cancels while editing an item.
- Verification: Not run yet; please edit an item and press Enter/Escape to confirm behavior.
- Notes: Uses event delegation on the inline input.

## Stage 7 - Add undo for deletes
- Changes: Added an undo toast that re-adds the deleted item within a short window.
- Verification: Not run yet; please delete an item, click Undo, and confirm the item returns.
- Notes: Undo restores the item text and section; a new item ID is created.
