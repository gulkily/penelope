## Stage 1 - Extend data model for archived state
- Changes: Added archived flag to projects, added DB helpers in a split data layer to keep modules small, and seeded archived defaults.
- Verification: Not run yet; please start the server and confirm project payloads include `archived`.
- Notes: Existing records default to archived=false.
