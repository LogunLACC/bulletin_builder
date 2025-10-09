# Logging System Guide

## Overview

Bulletin Builder uses Python's standard `logging` module for centralized logging configuration. This replaces the old `BB_DEBUG` environment variable pattern with a proper, configurable logging system.

## Basic Usage

### Getting a Logger

In any module, import and create a logger instance:

```python
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)
```

### Logging Messages

Use the appropriate level for your messages:

```python
logger.debug("Detailed debugging information - only shown when DEBUG level enabled")
logger.info("General informational message - shown by default")
logger.warning("Warning message - something unexpected but not an error")
logger.error("Error message - operation failed")
logger.critical("Critical message - application may not be able to continue")
```

### Example

```python
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)

def load_draft(file_path):
    logger.info(f"Loading draft from {file_path}")
    try:
        # ... load logic ...
        logger.debug(f"Draft loaded successfully: {draft_data}")
        return draft_data
    except FileNotFoundError:
        logger.error(f"Draft file not found: {file_path}")
        raise
    except Exception as e:
        logger.exception(f"Failed to load draft: {e}")
        raise
```

## Configuration

### Environment Variable

Set the `BB_LOG_LEVEL` environment variable to control logging verbosity:

```powershell
# Windows PowerShell
$env:BB_LOG_LEVEL = "DEBUG"
bulletin --gui

# Windows Command Prompt
set BB_LOG_LEVEL=DEBUG
bulletin --gui
```

Valid values:
- `DEBUG` - Show all messages (most verbose)
- `INFO` - Show info, warning, error, and critical (default)
- `WARNING` - Show warning, error, and critical
- `ERROR` - Show error and critical only
- `CRITICAL` - Show only critical messages

### Programmatic Configuration

The logging system is automatically configured when the application starts. You can also configure it manually:

```python
from bulletin_builder.app_core.logging_config import configure_logging
import logging

# Configure at application startup
configure_logging(
    level=logging.DEBUG,  # Set level
    log_file=Path("app.log"),  # Optional: write to file
    console_output=True  # Show in console
)
```

### Changing Level at Runtime

```python
from bulletin_builder.app_core.logging_config import set_log_level
import logging

# Enable debug logging at runtime
set_log_level(logging.DEBUG)

# Return to INFO level
set_log_level(logging.INFO)
```

## Best Practices

### 1. Use Appropriate Log Levels

- **DEBUG**: Detailed diagnostic information for troubleshooting
  ```python
  logger.debug(f"Processing section {section_id} with {len(items)} items")
  ```

- **INFO**: Confirmation that things are working as expected
  ```python
  logger.info("Draft saved successfully")
  ```

- **WARNING**: Something unexpected happened, but the application can continue
  ```python
  logger.warning(f"Image URL appears invalid: {url}")
  ```

- **ERROR**: A serious problem - a function/operation failed
  ```python
  logger.error(f"Failed to export HTML: {error}")
  ```

- **CRITICAL**: Very serious error - application may not be able to continue
  ```python
  logger.critical("Database connection lost and cannot be restored")
  ```

### 2. Use Logging Instead of Print

❌ **Don't do this:**
```python
print(f"[DEBUG] Loading {filename}")
if DEBUG:
    print(f"Data: {data}")
```

✅ **Do this:**
```python
logger.info(f"Loading {filename}")
logger.debug(f"Data: {data}")
```

### 3. Log Exceptions Properly

Use `logger.exception()` in except blocks to automatically include traceback:

```python
try:
    result = risky_operation()
except Exception as e:
    logger.exception("Operation failed")  # Includes full traceback
    raise
```

### 4. Conditional Debug Operations

For expensive debug operations, check if debug is enabled first:

```python
from bulletin_builder.app_core.logging_config import is_debug_enabled

if is_debug_enabled():
    expensive_data = generate_detailed_debug_info()
    logger.debug(f"Debug info: {expensive_data}")
```

### 5. Use String Formatting Properly

Prefer lazy formatting (faster when message won't be logged):

✅ **Good:**
```python
logger.debug("Processing %s items from %s", count, source)
```

❌ **Avoid:**
```python
logger.debug(f"Processing {count} items from {source}")
```

The first version only formats the string if DEBUG level is enabled.

## Migration from BB_DEBUG

### Old Pattern

```python
import os
DEBUG = bool(int(os.getenv('BB_DEBUG', '0') or '0'))

if DEBUG:
    print(f"[DEBUG] Section selected: {section_id}")
```

### New Pattern

```python
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)

logger.debug(f"Section selected: {section_id}")
```

### Benefits

1. **Configurable levels** - Not just on/off, but DEBUG/INFO/WARNING/ERROR/CRITICAL
2. **Consistent formatting** - Timestamps, module names, levels automatically included
3. **Multiple outputs** - Can log to console, file, or both
4. **Runtime control** - Change logging level without restarting
5. **Standard practice** - Uses Python's standard logging module

## Output Format

Default format includes:
```
2025-10-09 14:30:45 [INFO] bulletin_builder.exporter: Export completed successfully
2025-10-09 14:30:46 [DEBUG] bulletin_builder.sections: Loading section data for 'events'
2025-10-09 14:30:47 [ERROR] bulletin_builder.importer: Failed to parse JSON: Invalid syntax
```

Format: `timestamp [LEVEL] logger_name: message`

## Troubleshooting

### Not seeing debug messages?

Check that DEBUG level is enabled:
```python
from bulletin_builder.app_core.logging_config import is_debug_enabled
print(f"Debug enabled: {is_debug_enabled()}")
```

Set the level:
```python
from bulletin_builder.app_core.logging_config import set_log_level
import logging
set_log_level(logging.DEBUG)
```

### Too much output?

Increase the logging level:
```python
set_log_level(logging.WARNING)  # Only warnings and errors
```

Or use environment variable:
```powershell
$env:BB_LOG_LEVEL = "WARNING"
```

## Testing

The logging system is fully tested. Run tests with:
```bash
pytest tests/test_logging_config.py -v
```

All 13 logging configuration tests should pass.
