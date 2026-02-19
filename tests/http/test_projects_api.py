import os
import time


def test_project_endpoints_accept_updates(playwright):
    base_url = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    timestamp = int(time.time())
    name = f"API Project {timestamp}"
    objective = f"API Objective {timestamp}"
    progress = 42

    request_context = playwright.request.new_context(base_url=base_url)

    create_response = request_context.post(
        "/api/projects",
        data={"name": name, "house": "Actioners"},
    )
    assert create_response.ok
    create_payload = create_response.json()
    created_project = create_payload.get("project", {})
    project_id = created_project.get("id")
    assert project_id
    assert created_project.get("house") == "Actioners"

    objective_response = request_context.put(
        f"/api/projects/{project_id}/objective",
        data={"objective": objective},
    )
    assert objective_response.ok

    progress_response = request_context.put(
        f"/api/projects/{project_id}/progress",
        data={"progress": progress},
    )
    assert progress_response.ok

    project_response = request_context.get(f"/api/projects/{project_id}")
    assert project_response.ok
    project_payload = project_response.json()
    assert project_payload.get("objective") == objective
    assert project_payload.get("progress") == progress
    assert project_payload.get("house") == "Actioners"

    request_context.dispose()


def test_project_house_filter_and_update(playwright):
    base_url = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    timestamp = int(time.time())
    actioners_name = f"House Actioners {timestamp}"
    sf2_name = f"House SF2 {timestamp}"

    request_context = playwright.request.new_context(base_url=base_url)

    actioners_response = request_context.post(
        "/api/projects",
        data={"name": actioners_name, "house": "Actioners"},
    )
    assert actioners_response.ok
    actioners_project = actioners_response.json().get("project", {})
    actioners_id = actioners_project.get("id")
    assert actioners_id

    sf2_response = request_context.post(
        "/api/projects",
        data={"name": sf2_name, "house": "SF2"},
    )
    assert sf2_response.ok

    actioners_list = request_context.get("/api/projects?include_archived=1&house=Actioners")
    assert actioners_list.ok
    actioners_names = {
        project.get("name")
        for project in actioners_list.json().get("projects", [])
    }
    assert actioners_name in actioners_names
    assert sf2_name not in actioners_names

    update_house = request_context.put(
        f"/api/projects/{actioners_id}/house",
        data={"house": "SF2"},
    )
    assert update_house.ok
    assert update_house.json().get("project", {}).get("house") == "SF2"

    actioners_after_update = request_context.get(
        "/api/projects?include_archived=1&house=Actioners"
    )
    assert actioners_after_update.ok
    actioners_names_after_update = {
        project.get("name")
        for project in actioners_after_update.json().get("projects", [])
    }
    assert actioners_name not in actioners_names_after_update

    sf2_after_update = request_context.get("/api/projects?include_archived=1&house=SF2")
    assert sf2_after_update.ok
    sf2_names_after_update = {
        project.get("name")
        for project in sf2_after_update.json().get("projects", [])
    }
    assert actioners_name in sf2_names_after_update
    assert sf2_name in sf2_names_after_update

    request_context.dispose()


def test_create_project_requires_valid_house(playwright):
    base_url = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    timestamp = int(time.time())

    request_context = playwright.request.new_context(base_url=base_url)

    missing_house = request_context.post(
        "/api/projects",
        data={"name": f"Missing House {timestamp}"},
    )
    assert missing_house.status == 422

    invalid_house = request_context.post(
        "/api/projects",
        data={"name": f"Invalid House {timestamp}", "house": "Unknown"},
    )
    assert invalid_house.status == 400

    request_context.dispose()
