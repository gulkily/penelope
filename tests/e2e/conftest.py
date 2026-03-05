import os
from urllib.parse import urlparse

import pytest

from app import auth, db


def _resolve_base_url() -> str:
    return os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def _pick_admin_username() -> str:
    configured = os.getenv("MAGIC_LINK_ADMIN_USERNAMES", "")
    candidates = [entry.strip() for entry in configured.split(",") if entry.strip()]
    if candidates:
        return candidates[0]
    return "e2e-admin"


@pytest.fixture(scope="session")
def e2e_base_url() -> str:
    base_url = _resolve_base_url()
    parsed = urlparse(base_url)
    host = (parsed.hostname or "").lower()
    if host not in {"127.0.0.1", "localhost"}:
        raise RuntimeError(
            "E2E auth fixture currently supports local servers only "
            "(set E2E_BASE_URL to http://127.0.0.1:8000 or http://localhost:8000)."
        )
    return base_url


@pytest.fixture(scope="session")
def e2e_admin_account_id() -> int:
    db.init_db()
    username = _pick_admin_username()
    account = db.get_account_by_username_case_insensitive(username)
    if not account:
        account = db.create_account(username)
    return int(account["id"])


@pytest.fixture(autouse=True)
def authenticated_admin_page(
    page,
    e2e_base_url: str,
    e2e_admin_account_id: int,
) -> None:
    # Inject a signed session cookie before each test so routes behind auth load normally.
    cookie_value = auth._encode_cookie(e2e_admin_account_id)
    parsed = urlparse(e2e_base_url)
    domain = parsed.hostname or "127.0.0.1"
    page.context.add_cookies(
        [
            {
                "name": auth.COOKIE_NAME,
                "value": cookie_value,
                "domain": domain,
                "path": "/",
                "httpOnly": True,
                "secure": parsed.scheme == "https",
                "sameSite": "Lax",
            }
        ]
    )
