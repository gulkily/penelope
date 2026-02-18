from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from functools import lru_cache

logger = logging.getLogger(__name__)

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}

NAVBAR_ITEM_DEFINITIONS = (
    {
        "key": "lobby",
        "label": "Lobby",
        "href": "/lobby",
        "current_page": "lobby",
        "show_lobby_badge": True,
    },
    {
        "key": "projects",
        "label": "Manage residents",
        "href": "/projects",
        "current_page": "projects",
        "show_lobby_badge": False,
    },
    {
        "key": "settings",
        "label": "Settings",
        "href": "/settings",
        "current_page": "settings",
        "show_lobby_badge": False,
    },
)
VALID_NAVBAR_ITEM_KEYS = frozenset(item["key"] for item in NAVBAR_ITEM_DEFINITIONS)
DEFAULT_NAVBAR_ENABLED_ITEMS = frozenset(VALID_NAVBAR_ITEM_KEYS)


@dataclass(frozen=True)
class FeatureFlags:
    navbar_enabled_items: frozenset[str]
    lobby_auth_enabled: bool
    recorder_enabled: bool


def _parse_bool_env(name: str, *, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    normalized = raw_value.strip().lower()
    if not normalized:
        return default
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    logger.warning(
        "Invalid boolean for %s=%r. Falling back to default=%s.",
        name,
        raw_value,
        default,
    )
    return default


def _parse_navbar_enabled_items() -> frozenset[str]:
    raw_value = os.getenv("NAVBAR_ENABLED_ITEMS")
    if raw_value is None:
        return DEFAULT_NAVBAR_ENABLED_ITEMS
    normalized = raw_value.strip()
    if not normalized:
        return frozenset()

    configured = [entry.strip().lower() for entry in normalized.split(",") if entry.strip()]
    enabled = frozenset(entry for entry in configured if entry in VALID_NAVBAR_ITEM_KEYS)
    unknown = sorted({entry for entry in configured if entry not in VALID_NAVBAR_ITEM_KEYS})
    if unknown:
        logger.warning(
            "Ignoring unknown NAVBAR_ENABLED_ITEMS values: %s. Valid values: %s",
            ", ".join(unknown),
            ", ".join(sorted(VALID_NAVBAR_ITEM_KEYS)),
        )
    return enabled


@lru_cache(maxsize=1)
def get_feature_flags() -> FeatureFlags:
    return FeatureFlags(
        navbar_enabled_items=_parse_navbar_enabled_items(),
        lobby_auth_enabled=_parse_bool_env("LOBBY_AUTH_ENABLED", default=True),
        recorder_enabled=_parse_bool_env("RECORDER_ENABLED", default=True),
    )
