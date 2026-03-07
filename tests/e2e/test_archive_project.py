import os
import re

from playwright.sync_api import expect

from tests.e2e.data_factory import unique_project_name
from tests.e2e.helpers import create_resident

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def test_archive_unarchive_project(page):
    project_name = unique_project_name()
    project_id = create_resident(page, BASE_URL, project_name)

    row = page.locator(
        "tr",
        has=page.locator(f".table-house-select[data-project-id='{project_id}']"),
    )
    checkbox = row.get_by_role("checkbox")

    with page.expect_response(
        lambda response: "/archive" in response.url
        and response.request.method == "PUT"
        and response.status == 200
    ):
        checkbox.check()

    row = page.locator(
        "tr",
        has=page.locator(f".table-house-select[data-project-id='{project_id}']"),
    )
    expect(row).to_have_class(re.compile(r"\bis-archived\b"))

    with page.expect_response(
        lambda response: "/archive" in response.url
        and response.request.method == "PUT"
        and response.status == 200
    ):
        row.get_by_role("checkbox").uncheck()

    row = page.locator(
        "tr",
        has=page.locator(f".table-house-select[data-project-id='{project_id}']"),
    )
    expect(row).not_to_have_class(re.compile(r"\bis-archived\b"))
