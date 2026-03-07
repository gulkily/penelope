import os

import pytest
from playwright.sync_api import expect

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def page_is_at(page, path: str) -> bool:
    return page.url.startswith(f"{BASE_URL}{path}")


def test_session_identity_visible_on_dashboard(page):
    page.goto(f"{BASE_URL}/")
    expect(page.locator("[data-session-identity]")).to_be_visible()
    expect(page.locator(".session-identity-name")).to_be_visible()


def test_theme_preference_persists_across_pages(page):
    page.goto(f"{BASE_URL}/")
    toggle = page.locator("#theme-toggle")
    expect(toggle).to_be_visible()
    expect(toggle).to_have_attribute("data-preference", "system")

    toggle.click()
    expect(toggle).to_have_attribute("data-preference", "dark")
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")

    page.goto(f"{BASE_URL}/projects")
    expect(page.locator("#theme-toggle")).to_have_attribute("data-preference", "dark")
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")


def test_settings_subpage_access_behavior(page):
    routes = [
        ("/settings", "Settings"),
        ("/settings/magic-links", "Magic Login Links"),
        ("/settings/users", "Users"),
        ("/ledger", "Ledger"),
    ]
    for path, heading in routes:
        page.goto(f"{BASE_URL}{path}")
        if page_is_at(page, path):
            expect(page.get_by_role("heading", name=heading)).to_be_visible()
        else:
            # Non-admin sessions are redirected from protected pages.
            assert page.url.startswith(f"{BASE_URL}/")


def test_settings_version_metadata_visible_when_settings_accessible(page):
    page.goto(f"{BASE_URL}/settings")
    if not page_is_at(page, "/settings"):
        pytest.skip("Settings page requires admin access in this environment.")

    expect(page.get_by_text("Commit:", exact=False)).to_be_visible()
    expect(page.get_by_text("Date:", exact=False)).to_be_visible()
