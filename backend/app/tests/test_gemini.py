import pytest
from unittest.mock import patch, MagicMock
from app.services import gemini
import os
from datetime import datetime

def test_detect_content_type_all_branches():
    assert gemini.detect_content_type('rapat meeting') == 'meeting'
    assert gemini.detect_content_type('dokumen penelitian') == 'document'
    assert gemini.detect_content_type('slide presentasi') == 'presentation'
    assert gemini.detect_content_type('wawancara interview') == 'interview'
    assert gemini.detect_content_type('kuliah tutorial') == 'lecture'
    assert gemini.detect_content_type('youtube channel') == 'youtube'
    assert gemini.detect_content_type('random text') == 'general'

def test_create_summary_prompts():
    text = 'isi'
    assert 'Ringkasan dokumen' in gemini.create_document_summary_prompt(text)
    assert 'Ringkasan presentasi' in gemini.create_presentation_summary_prompt(text)
    assert 'Ringkasan materi' in gemini.create_lecture_summary_prompt(text)
    assert 'Ringkasan video YouTube' in gemini.create_youtube_summary_prompt(text)
    assert 'Ringkasan meeting' in gemini.create_meeting_summary_prompt(text)
    assert 'Ringkasan wawancara' in gemini.create_interview_summary_prompt(text)
    assert 'Ringkasan umum' in gemini.create_general_summary_prompt(text)

def test_create_content_specific_prompt():
    text = 'rapat meeting'
    assert 'Ringkasan meeting' in gemini.create_content_specific_prompt(text, 'meeting')
    assert 'Ringkasan dokumen' in gemini.create_content_specific_prompt(text, 'document')
    assert 'Ringkasan presentasi' in gemini.create_content_specific_prompt(text, 'presentation')
    assert 'Ringkasan wawancara' in gemini.create_content_specific_prompt(text, 'interview')
    assert 'Ringkasan materi' in gemini.create_content_specific_prompt(text, 'lecture')
    assert 'Ringkasan video YouTube' in gemini.create_content_specific_prompt(text, 'youtube')
    assert 'Ringkasan umum' in gemini.create_content_specific_prompt(text, 'general')

def test_format_content_specific_output_all_branches():
    parsed = {"format": "text", "content": "isi"}
    assert gemini.format_content_specific_output(parsed, "isi", "meeting").startswith('=')
    for ct in ["meeting", "document", "presentation", "interview", "lecture", "youtube", "general"]:
        parsed = {"executive_summary": "isi"}
        # Tambah field sesuai branch
        if ct == "meeting":
            parsed["meeting_info"] = {"title": "t", "date": "d", "duration": "dur", "participants": ["a"]}
            parsed["agenda"] = ["ag"]
            parsed["key_points"] = [{"topic": "t", "summary": "s", "decisions": ["d"], "notes": "n"}]
            parsed["action_items"] = [{"task": "t", "assignee": "a", "deadline": "d", "priority": "p"}]
            parsed["risk_issues"] = ["r"]
            parsed["success_metrics"] = ["m"]
            parsed["next_meeting"] = {"scheduled": "Ya", "date": "d", "agenda": "ag"}
        elif ct == "document":
            parsed["document_info"] = {"title": "t", "type": "t", "author": "a", "date": "d"}
            parsed["objectives"] = ["o"]
            parsed["methodology"] = {"approach": "a", "data_sources": ["d"], "tools": ["t"]}
            parsed["key_findings"] = [{"finding": "f", "description": "d", "significance": "s"}]
            parsed["conclusions"] = ["c"]
            parsed["recommendations"] = [{"recommendation": "r", "priority": "p", "implementation": "i"}]
        elif ct == "presentation":
            parsed["presentation_info"] = {"title": "t", "presenter": "p", "audience": "a", "duration": "d"}
            parsed["overview"] = "o"
            parsed["objectives"] = ["o"]
            parsed["key_sections"] = [{"section": "s", "content": "c", "key_points": ["k"], "data": ["d"]}]
            parsed["main_arguments"] = ["a"]
        elif ct == "interview":
            parsed["interview_info"] = {"topic": "t", "interviewee": "i", "interviewer": "r", "date": "d"}
            parsed["background"] = "b"
            parsed["key_questions"] = [{"question": "q", "answer": "a", "insights": ["i"]}]
            parsed["main_themes"] = ["t"]
            parsed["experiences"] = ["e"]
            parsed["recommendations"] = ["r"]
            parsed["key_learnings"] = ["l"]
        elif ct == "lecture":
            parsed["lecture_info"] = {"title": "t", "instructor": "i", "subject": "s", "level": "l"}
            parsed["learning_objectives"] = ["o"]
            parsed["main_concepts"] = [{"concept": "c", "explanation": "e", "examples": ["ex"], "importance": "i"}]
            parsed["key_theories"] = ["t"]
            parsed["important_points"] = ["p"]
            parsed["tips_and_tricks"] = ["t"]
            parsed["summary"] = "s"
        elif ct == "youtube":
            parsed["video_info"] = {"title": "t", "creator": "c", "category": "cat", "duration": "d"}
            parsed["executive_summary"] = "e"
            parsed["main_topics"] = ["t"]
            parsed["key_points"] = [{"point": "p", "description": "d", "timestamp": "t", "importance": "i"}]
            parsed["credits"] = ["c"]
        elif ct == "general":
            parsed["executive_summary"] = "e"
            parsed["key_points"] = ["k"]
            parsed["important_info"] = ["i"]
            parsed["conclusions"] = ["c"]
        out = gemini.format_content_specific_output(parsed, "isi", ct)
        assert isinstance(out, str)

def test_parse_gemini_response():
    d = {"a": 1}
    s = '{"a": 1}'
    assert gemini.parse_gemini_response(s) == d
    assert gemini.parse_gemini_response('not json') == {"format": "text", "content": 'not json'}

def test_create_summary_metadata():
    text = "ini text"
    summary = "ini summary"
    meta = gemini.create_summary_metadata(text, summary, "meeting")
    assert meta["content_type"] == "meeting"
    assert meta["original_length"] == len(text)
    assert meta["summary_length"] == len(summary)
    assert "generated_at" in meta

@patch('app.services.gemini.requests.post')
def test_summarize_with_gemini_all_branches(mock_post, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "def")
    monkeypatch.setenv("GEMINI_API_URL", "http://fake")
    # Sukses JSON
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"candidates": [{"content": {"parts": [{"text": '{"executive_summary": "ok"}'}}]}]}
    result = gemini.summarize_with_gemini('teks', content_type='meeting')
    assert isinstance(result, dict)
    # Sukses fallback string
    mock_post.return_value.json.return_value = {"candidates": [{"content": {"parts": [{"text": 'plain text'}]}}]}
    result = gemini.summarize_with_gemini('teks', content_type='meeting')
    assert isinstance(result, str)
    # JSONDecodeError fallback
    with patch('app.services.gemini.json.loads', side_effect=Exception('fail')):
        mock_post.return_value.json.return_value = {"candidates": [{"content": {"parts": [{"text": 'plain text'}]}}]}
        result = gemini.summarize_with_gemini('teks', content_type='meeting')
        assert isinstance(result, str)
    # API error
    mock_post.side_effect = Exception('fail')
    with pytest.raises(Exception):
        gemini.summarize_with_gemini('teks', content_type='meeting') 