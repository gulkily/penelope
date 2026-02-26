#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shlex
import sqlite3
import subprocess
import sys
import time

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.builder_import_llm import get_llm_debug_info, get_llm_preflight_issues
from app.builder_import_pipeline import ImportConfig, ImportProgressEvent, run_import
from app.builder_import_source import load_source_snapshot
from app.db_connection import get_db_path
from app.db_init import init_db


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load and summarize builder check-in history data from source SQLite.",
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
    total_checkins = sum(len(row.checkins) for row in builders)
    missing_progress = sum(
        len([checkin for checkin in row.checkins if checkin.north_star_value is None])
        for row in builders
    )

    lines = [
        f"Source DB: {Path(source_db)}",
        f"Builders: {len(builders)}",
        f"Weekly check-ins: {total_checkins}",
        f"Builders with latest check-in: {with_checkins}",
        f"Check-ins missing north_star_value: {missing_progress}",
        f"House normalization warnings: {len(snapshot.house_warnings)}",
        "",
        "Sample builders:",
    ]

    for row in builders[: max(0, sample)]:
        checkin_week = row.latest_checkin.week_of if row.latest_checkin else "none"
        lines.append(
            f"- {row.full_name} | house={row.normalized_house} | latest_week={checkin_week} | checkins={len(row.checkins)}"
        )

    if snapshot.house_warnings:
        lines.extend(["", "House warnings:"])
        lines.extend([f"- {warning}" for warning in snapshot.house_warnings])

    return "\n".join(lines)


def _read_import_map_schema_status() -> dict[str, str]:
    target_tables = (
        "import_builder_map",
        "import_checkin_map",
        "import_item_map",
    )
    db_path = get_db_path()
    if not db_path.exists():
        return {table: "no" for table in target_tables}

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name IN ('import_builder_map', 'import_checkin_map', 'import_item_map')
            """
        ).fetchall()
    finally:
        conn.close()

    existing = {str(row[0]) for row in rows}
    return {table: ("yes" if table in existing else "no") for table in target_tables}


def ensure_import_map_tables() -> None:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS import_builder_map (
                source_builder_id TEXT PRIMARY KEY,
                project_id INTEGER UNIQUE NOT NULL,
                imported_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS import_checkin_map (
                source_checkin_id TEXT PRIMARY KEY,
                source_builder_id TEXT NOT NULL,
                week_of TEXT NOT NULL,
                project_id INTEGER NOT NULL,
                imported_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(source_builder_id, week_of)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS import_item_map (
                project_id INTEGER NOT NULL,
                item_id INTEGER PRIMARY KEY,
                imported_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_import_builder_project
            ON import_builder_map (project_id)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_import_checkin_builder_week
            ON import_checkin_map (source_builder_id, week_of)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_import_item_project
            ON import_item_map (project_id)
            """
        )
        conn.commit()
    finally:
        conn.close()


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


def render_runtime_fingerprint(
    llm_debug: dict[str, str],
    import_schema_before: dict[str, str] | None = None,
    import_schema_after: dict[str, str] | None = None,
) -> str:
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
        f"- target_db_path: {get_db_path()}",
        f"- python_executable: {llm_debug['python_executable']}",
        f"- dedalus_sdk_version: {llm_debug['dedalus_sdk_version']}",
    ]
    if import_schema_before is not None:
        lines.append(
            "- import_map_schema_before: "
            f"builder={import_schema_before['import_builder_map']}, "
            f"checkin={import_schema_before['import_checkin_map']}, "
            f"item={import_schema_before['import_item_map']}"
        )
    if import_schema_after is not None:
        lines.append(
            "- import_map_schema_after: "
            f"builder={import_schema_after['import_builder_map']}, "
            f"checkin={import_schema_after['import_checkin_map']}, "
            f"item={import_schema_after['import_item_map']}"
        )
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
        f"Check-ins scanned: {report.checkins_scanned}",
        f"Check-ins created: {report.checkins_created}",
        f"Check-ins updated: {report.checkins_updated}",
        f"Check-ins skipped: {report.checkins_skipped}",
        f"Check-ins missing north_star_value: {report.missing_progress_checkins}",
        f"Latest check-ins missing north_star_value: {report.missing_progress_latest}",
        f"Imported items inserted: {report.imported_items_inserted}",
        f"Exact duplicates skipped: {report.exact_duplicates_skipped}",
        f"Near-duplicates skipped: {report.near_duplicates_skipped}",
        f"LLM duplicate arbitration attempted: {report.llm_duplicate_arbitration_attempted}",
        f"LLM duplicate arbitration kept: {report.llm_duplicate_arbitration_kept}",
        f"LLM duplicate arbitration dropped: {report.llm_duplicate_arbitration_dropped}",
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
    import_schema_before = _read_import_map_schema_status()
    ensure_import_map_tables()
    import_schema_after = _read_import_map_schema_status()
    llm_debug = get_llm_debug_info()
    llm_preflight_issues: list[str] = []
    if args.enable_llm:
        llm_debug, llm_preflight_issues = get_llm_preflight_issues()
    print(render_snapshot_preview(args.source_db, args.sample))
    print("")
    print(
        render_runtime_fingerprint(
            llm_debug,
            import_schema_before=import_schema_before,
            import_schema_after=import_schema_after,
        )
    )
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
