import os

import pytest
from playwright.sync_api import expect

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def test_magic_link_house_prefills_from_existing_user(page):
    page.route(
        "**/api/houses",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"houses":["Unassigned","Actioners","SF2"],"all_houses_filter":"All houses"}',
        ),
    )
    page.route(
        "**/api/auth/magic-links",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"entries":[]}',
        ),
    )
    page.route(
        "**/api/auth/users?limit=500",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=(
                '{"entries":[{"id":1,"username":"Casey","house":"SF2","created_at":"2026-01-01T00:00:00Z"}],'
                '"total":1,"limit":500,"offset":0}'
            ),
        ),
    )

    page.goto(f"{BASE_URL}/settings/magic-links")
    if not page.url.startswith(f"{BASE_URL}/settings/magic-links"):
        pytest.skip("Magic links page requires admin access in this environment.")

    username = page.locator("#magic-link-username")
    house_select = page.locator("#magic-link-house")
    expect(house_select).to_have_value("Unassigned")
    username.fill("  cAsEy ")
    username.blur()
    expect(house_select).to_have_value("SF2")


def test_lobby_badge_indicator_updates_with_pending_count(page):
    page.route(
        "**/api/auth/lobby",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"entries":[{"request_id":"1"},{"request_id":"2"}]}',
        ),
    )
    page.goto(f"{BASE_URL}/")
    badge = page.locator("[data-lobby-count]").first
    if badge.count() == 0:
        pytest.skip("Lobby nav item is not enabled in this environment.")
    expect(badge).to_have_text("2")
    expect(badge).to_be_visible()
