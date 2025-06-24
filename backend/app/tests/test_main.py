from fastapi.testclient import TestClient
from app.main import app
import pytest
import os

def test_health_endpoint(monkeypatch):
    monkeypatch.setenv("WHISPER_API_KEY", "abc")
    monkeypatch.setenv("GEMINI_API_KEY", "def")
    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_shutdown_event(monkeypatch):
    monkeypatch.setenv("WHISPER_API_KEY", "abc")
    monkeypatch.setenv("GEMINI_API_KEY", "def")
    with TestClient(app) as client:
        pass  # Exiting context triggers shutdown 