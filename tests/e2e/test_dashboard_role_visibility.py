import os

from playwright.sync_api import expect

from app import db
from app.house import list_houses
from tests.e2e.data_factory import unique_project_name

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def test_non_admin_scope_and_read_only_notes(
    authenticated_non_admin_page,
    e2e_non_admin_account_id,
):
    houses = list_houses()
    assert len(houses) >= 2
    house_a, house_b = houses[0], houses[1]
    db.update_account_house(e2e_non_admin_account_id, house_a)

    project_a = db.create_project(unique_project_name(), house_a)
    project_b = db.create_project(unique_project_name(), house_b)
    db.update_summary(int(project_a["id"]), "Admin-only summary")
    db.update_questions(int(project_a["id"]), "Admin-only questions")

    page = authenticated_non_admin_page
    page.goto(f"{BASE_URL}/")
    expect(page.locator("#house-filter")).to_have_count(0)

    option_values = page.evaluate(
        """
        () => Array.from(document.querySelectorAll("#project-select option"))
          .map((option) => option.value)
          .filter((value) => Boolean(value))
        """
    )
    assert str(project_a["id"]) in option_values
    assert str(project_b["id"]) not in option_values

    page.goto(f"{BASE_URL}/?project={project_a['id']}")
    expect(page.locator("#summary-input")).to_have_count(0)
    expect(page.locator("#questions-input")).to_have_count(0)
    expect(page.locator("#summary-display")).to_have_text("Admin-only summary")
    expect(page.locator("#questions-display")).to_have_text("Admin-only questions")

    summary_update = page.context.request.put(
        f"{BASE_URL}/api/projects/{project_a['id']}/summary",
        data={"summary": "Should fail"},
    )
    questions_update = page.context.request.put(
        f"{BASE_URL}/api/projects/{project_a['id']}/questions",
        data={"questions": "Should fail"},
    )
    assert summary_update.status == 403
    assert questions_update.status == 403


def test_non_admin_dashboard_hides_settings_nav(authenticated_non_admin_page):
    page = authenticated_non_admin_page
    page.goto(f"{BASE_URL}/")
    expect(page.get_by_role("link", name="Settings")).to_have_count(0)
    page.goto(f"{BASE_URL}/settings")
    assert page.url.startswith(f"{BASE_URL}/")
