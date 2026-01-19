from __future__ import annotations

from datetime import datetime, timezone
import sqlite3

from app.db_connection import connect


def log_progress_history(
    project_id: int,
    progress: int,
    recorded_at: str | None = None,
    conn: sqlite3.Connection | None = None,
) -> None:
    timestamp = recorded_at or datetime.now(timezone.utc).isoformat()
    if conn is None:
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO progress_history (project_id, progress, recorded_at)
                VALUES (?, ?, ?)
                """,
                (project_id, progress, timestamp),
            )
        return

    conn.execute(
        """
        INSERT INTO progress_history (project_id, progress, recorded_at)
        VALUES (?, ?, ?)
        """,
        (project_id, progress, timestamp),
    )


def list_progress_history(
    project_id: int,
    limit: int | None = None,
) -> list[dict]:
    query = """
        SELECT id, project_id, progress, recorded_at
        FROM progress_history
        WHERE project_id = ?
        ORDER BY recorded_at ASC, id ASC
    """
    params: list[int] = [project_id]
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
    with connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_history_entry(row) for row in rows]


def _row_to_history_entry(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "project_id": row["project_id"],
        "progress": row["progress"],
        "recorded_at": row["recorded_at"],
    }
