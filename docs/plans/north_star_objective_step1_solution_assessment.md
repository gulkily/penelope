# North Star Objective - Step 1 Solution Assessment

Problem statement: Decide how to store and surface a single North Star objective per project in the existing dashboard.

Option A - Add a dedicated "objective" field on the project
- Pros: Clear source of truth, simple read/write, aligns with "one objective per project".
- Cons: Requires a schema change and backfill for existing projects.

Option B - Store objectives in a separate table (one-to-one with projects)
- Pros: Keeps projects table lean, can extend later (history/audit).
- Cons: More joins and code paths for a simple single-field need.

Option C - Encode objective as a special item in existing sections
- Pros: No schema change, reuses existing item flow.
- Cons: Semantics are muddy, harder to enforce uniqueness, and UI becomes less explicit.

Recommendation: Option A. A dedicated project field keeps intent clear and supports a concise UI without overengineering.
