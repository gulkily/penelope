import pytest


@pytest.mark.prod_smoke
def test_prod_smoke_welcome_page_reachable(playwright, e2e_base_url: str):
    request_context = playwright.request.new_context(base_url=e2e_base_url)
    response = request_context.get("/welcome", max_redirects=0)
    assert response.status == 200
    assert "Welcome" in response.text()
    request_context.dispose()


@pytest.mark.prod_smoke
def test_prod_smoke_projects_api_requires_auth(playwright, e2e_base_url: str):
    request_context = playwright.request.new_context(base_url=e2e_base_url)
    response = request_context.get("/api/projects", max_redirects=0)
    assert response.status == 401
    request_context.dispose()


@pytest.mark.prod_smoke
def test_prod_smoke_lobby_route_reachable(playwright, e2e_base_url: str):
    request_context = playwright.request.new_context(base_url=e2e_base_url)
    response = request_context.get("/lobby", max_redirects=0)
    assert response.status == 200
    body = response.text()
    assert "Request Access" in body or "Lobby authentication is disabled" in body
    request_context.dispose()
