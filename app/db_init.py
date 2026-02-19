from datetime import datetime, timezone

from app.db_connection import connect
from app.house import DEFAULT_HOUSE, normalize_house

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
                house TEXT NOT NULL DEFAULT '{DEFAULT_HOUSE}',
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS public_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                public_key TEXT NOT NULL,
                public_key_format TEXT NOT NULL,
                fingerprint TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(account_id) REFERENCES accounts(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS magic_login_tokens (
                id TEXT PRIMARY KEY,
                token_hash TEXT NOT NULL,
                configured_username TEXT NOT NULL,
                created_by_account_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked_at TEXT,
                revoked_by_account_id INTEGER,
                consumed_at TEXT,
                consumed_by_account_id INTEGER,
                consumed_request_id TEXT,
                FOREIGN KEY(created_by_account_id) REFERENCES accounts(id),
                FOREIGN KEY(revoked_by_account_id) REFERENCES accounts(id),
                FOREIGN KEY(consumed_by_account_id) REFERENCES accounts(id),
                FOREIGN KEY(consumed_request_id) REFERENCES lobby_requests(request_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lobby_requests (
                request_id TEXT PRIMARY KEY,
                public_key_id INTEGER NOT NULL,
                requested_username TEXT NOT NULL,
                magic_token_id TEXT,
                code TEXT NOT NULL,
                status TEXT NOT NULL,
                requested_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                challenge TEXT NOT NULL,
                verified_at TEXT,
                account_id INTEGER,
                approved_by INTEGER,
                approved_at TEXT,
                rejected_by INTEGER,
                rejected_at TEXT,
                FOREIGN KEY(public_key_id) REFERENCES public_keys(id),
                FOREIGN KEY(magic_token_id) REFERENCES magic_login_tokens(id),
                FOREIGN KEY(account_id) REFERENCES accounts(id),
                FOREIGN KEY(approved_by) REFERENCES accounts(id),
                FOREIGN KEY(rejected_by) REFERENCES accounts(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ledger_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                actor_account_id INTEGER,
                subject_account_id INTEGER,
                metadata TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(actor_account_id) REFERENCES accounts(id),
                FOREIGN KEY(subject_account_id) REFERENCES accounts(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS import_builder_map (
                source_builder_id TEXT PRIMARY KEY,
                project_id INTEGER UNIQUE NOT NULL,
                imported_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS import_checkin_map (
                source_checkin_id TEXT PRIMARY KEY,
                source_builder_id TEXT NOT NULL,
                week_of TEXT NOT NULL,
                project_id INTEGER NOT NULL,
                imported_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(source_builder_id, week_of),
                FOREIGN KEY(project_id) REFERENCES projects(id)
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_public_keys_fingerprint
            ON public_keys (fingerprint)
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_magic_login_tokens_hash
            ON magic_login_tokens (token_hash)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_magic_login_tokens_created
            ON magic_login_tokens (created_at)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_lobby_requests_status
            ON lobby_requests (status, requested_at)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ledger_events_created
            ON ledger_events (created_at)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_import_builder_project
            ON import_builder_map (project_id)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_import_checkin_builder_week
            ON import_checkin_map (source_builder_id, week_of)
            """
        )
        _ensure_column(conn, "projects", "goal", "INTEGER NOT NULL DEFAULT 100")
        _ensure_column(
            conn,
            "projects",
            "house",
            f"TEXT NOT NULL DEFAULT '{DEFAULT_HOUSE}'",
        )
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
        _ensure_column(conn, "accounts", "username", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "accounts", "created_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "accounts", "updated_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "public_keys", "public_key", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "public_keys", "public_key_format", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "public_keys", "fingerprint", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "public_keys", "created_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "public_keys", "account_id", "INTEGER")
        _ensure_column(conn, "magic_login_tokens", "token_hash", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(
            conn, "magic_login_tokens", "configured_username", "TEXT NOT NULL DEFAULT ''"
        )
        _ensure_column(conn, "magic_login_tokens", "created_by_account_id", "INTEGER")
        _ensure_column(conn, "magic_login_tokens", "created_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "magic_login_tokens", "expires_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "magic_login_tokens", "revoked_at", "TEXT")
        _ensure_column(conn, "magic_login_tokens", "revoked_by_account_id", "INTEGER")
        _ensure_column(conn, "magic_login_tokens", "consumed_at", "TEXT")
        _ensure_column(conn, "magic_login_tokens", "consumed_by_account_id", "INTEGER")
        _ensure_column(conn, "magic_login_tokens", "consumed_request_id", "TEXT")
        _ensure_column(conn, "lobby_requests", "requested_username", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "lobby_requests", "magic_token_id", "TEXT")
        _ensure_column(conn, "lobby_requests", "code", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "lobby_requests", "status", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "lobby_requests", "requested_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "lobby_requests", "expires_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "lobby_requests", "challenge", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "lobby_requests", "verified_at", "TEXT")
        _ensure_column(conn, "lobby_requests", "account_id", "INTEGER")
        _ensure_column(conn, "lobby_requests", "approved_by", "INTEGER")
        _ensure_column(conn, "lobby_requests", "approved_at", "TEXT")
        _ensure_column(conn, "lobby_requests", "rejected_by", "INTEGER")
        _ensure_column(conn, "lobby_requests", "rejected_at", "TEXT")
        _ensure_column(conn, "ledger_events", "event_type", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "ledger_events", "actor_account_id", "INTEGER")
        _ensure_column(conn, "ledger_events", "subject_account_id", "INTEGER")
        _ensure_column(conn, "ledger_events", "metadata", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "ledger_events", "created_at", "TEXT NOT NULL DEFAULT ''")
        _seed_if_empty(conn)
        _backfill_project_houses(conn)
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


def _backfill_project_houses(conn) -> None:
    rows = conn.execute("SELECT id, house FROM projects ORDER BY id").fetchall()
    updates: list[tuple[str, int]] = []
    for row in rows:
        raw_house = (row["house"] or "").strip()
        try:
            normalized = normalize_house(raw_house)
        except ValueError:
            normalized = DEFAULT_HOUSE
        if normalized != raw_house:
            updates.append((normalized, row["id"]))
    if updates:
        conn.executemany("UPDATE projects SET house = ? WHERE id = ?", updates)
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
