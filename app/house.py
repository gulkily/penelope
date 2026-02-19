DEFAULT_HOUSE = "Unassigned"
ACTIONERS_HOUSE = "Actioners"
SF2_HOUSE = "SF2"
ALL_HOUSES_FILTER = "All houses"

ALLOWED_HOUSES = (
    DEFAULT_HOUSE,
    ACTIONERS_HOUSE,
    SF2_HOUSE,
)


def normalize_house(value: str) -> str:
    candidate = (value or "").strip()
    if not candidate:
        raise ValueError("house is required")
    for option in ALLOWED_HOUSES:
        if candidate.lower() == option.lower():
            return option
    raise ValueError(f"house must be one of: {', '.join(ALLOWED_HOUSES)}")


def normalize_house_filter(value: str | None) -> str | None:
    candidate = (value or "").strip()
    if not candidate:
        return None
    if candidate.lower() == ALL_HOUSES_FILTER.lower():
        return None
    return normalize_house(candidate)
