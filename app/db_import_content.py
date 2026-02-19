from datetime import datetime, timezone

from app.builder_import_transform import IMPORT_SNAPSHOT_PREFIX, SectionPayloads
from app.db_connection import connect


def replace_import_snapshot_items(project_id: int, payload: SectionPayloads) -> None:
    timestamp = payload.created_at or datetime.now(timezone.utc).isoformat()
    rows = [
        ("summary", payload.summary),
        ("challenges", payload.challenges),
        ("milestones", payload.milestones),
        ("opportunities", payload.opportunities),
    ]
    with connect() as conn:
        conn.execute(
            """
            DELETE FROM items
            WHERE project_id = ? AND content LIKE ?
            """,
            (project_id, f"{IMPORT_SNAPSHOT_PREFIX}%"),
        )
        for section, text in rows:
            if not text.strip():
                continue
            current_max = conn.execute(
                """
                SELECT COALESCE(MAX(sort_order), 0)
                FROM items
                WHERE project_id = ? AND section = ?
                """,
                (project_id, section),
            ).fetchone()[0]
            conn.execute(
                """
                INSERT INTO items (project_id, section, content, sort_order, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, section, text, current_max + 1, timestamp),
            )
        conn.commit()


def replace_import_notes(project_id: int, notes: list[str]) -> None:
    with connect() as conn:
        row = conn.execute(
            "SELECT questions FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()
        if not row:
            return
        existing_questions = (row["questions"] or "").strip()
        kept_lines: list[str] = []
        for line in existing_questions.splitlines():
            if line.strip().startswith("[Import"):
                continue
            kept_lines.append(line)

        merged_notes: list[str] = []
        seen: set[str] = set()
        for note in notes:
            candidate = note.strip()
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            merged_notes.append(candidate)

        sections: list[str] = []
        kept_text = "\n".join([line for line in kept_lines if line.strip()]).strip()
        notes_text = "\n".join(merged_notes).strip()
        if kept_text:
            sections.append(kept_text)
        if notes_text:
            sections.append(notes_text)
        next_questions = "\n\n".join(sections)

        conn.execute(
            "UPDATE projects SET questions = ? WHERE id = ?",
            (next_questions, project_id),
        )
        conn.commit()
