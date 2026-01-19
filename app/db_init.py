from datetime import datetime, timezone

from app.db_connection import connect


def init_db() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                progress INTEGER NOT NULL,
                goal INTEGER NOT NULL DEFAULT 100,
                questions TEXT NOT NULL DEFAULT '',
                summary TEXT NOT NULL DEFAULT '',
                objective TEXT NOT NULL DEFAULT '',
                archived INTEGER NOT NULL DEFAULT 0
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS progress_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                progress INTEGER NOT NULL,
                recorded_at TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_progress_history_project
            ON progress_history (project_id, recorded_at, id)
            """
        )
        _ensure_column(conn, "projects", "goal", "INTEGER NOT NULL DEFAULT 100")
        _ensure_column(conn, "projects", "objective", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "projects", "archived", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "projects", "summary", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "items", "created_at", "TEXT NOT NULL DEFAULT ''")
        _seed_if_empty(conn)


def _ensure_column(conn, table: str, name: str, definition: str) -> None:
    columns = conn.execute(f"PRAGMA table_info({table})").fetchall()
    if any(column["name"] == name for column in columns):
        return
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")


def _seed_if_empty(conn) -> None:
    cursor = conn.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone()[0] > 0:
        return

    projects = [
        ("Project North", 40, 10, "", "", "Reach 10 paying customers.", 0),
        ("Project Aurora", 62, 10, "", "", "Process 10GB of data per day.", 0),
        ("Project Horizon", 25, 3, "", "", "Launch to three design partners.", 0),
    ]
    conn.executemany(
        """
        INSERT INTO projects (name, progress, goal, questions, summary, objective, archived)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
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
