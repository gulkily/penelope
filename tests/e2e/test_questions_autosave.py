import os
import time

from playwright.sync_api import expect

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def create_project(page, project_name):
    page.goto(f"{BASE_URL}/projects")
    page.get_by_label("Project name").fill(project_name)
    page.get_by_role("button", name="Add project").click()
    expect(page.get_by_role("link", name=project_name)).to_be_visible()
    page.get_by_role("link", name=project_name).click()


def test_questions_autosave(page):
    timestamp = int(time.time())
    project_name = f"E2E Questions {timestamp}"
    questions = f"E2E Questions {timestamp}"

    create_project(page, project_name)

    questions_input = page.locator("#questions-input")
    expect(questions_input).to_be_enabled()

    with page.expect_response(
        lambda response: response.url.endswith("/questions")
        and response.request.method == "PUT"
        and response.status == 200
    ):
        questions_input.fill(questions)

    page.reload()
    expect(page.locator("#questions-input")).to_have_value(questions)
