import os
import re
import time

from playwright.sync_api import expect

from tests.e2e.data_factory import unique_project_name
from tests.e2e.helpers import create_resident, open_dashboard_project

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def create_resident_and_open_dashboard(page, resident_name: str) -> None:
    project_id = create_resident(page, BASE_URL, resident_name)
    open_dashboard_project(page, BASE_URL, project_id)


def add_summary_item(page, text: str) -> None:
    input_box = page.locator("[data-section='summary'] .inline-add-input")
    with page.expect_response(
        lambda response: "/items" in response.url
        and response.request.method == "POST"
        and response.status == 200
    ):
        input_box.fill(text)
        page.locator("[data-section='summary'] .inline-add-button").click()
    expect(
        page.locator(".section-list[data-section='summary'] .section-item", has_text=text).first
    ).to_be_visible()


def test_progress_graph_toggle_shows_panel_and_empty_state(page):
    resident_name = unique_project_name()
    create_resident_and_open_dashboard(page, resident_name)

    # Write progress twice to ensure history points exist.
    for value in ("20", "40"):
        with page.expect_response(
            lambda response: response.url.endswith("/progress")
            and response.request.method == "PUT"
            and response.status == 200
        ):
            page.evaluate(
                """
                (nextValue) => {
                  const slider = document.getElementById("progress-slider");
                  if (!slider) return;
                  slider.value = nextValue;
                  slider.dispatchEvent(new Event("input", { bubbles: true }));
                }
                """,
                value,
            )

    toggle = page.locator("#progress-graph-toggle")
    expect(toggle).to_be_enabled()
    toggle.click()

    panel = page.locator("#progress-graph-panel")
    expect(panel).to_be_visible()
    expect(page.locator("#progress-graph-indicator")).to_have_text("Hide")
    # Default residency range is Jan 1-31; runtime updates outside that window show empty-state.
    expect(page.locator("#progress-graph-empty")).to_be_visible()


def test_keyboard_reorder_moves_item_up(page):
    timestamp = int(time.time())
    resident_name = unique_project_name()
    item_a = f"Keyboard A {timestamp}"
    item_b = f"Keyboard B {timestamp}"

    create_resident_and_open_dashboard(page, resident_name)
    add_summary_item(page, item_a)
    add_summary_item(page, item_b)

    second_row = page.locator(
        ".section-list[data-section='summary'] .section-item",
        has_text=item_b,
    ).first
    drag_handle = second_row.locator(".item-drag-handle")
    expect(drag_handle).to_be_enabled()
    drag_handle.focus()

    with page.expect_response(
        lambda response: response.url.endswith("/items/order")
        and response.request.method == "PUT"
        and response.status == 200
    ):
        page.keyboard.press("ArrowUp")

    first_row = page.locator(".section-list[data-section='summary'] .section-item").first
    expect(first_row).to_contain_text(item_b)


def test_escape_cancels_item_edit(page):
    timestamp = int(time.time())
    resident_name = unique_project_name()
    item_text = f"Edit Escape {timestamp}"
    changed_text = f"{item_text} changed"

    create_resident_and_open_dashboard(page, resident_name)
    add_summary_item(page, item_text)

    row = page.locator(
        ".section-list[data-section='summary'] .section-item",
        has_text=item_text,
    ).first
    page.evaluate(
        """
        (label) => {
          const rows = Array.from(
            document.querySelectorAll(".section-list[data-section='summary'] .section-item")
          );
          const target = rows.find((entry) => entry.textContent?.includes(label));
          if (!target) {
            throw new Error("Unable to find target row for edit");
          }
          const editButton = target.querySelector("[data-action='edit']");
          if (!editButton) {
            throw new Error("Unable to find edit button");
          }
          editButton.click();
        }
        """,
        item_text,
    )

    edit_input = page.locator(
        ".section-list[data-section='summary'] .section-item.is-editing .item-input"
    )
    expect(edit_input).to_be_visible()
    edit_input.fill(changed_text)
    edit_input.press("Escape")

    expect(row.locator(".item-input")).to_have_count(0)
    expect(row.locator(".item-text")).to_have_text(re.compile(re.escape(item_text)))
