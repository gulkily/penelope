import os
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import expect

from tests.e2e.data_factory import unique_project_name

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def go_to_manage_residents(page) -> None:
    page.goto(f"{BASE_URL}/projects")
    expect(page.locator("#project-house")).not_to_have_value("")


def get_house_options(page) -> list[str]:
    return page.evaluate(
        """
        () => Array.from(document.querySelectorAll("#project-house option"))
          .map((option) => option.value)
          .filter((value) => Boolean(value))
        """
    )


def add_resident(page, resident_name: str, house: str) -> None:
    page.get_by_label("Resident name").fill(resident_name)
    page.locator("#project-house").select_option(house)
    page.get_by_role("button", name="Add resident").click()
    expect(page.get_by_role("link", name=resident_name)).to_be_visible()


def project_row(page, resident_name: str):
    return page.locator("tr", has=page.get_by_role("link", name=resident_name))


def test_manage_projects_house_update_persists(page):
    go_to_manage_residents(page)
    houses = get_house_options(page)
    assert len(houses) >= 2
    house_a, house_b = houses[0], houses[1]

    resident_name = unique_project_name()
    add_resident(page, resident_name, house_a)

    row = project_row(page, resident_name)
    house_select = row.locator(".table-house-select")
    expect(house_select).to_have_value(house_a)

    with page.expect_response(
        lambda response: response.url.endswith("/house")
        and response.request.method == "PUT"
        and response.status == 200
    ):
        house_select.select_option(house_b)

    row = project_row(page, resident_name)
    expect(row.locator(".table-house-select")).to_have_value(house_b)

    page.reload()
    row_after_reload = project_row(page, resident_name)
    expect(row_after_reload.locator(".table-house-select")).to_have_value(house_b)


def test_manage_projects_house_filter_syncs_url_and_rows(page):
    go_to_manage_residents(page)
    houses = get_house_options(page)
    assert len(houses) >= 2
    house_a, house_b = houses[0], houses[1]

    resident_a = unique_project_name()
    resident_b = unique_project_name()
    add_resident(page, resident_a, house_a)
    add_resident(page, resident_b, house_b)

    house_filter = page.locator("#manage-house-filter")
    house_filter.select_option(house_a)

    expect(project_row(page, resident_a)).to_be_visible()
    expect(project_row(page, resident_b)).to_have_count(0)

    params = parse_qs(urlparse(page.url).query)
    assert params.get("house", [""])[0] == house_a

    page.reload()
    expect(project_row(page, resident_a)).to_be_visible()
    expect(project_row(page, resident_b)).to_have_count(0)


def test_manage_projects_name_sort_updates_url(page):
    go_to_manage_residents(page)
    houses = get_house_options(page)
    assert len(houses) >= 1
    default_house = houses[0]

    resident_a = f"A-{unique_project_name()}"
    resident_z = f"Z-{unique_project_name()}"
    add_resident(page, resident_z, default_house)
    add_resident(page, resident_a, default_house)

    name_sort = page.locator("button.table-sort[data-sort='name']")

    # First click: sort by name ascending.
    name_sort.click()
    header = name_sort.locator("xpath=ancestor::th[1]")
    expect(header).to_have_attribute("aria-sort", "ascending")

    # Second click: sort by name descending.
    name_sort.click()
    expect(header).to_have_attribute("aria-sort", "descending")

    first_name_link = page.locator("#project-table-body tr td:nth-child(2) a").first
    expect(first_name_link).to_have_text(resident_z)

    params = parse_qs(urlparse(page.url).query)
    assert params.get("sort_key", [""])[0] == "name"
    assert params.get("sort_dir", [""])[0] == "desc"
