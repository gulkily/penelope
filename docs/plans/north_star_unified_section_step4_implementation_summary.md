## Stage 1 – Unify objective and progress markup
- Changes: Moved the progress slider block into the objective section so both render together.
- Verification: Manual smoke test suggested (load dashboard and confirm objective + progress appear in one section; not run here).
- Notes: None.

## Stage 2 – Align unified section styling
- Changes: Adjusted the objective section layout styles to keep the combined content grouped in one area.
- Verification: Manual smoke test suggested (resize the dashboard and confirm the objective + progress block wraps cleanly; not run here).
- Notes: None.

## Stage 3 – Confirm interaction wiring
- Changes: No code changes; verified DOM lookup assumptions remain valid after the layout move.
- Verification: Manual smoke test suggested (select a project, adjust progress, edit objective, and confirm autosave without console errors; not run here).
- Notes: None.
