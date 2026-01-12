## Stage 1 – Remove objective save button
- Changes: Removed the "Save objective" button from the dashboard objective section.
- Verification: Manual smoke test suggested (open dashboard and confirm the button is gone; not run here).
- Notes: None.

## Stage 2 – Add objective autosave
- Changes: Added an objective autosave timer and input listener to persist edits via the existing objective endpoint.
- Verification: Manual smoke test suggested (edit objective, pause typing, refresh to confirm persistence; not run here).
- Notes: Autosave skips when no project is selected.

## Stage 3 – Clean up objective save references
- Changes: Removed the unused objective save button hooks and handler from the dashboard script.
- Verification: Manual smoke test suggested (load the dashboard and confirm no console errors while editing the objective; not run here).
- Notes: None.
