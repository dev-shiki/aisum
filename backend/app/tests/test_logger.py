import pytest
import logging
from unittest.mock import AsyncMock, patch
from fastapi import Request, Response
from app.utils.logger import log_request, log_response

@pytest.mark.asyncio
def test_log_request_multipart_logs_file_upload(caplog):
    mock_request = AsyncMock(spec=Request)
    mock_request.headers = {"content-type": "multipart/form-data"}
    mock_request.method = "POST"
    mock_request.url = "http://test/upload"
    with caplog.at_level(logging.INFO):
        import asyncio; asyncio.run(log_request(mock_request))
    assert "File Upload Detected" in caplog.text

@pytest.mark.asyncio
def test_log_request_normal_logs_body(caplog):
    mock_request = AsyncMock(spec=Request)
    mock_request.headers = {"content-type": "application/json"}
    mock_request.method = "POST"
    mock_request.url = "http://test/upload"
    mock_request.body.return_value = b'{"foo": "bar"}'
    with caplog.at_level(logging.INFO):
        import asyncio; asyncio.run(log_request(mock_request))
    assert 'Body: {"foo": "bar"}' in caplog.text

@pytest.mark.asyncio
def test_log_request_exception_logs_error(caplog):
    mock_request = AsyncMock(spec=Request)
    mock_request.headers = {"content-type": "application/json"}
    mock_request.method = "POST"
    mock_request.url = "http://test/upload"
    mock_request.body.side_effect = Exception("fail body")
    with caplog.at_level(logging.ERROR):
        import asyncio; asyncio.run(log_request(mock_request))
    assert "Gagal mencatat request" in caplog.text

@pytest.mark.asyncio
def test_log_response_logs_status(caplog):
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = 200
    with caplog.at_level(logging.INFO):
        import asyncio; asyncio.run(log_response(mock_response))
    assert "Response: Status 200" in caplog.text

@pytest.mark.asyncio
def test_log_response_exception_logs_error(caplog):
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = 200
    with patch("logging.info", side_effect=Exception("fail log")):
        with caplog.at_level(logging.ERROR):
            import asyncio; asyncio.run(log_response(mock_response))
    assert "Gagal mencatat response" in caplog.text 