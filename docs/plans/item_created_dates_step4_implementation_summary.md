## Stage 1 – Add created_at to item data payloads
- Changes: Ensured item queries and creation responses include `created_at`, with a safety backfill column check for existing databases.
- Verification: Not run here (manual verification needed in a running app).
- Notes: Existing rows missing `created_at` will return an empty string.

## Stage 2 – Render compact item dates in the dashboard
- Changes: Added compact date labels to list items with local formatting and minimal styling updates.
- Verification: Not run here (manual verification needed in a running app).
- Notes: Dates are omitted when missing or invalid.
