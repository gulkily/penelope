# North Star Dashboard

This project provides a lightweight FastAPI + vanilla HTML/CSS/JS dashboard for tracking North Star progress across residents.

## Local development
1. Create a virtual environment and install dependencies:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
2. Run the server:
   - `./start.sh`
3. Open `http://127.0.0.1:8000/`.

## Task runner
- `./pnl venv` for virtual environment setup help.
- `./pnl install` to install dependencies.
- `./pnl start` to run the server.
- `./pnl test` to run all tests.
- `./pnl test e2e` or `./pnl test http` for focused test runs.
- `./pnl test e2e --headed` for visible browser runs.
- `./pnl test --workers 4` for parallel runs against a running server.
- `./pnl test --duration 60 --workers 2` for light load-style loops.
- `./pnl test --help` for test-specific options (looping, delay, parallelism, etc).
- `./pnl seed-demo` to add demo data (use `--allow-duplicates` if needed).
- `./pnl env-sync` to append missing `.env` settings from `.env.example`.
- `./pnl magic-link --admin-username <issuer> --username <target> [--house <house>]` to generate an admin-issued magic login link and assign house immediately.
  - If `MAGIC_LINK_ADMIN_USERNAMES` is unset and the issuer account does not exist yet, the command bootstraps that account locally.

## Git log timesheet script
- `python3 scripts/git_timesheet.py` to print a basic estimated-hours report for the last 2 weeks (default range).
- `python3 scripts/git_timesheet.py --since 2026-02-17 --until 2026-02-24` to run a specific date range.
- `python3 scripts/git_timesheet.py --since 2026-02-17 --until 2026-02-24 --author \"Jane Doe\"` to filter by author.
- `python3 scripts/git_timesheet.py --since 2026-02-17 --until 2026-02-24 --format csv --output timesheet.csv` to export CSV.
- Estimator details: the estimator groups commits by UTC day, gives each active day a 0.5-hour baseline, then adds elapsed time between consecutive commits with each gap capped at 0.5 hours.
- Each day is capped at 8.0 total hours, and the script sums those daily estimates into the final range total deterministically.

## Public hosting
- Server setup guide: `docs/production_install.md`
- DNS/TLS handoff notes: `docs/domain_admin_brief.md`

## Testing
1. Install test dependencies:
   - `pip install -r requirements.txt`
   - `python -m playwright install`
2. Start the server in a separate terminal:
   - `./start.sh`
3. Run tests:
   - `pytest tests/e2e` (browser-driven E2E)
   - `pytest tests/http` (HTTP-level integration)
   - `pytest` (all tests)
4. Optional: set `E2E_BASE_URL` to point at a non-default server.
5. Optional: run in parallel with `pytest -n 4` or `./pnl test --workers 4` (uses the current database).
6. Optional: loop tests with `./pnl test --loop 10 --workers 2` or `python scripts/run_e2e_loop.py 10 --workers 2`.

## Generate test audio
Generate a long WAV fixture from a transcript script using Dedalus Labs TTS:
- `python scripts/generate_test_audio.py --script-path tests/fixtures/transcripts/long_conversation_15min_all_fields_script.txt --output-path tests/fixtures/audio/long_conversation_15min_all_fields.wav`
- Requires `DEDALUS_API_KEY` (in env or `.env`).
- Use `python scripts/generate_test_audio.py --help` for voice/model/chunk options.

## Test coverage matrix
- See `docs/test_matrix.md` for frontend flow coverage and gaps.

## Data & persistence
- Default storage is SQLite at `data/north_star.db` (created automatically on first run).
- Override the database location with `DATABASE_URL` (use `sqlite:///path/to.db`).
- The seed data includes a few example residents and items to populate the UI.
- To add additional demo data, run `python scripts/seed_demo_data.py`.

## Notes
- Item additions use inline add rows; edit and delete are available per item with an undo toast.
- Project Management lists are paginated at 100 items per page with next/previous controls.
- Settings includes a database backup download for saving recovery copies.
- Settings includes admin tools to generate one-click magic login links with preconfigured usernames.
- Settings includes a Users page that lists accounts, shows current admin status, and allows admin house assignment.
- Resident Summary and Questions fields are read-only for non-admin users.
- The North Star objective can be updated per resident via the Save button.
- The North Star goal value sets the progress slider range per resident.
- Progress updates happen immediately via the integrated slider.
- Questions auto-save while typing.
- Interview guide prompts in the `Add update` dialog come from `static/templates/interview_questions_template.md`.
- To update interview prompts, edit `static/templates/interview_questions_template.md`; changes are picked up on next page load.
- Interview guide prompts render as a checklist with a live asked counter (`x/y asked`).
- In the `Add update` dialog, press `g` to toggle the interview guide when focus is not inside a text input.
- On mobile widths, the interview guide opens as a bottom drawer and closes via backdrop tap.
- Keyboard shortcuts: Enter submits add/edit, Shift+Enter inserts a newline, Escape cancels edits.
- Configure magic-link admins with `MAGIC_LINK_ADMIN_USERNAMES` (comma-separated usernames); when unset, any signed-in account can issue/revoke links.
- The Users page admin badge follows the same `MAGIC_LINK_ADMIN_USERNAMES` runtime logic used by admin-only APIs.
- Magic links remain valid until revoked by an admin.
- Configure optional navbar links with `NAVBAR_ENABLED_ITEMS` (valid keys: `lobby,projects,settings`; Dashboard remains visible).
- House selector options are loaded from the database (`houses` table) rather than hard-coded in the frontend.
- Non-admin dashboard resident selection is scoped to the signed-in account's assigned house.
- Set `LOBBY_AUTH_ENABLED=false` to disable general lobby request/approval flows while keeping magic-link login usable.
- Set `RECORDER_ENABLED=false` to hide the "Record audio" section in the Add update dialog.
- Startup now only warns when `.env` is missing keys from `.env.example`; run `./pnl env-sync` to append missing defaults.
- Unauthenticated users are redirected to `/session/reset` as a transient restore attempt page; if restore fails they are redirected to `/welcome` with login guidance.
