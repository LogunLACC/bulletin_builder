# Exception Handling Guide

## Overview

Bulletin Builder uses a hierarchy of custom exception classes to provide clear, specific error handling throughout the application. This replaces bare `except Exception` catches with typed exceptions that include contextual information.

## Exception Hierarchy

```
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
```

## Basic Usage

### Raising Exceptions

```python
from bulletin_builder.exceptions import DraftLoadError, PDFExportError

# Raise with message only
raise DraftLoadError("Failed to load draft file")

# Raise with context
raise DraftLoadError(
    "Failed to load draft file",
    file_path="/path/to/draft.json"
)

# Raise with multiple context values
raise PDFExportError(
    "PDF generation failed",
    output_path="/path/to/output.pdf"
)
```

### Catching Exceptions

```python
from bulletin_builder.exceptions import DraftLoadError, DraftSaveError, DraftError

# Catch specific exception
try:
    load_draft(path)
except DraftLoadError as e:
    logger.error(f"Load failed: {e}")
    show_error_dialog(str(e))

# Catch multiple related exceptions
try:
    save_draft(path)
except (DraftLoadError, DraftSaveError) as e:
    logger.error(f"Draft operation failed: {e}")
    show_error_dialog(str(e))

# Catch all draft-related errors
try:
    perform_draft_operation()
except DraftError as e:
    logger.error(f"Draft error: {e}")
    show_error_dialog(str(e))

# Catch all application errors
try:
    risky_operation()
except BulletinBuilderError as e:
    logger.error(f"Application error: {e}")
    show_error_dialog(str(e))
```

## Exception Classes

### Base Exception

**BulletinBuilderError** - Base class for all application exceptions

```python
from bulletin_builder.exceptions import BulletinBuilderError

raise BulletinBuilderError("Something went wrong")

# With context
raise BulletinBuilderError(
    "Something went wrong",
    context={'module': 'exporter', 'line': 42}
)
```

### Import Errors

**CSVImportError** - CSV file parsing failures

```python
from bulletin_builder.exceptions import CSVImportError

raise CSVImportError(
    "Invalid CSV format at line 5",
    file_path="announcements.csv",
    line_number=5
)
```

**JSONImportError** - JSON file parsing failures

```python
from bulletin_builder.exceptions import JSONImportError

raise JSONImportError(
    "Invalid JSON syntax: Missing closing brace",
    file_path="draft.json"
)
```

**EventsFeedError** - Events feed fetch/parse failures

```python
from bulletin_builder.exceptions import EventsFeedError

raise EventsFeedError(
    "Failed to fetch events feed",
    url="https://example.com/events.ics",
    status_code=404
)
```

**ImageImportError** - Image loading/processing failures

```python
from bulletin_builder.exceptions import ImageImportError

raise ImageImportError(
    "Image not found or invalid format",
    image_url="https://example.com/image.jpg"
)
```

### Export Errors

**HTMLExportError** - HTML export failures

```python
from bulletin_builder.exceptions import HTMLExportError

raise HTMLExportError(
    "Failed to write HTML file",
    output_path="output.html"
)
```

**PDFExportError** - PDF export failures

```python
from bulletin_builder.exceptions import PDFExportError

raise PDFExportError(
    "PDF generation failed: weasyprint error",
    output_path="bulletin.pdf"
)
```

**ValidationError** - Export validation failures

```python
from bulletin_builder.exceptions import ValidationError

issues = [
    {'type': 'error', 'message': 'Missing alt text'},
    {'type': 'warning', 'message': 'Link may be broken'}
]

raise ValidationError(
    "Validation failed with 2 issues",
    validation_issues=issues
)
```

**TemplateError** - Template loading failures

```python
from bulletin_builder.exceptions import TemplateError

raise TemplateError(
    "Template not found",
    template_name="custom.html"
)
```

### Draft Errors

**DraftLoadError** - Draft file loading failures

```python
from bulletin_builder.exceptions import DraftLoadError

raise DraftLoadError(
    "Cannot read draft file: File not found",
    file_path="user_drafts/bulletin.json"
)
```

**DraftSaveError** - Draft file saving failures

```python
from bulletin_builder.exceptions import DraftSaveError

raise DraftSaveError(
    "Permission denied: Cannot write to file",
    file_path="user_drafts/bulletin.json"
)
```

### Render Errors

**TemplateRenderError** - Template rendering failures

```python
from bulletin_builder.exceptions import TemplateRenderError

raise TemplateRenderError(
    "Template variable 'events' is undefined",
    template_name="main_layout.html",
    section_id="events"
)
```

### Configuration Errors

**MissingDependencyError** - Required dependency not installed

```python
from bulletin_builder.exceptions import MissingDependencyError

raise MissingDependencyError(
    "weasyprint is required for PDF export. Install with: pip install weasyprint",
    dependency_name="weasyprint"
)
```

**InvalidConfigError** - Configuration is invalid or missing

```python
from bulletin_builder.exceptions import InvalidConfigError

raise InvalidConfigError(
    "Google API key is required but not set",
    config_key="google_api_key"
)
```

## Best Practices

### 1. Use Specific Exceptions

❌ **Don't do this:**
```python
try:
    load_draft(path)
except Exception as e:
    print(f"Error: {e}")
```

✅ **Do this:**
```python
from bulletin_builder.exceptions import DraftLoadError, JSONImportError

try:
    load_draft(path)
except FileNotFoundError as e:
    raise DraftLoadError(f"Draft file not found", file_path=path)
except json.JSONDecodeError as e:
    raise JSONImportError(f"Invalid JSON: {e.msg}", file_path=path)
```

### 2. Include Context Information

❌ **Don't do this:**
```python
raise PDFExportError("Export failed")
```

✅ **Do this:**
```python
raise PDFExportError(
    "Failed to write PDF: Permission denied",
    output_path=output_path
)
```

### 3. Log Before Raising

```python
from bulletin_builder.app_core.logging_config import get_logger
from bulletin_builder.exceptions import DraftSaveError

logger = get_logger(__name__)

try:
    save_file(path, data)
except PermissionError as e:
    logger.error(f"Permission denied saving draft: {e}")
    raise DraftSaveError(
        f"Cannot write to {Path(path).name}: Permission denied",
        file_path=path
    )
```

### 4. Handle Exceptions at UI Boundaries

```python
from tkinter import messagebox
from bulletin_builder.exceptions import PDFExportError, MissingDependencyError

def export_pdf_handler():
    try:
        export_to_pdf(html, output_path)
    except MissingDependencyError as e:
        messagebox.showerror("Missing Dependency", str(e))
    except PDFExportError as e:
        messagebox.showerror("Export Failed", str(e))
    except Exception as e:
        logger.exception("Unexpected error during PDF export")
        messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")
```

### 5. Access Exception Context

```python
from bulletin_builder.exceptions import DraftLoadError

try:
    load_draft(path)
except DraftLoadError as e:
    print(f"Message: {e.message}")
    print(f"File path: {e.context.get('file_path')}")
    print(f"Full error: {str(e)}")  # Includes context in string
```

## Migration Examples

### Old Pattern (Bare Exception)

```python
def open_draft(path):
    try:
        data = json.loads(Path(path).read_text())
    except Exception:
        return  # Silent failure
```

### New Pattern (Specific Exceptions)

```python
from bulletin_builder.exceptions import DraftLoadError, JSONImportError
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)

def open_draft(path):
    try:
        logger.info(f"Opening draft from {path}")
        text = Path(path).read_text(encoding='utf-8')
        data = json.loads(text)
    except FileNotFoundError:
        logger.error(f"Draft file not found: {path}")
        raise DraftLoadError(
            f"Draft file not found: {Path(path).name}",
            file_path=path
        )
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in draft: {e}")
        raise JSONImportError(
            f"Invalid JSON format: {e.msg}",
            file_path=path
        )
```

## Testing Exceptions

```python
import pytest
from bulletin_builder.exceptions import DraftLoadError

def test_load_draft_file_not_found():
    """Test that DraftLoadError is raised for missing files."""
    with pytest.raises(DraftLoadError) as exc_info:
        load_draft("/nonexistent/path.json")
    
    assert "not found" in str(exc_info.value)
    assert exc_info.value.context['file_path'] == "/nonexistent/path.json"

def test_exception_context():
    """Test that exception context is accessible."""
    exc = DraftLoadError("Error message", file_path="/test/path.json")
    assert exc.context['file_path'] == "/test/path.json"
    assert "Error message" in str(exc)
    assert "/test/path.json" in str(exc)
```

## Error Messages

Good error messages are:
- **Specific**: Explain exactly what went wrong
- **Actionable**: Suggest how to fix the problem
- **Contextual**: Include relevant paths, values, or settings

✅ **Good error messages:**
- "Draft file not found: bulletin_2025.json"
- "PDF export failed: Permission denied when writing to C:\output\bulletin.pdf"
- "Invalid JSON syntax in draft file: Missing closing brace at line 42"

❌ **Bad error messages:**
- "Error"
- "Operation failed"
- "Something went wrong"

## Exception Testing

Run the exception tests with:

```bash
pytest tests/test_exceptions.py -v
```

All 28 tests should pass, covering:
- Exception hierarchy
- Context handling
- String representation
- Catch-all behavior
- Message attributes
