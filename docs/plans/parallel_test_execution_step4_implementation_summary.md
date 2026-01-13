## Stage 1 – Enable parallel test tooling
- Changes: Added `pytest-xdist` to `requirements.txt` for parallel worker support.
- Verification: Not run here (requires installing dependencies to confirm `pytest -n` help output).
- Notes: None.

## Stage 2 – Generalize loop runner for parallel + full suite
- Changes: Expanded `scripts/run_e2e_loop.py` to support full-suite or HTTP scope, loop duration, xdist worker options, and reusable command building.
- Verification: Ran `python3 scripts/run_e2e_loop.py --help`.
- Notes: Default scope remains `e2e` for backward compatibility.
