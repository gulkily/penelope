from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "north_star.db"
SECTIONS = ("summary", "challenges", "opportunities", "milestones")


def _resolve_sqlite_path() -> Path:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return DEFAULT_DB_PATH

    parsed = urlparse(db_url)
    if parsed.scheme == "sqlite":
        if parsed.netloc:
            return Path(f"/{parsed.netloc}{parsed.path}")
        return Path(parsed.path)

    raise ValueError("Only sqlite is supported right now; set DATABASE_URL to sqlite://.")


def _connect() -> sqlite3.Connection:
    db_path = _resolve_sqlite_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                progress INTEGER NOT NULL,
                questions TEXT NOT NULL DEFAULT '',
                objective TEXT NOT NULL DEFAULT ''
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                section TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            )
            """
        )
        _ensure_objective_column(conn)
        _seed_if_empty(conn)


def _ensure_objective_column(conn: sqlite3.Connection) -> None:
    columns = conn.execute("PRAGMA table_info(projects)").fetchall()
    if any(column["name"] == "objective" for column in columns):
        return
    conn.execute("ALTER TABLE projects ADD COLUMN objective TEXT NOT NULL DEFAULT ''")


def _seed_if_empty(conn: sqlite3.Connection) -> None:
    cursor = conn.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone()[0] > 0:
        return

    projects = [
        ("Project North", 40, "", "Reach 10 paying customers."),
        ("Project Aurora", 62, "", "Process 10GB of data per day."),
        ("Project Horizon", 25, "", "Launch to three design partners."),
    ]
    conn.executemany(
        "INSERT INTO projects (name, progress, questions, objective) VALUES (?, ?, ?, ?)",
        projects,
    )
    items = [
        (1, "summary", "Shared vision defined across teams."),
        (1, "challenges", "Metrics are not consistently tracked."),
        (1, "opportunities", "Expand onboarding experiments."),
        (1, "milestones", "Complete Q2 roadmap review."),
        (2, "summary", "Early user feedback is positive."),
        (2, "milestones", "Launch pilot with design partners."),
        (3, "challenges", "Resource constraints in engineering."),
    ]
    now = datetime.now(timezone.utc).isoformat()
    conn.executemany(
        "INSERT INTO items (project_id, section, content, created_at) VALUES (?, ?, ?, ?)",
        [(project_id, section, content, now) for project_id, section, content in items],
    )
    conn.commit()


def list_projects() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT id, name FROM projects ORDER BY id").fetchall()
    return [{"id": row["id"], "name": row["name"]} for row in rows]


def get_project(project_id: int) -> dict | None:
    with _connect() as conn:
        project_row = conn.execute(
            "SELECT id, name, progress, questions, objective FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()
        if not project_row:
            return None

        items_rows = conn.execute(
            "SELECT id, section, content FROM items WHERE project_id = ? ORDER BY id",
            (project_id,),
        ).fetchall()

    sections: dict[str, list[dict]] = {section: [] for section in SECTIONS}
    for row in items_rows:
        sections[row["section"]].append({"id": row["id"], "text": row["content"]})

    return {
        "id": project_row["id"],
        "name": project_row["name"],
        "progress": project_row["progress"],
        "objective": project_row["objective"],
        "sections": sections,
        "questions": project_row["questions"],
    }


def add_item(project_id: int, section: str, text: str) -> dict:
    if section not in SECTIONS:
        raise ValueError(f"Unknown section: {section}")

    with _connect() as conn:
        now = datetime.now(timezone.utc).isoformat()
        cursor = conn.execute(
            "INSERT INTO items (project_id, section, content, created_at) VALUES (?, ?, ?, ?)",
            (project_id, section, text, now),
        )
        conn.commit()
        item_id = cursor.lastrowid

    return {"id": item_id, "section": section, "text": text}


def update_questions(project_id: int, questions: str) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE projects SET questions = ? WHERE id = ?",
            (questions, project_id),
        )
        conn.commit()


def update_objective(project_id: int, objective: str) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE projects SET objective = ? WHERE id = ?",
            (objective, project_id),
        )
        conn.commit()


def update_progress(project_id: int, progress: int) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE projects SET progress = ? WHERE id = ?",
            (progress, project_id),
        )
        conn.commit()
