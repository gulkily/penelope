# Git Log Timesheet - Step 3 Development Plan

1. Stage 1 - Define script interface and estimation contract
   - Goal: Lock down inputs/outputs and the deterministic hour-estimation rule before building logic.
   - Dependencies: Approved Step 2 requirements.
   - Expected changes: Add script usage contract for required flags (`--since`, `--until`) and optional flags (`--author`, `--format`, `--output`); document estimation assumptions and limits.
   - Planned signatures: `parse_args(argv: list[str]) -> argparse.Namespace`.
   - Verification: Run script with `--help` and invalid argument combinations to confirm clear usage/error behavior.
   - Risks/open questions:
     - Estimation rule may over/under-count work for bursty commit patterns.
     - Need a default timezone assumption for date-boundary grouping.
   - Shared components/API contracts touched: None (standalone script only).

2. Stage 2 - Implement git history ingestion and normalization
   - Goal: Collect commit events consistently for the requested range/author scope.
   - Dependencies: Stage 1 interface and date/filter rules.
   - Expected changes: Add logic to execute git log, parse commit timestamps/authors, and normalize events into an internal structure ordered by time.
   - Planned signatures: `load_commit_events(since: str, until: str, author: str | None) -> list[CommitEvent]`.
   - Verification: Run script against a known short date window and confirm event counts match git log expectations.
   - Risks/open questions:
     - Local clone completeness affects accuracy.
     - Author matching may vary across name/email aliases.
   - Shared components/API contracts touched: Reuse git log as the canonical data source.

3. Stage 3 - Implement daily hour estimation and totals
   - Goal: Convert commit events into per-day estimated hours and an overall total.
   - Dependencies: Stage 2 normalized events.
   - Expected changes: Add deterministic grouping/estimation logic and total aggregation.
   - Planned signatures: `estimate_daily_hours(events: list[CommitEvent]) -> list[DailyEstimate]`, `calculate_total_hours(days: list[DailyEstimate]) -> float`.
   - Verification: Run on fixed sample ranges and confirm repeated runs produce identical outputs.
   - Risks/open questions:
     - Need a cap/floor rule so outlier commit spacing does not inflate totals.
   - Shared components/API contracts touched: None (new internal script logic).

4. Stage 4 - Add report rendering and export output
   - Goal: Provide readable terminal output plus export-friendly output.
   - Dependencies: Stage 3 estimated results.
   - Expected changes: Add text summary rendering and at least one export format (CSV or Markdown) with optional file write path.
   - Planned signatures: `render_report(days: list[DailyEstimate], total_hours: float, fmt: str) -> str`, `write_report(content: str, output_path: str) -> None`.
   - Verification: Generate text + export outputs for the same range and confirm totals match between formats.
   - Risks/open questions:
     - Output format expectations may differ for payroll/import workflows.
   - Shared components/API contracts touched: Script output contract (CLI-visible format/columns).

5. Stage 5 - Document usage and run smoke validation
   - Goal: Make the script discoverable and safe to use by other developers.
   - Dependencies: Stage 1-4 completed behavior.
   - Expected changes: Update `README.md` and/or `AGENTS.md` with command examples, key assumptions, and limitations.
   - Verification: Follow docs end-to-end to generate a timesheet for a sample date range.
   - Risks/open questions:
     - Documentation drift if flags or estimation rules change later.
   - Shared components/API contracts touched: Developer documentation conventions.
