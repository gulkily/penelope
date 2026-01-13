from app.db_connection import connect
from app.db_constants import SECTIONS
from app.db_items import list_items_for_project


def list_projects(
    include_archived: bool = False,
    limit: int | None = None,
    offset: int = 0,
    sort_key: str = "id",
    sort_direction: str = "asc",
) -> tuple[list[dict], int]:
    order_map = {
        "id": "id",
        "name": "name COLLATE NOCASE",
        "archived": "archived",
    }
    if sort_key not in order_map:
        raise ValueError("sort_key must be one of: id, name, archived")
    if sort_direction not in ("asc", "desc"):
        raise ValueError("sort_dir must be asc or desc")
    if offset < 0:
        raise ValueError("offset must be >= 0")

    direction = "ASC" if sort_direction == "asc" else "DESC"
    order_clause = f"{order_map[sort_key]} {direction}"
    if sort_key != "id":
        order_clause += ", id ASC"

    query = "SELECT id, name, archived FROM projects"
    count_query = "SELECT COUNT(*) FROM projects"
    params: list[int] = []
    if not include_archived:
        query += " WHERE archived = 0"
        count_query += " WHERE archived = 0"
    query += f" ORDER BY {order_clause}"
    if limit is not None:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
    with connect() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()
        total = conn.execute(count_query).fetchone()[0]
    projects = [
        {"id": row["id"], "name": row["name"], "archived": bool(row["archived"])}
        for row in rows
    ]
    return projects, total


def get_project(project_id: int) -> dict | None:
    with connect() as conn:
        project_row = conn.execute(
            """
            SELECT id, name, progress, questions, objective, archived
            FROM projects
            WHERE id = ?
            """,
            (project_id,),
        ).fetchone()
        if not project_row:
            return None

    items = list_items_for_project(project_id)
    sections: dict[str, list[dict]] = {section: [] for section in SECTIONS}
    for item in items:
        sections[item["section"]].append({"id": item["id"], "text": item["text"]})

    return {
        "id": project_row["id"],
        "name": project_row["name"],
        "progress": project_row["progress"],
        "objective": project_row["objective"],
        "archived": bool(project_row["archived"]),
        "sections": sections,
        "questions": project_row["questions"],
    }


def create_project(name: str) -> dict:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO projects (name, progress, questions, objective, archived)
            VALUES (?, 0, '', '', 0)
            """,
            (name,),
        )
        conn.commit()
        project_id = cursor.lastrowid
        row = conn.execute(
            "SELECT id, name, archived FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()

    return {"id": row["id"], "name": row["name"], "archived": bool(row["archived"])}


def set_project_archived(project_id: int, archived: bool) -> bool:
    with connect() as conn:
        cursor = conn.execute(
            "UPDATE projects SET archived = ? WHERE id = ?",
            (1 if archived else 0, project_id),
        )
        conn.commit()
    return cursor.rowcount > 0


def update_questions(project_id: int, questions: str) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE projects SET questions = ? WHERE id = ?",
            (questions, project_id),
        )
        conn.commit()


def update_objective(project_id: int, objective: str) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE projects SET objective = ? WHERE id = ?",
            (objective, project_id),
        )
        conn.commit()


def update_progress(project_id: int, progress: int) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE projects SET progress = ? WHERE id = ?",
            (progress, project_id),
        )
        conn.commit()
