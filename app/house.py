DEFAULT_HOUSE = "Unassigned"
ACTIONERS_HOUSE = "Actioners"
SF2_HOUSE = "SF2"
ALL_HOUSES_FILTER = "All houses"

FALLBACK_HOUSES = (
    DEFAULT_HOUSE,
    ACTIONERS_HOUSE,
    SF2_HOUSE,
)
ALLOWED_HOUSES = FALLBACK_HOUSES


def list_houses() -> list[str]:
    from app.db_houses import list_houses as list_houses_from_db

    options = list_houses_from_db()
    if not options:
        return list(FALLBACK_HOUSES)

    normalized: list[str] = []
    seen: set[str] = set()
    for option in options:
        candidate = str(option or "").strip()
        if not candidate:
            continue
        key = candidate.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(candidate)

    if not normalized:
        return list(FALLBACK_HOUSES)
    return normalized


def normalize_house(value: str) -> str:
    candidate = (value or "").strip()
    if not candidate:
        raise ValueError("house is required")
    options = list_houses()
    for option in options:
        if candidate.lower() == option.lower():
            return option
    raise ValueError(f"house must be one of: {', '.join(options)}")


def normalize_house_filter(value: str | None) -> str | None:
    candidate = (value or "").strip()
    if not candidate:
        return None
    if candidate.lower() == ALL_HOUSES_FILTER.lower():
        return None
    return normalize_house(candidate)
