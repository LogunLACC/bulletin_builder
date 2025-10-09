"""
Centralized logging configuration for Bulletin Builder.

This module provides a consistent logging setup across the application,
replacing the old BB_DEBUG environment variable pattern with proper
Python logging levels.

Usage:
    from bulletin_builder.app_core.logging_config import get_logger
    
    logger = get_logger(__name__)
    logger.debug("Detailed debugging information")
    logger.info("General informational message")
    logger.warning("Warning message")
    logger.error("Error message")
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Default logging level - can be overridden by BB_LOG_LEVEL environment variable
DEFAULT_LOG_LEVEL = logging.INFO

# Map string names to logging levels
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

# Global flag to track if logging has been configured
_logging_configured = False


def configure_logging(
    level: Optional[int] = None,
    log_file: Optional[Path] = None,
    console_output: bool = True
) -> None:
    """
    Configure the logging system for the application.
    
    This should be called once at application startup. Subsequent calls
    will be ignored unless force_reconfigure=True.
    
    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO).
               If None, reads from BB_LOG_LEVEL environment variable or uses DEFAULT_LOG_LEVEL.
        log_file: Optional path to write logs to a file.
        console_output: Whether to output logs to console (default: True).
    """
    global _logging_configured
    
    if _logging_configured:
        return
    
    # Determine logging level
    if level is None:
        env_level = os.getenv('BB_LOG_LEVEL', '').upper()
        level = LOG_LEVELS.get(env_level, DEFAULT_LOG_LEVEL)
    
    # Get root logger
    root_logger = logging.getLogger('bulletin_builder')
    root_logger.setLevel(level)
    
    # Remove any existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler if requested
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            # If we can't create the log file, just continue without it
            print(f"Warning: Could not create log file {log_file}: {e}", file=sys.stderr)
    
    _logging_configured = True
    
    # Log the configuration
    root_logger.info(f"Logging configured at level {logging.getLevelName(level)}")
    if log_file:
        root_logger.info(f"Logging to file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the specified module.
    
    This function ensures logging is configured before returning the logger.
    If configure_logging() hasn't been called yet, it will be called with
    default settings.
    
    Args:
        name: The name of the logger, typically __name__ from the calling module.
    
    Returns:
        A configured logger instance.
    
    Example:
        logger = get_logger(__name__)
        logger.info("Application started")
    """
    # Ensure logging is configured
    if not _logging_configured:
        configure_logging()
    
    # Return logger under the bulletin_builder namespace
    if name.startswith('bulletin_builder.'):
        logger_name = name
    else:
        logger_name = f'bulletin_builder.{name}'
    
    return logging.getLogger(logger_name)


def set_log_level(level: int) -> None:
    """
    Change the logging level at runtime.
    
    Args:
        level: The new logging level (e.g., logging.DEBUG).
    """
    root_logger = logging.getLogger('bulletin_builder')
    root_logger.setLevel(level)
    
    # Update all handlers
    for handler in root_logger.handlers:
        handler.setLevel(level)
    
    root_logger.info(f"Log level changed to {logging.getLevelName(level)}")


def is_debug_enabled() -> bool:
    """
    Check if DEBUG level logging is enabled.
    
    This is a convenience function for conditional debug operations
    that might be expensive to compute.
    
    Returns:
        True if DEBUG logging is enabled, False otherwise.
    
    Example:
        if is_debug_enabled():
            logger.debug(f"Complex data: {expensive_operation()}")
    """
    return logging.getLogger('bulletin_builder').isEnabledFor(logging.DEBUG)
