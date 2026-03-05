# Settings Version Visibility - Step 3 Development Plan

Sizing note: each stage is scoped to roughly <=1 hour or <=50 lines of net change.

1. Stage 1 - Add canonical build-metadata resolver with safe fallback
   - Goal: Create one backend source for commit SHA/date used by the Settings page.
   - Dependencies: Existing FastAPI app startup/runtime environment; no database dependencies.
   - Expected changes:
     - Add a small helper in `app/main.py` to resolve build metadata (commit SHA + commit date).
     - Return fallback values when git metadata cannot be read in a deployment context.
     - Planned signature updates (conceptual):
       - `_get_build_metadata() -> dict[str, str]`
       - `_build_template_context(request: Request, current_page: str) -> dict` (extended to include build metadata)
   - Verification approach: Manual local run with and without git metadata availability; confirm helper output remains non-empty and stable.
   - Risks or open questions:
     - Some packaged environments may not include `.git`; fallback behavior must stay explicit and user-friendly.
   - Canonical components/API touched: `app/main.py` template-context pipeline.

2. Stage 2 - Render build metadata in admin Settings surface
   - Goal: Show commit SHA/date in `/settings` without changing access-control behavior.
   - Dependencies: Stage 1 metadata available in template context.
   - Expected changes:
     - Extend `templates/settings.html` with a concise "Version" or "Build" section.
     - Display commit SHA and commit date values from server-rendered context.
     - Keep existing Settings cards and navigation patterns unchanged.
   - Verification approach: Manual admin smoke test on `/settings`; confirm values render and layout remains readable on desktop/mobile.
   - Risks or open questions:
     - Placement should avoid visual clutter in the current card stack.
   - Canonical components/API touched: `templates/settings.html`, `templates/partials/top_nav.html` (reused unchanged).

3. Stage 3 - Add focused regression coverage for metadata visibility
   - Goal: Prevent regressions in metadata rendering and fallback behavior.
   - Dependencies: Stages 1-2 behavior finalized.
   - Expected changes:
     - Extend existing settings-focused tests (or add a focused test module) to validate:
       - Build metadata is present in template context/render path for admin Settings.
       - Fallback values are used when metadata lookup fails.
       - Non-admin access restrictions to `/settings` remain intact.
     - Keep test scope narrow to this feature.
   - Verification approach: Run targeted pytest command for updated test module(s), then a quick manual admin Settings check.
   - Risks or open questions:
     - Template-content assertions should be resilient to minor wording changes.
   - Canonical components/API touched: `tests/test_settings_access_controls.py` (and/or related settings route tests), `app/main.py`, `templates/settings.html`.
