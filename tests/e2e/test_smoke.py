import os

from playwright.sync_api import expect

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def test_dashboard_loads(page):
    page.goto(f"{BASE_URL}/")
    expect(page).to_have_title("North Star Dashboard")
