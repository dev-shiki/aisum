import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes import summarize
from unittest.mock import patch

def test_validate_youtube_url_valid():
    valid_urls = [
        "https://www.youtube.com/watch?v=abc123",
        "https://youtu.be/abc123",
        "https://www.youtube.com/embed/abc123",
        "https://www.youtube.com/v/abc123",
        "https://www.youtube.com/shorts/abc123",
        "https://youtube.com/shorts/abc123"
    ]
    for url in valid_urls:
        assert summarize.validate_youtube_url(url)

def test_validate_youtube_url_invalid():
    invalid_urls = [
        "https://google.com",
        "https://vimeo.com/abc123",
        "random string"
    ]
    for url in invalid_urls:
        assert not summarize.validate_youtube_url(url)

def test_youtube_test_endpoint():
    client = TestClient(app)
    resp = client.post("/api/summarize/youtube/test", json={"youtube_url": "https://youtu.be/abc123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["test_mode"] is True

def test_health_check_endpoint():
    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

def test_download_youtube_audio_error(monkeypatch, tmp_path):
    # Simulasi error pada subprocess.run
    monkeypatch.setattr(summarize, "subprocess", __import__("subprocess"))
    def fake_run(*a, **kw):
        class Result: returncode = 1; stdout = ""; stderr = "";
        return Result()
    monkeypatch.setattr(summarize.subprocess, "run", fake_run)
    with pytest.raises(Exception):
        summarize.download_youtube_audio("https://youtu.be/abc123", str(tmp_path)) 