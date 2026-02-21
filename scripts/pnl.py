#!/usr/bin/env python3
"""Small task runner for common developer commands."""

from __future__ import annotations

import argparse
import importlib.util
import os
import signal
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


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
    process = subprocess.Popen(["./start.sh"])

    def handle_signal(signum, _frame) -> None:
        if process.poll() is None:
            process.send_signal(signum)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        return process.wait()
    except KeyboardInterrupt:
        handle_signal(signal.SIGINT, None)
        return process.wait()


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


def run_env_sync() -> int:
    from app.env_sync import get_missing_env_defaults
    from app.env_sync import sync_env_defaults

    env_path = REPO_ROOT / ".env"
    env_example_path = REPO_ROOT / ".env.example"

    try:
        status = get_missing_env_defaults(env_path=env_path, env_example_path=env_example_path)
    except OSError as exc:
        print(f"Failed to check env defaults: {exc}", file=sys.stderr)
        return 1

    if not status.get("example_found"):
        print(f"Missing defaults file: {env_example_path}", file=sys.stderr)
        return 1

    missing_count = int(status.get("missing_count", 0))
    if missing_count <= 0:
        print("No missing .env settings found. Nothing to sync.")
        return 0

    try:
        result = sync_env_defaults(env_path=env_path, env_example_path=env_example_path)
    except OSError as exc:
        print(f"Failed to sync .env defaults: {exc}", file=sys.stderr)
        return 1

    if not result.get("updated"):
        print("No missing .env settings found. Nothing to sync.")
        return 0

    added_count = int(result.get("added_count", 0))
    if result.get("env_created"):
        print(f"Created .env and added {added_count} default setting(s) from .env.example.")
    else:
        print(f"Added {added_count} missing setting(s) to .env from .env.example.")
    return 0


def run_magic_link_command(
    admin_username: str,
    target_username: str,
    base_url: str,
) -> int:
    from app import auth
    from app import db
    from app.magic_link_service import issue_magic_link

    admin_candidate = admin_username.strip()
    target_candidate = target_username.strip()
    if not admin_candidate:
        print("--admin-username is required.", file=sys.stderr)
        return 2
    if not target_candidate:
        print("--username is required.", file=sys.stderr)
        return 2

    db.init_db()
    admin_account = db.get_account_by_username_case_insensitive(admin_candidate)
    if not admin_account:
        print(
            f"Admin account not found for username: {admin_candidate}",
            file=sys.stderr,
        )
        return 2
    account_id = int(admin_account["id"])
    if not auth.is_admin_account(account_id):
        print(
            f"Account '{admin_account['username']}' is not authorized to issue magic links.",
            file=sys.stderr,
        )
        return 2

    try:
        issued = issue_magic_link(
            configured_username=target_candidate,
            issuer_account_id=account_id,
            base_url=base_url,
        )
    except ValueError as exc:
        print(f"Failed to issue magic link: {exc}", file=sys.stderr)
        return 2

    print("Magic link issued")
    print(f"issuer_username: {admin_account['username']}")
    print(f"target_username: {issued['configured_username']}")
    print(f"token_id: {issued['token_id']}")
    print(f"magic_link: {issued['magic_link']}")
    return 0


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
    subparsers.add_parser(
        "runserver",
        help="Alias for start.",
    )

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

    subparsers.add_parser(
        "env-sync",
        help="Append missing .env settings from .env.example.",
    )

    magic_link_parser = subparsers.add_parser(
        "magic-link",
        help="Generate an admin-issued magic login link for a username.",
    )
    magic_link_parser.add_argument(
        "--admin-username",
        required=True,
        help="Issuer username that must be admin-authorized.",
    )
    magic_link_parser.add_argument(
        "--username",
        required=True,
        help="Target username embedded in the generated magic link.",
    )
    magic_link_parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base app URL used to compose the output link.",
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
    if args.command in ("start", "runserver"):
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
    if args.command == "env-sync":
        return run_env_sync()
    if args.command == "magic-link":
        return run_magic_link_command(
            admin_username=args.admin_username,
            target_username=args.username,
            base_url=args.base_url,
        )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
