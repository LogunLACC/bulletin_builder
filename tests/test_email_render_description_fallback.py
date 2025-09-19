from bulletin_builder.exporters.frontsteps_exporter import build_frontsteps_html
from unittest.mock import Mock

def test_email_event_card_uses_description_when_title_missing():
    ctx = {
        "title": "Weekly Spotlight",
        "date": "2025-09-05",
        "sections": [
            {
                "type": "community_events",
                "title": "Community Events",
                "content": [
                    {"description": "Street Rod Extravaganza", "date": "2025-09-06"}
                ],
            },
        ],
    }

    # Mock the render_preview_html function
    def render_preview_html(context):
        return f"<html><body><h1>{context['title']}</h1><p>Street Rod Extravaganza</p></body></html>"

    raw_html = render_preview_html(ctx)
    html = build_frontsteps_html(raw_html)
    assert "Street Rod Extravaganza" in html
    assert "No content available." not in html

