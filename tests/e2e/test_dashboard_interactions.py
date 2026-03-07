import os
import re
import time

from playwright.sync_api import expect

from tests.e2e.data_factory import unique_project_name

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def create_resident_and_open_dashboard(page, resident_name: str) -> None:
    page.goto(f"{BASE_URL}/projects")
    expect(page.locator("#project-house")).not_to_have_value("")
    page.get_by_label("Resident name").fill(resident_name)
    page.get_by_role("button", name="Add resident").click()
    resident_link = page.get_by_role("link", name=resident_name)
    expect(resident_link).to_be_visible()
    resident_link.click()
    expect(page.locator("#objective-input")).to_be_enabled()


def add_summary_item(page, text: str) -> None:
    add_input = page.locator("[data-section='summary'] .inline-add-input")
    add_button = page.locator("[data-section='summary'] .inline-add-button")
    with page.expect_response(
        lambda response: "/items" in response.url
        and response.request.method == "POST"
        and response.status == 200
    ):
        add_input.fill(text)
        add_button.click()
    expect(
        page.locator(
            ".section-list[data-section='summary'] .section-item",
            has_text=text,
        ).first
    ).to_be_visible()


def test_goal_autosave_updates_progress_scale(page):
    resident_name = unique_project_name()
    new_goal = 200

    create_resident_and_open_dashboard(page, resident_name)

    with page.expect_response(
        lambda response: response.url.endswith("/progress")
        and response.request.method == "PUT"
        and response.status == 200
    ):
        page.evaluate(
            """
            () => {
              const slider = document.getElementById("progress-slider");
              if (!slider) return;
              slider.value = "50";
              slider.dispatchEvent(new Event("input", { bubbles: true }));
            }
            """
        )

    goal_input = page.locator("#goal-input")
    with page.expect_response(
        lambda response: response.url.endswith("/goal")
        and response.request.method == "PUT"
        and response.status == 200
    ):
        goal_input.fill(str(new_goal))

    expect(page.locator("#progress-percent")).to_have_text(
        re.compile(rf"100\s*/\s*{new_goal}")
    )

    page.reload()
    expect(page.locator("#objective-input")).to_be_enabled()
    expect(page.locator("#goal-input")).to_have_value(str(new_goal))
    expect(page.locator("#progress-percent")).to_have_text(
        re.compile(rf"100\s*/\s*{new_goal}")
    )


def test_delete_item_can_be_undone(page):
    timestamp = int(time.time())
    resident_name = unique_project_name()
    item_text = f"Undo Item {timestamp}"

    create_resident_and_open_dashboard(page, resident_name)
    add_summary_item(page, item_text)

    item_row = page.locator(
        ".section-list[data-section='summary'] .section-item",
        has_text=item_text,
    ).first
    with page.expect_response(
        lambda response: "/items/" in response.url
        and response.request.method == "DELETE"
        and response.status == 200
    ):
        item_row.locator(".item-delete").click()

    undo_toast = page.locator("#undo-toast")
    expect(undo_toast).to_be_visible()

    with page.expect_response(
        lambda response: "/items" in response.url
        and response.request.method == "POST"
        and response.status == 200
    ):
        page.locator("#undo-delete").click()

    expect(
        page.locator(
            ".section-list[data-section='summary'] .section-item",
            has_text=item_text,
        ).first
    ).to_be_visible()


def test_item_reorder_move_up_persists(page):
    timestamp = int(time.time())
    resident_name = unique_project_name()
    item_a = f"Reorder A {timestamp}"
    item_b = f"Reorder B {timestamp}"

    create_resident_and_open_dashboard(page, resident_name)
    add_summary_item(page, item_a)
    add_summary_item(page, item_b)

    row_b = page.locator(
        ".section-list[data-section='summary'] .section-item",
        has_text=item_b,
    ).first
    move_up = row_b.locator("[data-action='move-up']")
    expect(move_up).to_be_enabled()

    with page.expect_response(
        lambda response: response.url.endswith("/items/order")
        and response.request.method == "PUT"
        and response.status == 200
    ):
        move_up.click()

    first_row = page.locator(".section-list[data-section='summary'] .section-item").first
    expect(first_row).to_contain_text(item_b)

    page.reload()
    expect(page.locator("#objective-input")).to_be_enabled()
    first_row_after_reload = page.locator(
        ".section-list[data-section='summary'] .section-item"
    ).first
    expect(first_row_after_reload).to_contain_text(item_b)
