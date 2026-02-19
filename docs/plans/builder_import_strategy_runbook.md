# Builder Import Strategy Runbook (Phase 1)

## Purpose
Execute the latest-snapshot builder import safely with deterministic mapping, optional LLM enrichment, and rerun validation.

## Preconditions
- Source DB exists: `data/export_sebastian_ankita_amanda.db`
- Dependencies installed (`./pnl install` or `pip install -r requirements.txt`)
- Target DB chosen:
  - default app DB, or
  - isolated DB via `DATABASE_URL=sqlite:////path/to/db.sqlite`

## Commands

### 1) Dry-run (no writes)
```bash
python scripts/import_builder_snapshot.py --sample 5
```

### 2) Write run (deterministic only)
```bash
python scripts/import_builder_snapshot.py --sample 5 --write
```

### 3) Optional write run with LLM enrichment (`openai/gpt-5.2`)
```bash
DEDALUS_API_KEY=... \
python scripts/import_builder_snapshot.py \
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
