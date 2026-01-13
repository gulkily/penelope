#!/usr/bin/env python3
"""Run the E2E test suite multiple times."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run E2E tests in a loop using the current database.",
    )
    parser.add_argument(
        "count",
        type=int,
        help="Number of times to run the E2E suite.",
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
    return parser.parse_args()


def run_once(command: list[str]) -> int:
    result = subprocess.run(command, check=False)
    return result.returncode


def main() -> int:
    args = parse_args()
    if args.count <= 0:
        raise SystemExit("count must be a positive integer")

    os.chdir(REPO_ROOT)
    command = ["python3", "-m", "pytest", "tests/e2e"]
    if args.headed:
        command.append("--headed")

    for index in range(1, args.count + 1):
        print(f"Run {index}/{args.count}")
        exit_code = run_once(command)
        if exit_code != 0 and not args.keep_going:
            print("Stopping on first failure.")
            return exit_code
        if args.delay > 0 and index < args.count:
            time.sleep(args.delay)

    return 0


if __name__ == "__main__":
    sys.exit(main())
