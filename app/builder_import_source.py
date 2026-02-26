from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from pathlib import Path

from app.house import DEFAULT_HOUSE, normalize_house


@dataclass(frozen=True)
class SourceCheckinRecord:
    source_checkin_id: str
    source_builder_id: str
    week_of: str
    north_star_value: float | None
    textual_data: str
    llm_summary: str
    traction_text: str
    positive_summary: str
    blockers_text: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class SourceBuilderRecord:
    source_builder_id: str
    full_name: str
    email: str
    north_star_metric_name: str
    north_star_metric_unit: str
    source_house_name: str
    normalized_house: str
    ca_name: str
    checkins: list[SourceCheckinRecord]
    latest_checkin: SourceCheckinRecord | None


@dataclass(frozen=True)
class SourceSnapshot:
    builders: list[SourceBuilderRecord]
    house_warnings: list[str]


def normalize_source_house_name(source_house_name: str | None) -> tuple[str, bool]:
    candidate = (source_house_name or "").strip()
    if not candidate:
        return DEFAULT_HOUSE, False
    try:
        return normalize_house(candidate), False
    except ValueError:
        return DEFAULT_HOUSE, True


def load_source_snapshot(sqlite_path: str) -> SourceSnapshot:
    path = Path(sqlite_path)
    if not path.exists():
        raise FileNotFoundError(f"Source DB not found: {sqlite_path}")

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        builder_rows = conn.execute(
            """
            SELECT
                b.id AS source_builder_id,
                b.full_name,
                COALESCE(b.email, '') AS email,
                COALESCE(b.north_star_metric_name, '') AS north_star_metric_name,
                COALESCE(b.north_star_metric_unit, '') AS north_star_metric_unit,
                COALESCE(h.name, '') AS source_house_name,
                COALESCE(ca.full_name, '') AS ca_name
            FROM builders b
            LEFT JOIN community_architects ca ON ca.id = b.ca_id
            LEFT JOIN houses h ON h.id = ca.house_id
            ORDER BY b.full_name COLLATE NOCASE, b.id
            """
        ).fetchall()

        checkin_rows = conn.execute(
            """
            SELECT
                id AS source_checkin_id,
                builder_id AS source_builder_id,
                week_of,
                north_star_value,
                COALESCE(textual_data, '') AS textual_data,
                COALESCE(llm_summary, '') AS llm_summary,
                COALESCE(traction_text, '') AS traction_text,
                COALESCE(positive_summary, '') AS positive_summary,
                COALESCE(blockers_text, '') AS blockers_text,
                COALESCE(created_at, '') AS created_at,
                COALESCE(updated_at, '') AS updated_at
            FROM weekly_checkins
            """
        ).fetchall()
    finally:
        conn.close()

    checkins_by_builder: dict[str, list[SourceCheckinRecord]] = {}
    for row in checkin_rows:
        checkin = SourceCheckinRecord(
            source_checkin_id=row["source_checkin_id"],
            source_builder_id=row["source_builder_id"],
            week_of=row["week_of"],
            north_star_value=row["north_star_value"],
            textual_data=row["textual_data"],
            llm_summary=row["llm_summary"],
            traction_text=row["traction_text"],
            positive_summary=row["positive_summary"],
            blockers_text=row["blockers_text"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
        checkins_by_builder.setdefault(row["source_builder_id"], []).append(checkin)

    def _checkin_sort_key(checkin: SourceCheckinRecord) -> tuple[str, str, str, str]:
        return (
            checkin.week_of or "",
            checkin.updated_at or "",
            checkin.created_at or "",
            checkin.source_checkin_id,
        )

    for source_builder_id, records in checkins_by_builder.items():
        checkins_by_builder[source_builder_id] = sorted(records, key=_checkin_sort_key)

    builders: list[SourceBuilderRecord] = []
    house_warnings: list[str] = []
    for row in builder_rows:
        normalized_house, warned = normalize_source_house_name(row["source_house_name"])
        if warned:
            house_warnings.append(
                f"Unknown source house '{row['source_house_name']}' for builder {row['full_name']} "
                f"({row['source_builder_id']}); defaulted to {DEFAULT_HOUSE}."
            )
        checkins = checkins_by_builder.get(row["source_builder_id"], [])
        builders.append(
            SourceBuilderRecord(
                source_builder_id=row["source_builder_id"],
                full_name=row["full_name"],
                email=row["email"],
                north_star_metric_name=row["north_star_metric_name"],
                north_star_metric_unit=row["north_star_metric_unit"],
                source_house_name=row["source_house_name"],
                normalized_house=normalized_house,
                ca_name=row["ca_name"],
                checkins=checkins,
                latest_checkin=(checkins[-1] if checkins else None),
            )
        )
    return SourceSnapshot(builders=builders, house_warnings=house_warnings)
