# North Star Progress Confetti - Step 3 Development Plan

1. Confetti module scaffold
   - Goal: Define a small, reusable JS component for triggering the confetti burst.
   - Dependencies: None.
   - Expected changes: Add `static/js/confetti.js` with a minimal public API (e.g., `initConfetti(options)` and `triggerConfetti()`), plus reduced-motion detection logic.
   - Verification: Load the page and confirm the module initializes without console errors.
   - Risks/open questions: Confirm the preferred API shape (single init + trigger) keeps integration simple.
   - Canonical components/API touched: Frontend JS module layer (new file; no backend).

2. Visual layer + styling
   - Goal: Add the lightweight visual layer that the module controls.
   - Dependencies: Stage 1 (module API).
   - Expected changes: Extend `templates/index.html` with a confetti container element; add styles/animations in `static/css/main.css` scoped to the container and honoring reduced-motion.
   - Verification: Trigger confetti via console call to ensure it renders and clears without blocking slider interaction.
   - Risks/open questions: Ensure animations remain performant and unobtrusive across devices.
   - Canonical components/API touched: Dashboard markup and styles; no database changes.

3. Progress increase detection
   - Goal: Trigger confetti only on positive progress updates.
   - Dependencies: Stages 1–2.
   - Expected changes: Update `static/js/app.js` to track prior progress and call `triggerConfetti()` only when the current project's progress increases (excluding initial load).
   - Planned signature reference: `triggerConfetti(): void` (or `triggerConfetti({ intensity?: number }): void` if needed).
   - Verification: Move slider up/down and confirm confetti only on increases; reload page and confirm no confetti on initial render.
   - Risks/open questions: Avoid false positives when goal changes or when switching projects.
   - Canonical components/API touched: Progress slider handling and progress display logic; existing progress API stays unchanged.

4. Final smoke check
   - Goal: Ensure the flow feels correct and remains non-blocking.
   - Dependencies: Stages 1–3.
   - Expected changes: No new code unless minor tweaks are needed.
   - Verification: Manual smoke test of progress updates (increase, decrease, unchanged) plus reduced-motion behavior.
   - Risks/open questions: Confirm reduced-motion handling is acceptable and consistent with other animations.
   - Canonical components/API touched: None beyond prior stages.
