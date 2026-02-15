import os

from playwright.sync_api import expect

from tests.e2e.data_factory import unique_project_name

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def create_project(page, project_name):
    page.goto(f"{BASE_URL}/projects")
    page.get_by_label("Project name").fill(project_name)
    page.get_by_role("button", name="Add project").click()
    expect(page.get_by_role("link", name=project_name)).to_be_visible()
    page.get_by_role("link", name=project_name).click()


def open_update_dialog(page):
    page.get_by_role("button", name="Add update").click()
    expect(page.locator("#transcript-dialog")).to_be_visible()


def test_interview_guide_checklist_progress_updates(page):
    create_project(page, unique_project_name())
    open_update_dialog(page)

    page.locator("#interview-guide-toggle").click()
    expect(page.locator("#interview-guide")).to_be_visible()
    expect(page.locator("#interview-guide-status")).to_have_text("Guide loaded.")

    first_checkbox = page.locator("#interview-guide-body input[type='checkbox']").first
    expect(first_checkbox).to_be_visible()
    expect(page.locator("#interview-guide-progress")).to_have_text("0/9 asked")

    first_checkbox.check()
    expect(page.locator("#interview-guide-progress")).to_have_text("1/9 asked")

    first_checkbox.uncheck()
    expect(page.locator("#interview-guide-progress")).to_have_text("0/9 asked")


def test_interview_guide_mobile_drawer_closes_on_backdrop(page):
    page.set_viewport_size({"width": 700, "height": 920})
    create_project(page, unique_project_name())
    open_update_dialog(page)

    page.locator("#interview-guide-toggle").click()
    expect(page.locator("#interview-guide")).to_be_visible()
    expect(page.locator("#interview-guide-backdrop")).to_be_visible()

    page.locator("#interview-guide-backdrop").click()
    expect(page.locator("#interview-guide")).to_be_hidden()
