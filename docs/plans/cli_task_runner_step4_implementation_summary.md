## Stage 1 – Define the Python task utility
- Changes: Added a Python task runner with subcommands for venv help, install, start, and tests.
- Verification: Manual smoke test suggested (run `python3 scripts/pnl.py help`; not run here).
- Notes: None.

## Stage 2 – Add the ./pnl shell wrapper
- Changes: Added a POSIX-compatible wrapper that invokes the Python task runner.
- Verification: Manual smoke test suggested (run `./pnl help`; not run here).
- Notes: None.

## Stage 3 – Document and validate tasks
- Changes: Documented the new task runner and commands in README and AGENTS.
- Verification: Manual smoke test suggested (follow docs to run install/start/test; not run here).
- Notes: None.
