from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from app.builder_import_llm import DEFAULT_IMPORT_LLM_MODEL, enrich_payload_with_llm
from app.builder_import_source import SourceBuilderRecord, load_source_snapshot
from app.db_connection import connect
from app.db_import_content import (
    replace_import_notes,
    replace_import_snapshot_items,
    seed_resident_summary_if_empty,
)
from app.db_import_map import (
    get_checkin_map_for_source_builder,
    get_project_id_for_source_builder,
    upsert_builder_map,
    upsert_checkin_map,
)
from app.builder_import_transform import build_section_payloads


@dataclass
class ImportReport:
    builders_scanned: int = 0
    builders_imported: int = 0
    builders_updated: int = 0
    builders_skipped: int = 0
    builders_without_checkins: int = 0
    latest_checkins_created: int = 0
    latest_checkins_updated: int = 0
    latest_checkins_skipped: int = 0
    missing_progress_latest: int = 0
    house_warnings: list[str] = field(default_factory=list)
    llm_attempted: int = 0
    llm_enriched: int = 0
    llm_low_confidence: int = 0
    llm_errors: int = 0
    llm_error_types: dict[str, int] = field(default_factory=dict)
    llm_error_samples: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ImportConfig:
    source_db: str
    dry_run: bool = True
    enable_llm: bool = False
    llm_model: str = DEFAULT_IMPORT_LLM_MODEL
    llm_confidence_threshold: float = 0.7
    llm_timeout_seconds: float = 20.0


@dataclass(frozen=True)
class ImportProgressEvent:
    current: int
    total: int
    source_builder_id: str
    full_name: str
    phase: str
    detail: str = ""


ProgressCallback = Callable[[ImportProgressEvent], None]


def build_objective_seed(builder: SourceBuilderRecord) -> str:
    metric = builder.north_star_metric_name.strip()
    unit = builder.north_star_metric_unit.strip()
    if metric and unit:
        return f"{metric} ({unit})"
    if metric:
        return f"{metric}"
    return ""


def run_import(config: ImportConfig, progress_callback: ProgressCallback | None = None) -> ImportReport:
    snapshot = load_source_snapshot(config.source_db)
    report = ImportReport(house_warnings=list(snapshot.house_warnings))
    total_builders = len(snapshot.builders)
    for idx, builder in enumerate(snapshot.builders, start=1):
        if progress_callback:
            progress_callback(
                ImportProgressEvent(
                    current=idx,
                    total=total_builders,
                    source_builder_id=builder.source_builder_id,
                    full_name=builder.full_name,
                    phase="builder_start",
                )
            )
        report.builders_scanned += 1
        if not builder.source_builder_id.strip():
            report.errors.append("Encountered builder with empty source_builder_id.")
            if progress_callback:
                progress_callback(
                    ImportProgressEvent(
                        current=idx,
                        total=total_builders,
                        source_builder_id=builder.source_builder_id,
                        full_name=builder.full_name,
                        phase="builder_done",
                        detail="error: missing source_builder_id",
                    )
                )
            continue
        if not builder.full_name.strip():
            report.errors.append(
                f"{builder.source_builder_id}: missing full_name; skipped builder."
            )
            if progress_callback:
                progress_callback(
                    ImportProgressEvent(
                        current=idx,
                        total=total_builders,
                        source_builder_id=builder.source_builder_id,
                        full_name=builder.full_name,
                        phase="builder_done",
                        detail="error: missing full_name",
                    )
                )
            continue
        if builder.latest_checkin is None:
            report.builders_without_checkins += 1
        elif builder.latest_checkin.north_star_value is None:
            report.missing_progress_latest += 1
        payload = build_section_payloads(builder, builder.latest_checkin)
        if config.enable_llm and builder.latest_checkin is not None:
            if progress_callback:
                progress_callback(
                    ImportProgressEvent(
                        current=idx,
                        total=total_builders,
                        source_builder_id=builder.source_builder_id,
                        full_name=builder.full_name,
                        phase="llm_start",
                        detail=f"week {builder.latest_checkin.week_of}",
                    )
                )
            report.llm_attempted += 1
            payload, llm_status, llm_error = enrich_payload_with_llm(
                payload=payload,
                checkin=builder.latest_checkin,
                model=config.llm_model,
                confidence_threshold=config.llm_confidence_threshold,
                timeout_seconds=config.llm_timeout_seconds,
            )
            if llm_status == "enriched":
                report.llm_enriched += 1
            elif llm_status == "low_confidence":
                report.llm_low_confidence += 1
            else:
                report.llm_errors += 1
                error_type = (
                    (llm_error.split(":", 1)[0].strip() or "UnknownError")
                    if llm_error
                    else "UnknownError"
                )
                report.llm_error_types[error_type] = report.llm_error_types.get(error_type, 0) + 1
                if llm_error and len(report.llm_error_samples) < 5:
                    report.llm_error_samples.append(
                        f"{builder.source_builder_id} week {builder.latest_checkin.week_of}: {llm_error}"
                    )
            if progress_callback:
                progress_callback(
                    ImportProgressEvent(
                        current=idx,
                        total=total_builders,
                        source_builder_id=builder.source_builder_id,
                        full_name=builder.full_name,
                        phase="llm_done",
                        detail=llm_status,
                    )
                )

        try:
            action, project_id = _upsert_builder_project(builder, config.dry_run)
        except Exception as exc:  # pragma: no cover - defensive logging path
            report.errors.append(f"{builder.source_builder_id}: {exc}")
            if progress_callback:
                progress_callback(
                    ImportProgressEvent(
                        current=idx,
                        total=total_builders,
                        source_builder_id=builder.source_builder_id,
                        full_name=builder.full_name,
                        phase="builder_done",
                        detail=f"error: {exc}",
                    )
                )
            continue

        if action == "created":
            report.builders_imported += 1
        elif action == "updated":
            report.builders_updated += 1
        else:
            report.builders_skipped += 1

        if builder.latest_checkin is None:
            report.latest_checkins_skipped += 1
        else:
            existing_checkin = get_checkin_map_for_source_builder(builder.source_builder_id)
            checkin_action = "created"
            if existing_checkin:
                if existing_checkin.get("source_checkin_id") == builder.latest_checkin.source_checkin_id:
                    checkin_action = "skipped"
                else:
                    checkin_action = "updated"
            if not config.dry_run:
                upsert_checkin_map(
                    source_checkin_id=builder.latest_checkin.source_checkin_id,
                    source_builder_id=builder.source_builder_id,
                    week_of=builder.latest_checkin.week_of,
                    project_id=project_id,
                )
            if checkin_action == "created":
                report.latest_checkins_created += 1
            elif checkin_action == "updated":
                report.latest_checkins_updated += 1
            else:
                report.latest_checkins_skipped += 1

        if not config.dry_run:
            replace_import_snapshot_items(project_id, payload)
            replace_import_notes(project_id, payload.question_notes)
            seed_resident_summary_if_empty(project_id, payload.summary)
        if progress_callback:
            progress_callback(
                ImportProgressEvent(
                    current=idx,
                    total=total_builders,
                    source_builder_id=builder.source_builder_id,
                    full_name=builder.full_name,
                    phase="builder_done",
                    detail=action,
                )
            )
    return report


def _upsert_builder_project(builder: SourceBuilderRecord, dry_run: bool) -> tuple[str, int]:
    mapped_project_id = get_project_id_for_source_builder(builder.source_builder_id)
    objective_seed = build_objective_seed(builder)

    if mapped_project_id is None:
        if dry_run:
            return "created", -1
        project_id = _create_project(builder.full_name, builder.normalized_house)
        if objective_seed:
            _set_objective_if_empty(project_id, objective_seed)
        upsert_builder_map(builder.source_builder_id, project_id)
        return "created", project_id

    current = _get_project_identity(mapped_project_id)
    if not current:
        if dry_run:
            return "created", mapped_project_id
        project_id = _create_project(builder.full_name, builder.normalized_house)
        if objective_seed:
            _set_objective_if_empty(project_id, objective_seed)
        upsert_builder_map(builder.source_builder_id, project_id)
        return "created", project_id

    changed = False
    if current["name"] != builder.full_name or current["house"] != builder.normalized_house:
        changed = True
    if objective_seed and not (current["objective"] or "").strip():
        changed = True

    if dry_run:
        return ("updated" if changed else "skipped"), mapped_project_id

    if current["name"] != builder.full_name or current["house"] != builder.normalized_house:
        _update_project_identity(mapped_project_id, builder.full_name, builder.normalized_house)
    if objective_seed:
        _set_objective_if_empty(mapped_project_id, objective_seed)
    upsert_builder_map(builder.source_builder_id, mapped_project_id)
    return ("updated" if changed else "skipped"), mapped_project_id


def _create_project(name: str, house: str) -> int:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO projects (
                name, house, progress, goal, residency_start_date, residency_end_date,
                questions, summary, objective, archived
            )
            VALUES (?, ?, 0, 100, strftime('%Y-01-01', 'now'), strftime('%Y-01-31', 'now'), '', '', '', 0)
            """,
            (name, house),
        )
        project_id = int(cursor.lastrowid)
        conn.commit()
    return project_id


def _get_project_identity(project_id: int) -> dict | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT id, name, house, objective FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()
    return dict(row) if row else None


def _update_project_identity(project_id: int, name: str, house: str) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE projects SET name = ?, house = ? WHERE id = ?",
            (name, house, project_id),
        )
        conn.commit()


def _set_objective_if_empty(project_id: int, objective_seed: str) -> None:
    with connect() as conn:
        row = conn.execute(
            "SELECT objective FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()
        if not row or (row["objective"] or "").strip():
            return
        conn.execute(
            "UPDATE projects SET objective = ? WHERE id = ?",
            (objective_seed, project_id),
        )
        conn.commit()
