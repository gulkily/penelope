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
from dataclasses import dataclass
from datetime import datetime, timezone
import subprocess
import sys

MIN_DAY_HOURS = 0.5
MAX_GAP_HOURS = 2.0
MAX_DAY_HOURS = 8.0


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
        required=True,
        help="Start date/time for git log filtering (passed to git --since).",
    )
    parser.add_argument(
        "--until",
        required=True,
        help="End date/time for git log filtering (passed to git --until).",
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


@dataclass(frozen=True)
class CommitEvent:
    timestamp: datetime
    author_name: str
    author_email: str


def run_git_log(since: str, until: str, author: str | None) -> str:
    command = [
        "git",
        "log",
        "--since",
        since,
        "--until",
        until,
        "--pretty=format:%aI%x09%an%x09%ae",
    ]
    if author:
        command.extend(["--author", author])
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip() or "git log failed."
        raise RuntimeError(stderr)
    return result.stdout


def load_commit_events(since: str, until: str, author: str | None) -> list[CommitEvent]:
    raw_log = run_git_log(since=since, until=until, author=author)
    events: list[CommitEvent] = []
    for line in raw_log.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        try:
            parsed_timestamp = datetime.fromisoformat(parts[0]).astimezone(timezone.utc)
        except ValueError:
            continue
        events.append(
            CommitEvent(
                timestamp=parsed_timestamp,
                author_name=parts[1],
                author_email=parts[2],
            )
        )
    events.sort(key=lambda event: event.timestamp)
    return events


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        events = load_commit_events(since=args.since, until=args.until, author=args.author)
    except RuntimeError as exc:
        print(f"Failed to load git history: {exc}", file=sys.stderr)
        return 1
    print(
        f"Loaded {len(events)} commit event(s) from {args.since} to {args.until}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
