"""Tests for the health check endpoint."""


def test_root_endpoint(client):
    """Root endpoint should return app info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "CareBuddy API"
    assert "version" in data


def test_health_endpoint(client):
    """Health endpoint should return status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ollama" in data
