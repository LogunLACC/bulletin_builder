"""Test integration of sanitizer with the exporter module."""

import os
import tempfile
from unittest.mock import patch, MagicMock
from bulletin_builder.app_core.sanitize import sanitize_email_html


def test_exporter_calls_sanitizer():
    """Test that the exporter calls the sanitizer on HTML output."""
    from bulletin_builder.app_core.exporter import render_email_html, render_bulletin_html

    # Test data
    ctx = {
        "title": "Test Bulletin",
        "date": "Test Date",
        "sections": [
            {
                "type": "custom_text",
                "title": "Test Section",
                "content": {"text": "Test content"}
            }
        ]
    }

    # Test render_email_html calls sanitizer
    html = render_email_html(ctx)
    # The sanitizer should have been called internally, so check that HTML is properly formatted
    assert 'margin:0; padding:0;' in html or 'border:none;' in html

    # Test render_bulletin_html calls sanitizer
    html = render_bulletin_html(ctx)
    # The sanitizer should have been called internally, so check that HTML is properly formatted
    assert 'margin:0; padding:0;' in html or 'border:none;' in html


def test_sanitizer_integration_preserves_structure():
    """Test that sanitizer integration preserves the overall HTML structure."""
    # Sample HTML that should be sanitized
    raw_html = '''
    <!DOCTYPE html>
    <html>
    <head><link rel="stylesheet" href="style.css"></head>
    <body>
        <div class="container">
            <a href="#" style="color:blue;">Test Link</a>
            <table style="width:100%;">
                <tr><td style="background:yellow;">Cell Content</td></tr>
            </table>
        </div>
    </body>
    </html>
    '''

    # Apply sanitization
    sanitized = sanitize_email_html(raw_html)

    # Check that structural elements are preserved
    assert '<div class="container">' in sanitized, "Container div was removed"
    assert 'Test Link' in sanitized, "Link text was removed"
    assert 'Cell Content' in sanitized, "Table cell content was removed"

    # Check that unwanted elements are removed
    assert '<!DOCTYPE' not in sanitized, "DOCTYPE not removed"
    assert '<head>' not in sanitized, "Head tag not removed"
    assert '<link' not in sanitized, "Link tag not removed"


def test_sanitizer_integration_with_fixtures():
    """Test sanitizer integration using the gold fixtures."""
    for fixture_num in [1, 2, 3]:
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'correct', f'{fixture_num}.html')
        with open(fixture_path, 'r', encoding='utf-8') as f:
            original_html = f.read()

        # Apply sanitization (should be idempotent)
        sanitized = sanitize_email_html(original_html)

        # Apply sanitization again - should be identical (idempotent)
        sanitized_again = sanitize_email_html(sanitized)

        # The sanitizer should produce consistent output
        assert sanitized == sanitized_again, f"Sanitizer is not idempotent on fixture {fixture_num}"


def test_sanitizer_handles_edge_cases():
    """Test sanitizer handles edge cases in integration."""
    # Test with empty HTML
    assert sanitize_email_html("") == ""

    # Test with HTML that has no tags to modify
    simple_html = "<html><body><p>Simple text</p></body></html>"
    sanitized = sanitize_email_html(simple_html)
    assert sanitized == simple_html

    # Test with malformed HTML (should not crash)
    malformed_html = "<html><body><p>Unclosed paragraph"
    sanitized = sanitize_email_html(malformed_html)
    # Should still produce valid output
    assert "<p>Unclosed paragraph" in sanitized


def test_sanitizer_integration_performance():
    """Test that sanitizer performs adequately on typical bulletin sizes."""
    # Create a larger HTML document
    large_html = "<html><body>" + "<p>Paragraph</p>" * 1000 + "</body></html>"

    import time
    start_time = time.time()
    sanitized = sanitize_email_html(large_html)
    end_time = time.time()

    # Should complete in reasonable time (less than 1 second for 1000 paragraphs)
    assert end_time - start_time < 1.0, f"Sanitization took too long: {end_time - start_time} seconds"

    # Should still produce valid output
    assert len(sanitized) > 0
    assert "<p>Paragraph</p>" in sanitized
