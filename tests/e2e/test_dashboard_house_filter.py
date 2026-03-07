import os
from urllib.parse import parse_qs, urlparse

import pytest
from playwright.sync_api import expect

from app import db
from app.house import list_houses
from tests.e2e.data_factory import unique_project_name

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def test_dashboard_house_filter_syncs_url_storage_and_resident_options(page):
    houses = list_houses()
    if len(houses) < 2:
        pytest.skip("Need at least two houses for house-filter coverage.")
    house_a, house_b = houses[0], houses[1]

    project_a = db.create_project(unique_project_name(), house_a)
    project_b = db.create_project(unique_project_name(), house_b)

    page.goto(f"{BASE_URL}/")
    house_filter = page.locator("#house-filter")
    if house_filter.count() == 0:
        pytest.skip("Dashboard house filter is only shown for admin sessions.")

    house_filter.select_option(house_a)
    expect(house_filter).to_have_value(house_a)
    params = parse_qs(urlparse(page.url).query)
    assert params.get("house", [""])[0] == house_a
    stored_house_filter = page.evaluate("() => localStorage.getItem('houseFilter')")
    assert stored_house_filter == house_a

    page.wait_for_function(
        """
        (excludedId) => {
          const options = Array.from(document.querySelectorAll("#project-select option"))
            .map((option) => option.value)
            .filter((value) => Boolean(value));
          return !options.includes(excludedId);
        }
        """,
        arg=str(project_b["id"]),
    )
    resident_option_values = page.evaluate(
        """
        () => Array.from(document.querySelectorAll("#project-select option"))
          .map((option) => option.value)
          .filter((value) => Boolean(value))
        """
    )
    assert str(project_a["id"]) in resident_option_values
    assert str(project_b["id"]) not in resident_option_values

    page.reload()
    expect(page.locator("#house-filter")).to_have_value(house_a)
