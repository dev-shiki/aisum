import pytest
from unittest.mock import patch
from app.services import llama

def test_summarize_text_success():
    with patch('app.services.llama.requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'summary': 'ok'}
        result = llama.summarize_text('teks')
        assert 'summary' in result

def test_summarize_text_error():
    with patch('app.services.llama.requests.post') as mock_post:
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = 'fail'
        with pytest.raises(Exception):
            llama.summarize_text('teks') 