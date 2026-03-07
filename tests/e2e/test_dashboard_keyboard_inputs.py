import os

from playwright.sync_api import expect

from tests.e2e.data_factory import unique_project_name
from tests.e2e.helpers import create_resident, open_dashboard_project

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def open_project(page):
    project_id = create_resident(page, BASE_URL, unique_project_name())
    open_dashboard_project(page, BASE_URL, project_id)


def test_inline_add_shift_enter_newline_then_enter_submits(page):
    open_project(page)

    add_input = page.locator("[data-section='summary'] .inline-add-input")
    add_input.click()
    add_input.type("Line 1")
    add_input.press("Shift+Enter")
    add_input.type("Line 2")

    expect(
        page.locator(
            ".section-list[data-section='summary'] .section-item",
            has_text="Line 1",
        )
    ).to_have_count(0)

    with page.expect_response(
        lambda response: "/items" in response.url
        and response.request.method == "POST"
        and response.status == 200
    ):
        add_input.press("Enter")

    created_item = page.locator(
        ".section-list[data-section='summary'] .section-item",
        has_text="Line 1",
    ).first
    expect(created_item).to_contain_text("Line 1")
    expect(created_item).to_contain_text("Line 2")


def test_item_edit_enter_key_saves(page):
    open_project(page)

    item_text = f"Keyboard edit {unique_project_name()}"
    updated_text = f"{item_text} updated"

    add_input = page.locator("[data-section='summary'] .inline-add-input")
    with page.expect_response(
        lambda response: "/items" in response.url
        and response.request.method == "POST"
        and response.status == 200
    ):
        add_input.fill(item_text)
        add_input.press("Enter")

    row = page.locator(
        ".section-list[data-section='summary'] .section-item",
        has_text=item_text,
    ).first
    expect(row).to_be_visible()
    entered_edit_mode = page.evaluate(
        """
        (label) => {
          const rows = Array.from(
            document.querySelectorAll(".section-list[data-section='summary'] .section-item")
          );
          const target = rows.find((entry) =>
            entry.querySelector(".item-text")?.textContent?.trim() === label
          );
          if (!target) {
            return false;
          }
          const button = target.querySelector("[data-action='edit']");
          if (!button) {
            return false;
          }
          button.click();
          return target.classList.contains("is-editing");
        }
        """,
        item_text,
    )
    assert entered_edit_mode
    edit_input = page.locator(
        ".section-list[data-section='summary'] .section-item.is-editing .item-input"
    ).first
    expect(edit_input).to_be_visible()
    edit_input.fill(updated_text)

    with page.expect_response(
        lambda response: "/items/" in response.url
        and response.request.method == "PUT"
        and response.status == 200
    ):
        edit_input.press("Enter")

    expect(row.locator(".item-input")).to_have_count(0)
    expect(row.locator(".item-text")).to_have_text(updated_text)
