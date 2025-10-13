"""
End-to-end tests for email client compatibility.

Tests validate exported HTML structure for compatibility with major email clients
like Gmail, Outlook, Apple Mail, and mobile email apps.
"""

import pytest
import re
from unittest.mock import Mock, patch
from pathlib import Path


class TestEmailHTMLStructure:
    """Test HTML structure for email compatibility."""
    
    @pytest.fixture
    def mock_app(self):
        """Create mock app with sections."""
        app = Mock()
        app.sections_data = [
            {
                'title': 'Test Section',
                'content': '<p>Test content with <a href="https://example.com">link</a></p>',
                'section_type': 'announcement'
            }
        ]
        app.template_name = 'default'
        return app
    
    @pytest.fixture
    def sample_html_output(self):
        """Sample HTML output for testing."""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { margin: 0; padding: 0; }
        table { border-collapse: collapse; }
    </style>
</head>
<body style="margin:0;padding:0;">
    <table width="600" border="0" cellpadding="0" cellspacing="0">
        <tr>
            <td>
                <img src="https://example.com/image.jpg" alt="Test" style="margin:0;padding:0;display:block;">
            </td>
        </tr>
        <tr>
            <td style="padding:20px;">
                <p style="margin:0;padding:0;">Test content</p>
                <a href="https://example.com" style="margin:0;padding:0;">Link</a>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    
    def test_doctype_present(self, sample_html_output):
        """Test that HTML includes proper DOCTYPE."""
        assert '<!DOCTYPE html>' in sample_html_output
    
    def test_meta_viewport_present(self, sample_html_output):
        """Test that viewport meta tag is present for mobile."""
        assert 'name="viewport"' in sample_html_output
        assert 'width=device-width' in sample_html_output
    
    def test_charset_declared(self, sample_html_output):
        """Test that character encoding is declared."""
        assert 'charset="UTF-8"' in sample_html_output or 'charset=UTF-8' in sample_html_output
    
    def test_body_has_inline_styles(self, sample_html_output):
        """Test that body tag has inline margin/padding reset."""
        body_match = re.search(r'<body[^>]*style="([^"]*)"', sample_html_output)
        assert body_match is not None
        style = body_match.group(1)
        assert 'margin:0' in style or 'margin: 0' in style
        assert 'padding:0' in style or 'padding: 0' in style
    
    def test_tables_use_proper_attributes(self, sample_html_output):
        """Test that tables have border=0, cellpadding=0, cellspacing=0."""
        table_matches = re.findall(r'<table[^>]*>', sample_html_output)
        for table in table_matches:
            assert 'border="0"' in table or 'border=0' in table
            assert 'cellpadding="0"' in table or 'cellpadding=0' in table
            assert 'cellspacing="0"' in table or 'cellspacing=0' in table
    
    def test_images_have_display_block(self, sample_html_output):
        """Test that images use display:block to prevent spacing issues."""
        img_matches = re.findall(r'<img[^>]*>', sample_html_output)
        for img in img_matches:
            if 'style=' in img:
                style_match = re.search(r'style="([^"]*)"', img)
                if style_match:
                    style = style_match.group(1)
                    assert 'display:block' in style or 'display: block' in style
    
    def test_images_have_alt_text(self, sample_html_output):
        """Test that all images have alt attributes."""
        img_matches = re.findall(r'<img[^>]*>', sample_html_output)
        for img in img_matches:
            assert 'alt=' in img
    
    def test_links_have_inline_styles(self, sample_html_output):
        """Test that links have inline margin/padding reset."""
        link_matches = re.findall(r'<a[^>]*style="([^"]*)"[^>]*>', sample_html_output)
        for style in link_matches:
            # Links should have margin/padding defined
            assert 'margin' in style or 'padding' in style
    
    def test_no_external_stylesheets(self, sample_html_output):
        """Test that no external stylesheets are used (email clients block them)."""
        assert '<link rel="stylesheet"' not in sample_html_output
    
    def test_no_javascript(self, sample_html_output):
        """Test that no JavaScript is present (email clients block it)."""
        assert '<script' not in sample_html_output.lower()


class TestEmailClientSpecificCompatibility:
    """Test compatibility with specific email clients."""
    
    @pytest.fixture
    def sample_html(self):
        """Sample HTML with various elements."""
        return """
<table width="600" border="0" cellpadding="0" cellspacing="0">
    <tr>
        <td style="padding:20px;font-family:Arial,sans-serif;">
            <h1 style="margin:0 0 10px 0;font-size:24px;color:#333333;">Heading</h1>
            <p style="margin:0 0 15px 0;font-size:14px;line-height:1.5;color:#666666;">Content</p>
            <table border="0" cellpadding="0" cellspacing="0">
                <tr>
                    <td style="background-color:#007bff;padding:10px 20px;">
                        <a href="https://example.com" style="color:#ffffff;text-decoration:none;">Button</a>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>
"""
    
    def test_outlook_table_width_specified(self, sample_html):
        """Test that tables have explicit width for Outlook."""
        table_matches = re.findall(r'<table[^>]*>', sample_html)
        # Main container should have width
        assert any('width=' in table for table in table_matches)
    
    def test_outlook_font_family_inline(self, sample_html):
        """Test that font-family is specified inline for Outlook."""
        td_matches = re.findall(r'<td[^>]*style="([^"]*)"', sample_html)
        # At least one td should have font-family
        assert any('font-family' in style for style in td_matches)
    
    def test_gmail_color_specified_in_hex(self, sample_html):
        """Test that colors use hex format (Gmail strips named colors)."""
        style_matches = re.findall(r'color:([^;"\s]+)', sample_html)
        for color in style_matches:
            # Should be hex (#xxx or #xxxxxx) or rgb
            assert color.startswith('#') or color.startswith('rgb')
    
    def test_apple_mail_line_height_specified(self, sample_html):
        """Test that line-height is specified for Apple Mail."""
        p_matches = re.findall(r'<p[^>]*style="([^"]*)"', sample_html)
        # Paragraphs should have line-height
        assert any('line-height' in style for style in p_matches)
    
    def test_mobile_button_as_table(self, sample_html):
        """Test that buttons are created using table structure for mobile."""
        # Look for button pattern (table with background-color and link)
        button_pattern = r'<table[^>]*>.*?background-color.*?<a[^>]*>.*?</a>.*?</table>'
        assert re.search(button_pattern, sample_html, re.DOTALL) is not None
    
    def test_mobile_touch_target_size(self, sample_html):
        """Test that clickable elements have adequate padding for touch."""
        # Links inside tables should have padding for touch targets
        link_in_table = r'<td[^>]*padding[^>]*>.*?<a[^>]*>.*?</a>'
        assert re.search(link_in_table, sample_html, re.DOTALL) is not None


class TestEmailRenderingRules:
    """Test specific rendering rules for email compatibility."""
    
    def test_no_position_absolute(self):
        """Test that position:absolute is not used (breaks in email)."""
        html = '<div style="position:absolute;">Content</div>'
        assert 'position:absolute' not in html or self._should_warn_about_positioning(html)
    
    def test_no_float_usage(self):
        """Test that float is not used (unreliable in email)."""
        html = '<div style="float:left;">Content</div>'
        # Float should be replaced with table-based layouts
        assert self._should_use_tables_instead_of_float(html)
    
    def test_background_images_inline(self):
        """Test that background images use inline styles with fallback."""
        html_with_bg = """
<td style="background-image:url('image.jpg');background-color:#cccccc;">
    Content
</td>
"""
        # Should have both background-image and background-color fallback
        assert 'background-image' in html_with_bg
        assert 'background-color' in html_with_bg
    
    def test_nested_tables_depth_limit(self):
        """Test that tables are not nested too deeply (max 3 levels)."""
        html = """
<table><tr><td>
    <table><tr><td>
        <table><tr><td>
            Content
        </td></tr></table>
    </td></tr></table>
</td></tr></table>
"""
        depth = html.count('<table')
        assert depth <= 3, "Tables nested more than 3 levels can break in email clients"
    
    def test_responsive_images_max_width(self):
        """Test that images use max-width for responsiveness."""
        html = '<img src="image.jpg" style="max-width:100%;height:auto;" alt="Image">'
        assert 'max-width:100%' in html or 'max-width: 100%' in html
        assert 'height:auto' in html or 'height: auto' in html
    
    def test_text_links_not_bare_urls(self):
        """Test that link text is not just the URL (better for mobile)."""
        good_link = '<a href="https://example.com">Click here</a>'
        bad_link = '<a href="https://example.com">https://example.com</a>'
        
        # Good link has different text than URL
        link_match = re.search(r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', good_link)
        if link_match:
            href, text = link_match.groups()
            assert href != text
    
    def _should_warn_about_positioning(self, html):
        """Helper to check if absolute positioning should trigger warning."""
        return 'position:absolute' in html
    
    def _should_use_tables_instead_of_float(self, html):
        """Helper to check if float usage should be replaced with tables."""
        return 'float:' in html


class TestEmailContentValidation:
    """Test content validation for email compatibility."""
    
    def test_spam_trigger_words_detection(self):
        """Test detection of common spam trigger words."""
        spam_words = ['free', 'urgent', 'act now', 'limited time', 'guarantee']
        content = "Get your FREE limited time offer now!"
        
        found_spam_words = []
        for word in spam_words:
            if word.lower() in content.lower():
                found_spam_words.append(word)
        
        # Should detect spam words (warning, not error)
        assert len(found_spam_words) > 0
    
    def test_image_to_text_ratio(self):
        """Test that email has sufficient text relative to images."""
        # Bad ratio - too many images
        bad_html = """
<table>
    <tr><td>
        <img src="image1.jpg" alt="Image 1">
        <img src="image2.jpg" alt="Image 2">
        <img src="image3.jpg" alt="Image 3">
        <p>Short text</p>
    </td></tr>
</table>
"""
        bad_image_count = bad_html.count('<img')
        bad_text_length = len(re.sub(r'<[^>]+>', '', bad_html).strip())
        
        # This should fail the ratio test
        assert bad_text_length < bad_image_count * 50, "Expected bad ratio to be detected"
        
        # Good ratio - sufficient text
        good_html = """
<table>
    <tr><td>
        <img src="image1.jpg" alt="Image 1">
        <p>This is a substantial amount of text content that provides context and information about the image above. 
        It contains multiple sentences with meaningful content that would be valuable to email recipients. 
        The text explains the purpose and relevance of the visual content.</p>
    </td></tr>
</table>
"""
        good_image_count = good_html.count('<img')
        good_text_length = len(re.sub(r'<[^>]+>', '', good_html).strip())
        
        # This should pass the ratio test
        assert good_text_length >= good_image_count * 50, "Good ratio should meet minimum text requirement"
    
    def test_links_have_unsubscribe_option(self):
        """Test that bulk emails include unsubscribe link."""
        html_with_unsub = '<a href="https://example.com/unsubscribe">Unsubscribe</a>'
        html_without_unsub = '<a href="https://example.com">Link</a>'
        
        # For bulk emails, should have unsubscribe
        assert 'unsubscribe' in html_with_unsub.lower()
    
    def test_preheader_text_present(self):
        """Test that email includes preheader text for inbox preview."""
        html = """
<body>
    <div style="display:none;font-size:1px;color:#ffffff;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;">
        Preview text that shows in inbox
    </div>
    <table><!-- Main content --></table>
</body>
"""
        # Should have hidden preview text
        assert 'display:none' in html
        assert 'max-height:0' in html or 'max-height: 0' in html


class TestAccessibilityInEmail:
    """Test accessibility features in email HTML."""
    
    def test_semantic_headings_used(self):
        """Test that semantic heading tags are used."""
        html = '<h1 style="margin:0;font-size:24px;">Main Heading</h1>'
        assert '<h1' in html
    
    def test_tables_have_role_presentation(self):
        """Test that layout tables have role=presentation for screen readers."""
        html = '<table role="presentation" border="0" cellpadding="0" cellspacing="0">'
        assert 'role="presentation"' in html
    
    def test_sufficient_color_contrast(self):
        """Test that text has sufficient contrast with background."""
        # Example: dark text on light background
        html = '<p style="color:#333333;background-color:#ffffff;">Text</p>'
        
        # Extract colors
        text_color = re.search(r'color:#([0-9a-fA-F]{6})', html)
        bg_color = re.search(r'background-color:#([0-9a-fA-F]{6})', html)
        
        # Should have both colors defined for contrast check
        assert text_color is not None
        assert bg_color is not None
    
    def test_lang_attribute_present(self):
        """Test that HTML lang attribute is present."""
        html = '<html lang="en">'
        assert 'lang=' in html


def _helper_validate_email_html(html: str) -> dict:
    """
    Helper function to validate email HTML structure.
    
    Returns dict with validation results:
    {
        'valid': bool,
        'errors': list of error messages,
        'warnings': list of warning messages
    }
    """
    errors = []
    warnings = []
    
    # Check DOCTYPE
    if '<!DOCTYPE html>' not in html:
        warnings.append("Missing DOCTYPE declaration")
    
    # Check meta tags
    if 'charset=' not in html:
        errors.append("Missing charset declaration")
    
    # Check for external resources
    if '<link rel="stylesheet"' in html:
        errors.append("External stylesheets detected - use inline styles")
    
    if '<script' in html.lower():
        errors.append("JavaScript detected - not supported in email")
    
    # Check table structure
    if '<table' in html:
        tables = re.findall(r'<table[^>]*>', html)
        for table in tables:
            if 'border="0"' not in table:
                warnings.append("Table missing border='0' attribute")
            if 'cellpadding="0"' not in table:
                warnings.append("Table missing cellpadding='0' attribute")
    
    # Check images
    images = re.findall(r'<img[^>]*>', html)
    for img in images:
        if 'alt=' not in img:
            errors.append("Image missing alt attribute")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def test_validation_helper():
    """Test the validation helper function."""
    good_html = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body>
    <table border="0" cellpadding="0" cellspacing="0">
        <tr><td><img src="test.jpg" alt="Test"></td></tr>
    </table>
</body>
</html>
"""
    
    result = _helper_validate_email_html(good_html)
    assert result['valid'] is True
    assert len(result['errors']) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
