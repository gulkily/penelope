# Add Update Confetti Trigger - Step 3 Development Plan

1. Stage 1 - Remove slider-based confetti trigger
   - Goal: Stop celebrating North Star slider increases.
   - Dependencies: Existing slider input/save flow in `static/js/app.js`.
   - Expected changes: Update progress slider input handling to remove `NorthStarConfetti.triggerConfetti()` calls while preserving display updates and progress persistence timing.
   - Verification approach: Move the slider up/down and confirm no confetti appears while progress still saves normally.
   - Risks or open questions:
     - Ensure no regressions in progress display updates.
   - Canonical components/API contracts touched: Reuse existing progress slider UI and `PUT /api/projects/{id}/progress` contract with no payload changes.

2. Stage 2 - Add Add update success confetti trigger
   - Goal: Fire confetti once when `Apply selected updates` completes successfully.
   - Dependencies: Existing transcript apply orchestration (`applyTranscriptUpdates`) and confetti module API.
   - Expected changes: Extend the transcript apply success path to invoke the confetti trigger after all selected updates finish and before dialog teardown.
   - Planned function signature reference: `triggerConfetti(options?: { force?: boolean }): void` (reuse current global confetti API).
   - Verification approach: Apply selected updates with at least one selected change and confirm exactly one confetti animation plays.
   - Risks or open questions:
     - Confirm trigger placement does not get skipped by early returns.
     - Ensure one burst only, even when multiple update requests are part of one apply action.
   - Canonical components/API contracts touched: Reuse Add update dialog action and existing update endpoints (`/summary`, `/questions`, `/objective`, `/goal`, `/progress`, `/items`) without backend changes.

3. Stage 3 - Guardrail handling for no-op and failure paths
   - Goal: Ensure confetti only represents successful apply outcomes.
   - Dependencies: Stage 2.
   - Expected changes: Keep confetti out of validation/no-selection branches and catch/failure branches; confirm behavior remains tied only to successful completion.
   - Verification approach: Attempt apply with no selected updates and with a simulated failure path; confirm no confetti appears.
   - Risks or open questions:
     - Need a reliable local way to exercise failure without adding test-only code.
   - Canonical components/API contracts touched: Transcript status/error flow in `static/js/app.js`; no API changes.

4. Stage 4 - Smoke coverage update
   - Goal: Protect the new trigger behavior from regression.
   - Dependencies: Stages 1-3.
   - Expected changes: Add or update frontend test coverage to assert slider changes do not trigger confetti and successful Add update apply triggers one confetti call.
   - Verification approach: Run focused automated tests plus a quick manual smoke pass of Add update and slider interactions.
   - Risks or open questions:
     - Existing tests may need lightweight stubbing for global confetti calls.
   - Canonical components/API contracts touched: Existing frontend test surfaces for dashboard and Add update flows; no database or API contract changes.
