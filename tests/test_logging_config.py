"""
Tests for the centralized logging configuration system.
"""

import logging
import os
import sys
from pathlib import Path
from io import StringIO
import pytest


def test_logging_config_module_exists():
    """Verify the logging_config module can be imported."""
    from bulletin_builder.app_core import logging_config
    assert hasattr(logging_config, 'configure_logging')
    assert hasattr(logging_config, 'get_logger')
    assert hasattr(logging_config, 'set_log_level')
    assert hasattr(logging_config, 'is_debug_enabled')


def test_get_logger_returns_logger():
    """Verify get_logger returns a Logger instance."""
    from bulletin_builder.app_core.logging_config import get_logger
    
    logger = get_logger('test_module')
    assert isinstance(logger, logging.Logger)
    assert 'bulletin_builder' in logger.name


def test_get_logger_with_bulletin_builder_prefix():
    """Verify get_logger handles names already prefixed with bulletin_builder."""
    from bulletin_builder.app_core.logging_config import get_logger
    
    logger = get_logger('bulletin_builder.test_module')
    assert logger.name == 'bulletin_builder.test_module'


def test_configure_logging_sets_level():
    """Verify configure_logging sets the logging level correctly."""
    from bulletin_builder.app_core.logging_config import configure_logging, get_logger
    
    # Reset configuration state for testing
    import bulletin_builder.app_core.logging_config as lc
    lc._logging_configured = False
    
    configure_logging(level=logging.WARNING, console_output=False)
    logger = get_logger('test_module')
    
    # Logger should be set to WARNING level
    assert logger.getEffectiveLevel() == logging.WARNING


def test_configure_logging_from_environment(monkeypatch):
    """Verify logging level can be set via BB_LOG_LEVEL environment variable."""
    from bulletin_builder.app_core.logging_config import configure_logging, get_logger
    
    # Reset configuration state
    import bulletin_builder.app_core.logging_config as lc
    lc._logging_configured = False
    
    monkeypatch.setenv('BB_LOG_LEVEL', 'DEBUG')
    configure_logging(console_output=False)
    
    logger = get_logger('test_module')
    assert logger.getEffectiveLevel() == logging.DEBUG


def test_set_log_level_changes_level():
    """Verify set_log_level can change the logging level at runtime."""
    from bulletin_builder.app_core.logging_config import (
        configure_logging, get_logger, set_log_level
    )
    
    # Reset and configure
    import bulletin_builder.app_core.logging_config as lc
    lc._logging_configured = False
    configure_logging(level=logging.INFO, console_output=False)
    
    logger = get_logger('test_module')
    assert logger.getEffectiveLevel() == logging.INFO
    
    # Change level
    set_log_level(logging.DEBUG)
    assert logger.getEffectiveLevel() == logging.DEBUG


def test_is_debug_enabled():
    """Verify is_debug_enabled correctly reports DEBUG status."""
    from bulletin_builder.app_core.logging_config import (
        configure_logging, is_debug_enabled, set_log_level
    )
    
    # Reset and configure
    import bulletin_builder.app_core.logging_config as lc
    lc._logging_configured = False
    configure_logging(level=logging.INFO, console_output=False)
    
    assert not is_debug_enabled()
    
    set_log_level(logging.DEBUG)
    assert is_debug_enabled()


def test_logger_output_format():
    """Verify logger output includes expected format elements."""
    from bulletin_builder.app_core.logging_config import configure_logging, get_logger
    
    # Reset configuration
    import bulletin_builder.app_core.logging_config as lc
    lc._logging_configured = False
    
    # Capture log output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    configure_logging(level=logging.INFO, console_output=False)
    logger = get_logger('test_format')
    logger.addHandler(handler)
    
    logger.info("Test message")
    
    output = stream.getvalue()
    assert '[INFO]' in output
    assert 'bulletin_builder.test_format' in output
    assert 'Test message' in output


def test_multiple_loggers_share_config():
    """Verify multiple loggers share the same configuration."""
    from bulletin_builder.app_core.logging_config import configure_logging, get_logger
    
    # Reset configuration
    import bulletin_builder.app_core.logging_config as lc
    lc._logging_configured = False
    configure_logging(level=logging.WARNING, console_output=False)
    
    logger1 = get_logger('module1')
    logger2 = get_logger('module2')
    
    # Both should have same effective level
    assert logger1.getEffectiveLevel() == logging.WARNING
    assert logger2.getEffectiveLevel() == logging.WARNING


def test_log_levels_mapping():
    """Verify LOG_LEVELS dictionary contains expected mappings."""
    from bulletin_builder.app_core.logging_config import LOG_LEVELS
    
    assert LOG_LEVELS['DEBUG'] == logging.DEBUG
    assert LOG_LEVELS['INFO'] == logging.INFO
    assert LOG_LEVELS['WARNING'] == logging.WARNING
    assert LOG_LEVELS['ERROR'] == logging.ERROR
    assert LOG_LEVELS['CRITICAL'] == logging.CRITICAL


def test_configure_logging_idempotent():
    """Verify configure_logging can only be called once (unless reset)."""
    from bulletin_builder.app_core.logging_config import configure_logging
    
    # Reset configuration
    import bulletin_builder.app_core.logging_config as lc
    lc._logging_configured = False
    
    configure_logging(level=logging.INFO, console_output=False)
    
    # Second call should be ignored
    configure_logging(level=logging.DEBUG, console_output=False)
    
    # Should still be INFO level from first call
    from bulletin_builder.app_core.logging_config import get_logger
    logger = get_logger('test_idempotent')
    assert logger.getEffectiveLevel() == logging.INFO


def test_logger_can_log_at_all_levels():
    """Verify logger supports all standard logging levels."""
    from bulletin_builder.app_core.logging_config import configure_logging, get_logger
    
    # Reset configuration
    import bulletin_builder.app_core.logging_config as lc
    lc._logging_configured = False
    configure_logging(level=logging.DEBUG, console_output=False)
    
    logger = get_logger('test_levels')
    
    # All these should work without errors
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")


def test_default_log_level():
    """Verify default logging level is INFO when not specified."""
    from bulletin_builder.app_core.logging_config import (
        configure_logging, get_logger, DEFAULT_LOG_LEVEL
    )
    
    # Reset configuration
    import bulletin_builder.app_core.logging_config as lc
    lc._logging_configured = False
    
    assert DEFAULT_LOG_LEVEL == logging.INFO
    
    configure_logging(console_output=False)
    logger = get_logger('test_default')
    assert logger.getEffectiveLevel() == logging.INFO
