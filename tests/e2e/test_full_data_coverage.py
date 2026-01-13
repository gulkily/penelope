import os
import time

from playwright.sync_api import expect

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

SECTIONS = {
    "summary": "Summary",
    "challenges": "Challenges",
    "opportunities": "Opportunities",
    "milestones": "Milestones",
}


def create_project(page, name):
    page.goto(f"{BASE_URL}/projects")
    page.get_by_label("Project name").fill(name)
    page.get_by_role("button", name="Add project").click()
    expect(page.get_by_role("link", name=name)).to_be_visible()
    page.get_by_role("link", name=name).click()


def add_item(page, section, text):
    add_input = page.locator(f"[data-section='{section}'] .inline-add-input")
    add_button = page.locator(f"[data-section='{section}'] .inline-add-button")
    with page.expect_response(
        lambda response: "/items" in response.url
        and response.request.method == "POST"
        and response.status == 200
    ):
        add_input.fill(text)
        add_button.click()


def test_populates_all_fields(page):
    timestamp = int(time.time())
    project_name = f"E2E Full Data {timestamp}"
    objective_text = f"E2E Objective {timestamp}"
    questions_text = f"E2E Questions {timestamp}"

    create_project(page, project_name)

    objective_input = page.locator("#objective-input")
    with page.expect_response(
        lambda response: response.url.endswith("/objective")
        and response.request.method == "PUT"
        and response.status == 200
    ):
        objective_input.fill(objective_text)

    with page.expect_response(
        lambda response: response.url.endswith("/progress")
        and response.request.method == "PUT"
        and response.status == 200
    ):
        page.evaluate(
            """
            () => {
              const slider = document.getElementById("progress-slider");
              if (!slider) {
                return;
              }
              slider.value = "75";
              slider.dispatchEvent(new Event("input", { bubbles: true }));
            }
            """
        )
    expect(page.locator("#progress-percent")).to_have_text("75%")

    questions_input = page.locator("#questions-input")
    with page.expect_response(
        lambda response: response.url.endswith("/questions")
        and response.request.method == "PUT"
        and response.status == 200
    ):
        questions_input.fill(questions_text)

    for section, label in SECTIONS.items():
        add_item(page, section, f"{label} item {timestamp}")
        item = page.locator(
            f".section-list[data-section='{section}'] .section-item",
            has_text=f"{label} item {timestamp}",
        )
        expect(item).to_be_visible()

    page.reload()
    expect(page.locator("#objective-input")).to_have_value(objective_text)
    expect(page.locator("#questions-input")).to_have_value(questions_text)
    expect(page.locator("#progress-percent")).to_have_text("75%")
    for section, label in SECTIONS.items():
        item = page.locator(
            f".section-list[data-section='{section}'] .section-item",
            has_text=f"{label} item {timestamp}",
        )
        expect(item).to_be_visible()
