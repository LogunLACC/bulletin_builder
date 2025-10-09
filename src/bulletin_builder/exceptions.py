"""
Custom exception classes for Bulletin Builder.

This module defines a hierarchy of exceptions for different failure modes
in the application, replacing bare Exception catches with specific error types.

Exception Hierarchy:
    BulletinBuilderError (base)
    ├── ImportError (import/parsing failures)
    │   ├── CSVImportError
    │   ├── JSONImportError
    │   ├── EventsFeedError
    │   └── ImageImportError
    ├── ExportError (export/rendering failures)
    │   ├── HTMLExportError
    │   ├── PDFExportError
    │   ├── ValidationError
    │   └── TemplateError
    ├── DraftError (draft save/load failures)
    │   ├── DraftLoadError
    │   └── DraftSaveError
    ├── RenderError (preview/rendering failures)
    │   └── TemplateRenderError
    └── ConfigurationError (config/settings failures)
        ├── MissingDependencyError
        └── InvalidConfigError

Usage:
    from bulletin_builder.exceptions import DraftLoadError
    
    try:
        load_draft(path)
    except DraftLoadError as e:
        logger.error(f"Failed to load draft: {e}")
        show_error_dialog(str(e))
"""


class BulletinBuilderError(Exception):
    """
    Base exception for all Bulletin Builder errors.
    
    All custom exceptions in the application inherit from this class,
    making it easy to catch any application-specific error.
    
    Attributes:
        message: Human-readable error message
        context: Optional dictionary with additional error context
    """
    
    def __init__(self, message: str, context: dict = None):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            context: Optional dictionary with additional error context
                    (e.g., file path, line number, etc.)
        """
        self.message = message
        self.context = context or {}
        super().__init__(message)
    
    def __str__(self):
        """Return string representation including context if available."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} ({context_str})"
        return self.message


# ============================================================================
# Import/Parse Errors
# ============================================================================

class ImportError(BulletinBuilderError):
    """Base class for import and parsing errors."""
    pass


class CSVImportError(ImportError):
    """Raised when CSV file cannot be parsed or contains invalid data."""
    
    def __init__(self, message: str, file_path: str = None, line_number: int = None):
        context = {}
        if file_path:
            context['file_path'] = file_path
        if line_number:
            context['line_number'] = line_number
        super().__init__(message, context)


class JSONImportError(ImportError):
    """Raised when JSON file cannot be parsed or contains invalid data."""
    
    def __init__(self, message: str, file_path: str = None):
        context = {}
        if file_path:
            context['file_path'] = file_path
        super().__init__(message, context)


class EventsFeedError(ImportError):
    """Raised when events feed cannot be fetched or parsed."""
    
    def __init__(self, message: str, url: str = None, status_code: int = None):
        context = {}
        if url:
            context['url'] = url
        if status_code:
            context['status_code'] = status_code
        super().__init__(message, context)


class ImageImportError(ImportError):
    """Raised when image cannot be loaded or processed."""
    
    def __init__(self, message: str, image_url: str = None):
        context = {}
        if image_url:
            context['image_url'] = image_url
        super().__init__(message, context)


# ============================================================================
# Export Errors
# ============================================================================

class ExportError(BulletinBuilderError):
    """Base class for export and rendering errors."""
    pass


class HTMLExportError(ExportError):
    """Raised when HTML export fails."""
    
    def __init__(self, message: str, output_path: str = None):
        context = {}
        if output_path:
            context['output_path'] = output_path
        super().__init__(message, context)


class PDFExportError(ExportError):
    """Raised when PDF export fails."""
    
    def __init__(self, message: str, output_path: str = None):
        context = {}
        if output_path:
            context['output_path'] = output_path
        super().__init__(message, context)


class ValidationError(ExportError):
    """Raised when export validation fails."""
    
    def __init__(self, message: str, validation_issues: list = None):
        context = {}
        if validation_issues:
            context['issue_count'] = len(validation_issues)
        super().__init__(message, context)
        self.validation_issues = validation_issues or []


class TemplateError(ExportError):
    """Raised when template cannot be loaded or is invalid."""
    
    def __init__(self, message: str, template_name: str = None):
        context = {}
        if template_name:
            context['template_name'] = template_name
        super().__init__(message, context)


# ============================================================================
# Draft Errors
# ============================================================================

class DraftError(BulletinBuilderError):
    """Base class for draft save/load errors."""
    pass


class DraftLoadError(DraftError):
    """Raised when draft file cannot be loaded."""
    
    def __init__(self, message: str, file_path: str = None):
        context = {}
        if file_path:
            context['file_path'] = file_path
        super().__init__(message, context)


class DraftSaveError(DraftError):
    """Raised when draft file cannot be saved."""
    
    def __init__(self, message: str, file_path: str = None):
        context = {}
        if file_path:
            context['file_path'] = file_path
        super().__init__(message, context)


# ============================================================================
# Render Errors
# ============================================================================

class RenderError(BulletinBuilderError):
    """Base class for rendering errors."""
    pass


class TemplateRenderError(RenderError):
    """Raised when template rendering fails."""
    
    def __init__(self, message: str, template_name: str = None, section_id: str = None):
        context = {}
        if template_name:
            context['template_name'] = template_name
        if section_id:
            context['section_id'] = section_id
        super().__init__(message, context)


# ============================================================================
# Configuration Errors
# ============================================================================

class ConfigurationError(BulletinBuilderError):
    """Base class for configuration and setup errors."""
    pass


class MissingDependencyError(ConfigurationError):
    """Raised when a required dependency is missing."""
    
    def __init__(self, message: str, dependency_name: str = None):
        context = {}
        if dependency_name:
            context['dependency'] = dependency_name
        super().__init__(message, context)


class InvalidConfigError(ConfigurationError):
    """Raised when configuration is invalid or missing required values."""
    
    def __init__(self, message: str, config_key: str = None):
        context = {}
        if config_key:
            context['config_key'] = config_key
        super().__init__(message, context)
