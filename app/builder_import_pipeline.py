from __future__ import annotations

from dataclasses import dataclass, field

from app.builder_import_source import SourceBuilderRecord, load_source_snapshot
from app.db_connection import connect
from app.db_import_content import replace_import_notes, replace_import_snapshot_items
from app.db_import_map import (
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
    latest_checkins_imported: int = 0
    latest_checkins_skipped: int = 0
    missing_progress_latest: int = 0
    house_warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ImportConfig:
    source_db: str
    dry_run: bool = True


def build_objective_seed(builder: SourceBuilderRecord) -> str:
    metric = builder.north_star_metric_name.strip()
    unit = builder.north_star_metric_unit.strip()
    if metric and unit:
        return f"North Star: {metric} ({unit})."
    if metric:
        return f"North Star: {metric}."
    return ""


def run_import(config: ImportConfig) -> ImportReport:
    snapshot = load_source_snapshot(config.source_db)
    report = ImportReport(house_warnings=list(snapshot.house_warnings))
    for builder in snapshot.builders:
        report.builders_scanned += 1
        if builder.latest_checkin is None:
            report.builders_without_checkins += 1
        elif builder.latest_checkin.north_star_value is None:
            report.missing_progress_latest += 1
        payload = build_section_payloads(builder, builder.latest_checkin)

        try:
            action, project_id = _upsert_builder_project(builder, config.dry_run)
        except Exception as exc:  # pragma: no cover - defensive logging path
            report.errors.append(f"{builder.source_builder_id}: {exc}")
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
            if not config.dry_run:
                upsert_checkin_map(
                    source_checkin_id=builder.latest_checkin.source_checkin_id,
                    source_builder_id=builder.source_builder_id,
                    week_of=builder.latest_checkin.week_of,
                    project_id=project_id,
                )
            report.latest_checkins_imported += 1

        if not config.dry_run:
            replace_import_snapshot_items(project_id, payload)
            replace_import_notes(project_id, payload.question_notes)
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
