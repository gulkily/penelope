from datetime import datetime, timezone

from app.db_connection import connect

DEFAULT_RESIDENCY_YEAR = datetime.now(timezone.utc).year
DEFAULT_RESIDENCY_START = f"{DEFAULT_RESIDENCY_YEAR}-01-01"
DEFAULT_RESIDENCY_END = f"{DEFAULT_RESIDENCY_YEAR}-01-31"


def init_db() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                progress INTEGER NOT NULL,
                goal INTEGER NOT NULL DEFAULT 100,
                residency_start_date TEXT NOT NULL DEFAULT '{DEFAULT_RESIDENCY_START}',
                residency_end_date TEXT NOT NULL DEFAULT '{DEFAULT_RESIDENCY_END}',
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
                sort_order INTEGER NOT NULL DEFAULT 0,
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
        _ensure_column(
            conn,
            "projects",
            "residency_start_date",
            f"TEXT NOT NULL DEFAULT '{DEFAULT_RESIDENCY_START}'",
        )
        _ensure_column(
            conn,
            "projects",
            "residency_end_date",
            f"TEXT NOT NULL DEFAULT '{DEFAULT_RESIDENCY_END}'",
        )
        _ensure_column(conn, "projects", "objective", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "projects", "archived", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "projects", "summary", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "items", "sort_order", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "items", "created_at", "TEXT NOT NULL DEFAULT ''")
        _seed_if_empty(conn)
        _backfill_item_order(conn)


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
    raw_items = [
        (1, "summary", "Shared vision defined across teams."),
        (1, "challenges", "Metrics are not consistently tracked."),
        (1, "opportunities", "Expand onboarding experiments."),
        (1, "milestones", "Complete Q2 roadmap review."),
        (2, "summary", "Early user feedback is positive."),
        (2, "milestones", "Launch pilot with design partners."),
        (3, "challenges", "Resource constraints in engineering."),
    ]
    counters: dict[tuple[int, str], int] = {}
    items: list[tuple[int, str, str, int]] = []
    for project_id, section, content in raw_items:
        key = (project_id, section)
        counters[key] = counters.get(key, 0) + 1
        items.append((project_id, section, content, counters[key]))
    now = datetime.now(timezone.utc).isoformat()
    conn.executemany(
        """
        INSERT INTO items (project_id, section, content, sort_order, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (project_id, section, content, sort_order, now)
            for project_id, section, content, sort_order in items
        ],
    )
    conn.commit()


def _backfill_item_order(conn) -> None:
    rows = conn.execute(
        """
        SELECT id, project_id, section, sort_order
        FROM items
        ORDER BY project_id, section, id
        """
    ).fetchall()
    if not rows:
        return

    grouped: dict[tuple[int, str], list[dict]] = {}
    for row in rows:
        key = (row["project_id"], row["section"])
        grouped.setdefault(key, []).append(row)

    updates: list[tuple[int, int]] = []
    for key, items in grouped.items():
        has_assigned = any((item["sort_order"] or 0) > 0 for item in items)
        if not has_assigned:
            for index, item in enumerate(items, start=1):
                updates.append((index, item["id"]))
            continue
        max_order = max((item["sort_order"] or 0) for item in items)
        next_order = max_order
        for item in items:
            if (item["sort_order"] or 0) > 0:
                continue
            next_order += 1
            updates.append((next_order, item["id"]))

    if updates:
        conn.executemany("UPDATE items SET sort_order = ? WHERE id = ?", updates)
        conn.commit()
