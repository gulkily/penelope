import os

from playwright.sync_api import expect

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def test_theme_toggle_cycles_preferences(page):
    page.goto(f"{BASE_URL}/")

    toggle = page.locator("#theme-toggle")
    expect(toggle).to_be_visible()
    expect(toggle).to_have_attribute("data-preference", "system")

    toggle.click()
    expect(toggle).to_have_attribute("data-preference", "dark")
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")

    toggle.click()
    expect(toggle).to_have_attribute("data-preference", "light")
    expect(page.locator("html")).to_have_attribute("data-theme", "light")
