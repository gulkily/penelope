from playwright.sync_api import expect


def create_resident(page, base_url: str, resident_name: str) -> int:
    page.goto(f"{base_url}/projects?page=1&sort_key=id&sort_dir=desc&house=All%20houses")
    expect(page.locator("#project-house")).not_to_have_value("")
    page.get_by_label("Resident name").fill(resident_name)
    with page.expect_response(
        lambda response: response.url.endswith("/api/projects")
        and response.request.method == "POST"
        and response.status == 200
    ) as response_info:
        page.get_by_role("button", name="Add resident").click()
    payload = response_info.value.json()
    page.wait_for_load_state("networkidle")
    return int(payload["project"]["id"])


def open_dashboard_project(page, base_url: str, project_id: int) -> None:
    page.goto(f"{base_url}/?project={project_id}")
    expect(page.locator("#objective-input")).to_be_enabled()
