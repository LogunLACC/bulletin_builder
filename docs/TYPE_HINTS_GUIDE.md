# Type Hints Guide

## Overview

This guide documents the type hinting strategy for Bulletin Builder and provides patterns for adding type hints to the codebase.

## Why Type Hints?

1. **IDE Support**: Better auto complete, inline documentation, and error detection
2. **Code Clarity**: Makes function signatures and return types explicit
3. **Early Error Detection**: Catch type-related bugs before runtime
4. **Documentation**: Serves as inline documentation for function behavior

## Python Version

The project uses **Python 3.9+**, which supports:
- Modern type hint syntax (`list[str]`, `dict[str, Any]`)
- `Optional[T]` for nullable types
- `Union[T1, T2]` for multiple possible types
- `Any` for dynamic types

## Import Pattern

```python
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
```

For Python 3.10+, you can use builtin types:
```python
# Instead of typing.List[str]
list[str]

# Instead of typing.Dict[str, int]
dict[str, int]
```

## Type Hinting Patterns

### 1. Function Signatures

**Basic function:**
```python
def get_section_title(section_id: str) -> str:
    """Get the title of a section."""
    return f"Section {section_id}"
```

**Multiple parameters:**
```python
def create_section(title: str, content: str, section_type: str = "custom_text") -> Dict[str, Any]:
    """Create a new section dictionary."""
    return {
        'title': title,
        'content': content,
        'type': section_type
    }
```

**Optional parameters:**
```python
from typing import Optional

def load_draft(path: str, validate: bool = True) -> Optional[Dict[str, Any]]:
    """
    Load a draft from file.
    
    Returns:
        Draft data dictionary, or None if file not found
    """
    if not Path(path).exists():
        return None
    return json.loads(Path(path).read_text())
```

**No return value:**
```python
def save_config(settings: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_path.write_text(json.dumps(settings))
```

### 2. Collections

**Lists:**
```python
def get_section_ids() -> list[str]:
    """Get list of all section IDs."""
    return ["intro", "events", "announcements"]

def filter_sections(sections: list[Dict[str, Any]], section_type: str) -> list[Dict[str, Any]]:
    """Filter sections by type."""
    return [s for s in sections if s.get('type') == section_type]
```

**Dictionaries:**
```python
def get_settings() -> dict[str, Any]:
    """Get current settings as dictionary."""
    return {
        'title': 'LACC Bulletin',
        'date': '2025-10-09',
        'theme': 'default'
    }

def update_metadata(data: dict[str, str], key: str, value: str) -> None:
    """Update metadata dictionary in place."""
    data[key] = value
```

**Tuples:**
```python
def validate_html(html: str) -> tuple[bool, str]:
    """
    Validate HTML content.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not html:
        return False, "HTML content is empty"
    return True, ""

# Fixed-length tuple
def get_rgb_color() -> tuple[int, int, int]:
    """Get RGB color values."""
    return (255, 0, 0)
```

### 3. Union Types

**Multiple possible types:**
```python
from typing import Union

def parse_value(value: Union[str, int, float]) -> str:
    """Convert value to string."""
    return str(value)

# Python 3.10+ syntax
def process_data(data: str | dict[str, Any]) -> None:
    """Process data from string or dict."""
    if isinstance(data, str):
        data = json.loads(data)
    # ... process dict
```

### 4. Callable Types

**Function parameters:**
```python
from typing import Callable

def apply_transformation(
    content: str, 
    transform: Callable[[str], str]
) -> str:
    """Apply a transformation function to content."""
    return transform(content)

# With specific signature
def register_callback(
    callback: Callable[[str, int], None]
) -> None:
    """Register a callback function."""
    # callback takes str and int, returns None
    pass
```

### 5. Any Type

Use `Any` when the type is truly dynamic:

```python
from typing import Any

def init(app: Any) -> None:
    """
    Initialize module with app instance.
    
    Args:
        app: Application instance (CustomTk or mock for testing)
    """
    app.some_method = lambda: None
```

**Note:** `Any` disables type checking, so use sparingly and only when necessary.

### 6. Custom Types

**Type aliases:**
```python
from typing import TypeAlias

# Define type alias
SectionData: TypeAlias = dict[str, Any]
Settings: TypeAlias = dict[str, str | int | bool]

def create_section(title: str) -> SectionData:
    """Create a section data dictionary."""
    return {'title': title, 'content': ''}

def load_settings() -> Settings:
    """Load application settings."""
    return {'theme': 'dark', 'font_size': 14, 'auto_save': True}
```

### 7. Generic Types

**For reusable functions:**
```python
from typing import TypeVar, Generic

T = TypeVar('T')

def first_or_default(items: list[T], default: T) -> T:
    """Get first item from list or return default."""
    return items[0] if items else default

# Usage maintains type
result: str = first_or_default(['a', 'b'], 'default')
result2: int = first_or_default([1, 2, 3], 0)
```

## Module-Specific Patterns

### Init Functions

All `init(app)` functions follow this pattern:

```python
def init(app: Any) -> None:
    """
    Initialize [module name] functions.
    
    Attaches [list of functions] to the app instance.
    
    Args:
        app: The main application instance
    """
    # ... implementation
```

### Event Handlers

GUI event handlers don't return values:

```python
def on_button_clicked() -> None:
    """Handle button click event."""
    # ... implementation

def on_section_selected(section_id: str) -> None:
    """Handle section selection."""
    # ... implementation
```

### Validation Functions

Validation functions return results:

```python
from bulletin_builder.app_core.export_validator import ValidationResult

def validate_accessibility(html: str) -> ValidationResult:
    """
    Validate HTML for WCAG accessibility compliance.
    
    Args:
        html: HTML content to validate
        
    Returns:
        ValidationResult with issues found
    """
    # ... implementation
```

### Export Functions

Export functions can raise exceptions:

```python
from bulletin_builder.exceptions import PDFExportError

def export_to_pdf(
    html_content: str, 
    output_path: str,
    client_style: str = "desktop"
) -> tuple[bool, str]:
    """
    Export bulletin HTML content to PDF.
    
    Args:
        html_content: The HTML content to convert
        output_path: Path where PDF should be saved
        client_style: Email client style ("desktop", "gmail", etc.)
    
    Returns:
        Tuple of (success, message)
        
    Raises:
        PDFExportError: If PDF generation fails
        MissingDependencyError: If weasyprint is not installed
    """
    # ... implementation
```

## Progress Status

### Completed Modules

- ✅ `exceptions.py` - Full type hints with custom exceptions
- ✅ `logging_config.py` - Complete type coverage
- ✅ `drafts.py` - Init, new_draft, open_draft, save_draft
- ✅ `pdf_exporter.py` - Export functions with proper types
- ⏳ `export_validator.py` - Partial (needs validation functions)
- ⏳ `exporter.py` - Partial (needs handler functions)
- ⏳ `importer.py` - Needs type hints
- ⏳ `sections.py` - Needs type hints
- ⏳ `preview.py` - Needs type hints
- ⏳ `ui_setup.py` - Needs type hints

### Priority Order

1. **Core modules** (high impact, frequently used):
   - `export_validator.py` - Validation functions
   - `importer.py` - Import and parsing functions
   - `exporter.py` - Export handlers

2. **UI modules** (moderate impact):
   - `sections.py` - Section management
   - `ui_setup.py` - UI construction

3. **Supporting modules** (lower priority):
   - `preview.py` - Preview functions
   - `core_init.py` - Initialization
   - `loader.py` - Module loading

## Type Checking Tools

### mypy

Run type checking with mypy:

```bash
# Install mypy
pip install mypy

# Check a single file
mypy src/bulletin_builder/app_core/drafts.py

# Check entire package
mypy src/bulletin_builder/

# With specific configuration
mypy --ignore-missing-imports --no-strict-optional src/bulletin_builder/
```

### pyright

Alternative type checker (used by VS Code):

```bash
# Install pyright
pip install pyright

# Check files
pyright src/bulletin_builder/
```

## Configuration

### pyproject.toml

Add mypy configuration:

```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Set to true when most code is typed
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "customtkinter.*"
ignore_missing_imports = true
```

## Best Practices

### DO:

✅ Add type hints to all public functions
✅ Use `Optional[T]` for nullable values
✅ Document expected types in docstrings
✅ Use `Any` only when absolutely necessary
✅ Add return type hints, even for `None`
✅ Use type aliases for complex nested types

### DON'T:

❌ Don't use bare `dict` or `list` without parameters
❌ Don't ignore type errors without understanding them
❌ Don't add incorrect type hints just to satisfy mypy
❌ Don't use `Any` everywhere to avoid type checking
❌ Don't forget to import types from `typing`

## Examples from Codebase

### Good Type Hints

```python
# drafts.py
def init(app: Any) -> None:
    """Initialize draft management functions."""
    
def save_draft(save_as: bool = False) -> None:
    """Save draft with optional save-as dialog."""

# exceptions.py
class DraftLoadError(DraftError):
    def __init__(self, message: str, file_path: str = None):
        context = {}
        if file_path:
            context['file_path'] = file_path
        super().__init__(message, context)

# logging_config.py
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified module."""
    
def configure_logging(
    level: Optional[int] = None,
    log_file: Optional[Path] = None,
    console_output: bool = True
) -> None:
    """Configure the logging system."""
```

## Testing Type Hints

Type hints don't affect runtime behavior, but you can test them:

```python
# Test that function signatures are correct
from typing import get_type_hints

def test_function_signatures():
    from bulletin_builder.app_core.drafts import init
    
    hints = get_type_hints(init)
    assert 'app' in hints
    assert hints['return'] == type(None)
```

## Migration Strategy

1. **Start with new code**: All new functions should have type hints
2. **Add to existing code incrementally**: Focus on public APIs first
3. **Test as you go**: Run mypy after adding hints to each module
4. **Document patterns**: Update this guide with project-specific patterns
5. **Don't break tests**: Ensure tests still pass after adding type hints

## References

- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 585 - Type Hinting Generics In Standard Collections](https://peps.python.org/pep-0585/)
- [typing module documentation](https://docs.python.org/3/library/typing.html)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Real Python: Type Checking](https://realpython.com/python-type-checking/)
