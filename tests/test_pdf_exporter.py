"""
Tests for PDF exporter module.
"""

import pytest
import tempfile
import os
from bulletin_builder.app_core.pdf_exporter import (
    export_to_pdf,
    _prepare_html_for_pdf,
    _get_print_css,
    init
)


class TestPDFExporter:
    """Test PDF export functionality."""
    
    def test_prepare_html_for_pdf_wraps_fragment(self):
        """Test that HTML fragments are wrapped in proper structure."""
        html = '<p>Test content</p>'
        result = _prepare_html_for_pdf(html, "desktop")
        
        assert '<!DOCTYPE html>' in result
        assert '<html' in result
        assert '<body>' in result
        assert '<p>Test content</p>' in result
    
    def test_prepare_html_for_pdf_preserves_full_document(self):
        """Test that full HTML documents are preserved."""
        html = '<!DOCTYPE html><html><body><p>Test</p></body></html>'
        result = _prepare_html_for_pdf(html, "desktop")
        
        # Should not double-wrap
        assert result.count('<!DOCTYPE html>') == 1
        assert result.count('<html') == 1
    
    def test_get_print_css_returns_valid_css(self):
        """Test that print CSS is returned."""
        css = _get_print_css()
        
        assert '@page' in css
        assert 'body' in css
        assert 'font-family' in css
        assert 'page-break' in css
    
    def test_export_to_pdf_creates_file(self):
        """Test that PDF export creates an output file."""
        try:
            from weasyprint import HTML
            weasyprint_available = True
        except ImportError:
            weasyprint_available = False
        
        if not weasyprint_available:
            pytest.skip("weasyprint not installed")
        
        html = '<h1>Test Bulletin</h1><p>This is a test.</p>'
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            success, message = export_to_pdf(html, output_path)
            
            assert success is True
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            assert 'success' in message.lower()
        finally:
            try:
                os.unlink(output_path)
            except:
                pass
    
    def test_export_to_pdf_handles_errors(self):
        """Test error handling in PDF export."""
        try:
            from weasyprint import HTML
            weasyprint_available = True
        except ImportError:
            weasyprint_available = False
        
        if not weasyprint_available:
            pytest.skip("weasyprint not installed")
        
        # Try to export to invalid path
        html = '<p>Test</p>'
        invalid_path = '/invalid/path/that/does/not/exist/test.pdf'
        
        success, message = export_to_pdf(html, invalid_path)
        
        assert success is False
        assert 'failed' in message.lower()
    
    def test_init_attaches_function(self):
        """Test that init attaches export_to_pdf to app."""
        class MockApp:
            pass
        
        app = MockApp()
        init(app)
        
        assert hasattr(app, 'export_to_pdf')
        assert callable(app.export_to_pdf)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
