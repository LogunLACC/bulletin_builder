from bulletin_builder.postprocess import ensure_postprocessed
import pytest
from bulletin_builder.app_core import exporter

def test_render_bulletin_html_basic():
    ctx = {
        "title": "Test Bulletin",
        "date": "2025-08-20",
        "sections": [
            {"type": "custom_text", "title": "Intro", "content": {"text": "Hello world!"}},
            {"type": "announcements", "title": "News", "content": [
                {"title": "A1", "body": "Body1"},
                {"title": "A2", "body": "Body2"}
            ]}
        ]
    }
    html = exporter.render_bulletin_html(ctx)
    assert "Test Bulletin" in html
    assert "Hello world!" in html
    assert "A1" in html and "A2" in html

def test_render_email_html_basic():
    ctx = {
        "title": "Test Email",
        "date": "2025-08-20",
        "sections": [
            {"type": "custom_text", "title": "Intro", "content": {"text": "Hello email!"}},
            {"type": "announcements", "title": "News", "content": [
                {"title": "E1", "body": "BodyE1"},
                {"title": "E2", "body": "BodyE2"}
            ]}
        ]
    }
    html = exporter.render_email_html(ctx)
    assert "Test Email" in html
    assert "Hello email!" in html
    assert "E1" in html and "E2" in html
