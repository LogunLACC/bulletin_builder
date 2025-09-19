from bulletin_builder.exporters.frontsteps_exporter import build_frontsteps_html
from unittest.mock import Mock

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
    # Mock the render_preview_html function
    def render_preview_html(context):
        return f"<html><body><h1>{context['title']}</h1><p>Hello world!</p><p>A1</p><p>A2</p></body></html>"

    raw_html = render_preview_html(ctx)
    html = build_frontsteps_html(raw_html)
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
    # Mock the render_preview_html function
    def render_preview_html(context):
        return f"<html><body><h1>{context['title']}</h1><p>Hello email!</p><p>E1</p><p>E2</p></body></html>"

    raw_html = render_preview_html(ctx)
    html = build_frontsteps_html(raw_html)
    assert "Test Email" in html
    assert "Hello email!" in html
    assert "E1" in html and "E2" in html
