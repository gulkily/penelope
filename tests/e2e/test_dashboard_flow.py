import os
import re
import time

from playwright.sync_api import expect

from tests.e2e.data_factory import unique_project_name
from tests.e2e.helpers import create_resident, open_dashboard_project

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def test_can_create_project_and_update_north_star(page):
    timestamp = int(time.time())
    project_name = unique_project_name()
    objective = f"E2E Objective {timestamp}"

    project_id = create_resident(page, BASE_URL, project_name)
    open_dashboard_project(page, BASE_URL, project_id)

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

    expect(page.locator("#progress-percent")).to_have_text(re.compile(r"50\s*/\s*100"))

    page.reload()
    expect(page.locator("#objective-input")).to_have_value(objective)
