# Resident Progress Tracking - Step 1 Solution Assessment

Problem statement: Shift progress tracking from project-centered to resident-centered while keeping the dashboard usable and minimizing disruption.

Option A - Re-label projects as residents (reuse existing project model and progress fields)
- Pros: No schema changes; minimal code/UI changes; keeps existing CRUD flows.
- Cons: Loses ability to track projects separately; existing project data semantics change; may require data relabeling.

Option B - Add a resident entity with its own progress, keep projects intact
- Pros: Correct domain model; supports future project tracking; clearer separation of concerns.
- Cons: Requires schema changes/migration; more API/UI updates; more tests to update.

Option C - Derive resident progress from items tagged with resident (lightweight mapping)
- Pros: Avoids a new progress table; keeps project data mostly intact.
- Cons: Adds aggregation complexity; indirect updates; risk of inconsistent progress.

Recommendation: Option A. It delivers the resident-based view fastest with minimal schema changes, aligning with the guardrail to avoid migrations unless required. If stakeholders need both resident and project tracking, revisit Option B.
