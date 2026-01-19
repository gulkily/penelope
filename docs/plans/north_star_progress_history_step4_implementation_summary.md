## Stage 1 – Progress history storage and helpers
- Changes: Added the `progress_history` table and index during DB init, introduced history read/write helpers, exported new DB functions, and documented the table in the Postgres migration guide.
- Verification: Not run (requires running the app and confirming the table and helpers work).
- Notes: Uses UTC ISO timestamps for recorded history entries.
