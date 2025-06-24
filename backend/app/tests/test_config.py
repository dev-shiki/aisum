import os
import pytest
from app.config import Config

def test_config_getters(monkeypatch):
    monkeypatch.setenv("WHISPER_API_KEY", "abc")
    monkeypatch.setenv("GEMINI_API_KEY", "def")
    config = Config()
    assert config.WHISPER_API_URL.startswith("http")
    assert config.WHISPER_API_KEY == "abc"
    assert config.TEMP_FOLDER == "temp/"
    assert isinstance(config.MAX_SUMMARY_LENGTH, int)
    assert config.GEMINI_API_URL.startswith("http")
    assert config.GEMINI_API_KEY == "def"
    assert isinstance(config.GEMINI_RPM, int)
    assert isinstance(config.GEMINI_TPM, int)
    assert isinstance(config.GEMINI_RPD, int)

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