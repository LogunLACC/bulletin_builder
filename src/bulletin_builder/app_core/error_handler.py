"""
Error handling utilities for categorizing errors and generating suggestions.

This module provides intelligent error analysis to:
- Categorize errors automatically
- Generate actionable suggestions
- Format error details for logging and display
"""

import traceback
import re
from pathlib import Path
from typing import Optional, List, Tuple
from bulletin_builder.ui.error_dialog import ErrorCategory, ErrorSeverity
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)


class ErrorAnalyzer:
    """Analyzes exceptions and provides actionable suggestions."""
    
    @staticmethod
    def analyze_exception(
        exception: Exception,
        context: Optional[str] = None
    ) -> Tuple[ErrorCategory, ErrorSeverity, List[str]]:
        """
        Analyze an exception and return category, severity, and suggestions.
        
        Args:
            exception: The exception to analyze
            context: Optional context about what was being attempted
            
        Returns:
            Tuple of (category, severity, suggestions list)
        """
        error_str = str(exception).lower()
        error_type = type(exception).__name__
        
        # File I/O errors
        if isinstance(exception, FileNotFoundError):
            return (
                ErrorCategory.FILE_IO,
                ErrorSeverity.ERROR,
                [
                    "Check that the file path is correct",
                    "Ensure the file hasn't been moved or deleted",
                    f"Verify you have permission to access the directory",
                    "Try using 'File → Open Draft...' to browse for the file"
                ]
            )
        
        if isinstance(exception, PermissionError):
            return (
                ErrorCategory.PERMISSION,
                ErrorSeverity.ERROR,
                [
                    "Close any programs that might be using this file",
                    "Check file permissions and ensure you have write access",
                    "Try running the application as administrator",
                    "Save to a different location (like your Documents folder)"
                ]
            )
        
        if isinstance(exception, OSError) and "read-only" in error_str:
            return (
                ErrorCategory.PERMISSION,
                ErrorSeverity.ERROR,
                [
                    "The file or folder is marked as read-only",
                    "Right-click the file and uncheck 'Read-only' in Properties",
                    "Try saving to a different location"
                ]
            )
        
        # JSON/Import errors
        if "json" in error_type.lower() or "json" in error_str:
            return (
                ErrorCategory.IMPORT,
                ErrorSeverity.ERROR,
                [
                    "The file contains invalid JSON format",
                    "Open the file in a text editor to check for syntax errors",
                    "Look for missing commas, brackets, or quotes",
                    "Try importing a different file or creating a new draft"
                ]
            )
        
        if "csv" in error_str or "pandas" in error_str:
            return (
                ErrorCategory.IMPORT,
                ErrorSeverity.ERROR,
                [
                    "Check that the CSV file is properly formatted",
                    "Ensure the file has the expected columns",
                    "Try opening the CSV in Excel to verify the structure",
                    "Make sure the file encoding is UTF-8"
                ]
            )
        
        # Network errors
        if any(keyword in error_str for keyword in ["connection", "timeout", "network", "unreachable"]):
            return (
                ErrorCategory.NETWORK,
                ErrorSeverity.WARNING,
                [
                    "Check your internet connection",
                    "The server might be temporarily unavailable - try again later",
                    "Verify the URL is correct in Settings",
                    "Check if a firewall is blocking the connection"
                ]
            )
        
        if "401" in error_str or "unauthorized" in error_str:
            return (
                ErrorCategory.CONFIGURATION,
                ErrorSeverity.ERROR,
                [
                    "Check that your API key is correct in Settings",
                    "The API key might have expired - generate a new one",
                    "Verify you have permission to access this resource"
                ]
            )
        
        if "404" in error_str or "not found" in error_str:
            return (
                ErrorCategory.NETWORK,
                ErrorSeverity.WARNING,
                [
                    "The requested URL was not found",
                    "Check that the URL in Settings is correct",
                    "The resource might have been moved or deleted"
                ]
            )
        
        # Validation errors
        if "validation" in error_str or "invalid" in error_str:
            return (
                ErrorCategory.VALIDATION,
                ErrorSeverity.WARNING,
                [
                    "Check that all required fields are filled in",
                    "Verify the data format matches what's expected",
                    "Review any validation messages shown",
                    "Try correcting the highlighted issues and save again"
                ]
            )
        
        # Export/rendering errors
        if "render" in error_str or "template" in error_str:
            return (
                ErrorCategory.EXPORT,
                ErrorSeverity.ERROR,
                [
                    "There may be an issue with the bulletin template",
                    "Try switching to a different template in Settings",
                    "Check that all sections have valid content",
                    "Try removing sections one by one to identify the problem"
                ]
            )
        
        if "html" in error_str or "export" in error_str:
            return (
                ErrorCategory.EXPORT,
                ErrorSeverity.ERROR,
                [
                    "There was a problem generating the HTML",
                    "Try previewing the bulletin to identify issues",
                    "Check that all images and links are valid",
                    "Simplify complex formatting and try again"
                ]
            )
        
        # Memory/resource errors
        if "memory" in error_str or isinstance(exception, MemoryError):
            return (
                ErrorCategory.UNKNOWN,
                ErrorSeverity.CRITICAL,
                [
                    "The application ran out of memory",
                    "Try closing other applications to free up memory",
                    "Reduce the number or size of images in your bulletin",
                    "Save your work and restart the application"
                ]
            )
        
        # Generic fallback
        return (
            ErrorCategory.UNKNOWN,
            ErrorSeverity.ERROR,
            [
                "An unexpected error occurred",
                "Try saving your work and restarting the application",
                "Check the log files for more details",
                "If this persists, please report the issue with the error details"
            ]
        )
    
    @staticmethod
    def format_traceback(exception: Exception) -> str:
        """
        Format exception traceback for display.
        
        Args:
            exception: The exception to format
            
        Returns:
            Formatted traceback string
        """
        try:
            tb_lines = traceback.format_exception(
                type(exception),
                exception,
                exception.__traceback__
            )
            return "".join(tb_lines)
        except Exception as e:
            logger.error(f"Failed to format traceback: {e}")
            return f"{type(exception).__name__}: {str(exception)}"
    
    @staticmethod
    def get_user_friendly_message(exception: Exception, context: Optional[str] = None) -> str:
        """
        Get a user-friendly error message.
        
        Args:
            exception: The exception
            context: Optional context
            
        Returns:
            User-friendly message
        """
        error_type = type(exception).__name__
        error_msg = str(exception)
        
        # Build context-aware message
        if context:
            message = f"Error {context}: {error_msg}"
        else:
            message = error_msg
        
        # Clean up technical jargon
        message = re.sub(r'\[Errno \d+\]', '', message)
        message = re.sub(r'<.*?>', '', message)  # Remove angle brackets
        message = message.strip()
        
        # Limit message length
        if len(message) > 200:
            message = message[:197] + "..."
        
        return message


def handle_error(
    parent,
    exception: Exception,
    title: str = "Error",
    context: Optional[str] = None,
    retry_callback: Optional[callable] = None,
    view_logs_callback: Optional[callable] = None,
    show_dialog: bool = True
) -> None:
    """
    Handle an error with analysis and optional dialog display.
    
    Args:
        parent: Parent window for dialog
        exception: The exception to handle
        title: Dialog title
        context: Context about what was being attempted
        retry_callback: Optional retry function
        view_logs_callback: Optional log viewer function
        show_dialog: Whether to show the error dialog
    """
    analyzer = ErrorAnalyzer()
    
    # Analyze the error
    category, severity, suggestions = analyzer.analyze_exception(exception, context)
    
    # Get user-friendly message
    message = analyzer.get_user_friendly_message(exception, context)
    
    # Get technical details
    details = analyzer.format_traceback(exception)
    
    # Log the error
    log_msg = f"Error handled: {category.value} - {message}"
    if severity == ErrorSeverity.CRITICAL:
        logger.critical(log_msg, exc_info=exception)
    elif severity == ErrorSeverity.ERROR:
        logger.error(log_msg, exc_info=exception)
    elif severity == ErrorSeverity.WARNING:
        logger.warning(log_msg)
    else:
        logger.info(log_msg)
    
    # Show dialog if requested
    if show_dialog:
        from bulletin_builder.ui.error_dialog import show_error
        show_error(
            parent=parent,
            title=title,
            message=message,
            category=category,
            severity=severity,
            details=details,
            suggestions=suggestions,
            retry_callback=retry_callback,
            view_logs_callback=view_logs_callback
        )
