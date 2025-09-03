from bulletin_builder.app_core import exporter


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
    html = exporter.render_email_html(ctx)
    assert "Street Rod Extravaganza" in html
    assert "No content available." not in html

