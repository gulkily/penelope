#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.builder_import_source import load_source_snapshot


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


def main() -> int:
    args = build_parser().parse_args()
    print(render_snapshot_preview(args.source_db, args.sample))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
