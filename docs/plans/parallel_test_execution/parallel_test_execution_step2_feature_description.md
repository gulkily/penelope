# Parallel Test Execution - Step 2 Feature Description

Problem: The team needs a reliable way to run the full pytest suite in parallel (and repeatedly) against a manually managed server, adding light load-style pressure without test-driven server control.

User stories:
- As a developer, I want a single command to run parallel pytest suites against a running server so that I avoid manual terminal juggling.
- As a tester, I want optional repeated or sustained parallel runs so that I can surface concurrency regressions early.
- As a maintainer, I want tests to remain compatible with manual server operation so that local workflows stay simple.

Core requirements:
- Tests must assume a manually started server; no test command starts or stops the app.
- Provide a single command to run the full suite in parallel with configurable concurrency.
- Support repeated runs or sustained parallel execution to create light load pressure.
- Preserve existing E2E/HTTP selection and `E2E_BASE_URL` configuration.
- Keep outputs and exit codes straightforward for local or CI usage.

Shared component inventory:
- `scripts/pnl.py` test runner: reuse and extend to expose parallel/load-oriented options.
- `scripts/run_e2e_loop.py`: reuse or extend for repeated runs to avoid duplicating loop logic.
- `tests/e2e` and `tests/http`: reuse as the canonical suites under parallel execution.
- `README.md` testing section: extend to document the new parallel/load workflow.
- `E2E_BASE_URL` usage in tests: reuse as the canonical server target.

Simple user flow:
1. Start the server manually.
2. Run a single test command that executes the suite in parallel with optional repetition.
3. Review results and adjust concurrency or loop settings as needed.

Success criteria:
- A single command runs pytest in parallel against the running server and returns a single exit code.
- Tests never spawn or manage the server process.
- Users can configure concurrency or looping to generate light load (documented).
- Existing test commands continue to work as documented.
