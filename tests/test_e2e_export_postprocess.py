from bulletin_builder.app_core import exporter
from scripts.bulletin_email_postprocess import process_html


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

    raw_html = exporter.render_email_html(ctx)
    fixed = process_html(raw_html)

    # Basic assertions
    assert '<!DOCTYPE' not in fixed.upper()
    assert '<head' not in fixed.lower()

    # Reset present on anchors and images
    assert 'style="margin:0;padding:0' in fixed

    # Table collapse / td border none
    assert 'border-collapse' in fixed or 'border-spacing' in fixed
    assert 'border:none' in fixed