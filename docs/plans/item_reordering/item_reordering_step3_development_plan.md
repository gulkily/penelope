1. Data model for item ordering
- Goal: Add a stable per-section ordering field for items and preserve current order.
- Dependencies: None.
- Expected changes: Add `sort_order` column to `items` via `app/db_init.py` `_ensure_column`; backfill existing items per project/section using current `id` order; update `list_items_for_project(project_id: int)` to `ORDER BY section, sort_order, id`; update `add_item(project_id: int, section: str, text: str)` to assign the next `sort_order` value in that section.
- Verification: Start with seeded data, confirm list order is unchanged; add a new item and confirm it appears at the end.
- Risks/open questions: Should `sort_order` be contiguous or allow gaps; how to handle missing/zero values during backfill.
- Touched components/API contracts: `app/db_init.py`, `app/db_items.py`, `app/db_projects.py` (ordering of section data).

2. Reorder API surface
- Goal: Provide a backend entry point to persist ordering changes per section.
- Dependencies: Stage 1.
- Expected changes: Add `ItemOrderUpdate` schema (`section: str`, `ordered_ids: list[int]`); add endpoint (e.g., `PUT /projects/{project_id}/items/order`) with signature `def reorder_items(project_id: int, payload: ItemOrderUpdate) -> dict`; add db helper `reorder_items(project_id: int, section: str, ordered_ids: list[int]) -> None` that validates ids belong to the project/section before updating `sort_order`.
- Verification: Call the endpoint with a reordered list and confirm subsequent `GET /projects/{id}` returns the new order.
- Risks/open questions: Behavior if `ordered_ids` is missing or extra ids (append unknowns? reject?); concurrent edits while reordering.
- Touched components/API contracts: `app/api.py`, `app/schemas.py`, `app/db_items.py`.

3. Reorder UI interactions (pointer, touch, keyboard)
- Goal: Let users reorder items within a section using drag-and-drop and keyboard controls without disrupting edit/delete.
- Dependencies: Stage 2.
- Expected changes: Extend section item markup to include a drag handle and move up/down controls; add client logic in `static/js/app.js` to reorder DOM items, send the ordered ids to the reorder endpoint, and guard against reordering while an item is in edit mode; ensure touch uses long-press/drag on the handle and keyboard users can move items with focused controls.
- Verification: Manual test on desktop (mouse) and mobile emulation (touch); keyboard-only reorder using tab/enter/arrow or move buttons; confirm order persists after refresh.
- Risks/open questions: Interaction conflicts with text selection/editing; whether to lock reordering while inline add/edit is active.
- Touched components/API contracts: `templates/index.html`, `static/js/app.js`.

4. Styling and accessibility polish
- Goal: Keep the UI clean while making reorder affordances discoverable and accessible.
- Dependencies: Stage 3.
- Expected changes: Add CSS for the drag handle, move buttons, focus states, and drag placeholder; ensure controls are visible on touch and on focus; add a minimal `aria-live` announcement for reorder changes.
- Verification: Visual scan on desktop/mobile widths; keyboard focus ring visibility; screen reader announcement check if possible.
- Risks/open questions: Visual clutter in dense lists; consistent affordance behavior across sections.
- Touched components/API contracts: `static/css/main.css`.

5. Tests and regression checks
- Goal: Guard against ordering regressions in API behavior.
- Dependencies: Stages 2–3.
- Expected changes: Add or extend HTTP tests to validate reorder persistence and ordering in `GET /projects/{id}`; document manual smoke steps for drag, touch, and keyboard reorder.
- Verification: Run `pytest tests/http` (if available) and manual smoke pass.
- Risks/open questions: Playwright drag support may need more setup if we later add E2E coverage.
- Touched components/API contracts: `tests/http/*` (if adding), `docs/test_matrix.md` (if documenting gaps).
