# CLI Task Runner - Step 2 Feature Description

Problem: Running common tasks requires remembering multiple commands, which slows down onboarding and daily work.

User stories:
- As a developer, I want a short command that runs common tasks so that I do not have to remember long commands.
- As a new contributor, I want a discoverable help output so that I can learn the available tasks quickly.
- As a project lead, I want consistent task execution across environments so that instructions are reliable.

Core requirements:
- Provide a short shell wrapper (`./pnl`) that invokes a Python task utility.
- Support tasks for venv activation guidance, installing requirements, starting the server, and running tests.
- Include a help/usage output that lists available commands.
- Keep the shell wrapper compatible with common POSIX shells.
- Avoid introducing non-Python dependencies (no npm).

Shared component inventory:
- Reuse existing scripts like `start.sh` for server startup.
- Reuse documented commands in `README.md` and `AGENTS.md` for task behavior.
- Place new scripts in the repo root to keep them discoverable.

Simple user flow:
1. Run the short CLI command with `help` to see available tasks.
2. Use the command to install dependencies or start the server.
3. Use the command to run tests.

Success criteria:
- A short wrapper command exists and works in common shells.
- The Python utility provides clear help and executes tasks reliably.
- Tasks map to existing, documented behaviors.
- No npm tooling is introduced.
