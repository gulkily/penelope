## Stage 1 – Item ordering data model
- Changes: add `sort_order` to items, backfill existing rows, seed items with ordering, and order list queries by `sort_order` with new items appended at the end.
- Verification: Not run (please load a resident, confirm existing order, then add an item and ensure it appears last).
- Notes: Existing items with no ordering get backfilled per project/section based on current id order.

## Stage 2 – Reorder API surface
- Changes: add `ItemOrderUpdate`, expose `PUT /projects/{project_id}/items/order`, and store new per-section ordering with validation.
- Verification: Not run (please reorder a section via API and confirm `GET /api/projects/{id}` reflects the new order).
- Notes: The endpoint requires the full ordered list of item ids per section.

## Stage 3 – Reorder UI interactions
- Changes: add drag handles and move up/down controls in section items, wire pointer drag and keyboard arrow support, and persist new ordering from the UI.
- Verification: Not run (please drag items within a section, use Up/Down buttons or arrow keys on the handle, then refresh to confirm order persists).
- Notes: Reordering is blocked while any item in a section is in edit mode.

## Stage 4 – Styling and accessibility polish
- Changes: style drag handles and drag state, add touch-friendly handling, and include an `aria-live` announcer for reorder updates.
- Verification: Not run (please confirm handles are visible, focus rings appear, and reorder announcements are spoken by a screen reader).
- Notes: Move controls remain in the existing action strip to minimize visual clutter.
