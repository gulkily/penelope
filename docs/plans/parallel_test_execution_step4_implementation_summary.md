## Stage 1 – Enable parallel test tooling
- Changes: Added `pytest-xdist` to `requirements.txt` for parallel worker support.
- Verification: Not run here (requires installing dependencies to confirm `pytest -n` help output).
- Notes: None.

## Stage 2 – Generalize loop runner for parallel + full suite
- Changes: Expanded `scripts/run_e2e_loop.py` to support full-suite or HTTP scope, loop duration, xdist worker options, and reusable command building.
- Verification: Ran `python3 scripts/run_e2e_loop.py --help`.
- Notes: Default scope remains `e2e` for backward compatibility.

## Stage 3 – Expose parallel/load options via `./pnl test`
- Changes: Added `--workers`, `--dist`, and `--duration` support in `scripts/pnl.py`, and broadened loop mode to all scopes while preserving existing flags.
- Verification: Ran `./pnl test --help`.
- Notes: `--dist` now requires `--workers` to avoid confusing no-op runs.

## Stage 4 – Document the parallel/load workflow
- Changes: Updated `README.md` and `AGENTS.md` with new parallel and loop usage guidance for manual-server testing.
- Verification: Ran `./pnl help` and cross-checked documentation against the updated CLI output.
- Notes: None.
