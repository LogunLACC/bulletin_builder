from src.bulletin_builder.app_core.sanitize import sanitize_email_html


def test_a_img_margin_padding_zero():
    """Test that a and img tags have margin:0;padding:0 enforced."""
    html_with_bad_styles = """
    <table>
    <tr>
    <td>
    <a href="#" style="margin:10px;padding:5px;">Link</a>
    <img src="test.jpg" style="margin:20px;padding:15px;" alt="test">
    </td>
    </tr>
    </table>
    """

    sanitized = sanitize_email_html(html_with_bad_styles)

    # Check that a tags have margin:0;padding:0 as first rules
    assert 'style="margin:0; padding:0;"' in sanitized

    # Check that img tags have margin:0;padding:0 as first rules
    assert 'style="margin:0; padding:0;"' in sanitized


def test_table_border_collapse():
    """Test that table tags have border-collapse:collapse enforced."""
    html_with_bad_table = """
    <table style="border-collapse:separate;border:1px solid black;">
    <tr><td>Cell</td></tr>
    </table>
    """

    sanitized = sanitize_email_html(html_with_bad_table)

    # Check that table has border-collapse:collapse
    assert 'border-collapse:collapse' in sanitized


def test_td_border_none():
    """Test that td tags have border:none enforced."""
    html_with_bad_td = """
    <table>
    <tr><td style="border:1px solid black;">Cell</td></tr>
    </table>
    """

    sanitized = sanitize_email_html(html_with_bad_td)

    # Check that td has border:none as first rule
    assert 'style="border:none;"' in sanitized


def test_unwanted_tags_stripped():
    """Test that unwanted tags are stripped."""
    html_with_unwanted_tags = """
    <div>
    <!DOCTYPE html>
    <head><title>Test</title></head>
    <link rel="stylesheet" href="bad.css">
    <script>alert('bad');</script>
    <style>body{background:red;}</style>
    <p>Good content</p>
    </div>
    """

    sanitized = sanitize_email_html(html_with_unwanted_tags)

    # Check that unwanted tags are removed
    assert '<!DOCTYPE' not in sanitized
    assert '<head>' not in sanitized
    assert '<link' not in sanitized
    assert '<script>' not in sanitized
    assert '<style>' not in sanitized

    # Check that good content remains
    assert 'Good content' in sanitized


def test_event_handlers_stripped():
    """Test that event handlers are stripped."""
    html_with_events = """
    <div>
    <img src="test.jpg" onerror="alert('bad')" onload="doSomething()">
    <a href="#" onclick="clickHandler()">Link</a>
    <p>Good content</p>
    </div>
    """

    sanitized = sanitize_email_html(html_with_events)

    # Check that event handlers are removed
    assert 'onerror=' not in sanitized
    assert 'onload=' not in sanitized
    assert 'onclick=' not in sanitized

    # Check that good attributes remain
    assert 'src="test.jpg"' in sanitized
    assert 'href="#"' in sanitized


def test_complex_html_rules():
    """Test all rules work together on complex HTML."""
    complex_html = """
    <table style="border-collapse:separate;">
    <tr>
    <td style="border:2px solid red;">
    <a href="#" style="margin:10px;padding:5px;">Link</a>
    <img src="test.jpg" style="margin:20px;padding:15px;" alt="test">
    <script>bad();</script>
    </td>
    </tr>
    </table>
    """

    sanitized = sanitize_email_html(complex_html)

    # Check table border-collapse
    assert 'border-collapse:collapse' in sanitized

    # Check td border:none
    assert 'style="border:none;"' in sanitized

    # Check a and img margin/padding
    assert 'style="margin:0; padding:0;"' in sanitized

    # Check unwanted tags removed
    assert '<script>' not in sanitized


def test_malformed_tags_prevention():
    """Test that malformed tags are never produced."""
    html_input = '<a href="#">Link</a><img src="test.jpg" alt="test"><table><tr><td>Cell</td></tr></table>'

    sanitized = sanitize_email_html(html_input)

    # Should not contain malformed tags like <astyle=, <imgstyle=, <tdstyle=
    assert '<astyle=' not in sanitized
    assert '<imgstyle=' not in sanitized
    assert '<tdstyle=' not in sanitized
    assert '<tablestyle=' not in sanitized

    # Should contain properly formatted tags
    assert 'style="margin:0; padding:0;"' in sanitized
    assert 'style="border-collapse:collapse;"' in sanitized
    assert 'style="border:none;"' in sanitized


def test_style_ordering():
    """Test that enforced rules come first in style attributes."""
    html_input = '<a href="#" style="color:red; margin:10px;">Link</a>'

    sanitized = sanitize_email_html(html_input)

    # margin:0; padding:0; should come first
    style_start = sanitized.find('style="')
    style_content = sanitized[style_start:sanitized.find('"', style_start + 7)]

    assert style_content.startswith('style="margin:0; padding:0;')


def test_idempotent_behavior():
    """Test that sanitizer is idempotent."""
    html_input = '<a href="#" style="margin:10px; padding:5px; color:red;">Link</a>'

    first_pass = sanitize_email_html(html_input)
    second_pass = sanitize_email_html(first_pass)

    assert first_pass == second_pass
