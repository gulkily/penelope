# Env Defaults Sync Step 3: Development Plan

Sizing note: each stage targets <=1 hour or <=50 lines; if Stage 1 exceeds that, split parser and file-write concerns into separate stages before implementation.

1. **Stage 1: Default Key Sync Utility**
   - Goal: Define a safe utility that compares `.env.example` and `.env`, then computes missing keys to append.
   - Dependencies: Existing repository root path usage in app startup modules.
   - Expected changes:
     - Add a small env-sync module responsible for parsing env-style key lines from `.env.example` and existing keys from `.env`.
     - Handle missing `.env` by treating it as empty before append/create.
     - Planned signatures (conceptual):
       - `parse_env_keys(lines: list[str]) -> list[str]`
       - `sync_env_defaults(env_path: Path, env_example_path: Path) -> dict[str, int | bool]`
   - Verification approach: Manual dry-run style checks in local workspace with sample `.env`/`.env.example` content.
   - Risks or open questions:
     - Correctly ignoring comments/blank lines while preserving key detection accuracy.
   - Canonical components/API touched: new env-sync helper module under `app/`.

2. **Stage 2: Launch-Time Integration**
   - Goal: Run sync before settings are consumed during app startup.
   - Dependencies: Stage 1.
   - Expected changes:
     - Integrate env sync into startup boot path in `app/main.py` before `load_dotenv()` usage impacts runtime config.
     - Ensure behavior is launch-path agnostic (works for `./start.sh`, `./pnl start`, and direct `uvicorn`).
   - Verification approach: Start app with missing keys in `.env` and confirm keys are appended after launch.
   - Risks or open questions:
     - Startup ordering must avoid reading stale env values before sync completes.
   - Canonical components/API touched: `app/main.py`, `start.sh`/`scripts/pnl.py` behavior indirectly via shared app entrypoint.

3. **Stage 3: Safety, Idempotency, and Operator Visibility**
   - Goal: Ensure sync is safe to run repeatedly and clearly reports outcomes.
   - Dependencies: Stages 1-2.
   - Expected changes:
     - Enforce no-overwrite behavior for existing `.env` keys.
     - Enforce no duplicate-key insertion on repeated launches.
     - Add concise logging/summary when keys are added or when sync is skipped.
   - Verification approach: Launch app multiple times and confirm file content stabilizes after first sync.
   - Risks or open questions:
     - File permission issues on `.env` should fail clearly without partial/corrupt writes.
   - Canonical components/API touched: env-sync helper module, app startup logging surface.

4. **Stage 4: Documentation and Configuration Notes**
   - Goal: Document expected sync behavior for admins/operators.
   - Dependencies: Stage 3.
   - Expected changes:
     - Update `README.md` and/or `.env.example` comments to describe launch-time default key sync and no-overwrite guarantees.
     - Add notes for missing-file behavior (`.env` auto-created from defaults).
   - Verification approach: Follow documented steps with a fresh `.env` and validate documented outcomes.
   - Risks or open questions:
     - Keep docs aligned if additional env-loading paths are introduced later.
   - Canonical components/API touched: `README.md`, `.env.example`.
