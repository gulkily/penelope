# Resident Summary Section - Step 3 Development Plan

1) Data model and DB access
- Goal: Add a per-resident summary field to persisted project data.
- Dependencies: None.
- Expected changes: Extend the projects schema with a summary field and default; ensure migrations cover existing DBs; update project seed data; include summary in `get_project` output; update `create_project` defaults; add DB helper signature `update_summary(project_id: int, summary: str) -> None`.
- Verification: Create or select a resident and confirm the summary field loads (empty by default) and appears in the project payload.
- Risks/open questions: Any existing DBs missing the new column; confirm default empty summary behavior is acceptable.
- Canonical components touched: Projects table schema; resident detail payload shape returned by the existing project endpoint.

2) API contracts and schemas
- Goal: Expose summary read/write via existing resident APIs.
- Dependencies: Stage 1.
- Expected changes: Add a request schema for summary updates (e.g., `SummaryUpdate`); add a PUT endpoint for resident summary updates; export the new DB helper via the db module.
- Verification: Manual API call updates summary for a resident and returns the updated value.
- Risks/open questions: Confirm endpoint naming aligns with existing questions/objective patterns.
- Canonical components touched: Resident detail API payload; Questions update interaction pattern for text fields.

3) Dashboard layout placement
- Goal: Place the summary field in the same header section as the resident selector.
- Dependencies: Stage 2 for field name/contract consistency.
- Expected changes: Add a summary text area and label to the resident selector header section; reuse existing field styles and spacing tokens.
- Verification: Load the dashboard and confirm the summary field is visible and aligned with the resident selector.
- Risks/open questions: Header density on smaller screens; may need minor spacing tweaks.
- Canonical components touched: Resident selector header layout; shared field input styling.

4) Client-side data wiring
- Goal: Load and save summary text per resident.
- Dependencies: Stages 2–3.
- Expected changes: Populate the summary field when a resident loads; add autosave behavior that mirrors Questions editing; ensure summary clears when no resident is selected.
- Verification: Edit summary, switch residents, and confirm the text persists and reloads correctly.
- Risks/open questions: Autosave timing vs. request volume; ensure no conflicts with questions autosave.
- Canonical components touched: Resident detail fetch flow; Questions autosave behavior and UX.

5) Tests and documentation touch-ups
- Goal: Keep coverage in line with new summary behavior.
- Dependencies: Stages 1–4.
- Expected changes: Update HTTP or E2E tests to assert summary persistence; adjust any fixtures or data factories for the new field.
- Verification: Run focused tests for resident detail updates and confirm they pass.
- Risks/open questions: Existing tests that assert exact payload shapes may need updates.
- Canonical components touched: Resident detail API contract; dashboard edit flow.
