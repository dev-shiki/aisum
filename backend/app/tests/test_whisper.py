import pytest
from unittest.mock import patch, MagicMock
from app.services import whisper

def test_transcribe_audio_success():
    with patch('app.services.whisper.requests.post') as mock_post, \
         patch('builtins.open', create=True) as mock_open:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'text': 'transkrip'}
        mock_open.return_value.__enter__.return_value = MagicMock()
        result = whisper.transcribe_audio('file.mp3', language='id')
        assert result == 'transkrip'

def test_transcribe_audio_error():
    with patch('app.services.whisper.requests.post') as mock_post, \
         patch('builtins.open', create=True) as mock_open:
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = 'fail'
        mock_open.return_value.__enter__.return_value = MagicMock()
        with pytest.raises(Exception):
            whisper.transcribe_audio('file.mp3', language='id') 