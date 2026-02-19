#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.builder_import_pipeline import ImportConfig, run_import
from app.builder_import_source import load_source_snapshot
from app.db_init import init_db


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load and summarize latest builder snapshot data from source SQLite.",
    )
    parser.add_argument(
        "--source-db",
        default="data/export_sebastian_ankita_amanda.db",
        help="Path to source SQLite export DB.",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=5,
        help="How many builders to print in sample output.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Apply writes to target app DB (default is dry-run).",
    )
    return parser


def render_snapshot_preview(source_db: str, sample: int) -> str:
    snapshot = load_source_snapshot(source_db)
    builders = snapshot.builders
    with_checkins = sum(1 for row in builders if row.latest_checkin is not None)
    missing_progress = sum(
        1
        for row in builders
        if row.latest_checkin is not None and row.latest_checkin.north_star_value is None
    )

    lines = [
        f"Source DB: {Path(source_db)}",
        f"Builders: {len(builders)}",
        f"Builders with latest check-in: {with_checkins}",
        f"Latest check-ins missing north_star_value: {missing_progress}",
        f"House normalization warnings: {len(snapshot.house_warnings)}",
        "",
        "Sample builders:",
    ]

    for row in builders[: max(0, sample)]:
        checkin_week = row.latest_checkin.week_of if row.latest_checkin else "none"
        lines.append(
            f"- {row.full_name} | house={row.normalized_house} | latest_week={checkin_week}"
        )

    if snapshot.house_warnings:
        lines.extend(["", "House warnings:"])
        lines.extend([f"- {warning}" for warning in snapshot.house_warnings])

    return "\n".join(lines)


def render_import_report(config: ImportConfig) -> str:
    report = run_import(config)
    lines = [
        f"Mode: {'WRITE' if not config.dry_run else 'DRY-RUN'}",
        f"Builders scanned: {report.builders_scanned}",
        f"Builders imported: {report.builders_imported}",
        f"Builders updated: {report.builders_updated}",
        f"Builders skipped: {report.builders_skipped}",
        f"Builders without check-ins: {report.builders_without_checkins}",
        f"Latest check-ins imported: {report.latest_checkins_imported}",
        f"Latest check-ins skipped: {report.latest_checkins_skipped}",
        f"Latest check-ins missing north_star_value: {report.missing_progress_latest}",
        f"House normalization warnings: {len(report.house_warnings)}",
        f"Errors: {len(report.errors)}",
    ]
    if report.house_warnings:
        lines.extend(["", "House warnings:"])
        lines.extend([f"- {warning}" for warning in report.house_warnings])
    if report.errors:
        lines.extend(["", "Errors:"])
        lines.extend([f"- {error}" for error in report.errors])
    return "\n".join(lines)


def main() -> int:
    args = build_parser().parse_args()
    init_db()
    print(render_snapshot_preview(args.source_db, args.sample))
    print("")
    print(render_import_report(ImportConfig(source_db=args.source_db, dry_run=not args.write)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
