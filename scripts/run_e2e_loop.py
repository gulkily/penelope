#!/usr/bin/env python3
"""Run pytest suites multiple times."""

from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run pytest suites in a loop using the current database.",
    )
    parser.add_argument(
        "count",
        type=int,
        nargs="?",
        help="Number of times to run the suite.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Seconds to keep running the suite (alternative to count).",
    )
    parser.add_argument(
        "--scope",
        choices=["e2e", "http", "all"],
        default="e2e",
        help="Test scope to run (default: e2e).",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run E2E tests with a visible browser.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Seconds to wait between runs.",
    )
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="Continue running even if a test run fails.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of parallel workers (pytest-xdist).",
    )
    parser.add_argument(
        "--dist",
        type=str,
        default=None,
        help="xdist distribution mode (e.g., load, loadfile).",
    )
    return parser.parse_args()


def build_pytest_command(
    scope: str,
    headed: bool,
    workers: int | None,
    dist: str | None,
) -> list[str]:
    command = ["python3", "-m", "pytest"]
    if scope == "e2e":
        command.append("tests/e2e")
    elif scope == "http":
        command.append("tests/http")
    elif scope != "all":
        raise ValueError(f"Unsupported scope: {scope}")

    if headed:
        command.append("--headed")
    if workers is not None:
        command.extend(["-n", str(workers)])
    if dist:
        command.extend(["--dist", dist])
    return command


def run_once(command: list[str]) -> int:
    result = subprocess.run(command, check=False)
    return result.returncode


def has_xdist() -> bool:
    return importlib.util.find_spec("xdist") is not None


def validate_args(args: argparse.Namespace) -> None:
    if args.count is None and args.duration is None:
        raise SystemExit("count or --duration is required")
    if args.count is not None and args.duration is not None:
        raise SystemExit("use either count or --duration, not both")
    if args.count is not None and args.count <= 0:
        raise SystemExit("count must be a positive integer")
    if args.duration is not None and args.duration <= 0:
        raise SystemExit("--duration must be a positive number")
    if args.delay < 0:
        raise SystemExit("--delay cannot be negative")
    if args.workers is not None and args.workers <= 0:
        raise SystemExit("--workers must be a positive integer")
    if args.dist is not None and args.workers is None:
        raise SystemExit("--dist requires --workers")
    if args.workers is not None and not has_xdist():
        raise SystemExit(
            "pytest-xdist is required for --workers. "
            "Install dependencies with `./pnl install` or "
            "`pip install -r requirements.txt`."
        )


def main() -> int:
    args = parse_args()
    validate_args(args)

    os.chdir(REPO_ROOT)
    command = build_pytest_command(args.scope, args.headed, args.workers, args.dist)

    end_time = None
    if args.duration is not None:
        end_time = time.monotonic() + args.duration

    index = 1
    while True:
        if args.count is not None and index > args.count:
            break
        if end_time is not None and index > 1 and time.monotonic() >= end_time:
            break

        if args.count is not None:
            print(f"Run {index}/{args.count}")
        else:
            print(f"Run {index} (duration mode)")

        exit_code = run_once(command)
        if exit_code != 0 and not args.keep_going:
            print("Stopping on first failure.")
            return exit_code

        if args.delay > 0:
            if end_time is not None:
                remaining = end_time - time.monotonic()
                if remaining <= 0:
                    break
                time.sleep(min(args.delay, remaining))
            elif args.count is None or index < args.count:
                time.sleep(args.delay)

        index += 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
