import os
import time

from playwright.sync_api import expect

from tests.e2e.data_factory import unique_project_name

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def create_project(page, project_name):
    page.goto(f"{BASE_URL}/projects")
    page.get_by_label("Project name").fill(project_name)
    page.get_by_role("button", name="Add project").click()
    expect(page.get_by_role("link", name=project_name)).to_be_visible()
    page.get_by_role("link", name=project_name).click()


def test_item_add_edit_delete(page):
    timestamp = int(time.time())
    project_name = unique_project_name()
    item_text = f"E2E Item {timestamp}"
    updated_text = f"E2E Item Updated {timestamp}"

    create_project(page, project_name)

    add_input = page.locator("[data-section='summary'] .inline-add-input")
    add_button = page.locator("[data-section='summary'] .inline-add-button")

    with page.expect_response(
        lambda response: "/items" in response.url
        and response.request.method == "POST"
        and response.status == 200
    ):
        add_input.fill(item_text)
        add_button.click()

    item_row = page.locator(
        ".section-list[data-section='summary'] .section-item",
        has_text=item_text,
    ).first
    expect(item_row).to_be_visible()
    item_id = item_row.get_attribute("data-item-id")
    assert item_id

    row_by_id = page.locator(f'.section-item[data-item-id="{item_id}"]')

    with page.expect_response(
        lambda response: "/items/" in response.url
        and response.request.method == "PUT"
        and response.status == 200
    ):
        row_by_id.locator(".item-action-edit").click()
        edit_input = row_by_id.locator(".item-input")
        expect(edit_input).to_be_visible()
        edit_input.fill(updated_text)
        row_by_id.locator(".item-action-save").click()

    updated_row = page.locator(
        ".section-list[data-section='summary'] .section-item",
        has_text=updated_text,
    )
    expect(updated_row).to_be_visible()

    with page.expect_response(
        lambda response: "/items/" in response.url
        and response.request.method == "DELETE"
        and response.status == 200
    ):
        row_by_id.locator(".item-delete").click()

    expect(row_by_id).to_have_count(0)
