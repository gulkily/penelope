## Stage 1 – Add created_at to item data payloads
- Changes: Ensured item queries and creation responses include `created_at`, with a safety backfill column check for existing databases.
- Verification: Not run here (manual verification needed in a running app).
- Notes: Existing rows missing `created_at` will return an empty string.
