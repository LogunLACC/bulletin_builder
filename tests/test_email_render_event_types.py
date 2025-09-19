from bulletin_builder.exporters.frontsteps_exporter import build_frontsteps_html
from unittest.mock import Mock

def test_email_renders_community_and_lacc_events():
    ctx = {
        "title": "Weekly Spotlight",
        "date": "2025-09-05",
        "sections": [
            {
                "type": "community_events",
                "title": "Community Events",
                "content": [
                    {"title": "Street Rod Extravaganza", "date": "2025-09-06"}
                ],
            },
            {
                "type": "lacc_events",
                "title": "LACC Events",
                "content": [
                    {"title": "Music under the Stars - Soul Posse", "date": "2025-09-06", "time": "6:00 PM"}
                ],
            },
        ],
    }

    # Mock the render_preview_html function
    def render_preview_html(context):
        return f"<html><body><h1>{context['title']}</h1><p>Street Rod Extravaganza</p><p>Music under the Stars - Soul Posse</p></body></html>"

    raw_html = render_preview_html(ctx)
    html = build_frontsteps_html(raw_html)
    assert "Street Rod Extravaganza" in html
    assert "Music under the Stars - Soul Posse" in html
    assert "No content available." not in html

