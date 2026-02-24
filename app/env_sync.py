from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

_ACTIVE_ASSIGNMENT_RE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$")
_COMMENTED_ASSIGNMENT_RE = re.compile(
    r"^\s*#\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?!>)(.*)$"
)
_SYNC_NOTE = "# Added automatically from .env.example via ./pnl env-sync."


def parse_env_keys(lines: list[str]) -> list[str]:
    """Return ordered active assignment keys from env-style lines."""
    keys: list[str] = []
    seen: set[str] = set()
    for line in lines:
        match = _ACTIVE_ASSIGNMENT_RE.match(line)
        if not match:
            continue
        key = match.group(1)
        if key in seen:
            continue
        seen.add(key)
        keys.append(key)
    return keys


def _parse_default_entries(lines: list[str]) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line in lines:
        active_match = _ACTIVE_ASSIGNMENT_RE.match(line)
        commented_match = _COMMENTED_ASSIGNMENT_RE.match(line)
        match = active_match or commented_match
        if not match:
            continue
        key = match.group(1)
        if key in seen:
            continue
        seen.add(key)
        entries.append((key, match.group(2).strip()))
    return entries


def _build_missing_defaults_block(entries: list[tuple[str, str]]) -> str:
    lines = [_SYNC_NOTE]
    lines.extend(f"{key}={value}" for key, value in entries)
    return "\n".join(lines) + "\n"


def get_missing_env_defaults(
    env_path: Path,
    env_example_path: Path,
) -> dict[str, bool | int | list[str] | list[tuple[str, str]]]:
    if not env_example_path.exists():
        logger.warning("Env defaults sync check skipped: missing %s", env_example_path)
        return {
            "example_found": False,
            "env_exists": env_path.exists(),
            "missing_count": 0,
            "missing_keys": [],
            "missing_entries": [],
        }

    env_example_lines = env_example_path.read_text(encoding="utf-8").splitlines()
    default_entries = _parse_default_entries(env_example_lines)
    if not default_entries:
        return {
            "example_found": True,
            "env_exists": env_path.exists(),
            "missing_count": 0,
            "missing_keys": [],
            "missing_entries": [],
        }

    env_exists = env_path.exists()
    current_content = env_path.read_text(encoding="utf-8") if env_exists else ""
    current_keys = set(parse_env_keys(current_content.splitlines()))
    missing_entries = [(key, value) for key, value in default_entries if key not in current_keys]
    return {
        "example_found": True,
        "env_exists": env_exists,
        "missing_count": len(missing_entries),
        "missing_keys": [key for key, _ in missing_entries],
        "missing_entries": missing_entries,
    }


def sync_env_defaults(env_path: Path, env_example_path: Path) -> dict[str, int | bool]:
    """
    Append missing defaults from .env.example to .env.

    Existing keys are never overwritten.
    """
    status = get_missing_env_defaults(env_path=env_path, env_example_path=env_example_path)
    if not status.get("example_found"):
        return {
            "example_found": False,
            "env_created": False,
            "added_count": 0,
            "updated": False,
        }
    env_exists = bool(status.get("env_exists"))
    missing_entries = list(status.get("missing_entries", []))

    if not missing_entries:
        return {
            "example_found": True,
            "env_created": False,
            "added_count": 0,
            "updated": False,
        }

    env_path.parent.mkdir(parents=True, exist_ok=True)
    current_content = env_path.read_text(encoding="utf-8") if env_exists else ""
    append_block = _build_missing_defaults_block(missing_entries)
    if current_content:
        if not current_content.endswith("\n"):
            current_content += "\n"
        current_content += "\n"
    next_content = current_content + append_block

    temp_path = env_path.with_name(f".{env_path.name}.tmp")
    try:
        temp_path.write_text(next_content, encoding="utf-8")
        temp_path.replace(env_path)
    except OSError:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                logger.warning("Failed to clean up temp env sync file: %s", temp_path)
        raise

    return {
        "example_found": True,
        "env_created": not env_exists,
        "added_count": len(missing_entries),
        "updated": True,
    }
