from fastapi.testclient import TestClient
from app.main import app
import pytest

def test_health_endpoint():
    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_shutdown_event():
    # Just trigger shutdown event for coverage
    with TestClient(app) as client:
        pass  # Exiting context triggers shutdown 