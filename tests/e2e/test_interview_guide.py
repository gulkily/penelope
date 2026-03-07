import os
import re

from playwright.sync_api import expect

from tests.e2e.data_factory import unique_project_name

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def create_project(page, project_name):
    page.goto(f"{BASE_URL}/projects")
    expect(page.locator("#project-house")).not_to_have_value("")
    page.get_by_label("Resident name").fill(project_name)
    page.get_by_role("button", name="Add resident").click()
    expect(page.get_by_role("link", name=project_name)).to_be_visible()
    page.get_by_role("link", name=project_name).click()
    # Wait for dashboard interactivity to be restored for the selected resident.
    expect(page.locator("#objective-input")).to_be_enabled()
    expect(page.locator("#transcript-open")).to_be_enabled()


def open_update_dialog(page):
    trigger = page.get_by_role("button", name="Add update")
    expect(trigger).to_be_enabled()
    trigger.click()
    expect(page.locator("#transcript-dialog")).to_be_visible()


def open_loaded_guide(page):
    page.locator("#interview-guide-toggle").click()
    expect(page.locator("#interview-guide")).to_be_visible()
    first_checkbox = page.locator("#interview-guide-body input[type='checkbox']").first
    expect(first_checkbox).to_be_visible(timeout=15000)
    return first_checkbox


def test_interview_guide_checklist_progress_updates(page):
    create_project(page, unique_project_name())
    open_update_dialog(page)

    first_checkbox = open_loaded_guide(page)
    expect(page.locator("#interview-guide-progress")).to_have_text(
        re.compile(r"0/\d+\s+asked")
    )

    first_checkbox.set_checked(True, force=True)
    expect(page.locator("#interview-guide-progress")).to_have_text(
        re.compile(r"1/\d+\s+asked")
    )

    first_checkbox.set_checked(False, force=True)
    expect(page.locator("#interview-guide-progress")).to_have_text(
        re.compile(r"0/\d+\s+asked")
    )


def test_interview_guide_mobile_drawer_closes_on_backdrop(page):
    page.set_viewport_size({"width": 700, "height": 920})
    create_project(page, unique_project_name())
    open_update_dialog(page)

    open_loaded_guide(page)
    expect(page.locator("#interview-guide-backdrop")).to_be_visible()

    page.evaluate(
        """
        () => {
          const backdrop = document.getElementById("interview-guide-backdrop");
          if (!backdrop) {
            throw new Error("Missing interview guide backdrop");
          }
          backdrop.dispatchEvent(
            new MouseEvent("click", { bubbles: true, cancelable: true, view: window })
          );
        }
        """
    )
    page.wait_for_function(
        "() => document.getElementById('interview-guide')?.hidden === true"
    )
    expect(page.locator("#interview-guide")).to_be_hidden()
