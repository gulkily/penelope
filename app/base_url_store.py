from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CACHE_PATH = BASE_DIR / "data" / "magic_link_base_url.txt"
LOCAL_HOSTS = {"127.0.0.1", "localhost", "0.0.0.0", "::1"}
BASE_URL_ENV_KEYS = ("MAGIC_LINK_BASE_URL", "APP_BASE_URL", "PUBLIC_BASE_URL")


def _cache_path() -> Path:
    configured_path = (os.getenv("MAGIC_LINK_BASE_URL_CACHE_PATH", "") or "").strip()
    if configured_path:
        return Path(configured_path)
    return DEFAULT_CACHE_PATH


def _normalize_base_url(value: str) -> str | None:
    candidate = (value or "").strip()
    if not candidate:
        return None

    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    host = (parsed.hostname or "").strip().lower()
    if not host or host in LOCAL_HOSTS:
        return None

    path = parsed.path or ""
    if path == "/":
        path = ""
    return f"{parsed.scheme}://{parsed.netloc}{path}".rstrip("/")


def get_cached_base_url() -> str | None:
    path = _cache_path()
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return _normalize_base_url(value)


def write_cached_base_url(value: str) -> bool:
    normalized = _normalize_base_url(value)
    if not normalized:
        return False
    if get_cached_base_url() == normalized:
        return False

    path = _cache_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{normalized}\n", encoding="utf-8")
    except OSError:
        return False
    return True


def _infer_from_trusted_hosts() -> str | None:
    raw_hosts = os.getenv("TRUSTED_HOSTS", "")
    for entry in raw_hosts.split(","):
        host = entry.strip()
        if not host:
            continue
        if host.startswith(("http://", "https://")):
            candidate = host
        else:
            candidate = f"https://{host}"
        normalized = _normalize_base_url(candidate)
        if normalized:
            return normalized
    return None


def seed_cached_base_url() -> None:
    for key in BASE_URL_ENV_KEYS:
        value = os.getenv(key, "").strip()
        if value:
            write_cached_base_url(value)
            return
    inferred = _infer_from_trusted_hosts()
    if inferred:
        write_cached_base_url(inferred)


def maybe_cache_base_url_from_request(request) -> None:
    try:
        candidate = str(request.base_url)
    except Exception:
        return
    write_cached_base_url(candidate)
