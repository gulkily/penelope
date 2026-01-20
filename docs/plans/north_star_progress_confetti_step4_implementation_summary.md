## Stage 1 – Confetti module scaffold
- Changes: Added `static/js/confetti.js` with a small init + trigger API, reduced-motion detection, and cooldown-controlled bursts.
- Verification: Not run (needs manual browser load to confirm module initializes without console errors).
- Notes: Uses a global `window.NorthStarConfetti` to integrate with existing non-module scripts.

## Stage 2 – Visual layer + styling
- Changes: Added a confetti layer container in `templates/index.html`, loaded `static/js/confetti.js`, and introduced confetti styles/animation in `static/css/main.css`.
- Verification: Not run (needs manual browser load to confirm visuals render and do not block the slider).
- Notes: Confetti layer uses `pointer-events: none` and sits above the progress slider.

## Stage 3 – Progress increase detection
- Changes: Updated `static/js/app.js` to compare previous vs. new progress values and trigger the confetti module on positive moves.
- Verification: Not run (needs manual slider interaction to confirm confetti triggers only on increases).
- Notes: Confetti triggers only from slider input events, avoiding initial-load and goal-change noise.

## Stage 4 – Final smoke check
- Changes: No additional code changes.
- Verification: Not run (needs manual verification of increase/decrease behavior and reduced-motion handling).
- Notes: Ready for UI smoke testing on a running server.

## Stage 5 – Confetti init fallback
- Changes: Hardened `static/js/confetti.js` to lazily resolve the confetti layer and refresh reduced-motion state on each trigger.
- Verification: Not run (needs manual trigger to confirm confetti pieces appear).
- Notes: Addresses cases where the module initializes before the layer is available.

## Stage 6 – Confetti debug page
- Changes: Added `/debug/confetti` with `templates/confetti_debug.html`, diagnostics script `static/js/confetti-debug.js`, and supporting styles in `static/css/main.css`.
- Verification: Not run (manual load needed to confirm diagnostics populate and trigger works).
- Notes: Debug page includes a sandbox area and quick checks for reduced-motion, module load, and DOM piece count.

## Stage 7 – Show evaluated expressions
- Changes: Displayed the actual JS statements for each debug row in `templates/confetti_debug.html` and styled inline code in `static/css/main.css` for readability.
- Verification: Not run (manual page load needed to confirm expressions render and diagnostics still update).
- Notes: Expressions now match the console checks used during debugging.

## Stage 8 – Force confetti in debug
- Changes: Added a debug-only button that triggers confetti even when reduced-motion is true, plus an optional `force` flag on `triggerConfetti` in `static/js/confetti.js`.
- Verification: Not run (manual click needed on `/debug/confetti`).
- Notes: Force flag is used only in the debug page.

## Stage 9 – Legacy browser compatibility
- Changes: Removed optional chaining from `static/js/app.js` and `static/js/confetti-debug.js`, and updated debug page expressions in `templates/confetti_debug.html`.
- Verification: Not run (manual check in Waterfox Classic recommended).
- Notes: Avoids parse errors in older JS engines.

## Stage 10 – Full-page confetti overlay
- Changes: Moved the confetti layer to a page-level overlay on the main dashboard and scoped sandbox usage to the debug page via new layer classes in `static/css/main.css`.
- Verification: Not run (manual page reload needed to confirm confetti appears across the full viewport).
- Notes: Keeps the debug sandbox confined while allowing full-page coverage on `/`.

## Stage 11 – Full-height confetti fall
- Changes: Sized confetti drop distance based on the active layer height in `static/js/confetti.js` so particles fall through the full viewport.
- Verification: Not run (manual trigger needed to confirm full-page coverage).
- Notes: Drop distance now scales with viewport height.

## Stage 12 – Longer confetti duration
- Changes: Extended the default confetti duration to 7000ms in `static/js/confetti.js`.
- Verification: Not run (manual trigger needed to confirm timing).
- Notes: Animation now runs longer to create a slower, lingering effect.

## Stage 13 – Increased confetti density
- Changes: Increased default confetti piece count to 360 (15x) in `static/js/confetti.js`.
- Verification: Not run (manual trigger needed to confirm density and performance).
- Notes: Higher density may impact older devices; monitor performance.
