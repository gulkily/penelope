# CLI Task Runner - Step 3 Development Plan

1. Define the Python task utility
   - Goal: Provide a clear command interface and help output for common tasks.
   - Dependencies: Existing scripts (`start.sh`) and documented commands.
   - Expected changes: Add a Python module (e.g., `scripts/pnl.py`) with subcommands for install, run, test, and venv guidance; include a help command.
   - Verification: Run the utility directly (e.g., `python scripts/pnl.py help`) and confirm outputs.
   - Risks/open questions: Decide on required subcommands beyond install/run/test/venv.
   - Shared components/API contracts touched: None.

2. Add the `./pnl` shell wrapper
   - Goal: Provide a short, POSIX-compatible entrypoint for the task utility.
   - Dependencies: Python task utility from Stage 1.
   - Expected changes: Add a root-level `pnl` shell script that dispatches to the Python utility and passes through args.
   - Verification: Run `./pnl help` and confirm expected output.
   - Risks/open questions: Ensure the wrapper works in common POSIX shells and respects the active Python/venv.
   - Shared components/API contracts touched: None.

3. Document and validate tasks
   - Goal: Make the task runner discoverable and reliable.
   - Dependencies: README and AGENTS command sections.
   - Expected changes: Update docs to describe the `./pnl` command and supported subcommands.
   - Verification: Follow the documented steps to run install/start/test tasks.
   - Risks/open questions: Keep docs aligned as tasks evolve.
   - Shared components/API contracts touched: Documentation files.
