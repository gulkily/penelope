import os
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "north_star.db"


def resolve_sqlite_path() -> Path:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return DEFAULT_DB_PATH

    parsed = urlparse(db_url)
    if parsed.scheme == "sqlite":
        if parsed.netloc:
            return Path(f"/{parsed.netloc}{parsed.path}")
        return Path(parsed.path)

    raise ValueError("Only sqlite is supported right now; set DATABASE_URL to sqlite://.")


def connect() -> sqlite3.Connection:
    db_path = resolve_sqlite_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def get_db_path() -> Path:
    return resolve_sqlite_path()
