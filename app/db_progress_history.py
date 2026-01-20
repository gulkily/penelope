from __future__ import annotations

from datetime import datetime, timezone
import sqlite3

from app.db_connection import connect

COALESCE_WINDOW_SECONDS = 60


def log_progress_history(
    project_id: int,
    progress: int,
    recorded_at: str | None = None,
    conn: sqlite3.Connection | None = None,
) -> None:
    timestamp = recorded_at or datetime.now(timezone.utc).isoformat()
    if conn is None:
        with connect() as conn:
            _log_progress_history_with_conn(conn, project_id, progress, timestamp)
            conn.commit()
        return

    _log_progress_history_with_conn(conn, project_id, progress, timestamp)


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


def _log_progress_history_with_conn(
    conn: sqlite3.Connection,
    project_id: int,
    progress: int,
    recorded_at: str,
) -> None:
    latest = conn.execute(
        """
        SELECT id, recorded_at
        FROM progress_history
        WHERE project_id = ? AND recorded_at <= ?
        ORDER BY recorded_at DESC, id DESC
        LIMIT 1
        """,
        (project_id, recorded_at),
    ).fetchone()
    if latest:
        current_time = _parse_iso_timestamp(recorded_at)
        latest_time = _parse_iso_timestamp(latest["recorded_at"])
        delta_seconds = (current_time - latest_time).total_seconds()
        if 0 <= delta_seconds <= COALESCE_WINDOW_SECONDS:
            conn.execute(
                """
                UPDATE progress_history
                SET progress = ?, recorded_at = ?
                WHERE id = ?
                """,
                (progress, recorded_at, latest["id"]),
            )
            return

    conn.execute(
        """
        INSERT INTO progress_history (project_id, progress, recorded_at)
        VALUES (?, ?, ?)
        """,
        (project_id, progress, recorded_at),
    )


def _parse_iso_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _row_to_history_entry(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "project_id": row["project_id"],
        "progress": row["progress"],
        "recorded_at": row["recorded_at"],
    }
