import pytest
from unittest.mock import patch, MagicMock
from app.services import gemini

def test_detect_content_type_meeting():
    assert gemini.detect_content_type('rapat penting') == 'meeting'

def test_detect_content_type_document():
    assert gemini.detect_content_type('ini dokumen') == 'document'

def test_detect_content_type_default():
    assert gemini.detect_content_type('random text') == 'meeting'

@patch('app.services.gemini.requests.post')
def test_summarize_with_gemini_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'candidates': [{'content': {'parts': [{'text': 'summary'}]}}]}
    result = gemini.summarize_with_gemini('teks', content_type='meeting')
    assert 'summary' in result['summary'].lower()

@patch('app.services.gemini.requests.post')
def test_summarize_with_gemini_error(mock_post):
    mock_post.return_value.status_code = 500
    mock_post.return_value.text = 'error'
    with pytest.raises(Exception):
        gemini.summarize_with_gemini('teks', content_type='meeting')

@patch('app.services.gemini.requests.post')
def test_summarize_with_gemini_exception(mock_post):
    mock_post.side_effect = Exception('fail')
    with pytest.raises(Exception):
        gemini.summarize_with_gemini('teks', content_type='meeting') 