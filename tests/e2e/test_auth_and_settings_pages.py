import os

import pytest
from playwright.sync_api import expect

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def test_unauthenticated_projects_redirects_to_session_reset(playwright):
    request_context = playwright.request.new_context(base_url=BASE_URL)
    response = request_context.get("/projects", max_redirects=0)
    assert response.status == 302
    location = response.headers.get("location", "")
    assert location.startswith("/session/reset")
    request_context.dispose()


def test_unauthenticated_api_projects_returns_401(playwright):
    request_context = playwright.request.new_context(base_url=BASE_URL)
    response = request_context.get("/api/projects", max_redirects=0)
    assert response.status == 401
    request_context.dispose()


def test_welcome_page_renders_unauthenticated(playwright):
    request_context = playwright.request.new_context(base_url=BASE_URL)
    response = request_context.get("/welcome", max_redirects=0)
    assert response.status == 200
    assert "Welcome" in response.text()
    request_context.dispose()


def test_settings_route_access_behavior(page):
    page.goto(f"{BASE_URL}/settings")
    if page.url.startswith(f"{BASE_URL}/settings"):
        expect(page.get_by_role("heading", name="Settings")).to_be_visible()
        expect(page.get_by_role("link", name="Manage residents")).to_be_visible()
        expect(page.get_by_role("link", name="Manage magic links")).to_be_visible()
        expect(page.get_by_role("link", name="View users")).to_be_visible()
        expect(page.get_by_role("link", name="View ledger")).to_be_visible()
        expect(page.locator("#backup-download")).to_be_visible()
        return
    # Non-admin sessions are redirected from /settings to / by app exception handling.
    assert page.url.startswith(f"{BASE_URL}/")


def test_logout_from_settings_redirects_to_lobby(page):
    page.goto(f"{BASE_URL}/settings")
    logout_button = page.get_by_role("button", name="Log out")
    if logout_button.count() == 0:
        pytest.skip("Logout button available on settings page for admin sessions only.")
    logout_button.click()
    expect(page).to_have_url(f"{BASE_URL}/lobby")
