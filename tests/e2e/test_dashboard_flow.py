import os
import time

from playwright.sync_api import expect

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def test_can_create_project_and_update_north_star(page):
    timestamp = int(time.time())
    project_name = f"E2E Project {timestamp}"
    objective = f"E2E Objective {timestamp}"

    page.goto(f"{BASE_URL}/projects")
    page.get_by_label("Project name").fill(project_name)
    page.get_by_role("button", name="Add project").click()
    expect(page.get_by_role("link", name=project_name)).to_be_visible()

    page.get_by_role("link", name=project_name).click()

    objective_input = page.locator("#objective-input")
    expect(objective_input).to_be_enabled()

    with page.expect_response(
        lambda response: response.url.endswith("/objective")
        and response.request.method == "PUT"
        and response.status == 200
    ):
        objective_input.fill(objective)

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
              slider.value = "50";
              slider.dispatchEvent(new Event("input", { bubbles: true }));
            }
            """
        )

    expect(page.locator("#progress-percent")).to_have_text("50%")

    page.reload()
    expect(page.locator("#objective-input")).to_have_value(objective)
