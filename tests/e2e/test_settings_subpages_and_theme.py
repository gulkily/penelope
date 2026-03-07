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


def test_settings_backup_download_success_and_failure_status(page):
    page.goto(f"{BASE_URL}/settings")
    if not page_is_at(page, "/settings"):
        pytest.skip("Settings page requires admin access in this environment.")

    page.route(
        "**/api/backup",
        lambda route: route.fulfill(
            status=200,
            headers={
                "Content-Type": "application/x-sqlite3",
                "Content-Disposition": 'attachment; filename="north_star_backup.sqlite"',
            },
            body="sqlite",
        ),
    )
    page.locator("#backup-download").click()
    expect(page.locator("#backup-status")).to_have_text("Backup downloaded.")

    page.unroute("**/api/backup")
    page.route(
        "**/api/backup",
        lambda route: route.fulfill(status=500, body='{"detail":"failed"}'),
    )
    page.locator("#backup-download").click()
    expect(page.locator("#backup-status")).to_have_text("Backup failed. Please try again.")


def test_theme_toggle_cycles_on_major_pages(page):
    page.goto(f"{BASE_URL}/")
    page.evaluate("() => localStorage.removeItem('theme-preference')")
    page.reload()

    paths = ["/", "/projects", "/settings"]
    for path in paths:
        page.goto(f"{BASE_URL}{path}")
        if path == "/settings" and not page_is_at(page, "/settings"):
            continue
        toggle = page.locator("#theme-toggle")
        expect(toggle).to_be_visible()
        before = toggle.get_attribute("data-preference")
        toggle.click()
        after = toggle.get_attribute("data-preference")
        assert before is not None
        assert after is not None
        assert after != before
