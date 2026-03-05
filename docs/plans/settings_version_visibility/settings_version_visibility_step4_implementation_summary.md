## Stage 1 - Add canonical build-metadata resolver with safe fallback
- Changes:
  - Added `_run_git_command(args: list[str]) -> str | None` in `app/main.py` to read git metadata safely.
  - Added cached `_get_build_metadata() -> dict[str, str]` in `app/main.py` with explicit `Unknown` fallback values.
  - Extended `_build_template_context(...)` to include `build_metadata` for template rendering.
- Verification:
  - Ran `python -c "import app.main as m; print(m._get_build_metadata())"` and confirmed commit metadata resolved (`{'commit_sha': '784900c', 'commit_date': '2026-03-05'}`).
  - Ran `python -c "import app.main as m; m._get_build_metadata.cache_clear(); m._run_git_command=lambda args: None; print(m._get_build_metadata())"` and confirmed fallback output (`{'commit_sha': 'Unknown', 'commit_date': 'Unknown'}`).
- Notes:
  - Metadata is cached per process to avoid invoking git on every request.

## Stage 2 - Render build metadata in admin Settings surface
- Changes:
  - Extended `templates/settings.html` with a new `Version` card on the admin Settings page.
  - Added server-rendered display fields for commit SHA and commit date using `build_metadata` (`{{ build_metadata.commit_sha }}` and `{{ build_metadata.commit_date }}`).
  - Kept existing Settings cards, links, and access-control behavior unchanged.
- Verification:
  - Ran a manual route-render smoke command:
    - `python - <<'PY' ... response = m.settings(request) ... print(response.status_code); print(\"Version\" in body, \"Commit:\" in body, \"Date:\" in body) PY`
  - Confirmed status `200` for admin route rendering and presence of `Version`, `Commit:`, and `Date:` in rendered HTML.
- Notes:
  - The render check emitted an existing environment warning about `NAVBAR_ENABLED_ITEMS=dashboard`; this did not affect Settings rendering for this feature.

## Stage 3 - Add focused regression coverage for metadata visibility
- Changes:
  - Hardened `templates/settings.html` metadata rendering with Jinja `default("Unknown", true)` filters for both commit SHA and commit date.
  - Preserved existing admin-only access behavior for Settings routes while validating fallback rendering path.
- Verification:
  - Ran a manual fallback render + access-control smoke command:
    - `python - <<'PY' ... m._run_git_command = lambda args: None ... print(\"fallback_unknown_rendered\", ...) ... print(\"non_admin_blocked\", ...) PY`
  - Confirmed fallback values render as `Unknown` when metadata lookup is unavailable (`fallback_unknown_rendered True`).
  - Confirmed non-admin Settings access remains blocked with `403` (`non_admin_blocked True`).
- Notes:
  - Kept verification manual and targeted to align with Step 4 guidance (no new automated tests/fixtures).
