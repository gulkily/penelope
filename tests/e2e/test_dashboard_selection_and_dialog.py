import os

from playwright.sync_api import expect

from tests.e2e.data_factory import unique_project_name
from tests.e2e.helpers import create_resident, open_dashboard_project

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def test_dashboard_empty_state_before_selection(page):
    page.goto(f"{BASE_URL}/")
    expect(page.locator("#empty-state")).to_be_visible()
    expect(page.locator("#objective-input")).to_be_disabled()
    expect(page.locator("#transcript-open")).to_be_disabled()


def test_project_query_param_loads_selected_resident(page):
    resident_name = unique_project_name()
    project_id = create_resident(page, BASE_URL, resident_name)

    open_dashboard_project(page, BASE_URL, project_id)
    expect(page.locator("#project-select")).to_have_value(str(project_id))
    expect(page.locator("#objective-input")).to_be_enabled()


def test_add_update_dialog_open_close_and_g_shortcut(page):
    resident_name = unique_project_name()
    project_id = create_resident(page, BASE_URL, resident_name)
    open_dashboard_project(page, BASE_URL, project_id)

    open_button = page.get_by_role("button", name="Add update")
    expect(open_button).to_be_enabled()
    open_button.click()
    expect(page.locator("#transcript-dialog")).to_be_visible()

    # `g` toggles interview guide while dialog is open.
    page.locator("#transcript-analyze").focus()
    page.keyboard.press("g")
    expect(page.locator("#interview-guide")).to_be_visible()
    page.keyboard.press("g")
    expect(page.locator("#interview-guide")).to_be_hidden()

    # Escape closes dialog when guide is closed.
    page.keyboard.press("Escape")
    expect(page.locator("#transcript-dialog")).to_be_hidden()
