"""Tests for UI Foundation routes."""


def test_dashboard_returns_200(logged_in_client):
    """GET /dashboard should return 200 when authenticated."""
    response = logged_in_client.get("/dashboard")
    assert response.status_code == 200


def test_login_returns_200(client):
    """GET /login should return 200."""
    response = client.get("/login")
    assert response.status_code == 200


def test_dashboard_contains_app_name(logged_in_client):
    """Dashboard page should contain 'RailOps Nusantara'."""
    response = logged_in_client.get("/dashboard")
    assert b"RailOps Nusantara" in response.data


def test_index_redirects_to_dashboard(logged_in_client):
    """GET / should redirect to /dashboard."""
    response = logged_in_client.get("/")
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]


def test_404_page(client):
    """Non-existent route should return 404 with custom page."""
    response = client.get("/halaman-tidak-ada")
    assert response.status_code == 404
    assert b"404" in response.data
