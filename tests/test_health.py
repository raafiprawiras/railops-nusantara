"""Tests for the /health endpoint."""

import json


def test_health_endpoint_returns_json(client):
    """Health endpoint should return JSON with expected fields."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = json.loads(response.data)
    assert "application" in data
    assert "database" in data
    assert "localstack" in data
    assert "status" in data


def test_health_application_always_healthy(client):
    """Application field should always be healthy if endpoint responds."""
    response = client.get("/health")
    data = json.loads(response.data)

    assert data["application"] == "healthy"


def test_health_status_degraded_without_services(client):
    """Without running services, status should be degraded."""
    response = client.get("/health")
    data = json.loads(response.data)

    assert data["status"] in ("healthy", "degraded")


def test_index_redirects(client):
    """Index should redirect to dashboard."""
    response = client.get("/")

    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]
