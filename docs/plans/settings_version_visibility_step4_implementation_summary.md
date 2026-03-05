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
