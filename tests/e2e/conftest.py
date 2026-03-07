import os
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

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


def _pick_non_admin_username() -> str | None:
    configured = os.getenv("MAGIC_LINK_ADMIN_USERNAMES", "")
    admins = {entry.strip().lower() for entry in configured.split(",") if entry.strip()}
    if not admins:
        # When no explicit admin list is configured, all users are admins.
        return None
    for candidate in ("e2e-non-admin", "e2e-user", "e2e-member"):
        if candidate.lower() not in admins:
            return candidate
    return None


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


@pytest.fixture(scope="session", autouse=True)
def ensure_e2e_server_is_reachable(e2e_base_url: str) -> None:
    try:
        with urlopen(f"{e2e_base_url}/welcome", timeout=5) as response:
            status = getattr(response, "status", 200)
            if status >= 500:
                raise RuntimeError(
                    f"E2E target is not healthy: GET /welcome returned {status}"
                )
    except URLError as exc:
        raise RuntimeError(
            f"E2E target is unreachable at {e2e_base_url}. "
            "Start the app before running tests."
        ) from exc


@pytest.fixture(scope="session")
def e2e_admin_account_id() -> int:
    db.init_db()
    username = _pick_admin_username()
    account = db.get_account_by_username_case_insensitive(username)
    if not account:
        account = db.create_account(username)
    return int(account["id"])


@pytest.fixture(scope="session")
def e2e_non_admin_account_id() -> int | None:
    db.init_db()
    username = _pick_non_admin_username()
    if not username:
        return None
    account = db.get_account_by_username_case_insensitive(username)
    if not account:
        account = db.create_account(username)
    return int(account["id"])


@pytest.fixture
def set_session_account(page, e2e_base_url: str):
    def _set_session(account_id: int) -> None:
        cookie_value = auth._encode_cookie(account_id)
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

    return _set_session


@pytest.fixture(autouse=True)
def authenticated_admin_page(
    page,
    e2e_admin_account_id: int,
    set_session_account,
) -> None:
    # Inject a signed session cookie before each test so routes behind auth load normally.
    set_session_account(e2e_admin_account_id)


@pytest.fixture
def authenticated_non_admin_page(
    page,
    e2e_non_admin_account_id: int | None,
    set_session_account,
):
    if e2e_non_admin_account_id is None:
        pytest.skip(
            "Non-admin E2E fixture requires MAGIC_LINK_ADMIN_USERNAMES "
            "to include at least one explicit admin username."
        )
    page.context.clear_cookies()
    set_session_account(e2e_non_admin_account_id)
    return page
