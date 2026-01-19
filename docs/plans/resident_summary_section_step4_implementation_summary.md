## Stage 1 – Data model and DB access
- Changes: Added a resident summary column to the projects table, seeded default summaries, and exposed the summary field in project retrieval/creation plus a DB helper to update it.
- Verification: Not run (per instructions, manual verification should be done by running the app).
- Notes: Requires a new projects column on existing databases via the initialization migration helper.

## Stage 2 – API contracts and schemas
- Changes: Added a summary update schema and API endpoint for updating resident summaries.
- Verification: Not run (per instructions, manual verification should be done by running the app).
- Notes: Endpoint follows the existing resident text update pattern.

## Stage 3 – Dashboard layout placement
- Changes: Added the resident summary field to the header section alongside the resident selector.
- Verification: Not run (per instructions, manual verification should be done by running the app).
- Notes: Layout relies on existing field styles in the header.

## Stage 4 – Client-side data wiring
- Changes: Wired the summary field to load per resident, reset on empty state, and autosave via a new summary update request.
- Verification: Not run (per instructions, manual verification should be done by running the app).
- Notes: Autosave timing mirrors the questions field.
