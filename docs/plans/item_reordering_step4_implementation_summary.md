## Stage 1 – Item ordering data model
- Changes: add `sort_order` to items, backfill existing rows, seed items with ordering, and order list queries by `sort_order` with new items appended at the end.
- Verification: Not run (please load a resident, confirm existing order, then add an item and ensure it appears last).
- Notes: Existing items with no ordering get backfilled per project/section based on current id order.
