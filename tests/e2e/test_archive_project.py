import os
import re

from playwright.sync_api import expect

from tests.e2e.data_factory import unique_project_name

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def test_archive_unarchive_project(page):
    project_name = unique_project_name()

    page.goto(f"{BASE_URL}/projects")
    page.get_by_label("Project name").fill(project_name)
    page.get_by_role("button", name="Add project").click()
    expect(page.get_by_role("link", name=project_name)).to_be_visible()

    row = page.locator("tr", has=page.get_by_role("link", name=project_name))
    checkbox = row.get_by_role("checkbox")

    with page.expect_response(
        lambda response: "/archive" in response.url
        and response.request.method == "PUT"
        and response.status == 200
    ):
        checkbox.check()

    row = page.locator("tr", has=page.get_by_role("link", name=project_name))
    expect(row).to_have_class(re.compile(r"\bis-archived\b"))

    with page.expect_response(
        lambda response: "/archive" in response.url
        and response.request.method == "PUT"
        and response.status == 200
    ):
        row.get_by_role("checkbox").uncheck()

    row = page.locator("tr", has=page.get_by_role("link", name=project_name))
    expect(row).not_to_have_class(re.compile(r"\bis-archived\b"))
