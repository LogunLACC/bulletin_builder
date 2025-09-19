from bulletin_builder.exporters.frontsteps_exporter import build_frontsteps_html
from unittest.mock import Mock

def test_export_then_postprocess_smoke():
    # Build a minimal context with an announcements section containing an image and a link
    ctx = {
        "title": "Test Bulletin",
        "date": "August 29, 2025",
        "sections": [
            {
                "type": "announcements",
                "title": "Announcements",
                "content": [
                    {"title": "One", "body": "Hello world", "link": "https://example.com"}
                ],
            }
        ],
    }

    # Mock the render_preview_html function
    def render_preview_html(context):
        return f"<html><body><h1>{context['title']}</h1></body></html>"

    raw_html = render_preview_html(ctx)
    fixed = build_frontsteps_html(raw_html)

    # Basic assertions
    assert '<!DOCTYPE' not in fixed.upper()
    assert '<head' not in fixed.lower()
    assert '<body>' not in fixed.lower()