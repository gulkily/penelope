#!/usr/bin/env python3
"""Small task runner for common developer commands."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_command(command: list[str]) -> int:
    result = subprocess.run(command, check=False)
    return result.returncode


def print_venv_help() -> int:
    venv_path = REPO_ROOT / ".venv"
    print("Activate the virtual environment:")
    print(f"  python3 -m venv {venv_path}")
    print("  source .venv/bin/activate")
    return 0


def install_requirements() -> int:
    return run_command(["python3", "-m", "pip", "install", "-r", "requirements.txt"])


def start_server() -> int:
    return run_command(["./start.sh"])


def run_tests(scope: str | None) -> int:
    if scope == "e2e":
        return run_command(["python3", "-m", "pytest", "tests/e2e"])
    if scope == "http":
        return run_command(["python3", "-m", "pytest", "tests/http"])
    return run_command(["python3", "-m", "pytest"])


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

    test_parser = subparsers.add_parser("test", help="Run tests.")
    test_parser.add_argument(
        "scope",
        nargs="?",
        choices=["e2e", "http"],
        help="Optional scope: e2e or http (default: all).",
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
        return run_tests(args.scope)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
