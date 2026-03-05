## Stage 1 – Add created_at to item data payloads
- Changes: Ensured item queries and creation responses include `created_at`, with a safety backfill column check for existing databases.
- Verification: Not run here (manual verification needed in a running app).
- Notes: Existing rows missing `created_at` will return an empty string.

## Stage 2 – Render compact item dates in the dashboard
- Changes: Added compact date labels to list items with local formatting and minimal styling updates.
- Verification: Not run here (manual verification needed in a running app).
- Notes: Dates are omitted when missing or invalid.

## Stage 3 – Preserve dates through edit/delete/undo flows
- Changes: Extended item update responses to retain the original `created_at` value.
- Verification: Not run here (manual verification needed in a running app).
- Notes: Undo still re-adds items with a new timestamp, since it creates a new item record.

## Stage 4 – Include created_at in project section payloads
- Changes: Added `created_at` to the item data returned in project section payloads so the dashboard can render dates.
- Verification: Not run here (manual verification needed in a running app).
- Notes: This fixes missing dates in the UI for project loads.

## Stage 5 – Reposition item actions to avoid date spacing
- Changes: Moved item action buttons to the bottom-right with absolute positioning to remove reserved space beside the date pill.
- Verification: Not run here (manual verification needed in a running app).
- Notes: Hidden actions no longer affect layout.
