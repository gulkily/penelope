## Stage 1 - Extend data layer and API for progress updates
- Changes: Added progress update schema, API endpoint, and data layer helper to persist progress updates.
- Verification: Not run yet; please start the server and `PUT /api/projects/{id}/progress` to confirm updates persist.
- Notes: Progress validation enforces 0-100 bounds via the request schema.

## Stage 2 - Add integrated progress slider UI and value display
- Changes: Replaced the static progress bar with a slider control and wired it to display the current percentage.
- Verification: Not run yet; please load the dashboard and confirm the slider reflects the selected project’s progress.
- Notes: Slider is disabled until a project is selected.

## Stage 3 - Wire slider to immediate backend update
- Changes: Added slider input handling with a short debounce to persist progress updates immediately while dragging.
- Verification: Not run yet; please move the slider and reselect the project to confirm persistence.
- Notes: Updates use the new progress endpoint without a separate save action.
