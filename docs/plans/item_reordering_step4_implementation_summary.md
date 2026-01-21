## Stage 1 – Item ordering data model
- Changes: add `sort_order` to items, backfill existing rows, seed items with ordering, and order list queries by `sort_order` with new items appended at the end.
- Verification: Not run (please load a resident, confirm existing order, then add an item and ensure it appears last).
- Notes: Existing items with no ordering get backfilled per project/section based on current id order.

## Stage 2 – Reorder API surface
- Changes: add `ItemOrderUpdate`, expose `PUT /projects/{project_id}/items/order`, and store new per-section ordering with validation.
- Verification: Not run (please reorder a section via API and confirm `GET /api/projects/{id}` reflects the new order).
- Notes: The endpoint requires the full ordered list of item ids per section.
