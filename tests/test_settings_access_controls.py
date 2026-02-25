from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request

import app.main as main


def _request_with_session(account_id: int | None) -> Request:
    request = Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "headers": [],
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
        }
    )
    if account_id is None:
        request.state.session_account = None
    else:
        request.state.session_account = SimpleNamespace(
            account_id=account_id,
            username=f"user-{account_id}",
        )
    return request


def _request_for_exception_handler(path: str, accept: str = "text/html") -> Request:
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode("utf-8"),
            "query_string": b"",
            "headers": [(b"accept", accept.encode("utf-8"))],
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
        }
    )


def test_build_navbar_items_hides_settings_for_non_admin() -> None:
    items = main._build_navbar_items(
        {"lobby", "projects", "settings"},
        session_is_admin=False,
    )
    keys = [item["key"] for item in items]
    assert keys == ["lobby", "projects"]


def test_build_navbar_items_shows_settings_for_admin() -> None:
    items = main._build_navbar_items(
        {"lobby", "projects", "settings"},
        session_is_admin=True,
    )
    keys = [item["key"] for item in items]
    assert keys == ["lobby", "projects", "settings"]


def test_require_admin_session_rejects_missing_session() -> None:
    request = _request_with_session(None)
    with pytest.raises(HTTPException) as excinfo:
        main._require_admin_session(request)
    assert excinfo.value.status_code == 403


def test_require_admin_session_rejects_non_admin(monkeypatch) -> None:
    request = _request_with_session(2)
    monkeypatch.setattr(main.auth, "is_admin_account", lambda account_id: False)
    with pytest.raises(HTTPException) as excinfo:
        main._require_admin_session(request)
    assert excinfo.value.status_code == 403


def test_settings_routes_reject_non_admin_without_rendering() -> None:
    request = _request_with_session(None)
    for route in (main.settings, main.magic_links, main.users):
        with pytest.raises(HTTPException) as excinfo:
            route(request)
        assert excinfo.value.status_code == 403


def test_settings_routes_allow_admin(monkeypatch) -> None:
    request = _request_with_session(1)
    monkeypatch.setattr(main.auth, "is_admin_account", lambda account_id: True)

    settings_response = main.settings(request)
    magic_links_response = main.magic_links(request)
    users_response = main.users(request)

    assert settings_response.status_code == 200
    assert magic_links_response.status_code == 200
    assert users_response.status_code == 200


def test_http_exception_handler_redirects_settings_403_for_html() -> None:
    request = _request_for_exception_handler("/settings", accept="text/html")
    response = asyncio.run(
        main.app_http_exception_handler(
            request,
            HTTPException(status_code=403, detail="Admin access required"),
        )
    )
    assert response.status_code == 302
    assert response.headers["location"] == "/"


def test_http_exception_handler_keeps_non_html_settings_403() -> None:
    request = _request_for_exception_handler("/settings", accept="application/json")
    response = asyncio.run(
        main.app_http_exception_handler(
            request,
            HTTPException(status_code=403, detail="Admin access required"),
        )
    )
    assert response.status_code == 403
    assert response.body == b'{"detail":"Admin access required"}'


def test_http_exception_handler_keeps_non_settings_403() -> None:
    request = _request_for_exception_handler("/api/auth/users", accept="text/html")
    response = asyncio.run(
        main.app_http_exception_handler(
            request,
            HTTPException(status_code=403, detail="Admin access required"),
        )
    )
    assert response.status_code == 403
    assert response.body == b'{"detail":"Admin access required"}'
