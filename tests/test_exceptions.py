"""
Tests for the custom exceptions module.
"""

import pytest
from bulletin_builder import exceptions


def test_exceptions_module_exists():
    """Verify the exceptions module can be imported."""
    assert hasattr(exceptions, 'BulletinBuilderError')
    assert hasattr(exceptions, 'ImportError')
    assert hasattr(exceptions, 'ExportError')
    assert hasattr(exceptions, 'DraftError')
    assert hasattr(exceptions, 'RenderError')
    assert hasattr(exceptions, 'ConfigurationError')


def test_base_exception():
    """Verify BulletinBuilderError base class."""
    exc = exceptions.BulletinBuilderError("Test error")
    assert str(exc) == "Test error"
    assert exc.message == "Test error"
    assert exc.context == {}
    assert isinstance(exc, Exception)


def test_base_exception_with_context():
    """Verify BulletinBuilderError includes context in string representation."""
    exc = exceptions.BulletinBuilderError(
        "Test error",
        context={'file': 'test.json', 'line': 42}
    )
    error_str = str(exc)
    assert "Test error" in error_str
    assert "file=test.json" in error_str
    assert "line=42" in error_str


# ============================================================================
# Import Error Tests
# ============================================================================

def test_import_error_hierarchy():
    """Verify ImportError inherits from BulletinBuilderError."""
    exc = exceptions.ImportError("Import failed")
    assert isinstance(exc, exceptions.BulletinBuilderError)
    assert isinstance(exc, Exception)


def test_csv_import_error():
    """Verify CSVImportError includes file path and line number."""
    exc = exceptions.CSVImportError(
        "Invalid CSV format",
        file_path="data.csv",
        line_number=5
    )
    assert str(exc) == "Invalid CSV format (file_path=data.csv, line_number=5)"
    assert exc.context['file_path'] == "data.csv"
    assert exc.context['line_number'] == 5
    assert isinstance(exc, exceptions.ImportError)


def test_csv_import_error_without_context():
    """Verify CSVImportError works without optional context."""
    exc = exceptions.CSVImportError("Invalid CSV format")
    assert str(exc) == "Invalid CSV format"
    assert exc.context == {}


def test_json_import_error():
    """Verify JSONImportError includes file path."""
    exc = exceptions.JSONImportError(
        "Invalid JSON syntax",
        file_path="draft.json"
    )
    assert "draft.json" in str(exc)
    assert exc.context['file_path'] == "draft.json"
    assert isinstance(exc, exceptions.ImportError)


def test_events_feed_error():
    """Verify EventsFeedError includes URL and status code."""
    exc = exceptions.EventsFeedError(
        "Feed unavailable",
        url="https://example.com/events",
        status_code=404
    )
    assert "Feed unavailable" in str(exc)
    assert exc.context['url'] == "https://example.com/events"
    assert exc.context['status_code'] == 404
    assert isinstance(exc, exceptions.ImportError)


def test_image_import_error():
    """Verify ImageImportError includes image URL."""
    exc = exceptions.ImageImportError(
        "Image not found",
        image_url="https://example.com/image.jpg"
    )
    assert "Image not found" in str(exc)
    assert exc.context['image_url'] == "https://example.com/image.jpg"
    assert isinstance(exc, exceptions.ImportError)


# ============================================================================
# Export Error Tests
# ============================================================================

def test_export_error_hierarchy():
    """Verify ExportError inherits from BulletinBuilderError."""
    exc = exceptions.ExportError("Export failed")
    assert isinstance(exc, exceptions.BulletinBuilderError)


def test_html_export_error():
    """Verify HTMLExportError includes output path."""
    exc = exceptions.HTMLExportError(
        "Failed to write HTML",
        output_path="output.html"
    )
    assert "Failed to write HTML" in str(exc)
    assert exc.context['output_path'] == "output.html"
    assert isinstance(exc, exceptions.ExportError)


def test_pdf_export_error():
    """Verify PDFExportError includes output path."""
    exc = exceptions.PDFExportError(
        "PDF generation failed",
        output_path="bulletin.pdf"
    )
    assert "PDF generation failed" in str(exc)
    assert exc.context['output_path'] == "bulletin.pdf"
    assert isinstance(exc, exceptions.ExportError)


def test_validation_error():
    """Verify ValidationError includes validation issues."""
    issues = [
        {'type': 'error', 'message': 'Missing alt text'},
        {'type': 'warning', 'message': 'Link may be broken'}
    ]
    exc = exceptions.ValidationError(
        "Validation failed",
        validation_issues=issues
    )
    assert "Validation failed" in str(exc)
    assert exc.validation_issues == issues
    assert exc.context['issue_count'] == 2
    assert isinstance(exc, exceptions.ExportError)


def test_validation_error_without_issues():
    """Verify ValidationError works without validation issues."""
    exc = exceptions.ValidationError("Validation failed")
    assert exc.validation_issues == []
    assert exc.context == {}


def test_template_error():
    """Verify TemplateError includes template name."""
    exc = exceptions.TemplateError(
        "Template not found",
        template_name="custom.html"
    )
    assert "Template not found" in str(exc)
    assert exc.context['template_name'] == "custom.html"
    assert isinstance(exc, exceptions.ExportError)


# ============================================================================
# Draft Error Tests
# ============================================================================

def test_draft_error_hierarchy():
    """Verify DraftError inherits from BulletinBuilderError."""
    exc = exceptions.DraftError("Draft operation failed")
    assert isinstance(exc, exceptions.BulletinBuilderError)


def test_draft_load_error():
    """Verify DraftLoadError includes file path."""
    exc = exceptions.DraftLoadError(
        "Cannot read draft file",
        file_path="user_drafts/bulletin.json"
    )
    assert "Cannot read draft file" in str(exc)
    assert exc.context['file_path'] == "user_drafts/bulletin.json"
    assert isinstance(exc, exceptions.DraftError)


def test_draft_save_error():
    """Verify DraftSaveError includes file path."""
    exc = exceptions.DraftSaveError(
        "Cannot write draft file",
        file_path="user_drafts/bulletin.json"
    )
    assert "Cannot write draft file" in str(exc)
    assert exc.context['file_path'] == "user_drafts/bulletin.json"
    assert isinstance(exc, exceptions.DraftError)


# ============================================================================
# Render Error Tests
# ============================================================================

def test_render_error_hierarchy():
    """Verify RenderError inherits from BulletinBuilderError."""
    exc = exceptions.RenderError("Render failed")
    assert isinstance(exc, exceptions.BulletinBuilderError)


def test_template_render_error():
    """Verify TemplateRenderError includes template and section info."""
    exc = exceptions.TemplateRenderError(
        "Template rendering failed",
        template_name="main_layout.html",
        section_id="events"
    )
    assert "Template rendering failed" in str(exc)
    assert exc.context['template_name'] == "main_layout.html"
    assert exc.context['section_id'] == "events"
    assert isinstance(exc, exceptions.RenderError)


def test_template_render_error_without_context():
    """Verify TemplateRenderError works without optional context."""
    exc = exceptions.TemplateRenderError("Template rendering failed")
    assert str(exc) == "Template rendering failed"
    assert exc.context == {}


# ============================================================================
# Configuration Error Tests
# ============================================================================

def test_configuration_error_hierarchy():
    """Verify ConfigurationError inherits from BulletinBuilderError."""
    exc = exceptions.ConfigurationError("Configuration invalid")
    assert isinstance(exc, exceptions.BulletinBuilderError)


def test_missing_dependency_error():
    """Verify MissingDependencyError includes dependency name."""
    exc = exceptions.MissingDependencyError(
        "Required package not installed",
        dependency_name="weasyprint"
    )
    assert "Required package not installed" in str(exc)
    assert exc.context['dependency'] == "weasyprint"
    assert isinstance(exc, exceptions.ConfigurationError)


def test_invalid_config_error():
    """Verify InvalidConfigError includes config key."""
    exc = exceptions.InvalidConfigError(
        "Missing required configuration",
        config_key="google_api_key"
    )
    assert "Missing required configuration" in str(exc)
    assert exc.context['config_key'] == "google_api_key"
    assert isinstance(exc, exceptions.ConfigurationError)


# ============================================================================
# Catch-All Tests
# ============================================================================

def test_catch_all_bulletin_builder_errors():
    """Verify all custom exceptions can be caught with base class."""
    exceptions_to_test = [
        exceptions.CSVImportError("CSV error"),
        exceptions.JSONImportError("JSON error"),
        exceptions.HTMLExportError("HTML error"),
        exceptions.DraftLoadError("Load error"),
        exceptions.TemplateRenderError("Render error"),
        exceptions.MissingDependencyError("Dependency error"),
    ]
    
    for exc in exceptions_to_test:
        try:
            raise exc
        except exceptions.BulletinBuilderError as e:
            assert isinstance(e, exceptions.BulletinBuilderError)
        else:
            pytest.fail(f"Exception {type(exc)} was not caught")


def test_exception_can_be_raised_and_caught():
    """Verify exceptions can be raised and caught normally."""
    with pytest.raises(exceptions.DraftLoadError) as exc_info:
        raise exceptions.DraftLoadError("Test error", file_path="test.json")
    
    assert "Test error" in str(exc_info.value)
    assert exc_info.value.context['file_path'] == "test.json"


def test_exception_context_is_dict():
    """Verify all exceptions have context as dict."""
    exc = exceptions.HTMLExportError("Error")
    assert isinstance(exc.context, dict)
    
    exc_with_context = exceptions.PDFExportError("Error", output_path="test.pdf")
    assert isinstance(exc_with_context.context, dict)
    assert len(exc_with_context.context) > 0


def test_exception_message_attribute():
    """Verify all exceptions have message attribute."""
    test_message = "This is a test error message"
    exceptions_to_test = [
        exceptions.BulletinBuilderError(test_message),
        exceptions.ImportError(test_message),
        exceptions.ExportError(test_message),
        exceptions.DraftError(test_message),
        exceptions.RenderError(test_message),
        exceptions.ConfigurationError(test_message),
    ]
    
    for exc in exceptions_to_test:
        assert exc.message == test_message
        assert test_message in str(exc)
