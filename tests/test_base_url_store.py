from __future__ import annotations

from starlette.requests import Request

from app.base_url_store import get_cached_base_url
from app.base_url_store import maybe_cache_base_url_from_request
from app.base_url_store import seed_cached_base_url
from app.base_url_store import write_cached_base_url


def _request_for_base_url(host: str, scheme: str = "https") -> Request:
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": scheme,
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "headers": [(b"host", host.encode("utf-8"))],
            "client": ("testclient", 50000),
            "server": (host, 443 if scheme == "https" else 80),
        }
    )


def test_write_cached_base_url_rejects_localhost(tmp_path, monkeypatch) -> None:
    cache_path = tmp_path / "magic_link_base_url.txt"
    monkeypatch.setenv("MAGIC_LINK_BASE_URL_CACHE_PATH", str(cache_path))

    changed = write_cached_base_url("http://127.0.0.1:8000")

    assert changed is False
    assert get_cached_base_url() is None


def test_seed_cached_base_url_from_trusted_hosts(tmp_path, monkeypatch) -> None:
    cache_path = tmp_path / "magic_link_base_url.txt"
    monkeypatch.setenv("MAGIC_LINK_BASE_URL_CACHE_PATH", str(cache_path))
    monkeypatch.delenv("MAGIC_LINK_BASE_URL", raising=False)
    monkeypatch.delenv("APP_BASE_URL", raising=False)
    monkeypatch.delenv("PUBLIC_BASE_URL", raising=False)
    monkeypatch.setenv("TRUSTED_HOSTS", "127.0.0.1,localhost,beta.penelope.example")

    seed_cached_base_url()

    assert get_cached_base_url() == "https://beta.penelope.example"


def test_request_updates_cached_base_url(tmp_path, monkeypatch) -> None:
    cache_path = tmp_path / "magic_link_base_url.txt"
    monkeypatch.setenv("MAGIC_LINK_BASE_URL_CACHE_PATH", str(cache_path))

    maybe_cache_base_url_from_request(_request_for_base_url("new.penelope.example", "https"))

    assert get_cached_base_url() == "https://new.penelope.example"
