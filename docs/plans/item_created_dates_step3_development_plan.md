# Step 3: Development Plan

1. Stage 1: Ensure item creation dates are available in storage and payloads
   - Goal: Make sure every item includes a creation date in data access and API responses.
   - Dependencies: Existing `items.created_at` column and item list queries.
   - Expected changes: If needed, ensure the `created_at` column exists with a safe default for existing rows. Update item list queries and returned item dicts to include `created_at`. Keep add/update/delete behavior unchanged beyond returning the date.
   - Planned function signatures: `list_items_for_project(project_id: int) -> list[dict]` returns `created_at`; `add_item(project_id: int, section: str, text: str) -> dict` returns `created_at`.
   - Verification approach: Manual check of project detail API payload includes `created_at` for items.
   - Risks/open questions: How to handle existing rows with missing dates (use empty string, current time, or a placeholder label?).
   - Canonical components/API contracts: Project detail API payload for items.

2. Stage 2: Render compact dates in dashboard list items
   - Goal: Display each item’s creation date in a compact format alongside the text.
   - Dependencies: Stage 1 item payload updates.
   - Expected changes: Extend client-side list rendering to include a date label per item. Add a compact date formatting helper (e.g., `MMM D` or `YYYY-MM-DD`). Add minimal CSS for the date chip/label to keep the layout compact.
   - Verification approach: Manual check that item dates appear and remain readable across all sections.
   - Risks/open questions: Final date format and timezone (local vs UTC) for display.
   - Canonical components/API contracts: Dashboard list item markup and styling.

3. Stage 3: Preserve dates across edit/delete/undo flows
   - Goal: Ensure editing or undoing items keeps original dates consistent.
   - Dependencies: Stage 2 UI changes.
   - Expected changes: Ensure edit flow preserves the date label in DOM updates. Ensure undo re-adds items with a new date or retains a stored date (decide and document). Update client logic to handle missing dates gracefully.
   - Verification approach: Manual check of add/edit/delete/undo interactions and date display.
   - Risks/open questions: Decide whether undo should reuse the original date or the new add date.
   - Canonical components/API contracts: Item add/edit/delete API and UI behavior.
