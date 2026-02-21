from datetime import datetime, timezone

from app.db_connection import connect


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_project_id_for_source_builder(source_builder_id: str) -> int | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT project_id
            FROM import_builder_map
            WHERE source_builder_id = ?
            """,
            (source_builder_id,),
        ).fetchone()
    if not row:
        return None
    return int(row["project_id"])


def upsert_builder_map(source_builder_id: str, project_id: int) -> None:
    now = _utc_now()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO import_builder_map (source_builder_id, project_id, imported_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(source_builder_id) DO UPDATE SET
                project_id = excluded.project_id,
                updated_at = excluded.updated_at
            """,
            (source_builder_id, project_id, now, now),
        )
        conn.commit()


def get_checkin_map_for_source_builder(source_builder_id: str) -> dict | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT source_checkin_id, source_builder_id, week_of, project_id
            FROM import_checkin_map
            WHERE source_builder_id = ?
            ORDER BY updated_at DESC, imported_at DESC
            LIMIT 1
            """,
            (source_builder_id,),
        ).fetchone()
    return dict(row) if row else None


def upsert_checkin_map(
    source_checkin_id: str,
    source_builder_id: str,
    week_of: str,
    project_id: int,
) -> None:
    now = _utc_now()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO import_checkin_map (
                source_checkin_id, source_builder_id, week_of, project_id, imported_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_checkin_id) DO UPDATE SET
                source_builder_id = excluded.source_builder_id,
                week_of = excluded.week_of,
                project_id = excluded.project_id,
                updated_at = excluded.updated_at
            """,
            (source_checkin_id, source_builder_id, week_of, project_id, now, now),
        )
        conn.execute(
            """
            UPDATE import_checkin_map
            SET source_checkin_id = ?, project_id = ?, updated_at = ?
            WHERE source_builder_id = ? AND week_of = ? AND source_checkin_id != ?
            """,
            (source_checkin_id, project_id, now, source_builder_id, week_of, source_checkin_id),
        )
        conn.commit()


def list_import_item_ids_for_project(project_id: int) -> list[int]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT item_id
            FROM import_item_map
            WHERE project_id = ?
            ORDER BY item_id
            """,
            (project_id,),
        ).fetchall()
    return [int(row["item_id"]) for row in rows]


def replace_import_item_ids_for_project(project_id: int, item_ids: list[int]) -> None:
    now = _utc_now()
    with connect() as conn:
        conn.execute(
            """
            DELETE FROM import_item_map
            WHERE project_id = ?
            """,
            (project_id,),
        )
        if item_ids:
            conn.executemany(
                """
                INSERT INTO import_item_map (project_id, item_id, imported_at)
                VALUES (?, ?, ?)
                """,
                [(project_id, item_id, now) for item_id in item_ids],
            )
        conn.commit()
