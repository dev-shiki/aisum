import os
import pytest
from app.config import Config

def test_config_getters(monkeypatch):
    monkeypatch.setenv("WHISPER_API_KEY", "abc")
    monkeypatch.setenv("GEMINI_API_KEY", "def")
    assert Config.WHISPER_API_URL.startswith("http")
    assert Config.WHISPER_API_KEY == "abc"
    assert Config.TEMP_FOLDER == "temp/"
    assert isinstance(Config.MAX_SUMMARY_LENGTH, int)
    assert Config.GEMINI_API_URL.startswith("http")
    assert Config.GEMINI_API_KEY == "def"
    assert isinstance(Config.GEMINI_RPM, int)
    assert isinstance(Config.GEMINI_TPM, int)
    assert isinstance(Config.GEMINI_RPD, int)

def test_validate_config_success(monkeypatch):
    monkeypatch.setenv("WHISPER_API_KEY", "abc")
    monkeypatch.setenv("GEMINI_API_KEY", "def")
    Config.validate_config()

def test_validate_config_missing_whisper(monkeypatch):
    monkeypatch.delenv("WHISPER_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "def")
    with pytest.raises(ValueError):
        Config.validate_config()

def test_validate_config_missing_gemini(monkeypatch, capsys):
    monkeypatch.setenv("WHISPER_API_KEY", "abc")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    Config.validate_config()
    captured = capsys.readouterr()
    assert "GEMINI_API_KEY tidak ditemukan" in captured.out 