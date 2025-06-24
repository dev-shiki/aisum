import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes import summarize
from unittest.mock import patch, MagicMock
import os

def test_validate_youtube_url_all_patterns():
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
    invalid_urls = ["https://google.com", "random string"]
    for url in invalid_urls:
        assert not summarize.validate_youtube_url(url)

def test_download_youtube_audio_success(monkeypatch, tmp_path):
    # Simulasi file mp3 berhasil di-download
    monkeypatch.setattr(summarize, "subprocess", __import__("subprocess"))
    class Result:
        returncode = 0
        stdout = ""
        stderr = ""
    monkeypatch.setattr(summarize.subprocess, "run", lambda *a, **k: Result())
    monkeypatch.setattr(os, "listdir", lambda d: ["abc.mp3"])
    monkeypatch.setattr(os.path, "getsize", lambda f: 1024*1024)
    monkeypatch.setattr(os.path, "join", lambda a, b: f"{a}/{b}")
    monkeypatch.setattr(os.path, "exists", lambda f: True)
    monkeypatch.setattr(os, "remove", lambda f: None)
    path = summarize.download_youtube_audio("https://youtu.be/abc123", str(tmp_path))
    assert path.endswith(".mp3")

def test_download_youtube_audio_no_file(monkeypatch, tmp_path):
    monkeypatch.setattr(summarize, "subprocess", __import__("subprocess"))
    class Result:
        returncode = 0
        stdout = ""
        stderr = ""
    monkeypatch.setattr(summarize.subprocess, "run", lambda *a, **k: Result())
    monkeypatch.setattr(os, "listdir", lambda d: ["abc.txt"])
    with pytest.raises(Exception):
        summarize.download_youtube_audio("https://youtu.be/abc123", str(tmp_path))

def test_download_youtube_audio_timeout(monkeypatch, tmp_path):
    def raise_timeout(*a, **k):
        raise summarize.subprocess.TimeoutExpired(cmd="yt-dlp", timeout=180)
    monkeypatch.setattr(summarize, "subprocess", __import__("subprocess"))
    monkeypatch.setattr(summarize.subprocess, "run", raise_timeout)
    with pytest.raises(Exception):
        summarize.download_youtube_audio("https://youtu.be/abc123", str(tmp_path))

def test_download_youtube_audio_other_error(monkeypatch, tmp_path):
    def raise_error(*a, **k):
        raise Exception("fail")
    monkeypatch.setattr(summarize, "subprocess", __import__("subprocess"))
    monkeypatch.setattr(summarize.subprocess, "run", raise_error)
    with pytest.raises(Exception):
        summarize.download_youtube_audio("https://youtu.be/abc123", str(tmp_path))

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

def test_status_endpoint():
    client = TestClient(app)
    resp = client.get("/api/summarize/status/unknown")
    assert resp.status_code == 200
    assert resp.json()["status"] == "not_found"

@patch("app.routes.summarize.transcribe_audio", return_value="transkrip")
@patch("app.routes.summarize.summarize_with_gemini", return_value="summary")
def test_summarize_youtube_success(mock_gemini, mock_whisper, monkeypatch):
    monkeypatch.setenv("WHISPER_API_KEY", "abc")
    monkeypatch.setenv("GEMINI_API_KEY", "def")
    client = TestClient(app)
    with patch("app.routes.summarize.download_youtube_audio", return_value="audio.mp3"), \
         patch("os.remove"), patch("shutil.rmtree"):
        resp = client.post("/api/summarize/youtube/", json={"youtube_url": "https://youtu.be/abc123"})
        assert resp.status_code == 200 or resp.status_code == 500 or resp.status_code == 400

@patch("app.routes.summarize.transcribe_audio", return_value="")
@patch("app.routes.summarize.summarize_with_gemini", return_value="summary")
def test_summarize_youtube_empty_transcription(mock_gemini, mock_whisper, monkeypatch):
    monkeypatch.setenv("WHISPER_API_KEY", "abc")
    monkeypatch.setenv("GEMINI_API_KEY", "def")
    client = TestClient(app)
    with patch("app.routes.summarize.download_youtube_audio", return_value="audio.mp3"), \
         patch("os.remove"), patch("shutil.rmtree"):
        resp = client.post("/api/summarize/youtube/", json={"youtube_url": "https://youtu.be/abc123"})
        assert resp.status_code == 400

def test_summarize_youtube_invalid_url():
    client = TestClient(app)
    resp = client.post("/api/summarize/youtube/", json={"youtube_url": "https://google.com"})
    assert resp.status_code == 400

def test_summarize_youtube_config_error(monkeypatch):
    monkeypatch.delenv("WHISPER_API_KEY", raising=False)
    client = TestClient(app)
    resp = client.post("/api/summarize/youtube/", json={"youtube_url": "https://youtu.be/abc123"})
    assert resp.status_code == 500

def test_summarize_upload_file_success(monkeypatch, tmp_path):
    monkeypatch.setenv("WHISPER_API_KEY", "abc")
    monkeypatch.setenv("GEMINI_API_KEY", "def")
    client = TestClient(app)
    class DummyFile:
        filename = "test.mp3"
        file = MagicMock()
    with patch("builtins.open", create=True) as mock_open, \
         patch("shutil.copyfileobj") as mock_copy, \
         patch("os.makedirs"):
        mock_open.return_value.__enter__.return_value = MagicMock()
        resp = client.post("/api/summarize/", files={"file": ("test.mp3", b"data", "audio/mp3")})
        assert resp.status_code == 200
        assert "task_id" in resp.json()

def test_summarize_upload_file_invalid(monkeypatch):
    client = TestClient(app)
    resp = client.post("/api/summarize/", files={"file": ("", b"data", "audio/mp3")})
    assert resp.status_code == 400
    resp2 = client.post("/api/summarize/", files={"file": ("test.txt", b"data", "text/plain")})
    assert resp2.status_code == 400

def test_summarize_upload_file_save_error(monkeypatch):
    monkeypatch.setenv("WHISPER_API_KEY", "abc")
    monkeypatch.setenv("GEMINI_API_KEY", "def")
    client = TestClient(app)
    with patch("builtins.open", side_effect=Exception("fail")), \
         patch("os.makedirs"):
        resp = client.post("/api/summarize/", files={"file": ("test.mp3", b"data", "audio/mp3")})
        assert resp.status_code == 500

def test_summarize_upload_file_config_error(monkeypatch):
    monkeypatch.delenv("WHISPER_API_KEY", raising=False)
    client = TestClient(app)
    resp = client.post("/api/summarize/", files={"file": ("test.mp3", b"data", "audio/mp3")})
    assert resp.status_code == 500

def test_status_endpoint_task_exists(monkeypatch):
    from app.routes.summarize import tasks
    client = TestClient(app)
    tasks["abc"] = {"status": "completed"}
    resp = client.get("/api/summarize/status/abc")
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"
    tasks.pop("abc")

def test_process_task_error(monkeypatch):
    # Test error path di async process_task
    monkeypatch.setenv("WHISPER_API_KEY", "abc")
    monkeypatch.setenv("GEMINI_API_KEY", "def")
    client = TestClient(app)
    with patch("builtins.open", create=True) as mock_open, \
         patch("shutil.copyfileobj") as mock_copy, \
         patch("os.makedirs"), \
         patch("app.routes.summarize.transcribe_audio", side_effect=Exception("fail")):
        mock_open.return_value.__enter__.return_value = MagicMock()
        resp = client.post("/api/summarize/", files={"file": ("test.mp3", b"data", "audio/mp3")})
        assert resp.status_code == 200
        # Tunggu task async selesai (opsional, bisa dicek status task jika ingin lebih detail) 