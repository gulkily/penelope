# Builder Import Strategy Runbook (Phase 1)

## Purpose
Execute the latest-snapshot builder import safely with deterministic mapping, optional LLM enrichment, and rerun validation.

## Environment Setup
```bash
# 1) Activate venv
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt
```

Optional, but strongly recommended for test runs:
```bash
# Use an isolated SQLite DB so you do not touch main app data
export DATABASE_URL=sqlite:////tmp/builder_import_test.sqlite
```

For LLM enrichment runs only:
```bash
export DEDALUS_API_KEY=your_key_here
```

To run against the default app DB again:
```bash
unset DATABASE_URL
```

Set a placeholder source DB path (rename your local file as needed):
```bash
export IMPORT_SOURCE_DB=data/builder_import_source.db
```

## Preconditions
- Source DB exists at a neutral placeholder path (example): `data/builder_import_source.db`
- Python environment is activated and dependencies are installed.
- Target DB is chosen:
  - default app DB, or
  - isolated DB via `DATABASE_URL=sqlite:////path/to/db.sqlite`
- `DEDALUS_API_KEY` is set only if running with `--enable-llm`.
- App server is not required for this import script.

## Commands

### 1) Dry-run (no writes)
```bash
python scripts/import_builder_snapshot.py --source-db "$IMPORT_SOURCE_DB" --sample 5
```

### 2) Write run (deterministic only)
```bash
python scripts/import_builder_snapshot.py --source-db "$IMPORT_SOURCE_DB" --sample 5 --write
```

### 3) Optional write run with LLM enrichment (`openai/gpt-5.2`)
```bash
DEDALUS_API_KEY=... \
python scripts/import_builder_snapshot.py \
  --source-db "$IMPORT_SOURCE_DB" \
  --sample 5 \
  --write \
  --enable-llm \
  --llm-model openai/gpt-5.2 \
  --llm-confidence-threshold 0.7
```

### 4) Rerun idempotency check
Run the same write command again and confirm:
- `Builders imported: 0`
- `Builders skipped: 21` (or total builders in source)
- `Latest check-ins created: 0`
- `Latest check-ins updated: 0`

## Validation Checklist
- Report counters present and reasonable:
  - builders scanned/imported/updated/skipped
  - builders without check-ins
  - latest check-ins created/updated/skipped
  - missing latest `north_star_value`
  - house warnings
  - error count
  - LLM counters (if enabled)
- Mapping table counts:
  - `import_builder_map` equals imported builders
  - `import_checkin_map` equals builders with latest check-ins
- Data quality spot checks:
  - house values normalized to `Unassigned`/`Actioners`/`SF2`
  - imported section items tagged `[Import Snapshot]`
  - `questions` include relevant `[Import]` / `[Import TODO]` notes

## Rollback / Safety Notes
- Preferred rollback: restore target DB from backup/snapshot.
- For test runs, use isolated DB path via `DATABASE_URL` to avoid touching production data.
- Keep LLM optional; deterministic mode remains the baseline fallback.
