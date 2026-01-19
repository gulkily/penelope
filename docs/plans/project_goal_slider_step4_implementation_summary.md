## Stage 1 – Add goal storage and API support
- Changes: Added project goal persistence, defaults, and API support for reading/updating goals.
- Verification: Manual review of updated data/API wiring (no runtime checks).
- Notes: Added a new goal column with a default value for existing projects.

## Stage 2 – Add goal input and progress display placeholders
- Changes: Added a goal input field and updated the progress label placeholder in the dashboard template.
- Verification: Manual review of template changes (no runtime checks).
- Notes: Interactive behavior is handled in the next stage.

## Stage 3 – Map slider to goal units and persist goal updates
- Changes: Added goal-aware slider logic, percent-to-units mapping, and goal auto-save handling in the dashboard client.
- Verification: Manual review of updated client logic (no runtime checks).
- Notes: Progress remains stored as percent while the UI shows goal units.
