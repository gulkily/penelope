import os
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

import pytest

from app import auth, db

LOCAL_E2E_HOSTS = {"127.0.0.1", "localhost"}


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


def _is_local_e2e_target(base_url: str) -> bool:
    parsed = urlparse(base_url)
    host = (parsed.hostname or "").lower()
    return host in LOCAL_E2E_HOSTS


@pytest.fixture(scope="session")
def e2e_base_url() -> str:
    return _resolve_base_url()


@pytest.fixture(scope="session", autouse=True)
def ensure_e2e_server_is_reachable(
    e2e_base_url: str,
    e2e_admin_account_id: int,
) -> None:
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

    # Auth-cookie bootstrap checks are only deterministic for local E2E targets.
    if _is_local_e2e_target(e2e_base_url):
        admin_cookie = auth._encode_cookie(e2e_admin_account_id)
        from urllib.request import Request  # local import to keep module imports tidy

        request = Request(
            f"{e2e_base_url}/",
            headers={"Cookie": f"{auth.COOKIE_NAME}={admin_cookie}"},
        )
        with urlopen(request, timeout=5) as dashboard_response:
            dashboard_status = getattr(dashboard_response, "status", 200)
            if dashboard_status >= 400:
                raise RuntimeError(
                    "E2E authenticated bootstrap check failed: "
                    f"GET / returned {dashboard_status} with admin session cookie."
                )


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
    request,
    e2e_admin_account_id: int,
    e2e_base_url: str,
) -> None:
    if request.node.get_closest_marker("prod_smoke"):
        return
    if not _is_local_e2e_target(e2e_base_url):
        raise RuntimeError(
            "Full E2E suite with injected auth cookie supports local targets only. "
            "Run against local/staging on localhost, or use `-m prod_smoke` for remote checks."
        )
    request.getfixturevalue("page")
    set_session_account = request.getfixturevalue("set_session_account")
    # Inject a signed session cookie before each test so routes behind auth load normally.
    set_session_account(e2e_admin_account_id)


@pytest.fixture
def authenticated_non_admin_page(
    request,
    page,
    e2e_non_admin_account_id: int | None,
    e2e_base_url: str,
    set_session_account,
):
    if request.node.get_closest_marker("prod_smoke"):
        pytest.skip("Non-admin auth fixture is not used for prod_smoke tests.")
    if not _is_local_e2e_target(e2e_base_url):
        pytest.skip("Non-admin auth fixture requires a local E2E target.")
    if e2e_non_admin_account_id is None:
        pytest.skip(
            "Non-admin E2E fixture requires MAGIC_LINK_ADMIN_USERNAMES "
            "to include at least one explicit admin username."
        )
    page.context.clear_cookies()
    set_session_account(e2e_non_admin_account_id)
    return page
