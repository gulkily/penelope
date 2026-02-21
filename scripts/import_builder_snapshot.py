#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shlex
import subprocess
import sys
import time

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.builder_import_llm import get_llm_debug_info, get_llm_preflight_issues
from app.builder_import_pipeline import ImportConfig, ImportProgressEvent, run_import
from app.builder_import_source import load_source_snapshot
from app.db_init import init_db


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load and summarize latest builder snapshot data from source SQLite.",
    )
    parser.add_argument(
        "--source-db",
        default="data/builder_import_source.db",
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
    parser.add_argument(
        "--enable-llm",
        action="store_true",
        help="Enable optional LLM enrichment for section text.",
    )
    parser.add_argument(
        "--llm-model",
        default="openai/gpt-5.2",
        help="Dedalus model ID for enrichment (default: openai/gpt-5.2).",
    )
    parser.add_argument(
        "--llm-confidence-threshold",
        type=float,
        default=0.7,
        help="Confidence threshold for accepting LLM output (default: 0.7).",
    )
    parser.add_argument(
        "--llm-timeout-seconds",
        type=float,
        default=20.0,
        help="Per-checkin LLM timeout in seconds (default: 20.0).",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable real-time progress output while import is running.",
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


def _sha256_head(path: Path, length: int = 12) -> str:
    try:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return digest[:length]
    except OSError:
        return "unavailable"


def _read_git_value(args: list[str]) -> str:
    try:
        result = subprocess.run(
            args,
            cwd=str(REPO_ROOT),
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return "unavailable"
    if result.returncode != 0:
        return "unavailable"
    return result.stdout.strip()


def render_runtime_fingerprint(llm_debug: dict[str, str]) -> str:
    fingerprint_targets = [
        ("scripts/import_builder_snapshot.py", Path(__file__).resolve()),
        ("app/builder_import_llm.py", REPO_ROOT / "app" / "builder_import_llm.py"),
        (
            "app/builder_import_pipeline.py",
            REPO_ROOT / "app" / "builder_import_pipeline.py",
        ),
    ]
    git_commit = _read_git_value(["git", "rev-parse", "--short", "HEAD"])
    git_status = _read_git_value(["git", "status", "--porcelain"])
    git_dirty = (
        "unavailable" if git_status == "unavailable" else ("yes" if git_status else "no")
    )
    lines = [
        "Runtime fingerprint:",
        f"- argv: {shlex.join(sys.argv)}",
        f"- cwd: {Path.cwd()}",
        f"- repo_root: {REPO_ROOT}",
        f"- script_path: {Path(__file__).resolve()}",
        f"- git_commit: {git_commit}",
        f"- git_dirty: {git_dirty}",
        f"- python_executable: {llm_debug['python_executable']}",
        f"- dedalus_sdk_version: {llm_debug['dedalus_sdk_version']}",
    ]
    for label, path in fingerprint_targets:
        lines.append(f"- sha256[{label}]: {_sha256_head(path)}")
    return "\n".join(lines)


def _build_progress_callback(enabled: bool):
    if not enabled:
        return None

    started = time.perf_counter()

    def _callback(event: ImportProgressEvent) -> None:
        elapsed = time.perf_counter() - started
        progress = f"[{event.current}/{event.total}]"
        if event.phase == "builder_start":
            print(
                f"{progress} {event.full_name} ({event.source_builder_id}) started | +{elapsed:.1f}s",
                flush=True,
            )
        elif event.phase == "llm_start":
            print(f"{progress} LLM started ({event.detail}) | +{elapsed:.1f}s", flush=True)
        elif event.phase == "llm_done":
            print(f"{progress} LLM result={event.detail} | +{elapsed:.1f}s", flush=True)
        elif event.phase == "builder_done":
            print(f"{progress} builder result={event.detail or 'done'} | +{elapsed:.1f}s", flush=True)

    return _callback


def render_import_report(
    config: ImportConfig,
    llm_debug: dict[str, str] | None = None,
    progress_enabled: bool = True,
) -> str:
    report = run_import(config, progress_callback=_build_progress_callback(progress_enabled))
    llm_debug = llm_debug or get_llm_debug_info()
    lines = [
        f"Mode: {'WRITE' if not config.dry_run else 'DRY-RUN'}",
        f"LLM enabled: {'yes' if config.enable_llm else 'no'}",
        f"LLM model: {config.llm_model}",
        f"LLM confidence threshold: {config.llm_confidence_threshold:.2f}",
        f"LLM timeout seconds: {config.llm_timeout_seconds:.2f}",
        f"LLM debug - python executable: {llm_debug['python_executable']}",
        f"LLM debug - dotenv available: {llm_debug['dotenv_available']}",
        f"LLM debug - .env file exists: {llm_debug['dotenv_file_exists']}",
        f"LLM debug - .env loaded: {llm_debug['dotenv_loaded']}",
        f"LLM debug - dedalus SDK available: {llm_debug['dedalus_sdk_available']}",
        f"LLM debug - dedalus SDK version: {llm_debug['dedalus_sdk_version']}",
        f"LLM debug - DEDALUS_API_KEY present: {llm_debug['dedalus_api_key_present']}",
        f"LLM debug - DEDALUS_API_KEY length: {llm_debug['dedalus_api_key_length']}",
        f"Builders scanned: {report.builders_scanned}",
        f"Builders imported: {report.builders_imported}",
        f"Builders updated: {report.builders_updated}",
        f"Builders skipped: {report.builders_skipped}",
        f"Builders without check-ins: {report.builders_without_checkins}",
        f"Latest check-ins created: {report.latest_checkins_created}",
        f"Latest check-ins updated: {report.latest_checkins_updated}",
        f"Latest check-ins skipped: {report.latest_checkins_skipped}",
        f"Latest check-ins missing north_star_value: {report.missing_progress_latest}",
        f"House normalization warnings: {len(report.house_warnings)}",
        f"LLM attempted: {report.llm_attempted}",
        f"LLM enriched: {report.llm_enriched}",
        f"LLM low-confidence fallback: {report.llm_low_confidence}",
        f"LLM errors fallback: {report.llm_errors}",
        f"Errors: {len(report.errors)}",
    ]
    if report.house_warnings:
        lines.extend(["", "House warnings:"])
        lines.extend([f"- {warning}" for warning in report.house_warnings])
    if report.errors:
        lines.extend(["", "Errors:"])
        lines.extend([f"- {error}" for error in report.errors])
    if report.llm_error_types:
        lines.extend(["", "LLM error type counts:"])
        for error_type in sorted(report.llm_error_types):
            lines.append(f"- {error_type}: {report.llm_error_types[error_type]}")
    if report.llm_error_samples:
        lines.extend(["", "LLM error samples:"])
        lines.extend([f"- {error}" for error in report.llm_error_samples])
    return "\n".join(lines)


def main() -> int:
    args = build_parser().parse_args()
    init_db()
    llm_debug = get_llm_debug_info()
    llm_preflight_issues: list[str] = []
    if args.enable_llm:
        llm_debug, llm_preflight_issues = get_llm_preflight_issues()
    print(render_snapshot_preview(args.source_db, args.sample))
    print("")
    print(render_runtime_fingerprint(llm_debug))
    print("")
    if llm_preflight_issues:
        print("LLM preflight failed. Skipping import run.")
        print(f"- python executable: {llm_debug['python_executable']}")
        print(f"- dedalus SDK available: {llm_debug['dedalus_sdk_available']}")
        print(f"- dedalus SDK version: {llm_debug['dedalus_sdk_version']}")
        print(f"- DEDALUS_API_KEY present: {llm_debug['dedalus_api_key_present']}")
        print(f"- DEDALUS_API_KEY length: {llm_debug['dedalus_api_key_length']}")
        print("")
        print("Fixes:")
        for issue in llm_preflight_issues:
            print(f"- {issue}")
        return 2

    try:
        print(
            render_import_report(
                ImportConfig(
                    source_db=args.source_db,
                    dry_run=not args.write,
                    enable_llm=args.enable_llm,
                    llm_model=args.llm_model,
                    llm_confidence_threshold=args.llm_confidence_threshold,
                    llm_timeout_seconds=args.llm_timeout_seconds,
                ),
                llm_debug=llm_debug,
                progress_enabled=not args.no_progress,
            )
        )
    except KeyboardInterrupt:
        print("\nImport interrupted by user.")
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
