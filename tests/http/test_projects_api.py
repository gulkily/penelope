import os
import time


def test_project_endpoints_accept_updates(playwright):
    base_url = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    timestamp = int(time.time())
    name = f"API Project {timestamp}"
    objective = f"API Objective {timestamp}"
    progress = 42

    request_context = playwright.request.new_context(base_url=base_url)

    create_response = request_context.post("/api/projects", json={"name": name})
    assert create_response.ok
    create_payload = create_response.json()
    project_id = create_payload.get("project", {}).get("id")
    assert project_id

    objective_response = request_context.put(
        f"/api/projects/{project_id}/objective",
        json={"objective": objective},
    )
    assert objective_response.ok

    progress_response = request_context.put(
        f"/api/projects/{project_id}/progress",
        json={"progress": progress},
    )
    assert progress_response.ok

    project_response = request_context.get(f"/api/projects/{project_id}")
    assert project_response.ok
    project_payload = project_response.json()
    assert project_payload.get("objective") == objective
    assert project_payload.get("progress") == progress

    request_context.dispose()
