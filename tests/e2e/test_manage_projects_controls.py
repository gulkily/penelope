import os
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import expect

from app import db
from tests.e2e.data_factory import unique_project_name

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def go_to_manage_residents(page) -> None:
    page.goto(f"{BASE_URL}/projects?page=1&sort_key=id&sort_dir=desc&house=All%20houses")
    expect(page.locator("#project-house")).not_to_have_value("")
    expect(page.locator("#pagination-status")).to_contain_text("Page")


def get_house_options(page) -> list[str]:
    return page.evaluate(
        """
        () => Array.from(document.querySelectorAll("#project-house option"))
          .map((option) => option.value)
          .filter((value) => Boolean(value))
        """
    )


def add_resident(page, resident_name: str, house: str) -> int:
    page.get_by_label("Resident name").fill(resident_name)
    page.locator("#project-house").select_option(house)
    with page.expect_response(
        lambda response: response.url.endswith("/api/projects")
        and response.request.method == "POST"
        and response.status == 200
    ) as response_info:
        page.get_by_role("button", name="Add resident").click()
    payload = response_info.value.json()
    project_id = int(payload["project"]["id"])
    page.wait_for_load_state("networkidle")
    return project_id


def project_row_by_id(page, project_id: int):
    return page.locator("tr", has=page.locator(f".table-house-select[data-project-id='{project_id}']"))


def get_project_via_api(page, project_id: int) -> dict:
    response = page.context.request.get(f"{BASE_URL}/api/projects/{project_id}")
    assert response.ok
    return response.json()


def ensure_manage_projects_multiple_pages(page, minimum_total: int = 101) -> None:
    response = page.context.request.get(
        f"{BASE_URL}/api/projects?include_archived=1&page=1&house=All%20houses"
    )
    assert response.ok
    payload = response.json()
    current_total = int(payload.get("total") or 0)
    if current_total >= minimum_total:
        return
    houses = get_house_options(page)
    assert houses
    seed_house = houses[0]
    for _ in range(minimum_total - current_total):
        db.create_project(unique_project_name(), seed_house)


def test_manage_projects_house_update_persists(page):
    go_to_manage_residents(page)
    houses = get_house_options(page)
    assert len(houses) >= 2
    house_a, house_b = houses[0], houses[1]

    resident_name = unique_project_name()
    project_id = add_resident(page, resident_name, house_a)

    row = project_row_by_id(page, project_id)
    house_select = row.locator(".table-house-select")
    expect(house_select).to_have_value(house_a)

    with page.expect_response(
        lambda response: response.url.endswith("/house")
        and response.request.method == "PUT"
        and response.status == 200
    ):
        house_select.select_option(house_b)

    row = project_row_by_id(page, project_id)
    expect(row.locator(".table-house-select")).to_have_value(house_b)

    page.reload()
    project = get_project_via_api(page, project_id)
    assert project.get("house") == house_b


def test_manage_projects_house_filter_syncs_url_and_rows(page):
    go_to_manage_residents(page)
    houses = get_house_options(page)
    assert len(houses) >= 2
    house_a, house_b = houses[0], houses[1]

    resident_a = f"AAA-{unique_project_name()}"
    resident_b = f"ZZZ-{unique_project_name()}"
    project_id_a = add_resident(page, resident_a, house_a)
    project_id_b = add_resident(page, resident_b, house_b)

    name_sort = page.locator("button.table-sort[data-sort='name']")
    name_sort.click()
    expect(name_sort.locator("xpath=ancestor::th[1]")).to_have_attribute(
        "aria-sort", "ascending"
    )

    house_filter = page.locator("#manage-house-filter")
    house_filter.select_option(house_a)

    expect(project_row_by_id(page, project_id_a)).to_be_visible()
    expect(project_row_by_id(page, project_id_b)).to_have_count(0)

    params = parse_qs(urlparse(page.url).query)
    assert params.get("house", [""])[0] == house_a

    page.reload()
    expect(project_row_by_id(page, project_id_a)).to_be_visible()
    expect(project_row_by_id(page, project_id_b)).to_have_count(0)


def test_manage_projects_name_sort_updates_url(page):
    go_to_manage_residents(page)

    name_sort = page.locator("button.table-sort[data-sort='name']")

    # First click: sort by name ascending.
    name_sort.click()
    header = name_sort.locator("xpath=ancestor::th[1]")
    expect(header).to_have_attribute("aria-sort", "ascending")

    # Second click: sort by name descending.
    name_sort.click()
    expect(header).to_have_attribute("aria-sort", "descending")

    params = parse_qs(urlparse(page.url).query)
    assert params.get("sort_key", [""])[0] == "name"
    assert params.get("sort_dir", [""])[0] == "desc"


def test_manage_projects_id_and_archived_sort_update_url(page):
    go_to_manage_residents(page)

    id_sort = page.locator("button.table-sort[data-sort='id']")
    id_header = id_sort.locator("xpath=ancestor::th[1]")
    id_sort.click()
    expect(id_header).to_have_attribute("aria-sort", "ascending")
    id_sort.click()
    expect(id_header).to_have_attribute("aria-sort", "descending")

    params = parse_qs(urlparse(page.url).query)
    assert params.get("sort_key", [""])[0] == "id"
    assert params.get("sort_dir", [""])[0] == "desc"

    archived_sort = page.locator("button.table-sort[data-sort='archived']")
    archived_header = archived_sort.locator("xpath=ancestor::th[1]")
    archived_sort.click()
    expect(archived_header).to_have_attribute("aria-sort", "ascending")

    params = parse_qs(urlparse(page.url).query)
    assert params.get("sort_key", [""])[0] == "archived"
    assert params.get("sort_dir", [""])[0] == "asc"


def test_manage_projects_pagination_next_prev_and_status(page):
    go_to_manage_residents(page)
    ensure_manage_projects_multiple_pages(page)

    page.goto(f"{BASE_URL}/projects?page=1&sort_key=id&sort_dir=asc&house=All%20houses")
    expect(page.locator("#pagination-status")).to_contain_text("Page 1 of")
    next_button = page.locator("#pagination-next")
    prev_button = page.locator("#pagination-prev")
    expect(next_button).to_be_enabled()
    expect(prev_button).to_be_disabled()

    next_button.click()
    expect(page.locator("#pagination-status")).to_contain_text("Page 2 of")
    expect(prev_button).to_be_enabled()
    params = parse_qs(urlparse(page.url).query)
    assert params.get("page", [""])[0] == "2"

    prev_button.click()
    expect(page.locator("#pagination-status")).to_contain_text("Page 1 of")
    expect(prev_button).to_be_disabled()


def test_manage_projects_back_forward_restores_filter_and_sort(page):
    go_to_manage_residents(page)
    houses = get_house_options(page)
    selected_house = houses[1] if len(houses) > 1 else houses[0]

    house_filter = page.locator("#manage-house-filter")
    house_filter.select_option(selected_house)
    params = parse_qs(urlparse(page.url).query)
    assert params.get("house", [""])[0] == selected_house

    name_sort = page.locator("button.table-sort[data-sort='name']")
    name_header = name_sort.locator("xpath=ancestor::th[1]")
    name_sort.click()
    expect(name_header).to_have_attribute("aria-sort", "ascending")
    url_after_name_sort = page.url

    archived_sort = page.locator("button.table-sort[data-sort='archived']")
    archived_header = archived_sort.locator("xpath=ancestor::th[1]")
    archived_sort.click()
    expect(archived_header).to_have_attribute("aria-sort", "ascending")

    page.go_back()
    expect(page).to_have_url(url_after_name_sort)
    expect(name_header).to_have_attribute("aria-sort", "ascending")
    expect(house_filter).to_have_value(selected_house)

    page.go_forward()
    expect(archived_header).to_have_attribute("aria-sort", "ascending")
    expect(house_filter).to_have_value(selected_house)
