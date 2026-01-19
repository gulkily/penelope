## Stage 1 – Data model and DB access
- Changes: Added a resident summary column to the projects table, seeded default summaries, and exposed the summary field in project retrieval/creation plus a DB helper to update it.
- Verification: Not run (per instructions, manual verification should be done by running the app).
- Notes: Requires a new projects column on existing databases via the initialization migration helper.
