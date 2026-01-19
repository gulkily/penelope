from datetime import datetime, timezone

from app.db_connection import connect
from app.db_constants import SECTIONS


def list_items_for_project(project_id: int) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, section, content, created_at FROM items WHERE project_id = ? ORDER BY id",
            (project_id,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "section": row["section"],
            "text": row["content"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def add_item(project_id: int, section: str, text: str) -> dict:
    if section not in SECTIONS:
        raise ValueError(f"Unknown section: {section}")

    with connect() as conn:
        now = datetime.now(timezone.utc).isoformat()
        cursor = conn.execute(
            "INSERT INTO items (project_id, section, content, created_at) VALUES (?, ?, ?, ?)",
            (project_id, section, text, now),
        )
        conn.commit()
        item_id = cursor.lastrowid

    return {"id": item_id, "section": section, "text": text, "created_at": now}


def update_item(item_id: int, text: str) -> dict | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT id, section FROM items WHERE id = ?",
            (item_id,),
        ).fetchone()
        if not row:
            return None
        conn.execute(
            "UPDATE items SET content = ? WHERE id = ?",
            (text, item_id),
        )
        conn.commit()
    return {"id": row["id"], "section": row["section"], "text": text}


def delete_item(item_id: int) -> bool:
    with connect() as conn:
        cursor = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
    return cursor.rowcount > 0
