import os
import re

from playwright.sync_api import expect

from app import auth

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def seed_browser_keypair(page) -> None:
    page.goto(f"{BASE_URL}/welcome")
    page.evaluate(
        """
        async () => {
          const keyPair = await window.crypto.subtle.generateKey(
            { name: "ECDSA", namedCurve: "P-256" },
            true,
            ["sign", "verify"]
          );
          const publicKey = await window.crypto.subtle.exportKey("spki", keyPair.publicKey);
          const privateKey = await window.crypto.subtle.exportKey("jwk", keyPair.privateKey);
          const bytes = new Uint8Array(publicKey);
          let binary = "";
          bytes.forEach((byte) => {
            binary += String.fromCharCode(byte);
          });
          localStorage.setItem("auth_public_key_spki", btoa(binary));
          localStorage.setItem("auth_private_key_jwk", JSON.stringify(privateKey));
        }
        """
    )


def test_session_reset_with_active_session_redirects_to_next(page):
    page.goto(f"{BASE_URL}/session/reset?next=/projects")
    assert page.url.startswith(f"{BASE_URL}/projects")


def test_session_reset_restore_success_redirects_to_requested_route(
    page,
    e2e_admin_account_id: int,
):
    # Use a fresh browser context so this test doesn't inherit autouse admin cookies.
    context = page.context.browser.new_context(base_url=BASE_URL)
    fresh_page = context.new_page()
    try:
        seed_browser_keypair(fresh_page)

        route_hits = {"challenge": 0, "restore": 0}

        def handle_challenge(route):
            route_hits["challenge"] += 1
            route.fulfill(
                status=200,
                content_type="application/json",
                body='{"challenge":"test.challenge"}',
            )

        def handle_restore(route):
            route_hits["restore"] += 1
            cookie_value = auth._encode_cookie(e2e_admin_account_id)
            route.fulfill(
                status=200,
                content_type="application/json",
                headers={
                    "Set-Cookie": (
                        f"{auth.COOKIE_NAME}={cookie_value}; "
                        "Path=/; HttpOnly; SameSite=Lax"
                    )
                },
                body='{"status":"ok"}',
            )

        fresh_page.route(
            "**/api/auth/session/challenge",
            handle_challenge,
        )
        fresh_page.route(
            "**/api/auth/session/restore",
            handle_restore,
        )

        fresh_page.goto(f"{BASE_URL}/session/reset?next=/projects")
        expect(fresh_page).to_have_url(re.compile(rf"{re.escape(BASE_URL)}/projects.*"))
        assert route_hits["challenge"] >= 1
        assert route_hits["restore"] >= 1
    finally:
        context.close()


def test_session_reset_without_keypair_redirects_to_welcome(page):
    page.context.clear_cookies()
    page.goto(f"{BASE_URL}/welcome")
    page.evaluate(
        """
        () => {
          localStorage.removeItem("auth_public_key_spki");
          localStorage.removeItem("auth_private_key_jwk");
        }
        """
    )

    page.goto(f"{BASE_URL}/session/reset?next=/projects")
    expect(page).to_have_url(f"{BASE_URL}/welcome")


def test_lobby_page_renders_enabled_or_disabled_state(playwright):
    request_context = playwright.request.new_context(base_url=BASE_URL)
    response = request_context.get("/lobby", max_redirects=0)
    assert response.status == 200
    body = response.text()
    assert "Request Access" in body or "Lobby authentication is disabled" in body
    request_context.dispose()


def test_welcome_token_handoff_renders_lobby_request_panel(playwright):
    request_context = playwright.request.new_context(base_url=BASE_URL)
    response = request_context.get("/welcome?token=e2e-token", max_redirects=0)
    assert response.status == 200
    assert "Request Access" in response.text()
    request_context.dispose()


def test_lobby_token_handoff_renders_request_panel(playwright):
    request_context = playwright.request.new_context(base_url=BASE_URL)
    response = request_context.get("/lobby?token=e2e-token", max_redirects=0)
    assert response.status == 200
    assert "Request Access" in response.text()
    request_context.dispose()
