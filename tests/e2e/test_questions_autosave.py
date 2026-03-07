import os
import time

import pytest
from playwright.sync_api import expect

from tests.e2e.data_factory import unique_project_name
from tests.e2e.helpers import create_resident, open_dashboard_project

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def create_project(page, project_name):
    project_id = create_resident(page, BASE_URL, project_name)
    open_dashboard_project(page, BASE_URL, project_id)


def test_questions_autosave(page):
    timestamp = int(time.time())
    project_name = unique_project_name()
    questions = f"E2E Questions {timestamp}"

    create_project(page, project_name)

    questions_input = page.locator("#questions-input")
    if questions_input.count() == 0:
        pytest.skip("Questions autosave requires admin-visible questions input.")
    expect(questions_input).to_be_enabled()

    with page.expect_response(
        lambda response: response.url.endswith("/questions")
        and response.request.method == "PUT"
        and response.status == 200
    ):
        questions_input.fill(questions)

    page.reload()
    expect(page.locator("#questions-input")).to_have_value(questions)
