# Step 3: Development Plan

1. Stage 1: Add goal data to project storage and API payloads
   - Goal: Persist a numeric goal per project and expose it in project detail responses.
   - Dependencies: Existing project table, project detail API response.
   - Expected changes: Conceptually add a `goal` field to project storage with a default value (e.g., 100). Update `get_project`-style responses to include `goal`. Update project creation to seed the default goal. Add schema validation for goal updates.
   - Planned function signatures: `update_goal(project_id: int, goal: int) -> None` in project data layer; `update_goal(project_id: int, payload: GoalUpdate) -> dict` in API router.
   - Verification approach: Manual check that project detail payload includes goal and existing projects load with the default.
   - Risks/open questions: Should goal allow 0 or require >= 1? What should the default be to preserve existing percent semantics?
   - Canonical components/API contracts: Project detail API payload (dashboard uses it).

2. Stage 2: Add goal input and display to the dashboard UI
   - Goal: Let users view/edit the numeric goal alongside the objective and see progress in goal units.
   - Dependencies: Stage 1 goal field in API responses.
   - Expected changes: Add a goal input control to the dashboard card near the objective. Update the progress label to show units (e.g., "12 / 20") instead of only percent. Keep slider markers aligned with percent positions.
   - Verification approach: Manual check that the goal input populates from API data and the progress label shows goal units.
   - Risks/open questions: Desired label format (e.g., "12 of 20" vs "12 / 20") and whether to show percent alongside units.
   - Canonical components/API contracts: Dashboard progress slider and label.

3. Stage 3: Map slider behavior to goal units and persist goal updates
   - Goal: Make the slider max equal the goal and keep progress updates stored as percent under the hood.
   - Dependencies: Stage 1 API endpoint for goal updates; Stage 2 UI elements.
   - Expected changes: In client logic, compute percent = value/goal and use it for the slider fill while displaying value in units. Clamp progress on goal changes and refresh the slider range. Add debounced save for the goal input using the new API endpoint.
   - Planned function signatures: `scheduleGoalSave()` (client) and `PUT /api/projects/{project_id}/goal` request body with `{ goal: int }`.
   - Verification approach: Manual check that changing the goal adjusts slider max, progress stays within range, and refresh preserves both values.
   - Risks/open questions: Rounding behavior for percent mapping; behavior when the goal is reduced below current progress.
   - Canonical components/API contracts: Progress update API contract and dashboard slider behavior.

4. Stage 4: Update tests and docs touchpoints
   - Goal: Align automated checks and documentation with goal-based progress behavior.
   - Dependencies: Stages 1-3.
   - Expected changes: Update HTTP tests to assert goal in project payload and validate goal update behavior. Update E2E tests to reflect goal-based slider range and label display. Note any new defaults in docs if needed.
   - Verification approach: Run targeted HTTP and E2E tests against a running app.
   - Risks/open questions: Existing tests may assume percent labels; ensure test data uses a goal > 0.
   - Canonical components/API contracts: Project detail API payload; dashboard progress UI.
