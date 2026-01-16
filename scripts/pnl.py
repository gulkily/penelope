#!/usr/bin/env python3
"""Small task runner for common developer commands."""

from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_command(command: list[str]) -> int:
    result = subprocess.run(command, check=False)
    return result.returncode


def has_xdist() -> bool:
    return importlib.util.find_spec("xdist") is not None


def print_venv_help() -> int:
    active_venv = os.getenv("VIRTUAL_ENV")
    if active_venv:
        print(f"Virtualenv already active: {active_venv}")
        return 0
    venv_path = REPO_ROOT / ".venv"
    print("Activate the virtual environment:")
    print(f"  python3 -m venv {venv_path}")
    print("  source .venv/bin/activate")
    print("  Tip: source ./pnl venv")
    return 0


def install_requirements() -> int:
    return run_command(["python3", "-m", "pip", "install", "-r", "requirements.txt"])


def start_server() -> int:
    return run_command(["./start.sh"])


def run_tests(
    scope: str | None,
    headed: bool,
    loop_count: int | None,
    delay: float,
    keep_going: bool,
    workers: int | None,
    dist: str | None,
    duration: float | None,
) -> int:
    if loop_count is not None and loop_count <= 0:
        print("--loop must be a positive integer.", file=sys.stderr)
        return 2
    if duration is not None and duration <= 0:
        print("--duration must be a positive number.", file=sys.stderr)
        return 2
    if loop_count is not None and duration is not None:
        print("Use either --loop or --duration, not both.", file=sys.stderr)
        return 2
    if delay < 0:
        print("--delay cannot be negative.", file=sys.stderr)
        return 2
    if workers is not None and workers <= 0:
        print("--workers must be a positive integer.", file=sys.stderr)
        return 2
    if dist is not None and workers is None:
        print("--dist requires --workers.", file=sys.stderr)
        return 2
    if workers is not None and not has_xdist():
        print(
            "pytest-xdist is required for --workers. "
            "Install dependencies with `./pnl install` or "
            "`pip install -r requirements.txt`.",
            file=sys.stderr,
        )
        return 2

    if loop_count is not None or duration is not None:
        command = ["python3", "scripts/run_e2e_loop.py"]
        if loop_count is not None:
            command.append(str(loop_count))
        if duration is not None:
            command.extend(["--duration", str(duration)])
        if scope is None:
            command.extend(["--scope", "all"])
        else:
            command.extend(["--scope", scope])
        if headed:
            command.append("--headed")
        if delay > 0:
            command.extend(["--delay", str(delay)])
        if keep_going:
            command.append("--keep-going")
        if workers is not None:
            command.extend(["--workers", str(workers)])
        if dist is not None:
            command.extend(["--dist", dist])
        return run_command(command)

    command = ["python3", "-m", "pytest"]
    if scope == "e2e":
        command.append("tests/e2e")
    elif scope == "http":
        command.append("tests/http")
    if headed:
        command.append("--headed")
    if workers is not None:
        command.extend(["-n", str(workers)])
    if dist is not None:
        command.extend(["--dist", dist])
    return run_command(command)


def run_seed_demo(allow_duplicates: bool) -> int:
    command = ["python3", "scripts/seed_demo_data.py"]
    if allow_duplicates:
        command.append("--allow-duplicates")
    return run_command(command)


def parse_args() -> tuple[argparse.ArgumentParser, argparse.Namespace]:
    parser = argparse.ArgumentParser(
        prog="pnl",
        description="Penelope task runner.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("help", help="Show help output.")
    subparsers.add_parser("venv", help="Show venv activation help.")
    subparsers.add_parser("install", help="Install Python dependencies.")
    subparsers.add_parser("start", help="Start the development server.")

    test_parser = subparsers.add_parser(
        "test",
        help="Run tests.",
        description=(
            "Run test suites. Default runs all tests. "
            "Use --loop or --duration to repeat tests."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  ./pnl test\n"
            "  ./pnl test e2e\n"
            "  ./pnl test e2e --headed\n"
            "  ./pnl test e2e --loop 100\n"
            "  ./pnl test --loop 10 --workers 4\n"
            "  ./pnl test http --loop 10 --delay 1 --keep-going\n"
            "  ./pnl test --duration 60 --workers 2\n"
        ),
    )
    test_parser.add_argument(
        "scope",
        nargs="?",
        choices=["e2e", "http"],
        help="Optional scope: e2e or http (default: all).",
    )
    test_parser.add_argument(
        "--headed",
        action="store_true",
        help="Run E2E tests with a visible browser.",
    )
    test_parser.add_argument(
        "--loop",
        type=int,
        help="Repeat tests N times using scripts/run_e2e_loop.py.",
    )
    test_parser.add_argument(
        "--duration",
        type=float,
        help="Run looped tests for N seconds using scripts/run_e2e_loop.py.",
    )
    test_parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Delay between looped runs (seconds).",
    )
    test_parser.add_argument(
        "--keep-going",
        action="store_true",
        help="Continue looping after a test failure.",
    )
    test_parser.add_argument(
        "--workers",
        type=int,
        help="Run tests with N parallel workers (pytest-xdist).",
    )
    test_parser.add_argument(
        "--dist",
        type=str,
        help="xdist distribution mode (requires --workers).",
    )

    seed_parser = subparsers.add_parser(
        "seed-demo",
        help="Seed the database with demo data.",
    )
    seed_parser.add_argument(
        "--allow-duplicates",
        action="store_true",
        help="Insert demo projects even if names already exist.",
    )

    return parser, parser.parse_args()


def main() -> int:
    parser, args = parse_args()
    os.chdir(REPO_ROOT)

    if args.command in (None, "help"):
        parser.print_help()
        return 0

    if args.command == "venv":
        return print_venv_help()
    if args.command == "install":
        return install_requirements()
    if args.command == "start":
        return start_server()
    if args.command == "test":
        return run_tests(
            args.scope,
            args.headed,
            args.loop,
            args.delay,
            args.keep_going,
            args.workers,
            args.dist,
            args.duration,
        )
    if args.command == "seed-demo":
        return run_seed_demo(args.allow_duplicates)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
