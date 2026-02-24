#!/usr/bin/env python3
"""Generate basic estimated-hours timesheets from git history.

Estimation contract (deterministic):
- Group commits by UTC calendar day.
- Base minimum of 0.5 hours for any day with at least one commit.
- Add time gaps between consecutive commits, capped at 2.0 hours per gap.
- Cap each day at 8.0 estimated hours.
"""

from __future__ import annotations

import argparse
import sys

from git_timesheet_core import calculate_total_hours
from git_timesheet_core import estimate_daily_hours
from git_timesheet_core import load_commit_events
from git_timesheet_core import render_report
from git_timesheet_core import write_report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="git_timesheet",
        description="Generate a basic timesheet estimate from git log history.",
        epilog=(
            "Examples:\n"
            "  python scripts/git_timesheet.py --since 2026-02-01 --until 2026-02-07\n"
            "  python scripts/git_timesheet.py --since 2026-02-01 --until 2026-02-07 --author 'Jane Doe'\n"
            "  python scripts/git_timesheet.py --since 2026-02-01 --until 2026-02-07 --format csv --output timesheet.csv\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--since",
        default="14 days ago",
        help=(
            "Start date/time for git log filtering (passed to git --since). "
            "Default: 14 days ago."
        ),
    )
    parser.add_argument(
        "--until",
        default="now",
        help=(
            "End date/time for git log filtering (passed to git --until). "
            "Default: now."
        ),
    )
    parser.add_argument(
        "--author",
        help="Optional author filter (name or email pattern; passed to git --author).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "csv", "markdown"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--output",
        help="Optional file path to write the generated report.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        events = load_commit_events(since=args.since, until=args.until, author=args.author)
    except RuntimeError as exc:
        print(f"Failed to load git history: {exc}", file=sys.stderr)
        return 1

    daily_estimates = estimate_daily_hours(events)
    total_hours = calculate_total_hours(daily_estimates)
    report = render_report(
        days=daily_estimates,
        total_hours=total_hours,
        fmt=args.format,
        since=args.since,
        until=args.until,
        author=args.author,
    )

    if args.output:
        try:
            write_report(report, args.output)
        except OSError as exc:
            print(f"Failed to write report: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {args.format} report to {args.output}")
        return 0

    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
