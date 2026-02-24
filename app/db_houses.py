from app.db_connection import connect
from app.house import FALLBACK_HOUSES


def list_houses() -> list[str]:
    try:
        with connect() as conn:
            rows = conn.execute(
                """
                SELECT name
                FROM houses
                ORDER BY id ASC
                """
            ).fetchall()
    except Exception:
        return list(FALLBACK_HOUSES)

    names: list[str] = []
    seen: set[str] = set()
    for row in rows:
        candidate = str(row["name"] or "").strip()
        if not candidate:
            continue
        key = candidate.lower()
        if key in seen:
            continue
        seen.add(key)
        names.append(candidate)

    if not names:
        return list(FALLBACK_HOUSES)
    return names
