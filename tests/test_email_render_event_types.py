from bulletin_builder.app_core import exporter


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
    html = exporter.render_email_html(ctx)
    assert "Street Rod Extravaganza" in html
    assert "Music under the Stars" in html
    assert "No content available." not in html

