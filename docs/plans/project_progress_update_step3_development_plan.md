# Project Progress Update - Step 3 Development Plan

1. Stage 1 - Extend data layer and API for progress updates
   - Goal: Allow progress to be updated per project in the backend.
   - Dependencies: Existing SQLite projects table and API.
   - Expected changes: Add DB helper to update progress; add `PUT /api/projects/{project_id}/progress` route; add request schema for progress.
   - Planned signatures: `PUT /api/projects/{project_id}/progress`.
   - Verification: Manually call the endpoint and re-fetch the project.
   - Risks/open questions: Validate progress bounds (0–100) and rounding behavior.
   - Shared components/API contracts: Reuse project detail payload with updated `progress`.

2. Stage 2 - Add integrated progress slider UI and value display
   - Goal: Provide an admin-facing slider integrated with the progress bar so the control and display are unified.
   - Dependencies: Stage 1.
   - Expected changes: Replace or overlay the existing progress bar with a slider track; display current value alongside the control.
   - Verification: Load the dashboard and confirm the slider reflects the selected project’s progress.
   - Risks/open questions: Ensure the slider styling preserves the existing progress bar visual intent.
   - Shared components/API contracts: Reuse existing progress display and project selection flow.

3. Stage 3 - Wire slider to immediate backend update
   - Goal: Persist slider changes immediately and refresh UI.
   - Dependencies: Stages 1–2.
   - Expected changes: Add JS handler to send updates on slider change/input; update progress bar immediately without a separate save action.
   - Verification: Adjust slider, refresh, and confirm persistence.
   - Risks/open questions: Consider debouncing to avoid excessive updates.
   - Shared components/API contracts: Use new progress update endpoint.

4. Stage 4 - Styling and UX polish
   - Goal: Align the slider UI with existing dashboard styling.
   - Dependencies: Stage 2.
   - Expected changes: Add CSS for slider, value badge, and layout spacing.
   - Verification: Visual check on desktop and mobile widths.
   - Risks/open questions: Ensure slider remains accessible and readable.
   - Shared components/API contracts: None.
