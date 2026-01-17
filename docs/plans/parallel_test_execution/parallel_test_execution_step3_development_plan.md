# Parallel Test Execution - Step 3 Development Plan

1. Stage 1 - Enable parallel test tooling
   - Goal: Add pytest-xdist so parallel workers are available for the suite.
   - Dependencies: Existing `requirements.txt` and pytest setup.
   - Expected changes: Add `pytest-xdist` to `requirements.txt` so `pytest -n` is available; no server orchestration changes.
   - Verification: Run `python -m pytest --help` to confirm xdist options are present.
   - Risks/open questions: Confirm pytest-playwright remains stable under xdist for shared server usage.
   - Shared components/API contracts touched: `requirements.txt`.

2. Stage 2 - Generalize loop runner for parallel + full suite
   - Goal: Support repeated or sustained runs (light load) for the full suite without starting the server.
   - Dependencies: Stage 1.
   - Expected changes: Refactor `scripts/run_e2e_loop.py` into shared loop logic or introduce a new loop runner that can target `tests/e2e`, `tests/http`, or full suite; add optional parallel worker arguments (`-n`, dist mode) and optional duration/loop count controls; keep outputs and exit codes straightforward.
   - Planned signatures: `build_pytest_command(scope: str | None, headed: bool, workers: int | None, dist: str | None) -> list[str]`; `run_loop(scope: str | None, count: int | None, duration: float | None, delay: float, keep_going: bool, headed: bool, workers: int | None, dist: str | None) -> int`.
   - Verification: With the server running, run the loop script directly (e.g., looped full suite with `-n` workers) and confirm exit code behavior on pass/fail.
   - Risks/open questions: Decide whether to keep the loop runner name for backward compatibility or add a wrapper to preserve `run_e2e_loop.py` usage.
   - Shared components/API contracts touched: `scripts/run_e2e_loop.py` (or a new loop script), `tests/e2e`, `tests/http`.

3. Stage 3 - Expose parallel/load options via `./pnl test`
   - Goal: Provide a single command to run the suite in parallel with optional looping.
   - Dependencies: Stage 1–2.
   - Expected changes: Extend `scripts/pnl.py` to accept worker count/dist options and forward them to pytest or the loop runner; broaden `--loop` to support all scopes (or add a new flag for full-suite loops) while keeping existing behavior; ensure `E2E_BASE_URL` continues to control the target server.
   - Planned signatures: `run_tests(scope: str | None, headed: bool, loop_count: int | None, delay: float, keep_going: bool, workers: int | None, dist: str | None, duration: float | None) -> int`.
   - Verification: With the server running, run `./pnl test --workers 4` and a looped run (e.g., `./pnl test --loop 5 --workers 2`) and confirm exit codes and output clarity.
   - Risks/open questions: Determine default worker count when `--workers` is omitted and ensure resource usage is reasonable on typical laptops.
   - Shared components/API contracts touched: `scripts/pnl.py`, `E2E_BASE_URL` usage in tests.

4. Stage 4 - Document the parallel/load workflow
   - Goal: Keep the manual-server workflow and new options discoverable.
   - Dependencies: Stage 2–3.
   - Expected changes: Update `README.md` (and `AGENTS.md` if needed) to document parallel and loop flags, manual server requirement, and warnings about shared-state flakiness under load-style runs.
   - Verification: Follow the documented steps end-to-end with a running server.
   - Risks/open questions: Ensure docs stay aligned with the actual CLI behavior and defaults.
   - Shared components/API contracts touched: `README.md`, `AGENTS.md`.
