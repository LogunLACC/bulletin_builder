"""
Enhanced error reporting dialog with actionable suggestions.

This module provides a user-friendly error dialog that:
- Categorizes errors for better understanding
- Provides actionable suggestions for common problems
- Allows copying error details for support
- Offers retry and recovery options
"""

import customtkinter as ctk
from pathlib import Path
from typing import Optional, Callable, List
from datetime import datetime
from enum import Enum

from ..app_core.logging_config import get_logger

logger = get_logger(__name__)


class ErrorCategory(Enum):
    """Categories of errors for better user guidance."""
    FILE_IO = "File Error"
    NETWORK = "Network Error"
    IMPORT = "Import Error"
    EXPORT = "Export Error"
    VALIDATION = "Validation Error"
    PERMISSION = "Permission Error"
    CONFIGURATION = "Configuration Error"
    UNKNOWN = "Unexpected Error"


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorDialog(ctk.CTkToplevel):
    """Enhanced error dialog with suggestions and actions."""
    
    def __init__(
        self,
        parent,
        title: str,
        error_message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
        retry_callback: Optional[Callable] = None,
        view_logs_callback: Optional[Callable] = None
    ):
        """
        Initialize error dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            error_message: Main error message
            category: Error category for better guidance
            severity: Error severity level
            details: Additional technical details
            suggestions: List of actionable suggestions
            retry_callback: Optional callback to retry the failed operation
            view_logs_callback: Optional callback to open log viewer
        """
        super().__init__(parent)
        
        self.parent = parent
        self.error_message = error_message
        self.category = category
        self.severity = severity
        self.details = details
        self.suggestions = suggestions or []
        self.retry_callback = retry_callback
        self.view_logs_callback = view_logs_callback
        
        # Window setup
        self.title(title)
        self.geometry("600x500")
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self._center_on_parent()
        
        # Build UI
        self._create_widgets()
        
        # Log error
        self._log_error()
        
        logger.info(f"Error dialog shown: {category.value} - {error_message}")
    
    def _center_on_parent(self):
        """Center dialog on parent window."""
        self.update_idletasks()
        
        try:
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_w = self.parent.winfo_width()
            parent_h = self.parent.winfo_height()
            
            dialog_w = self.winfo_width()
            dialog_h = self.winfo_height()
            
            x = parent_x + (parent_w - dialog_w) // 2
            y = parent_y + (parent_h - dialog_h) // 2
            
            self.geometry(f"+{x}+{y}")
        except Exception as e:
            logger.debug(f"Could not center dialog: {e}")
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Error icon and header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))
        
        # Icon based on severity
        icon = self._get_severity_icon()
        icon_label = ctk.CTkLabel(
            header_frame,
            text=icon,
            font=ctk.CTkFont(size=36),
            text_color=self._get_severity_color()
        )
        icon_label.pack(side="left", padx=(0, 15))
        
        # Title and category
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)
        
        category_label = ctk.CTkLabel(
            title_frame,
            text=self.category.value,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self._get_severity_color()
        )
        category_label.pack(anchor="w")
        
        message_label = ctk.CTkLabel(
            title_frame,
            text=self.error_message,
            font=ctk.CTkFont(size=13),
            wraplength=450,
            justify="left"
        )
        message_label.pack(anchor="w", pady=(5, 0))
        
        # Suggestions section (if any)
        if self.suggestions:
            suggestions_frame = ctk.CTkFrame(main_frame)
            suggestions_frame.pack(fill="x", pady=(0, 10))
            
            suggestions_label = ctk.CTkLabel(
                suggestions_frame,
                text="💡 Suggestions:",
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            )
            suggestions_label.pack(anchor="w", padx=15, pady=(10, 5))
            
            for i, suggestion in enumerate(self.suggestions, 1):
                suggestion_text = ctk.CTkLabel(
                    suggestions_frame,
                    text=f"{i}. {suggestion}",
                    font=ctk.CTkFont(size=12),
                    wraplength=520,
                    justify="left",
                    anchor="w"
                )
                suggestion_text.pack(anchor="w", padx=30, pady=2)
            
            # Add spacing at bottom
            ctk.CTkLabel(suggestions_frame, text="", height=5).pack()
        
        # Details section (collapsible)
        if self.details:
            details_frame = ctk.CTkFrame(main_frame)
            details_frame.pack(fill="both", expand=True, pady=(0, 10))
            
            details_header = ctk.CTkLabel(
                details_frame,
                text="Technical Details:",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            details_header.pack(anchor="w", padx=10, pady=(10, 5))
            
            details_text = ctk.CTkTextbox(
                details_frame,
                height=100,
                wrap="word",
                font=ctk.CTkFont(family="Consolas", size=11)
            )
            details_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            details_text.insert("1.0", self.details)
            details_text.configure(state="disabled")
        
        # Action buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Left side buttons
        left_buttons = ctk.CTkFrame(button_frame, fg_color="transparent")
        left_buttons.pack(side="left")
        
        copy_btn = ctk.CTkButton(
            left_buttons,
            text="📋 Copy Details",
            command=self._copy_to_clipboard,
            width=120,
            fg_color="#6366f1",
            hover_color="#4f46e5"
        )
        copy_btn.pack(side="left", padx=(0, 5))
        
        if self.view_logs_callback:
            logs_btn = ctk.CTkButton(
                left_buttons,
                text="📄 View Logs",
                command=self._view_logs,
                width=120,
                fg_color="#6366f1",
                hover_color="#4f46e5"
            )
            logs_btn.pack(side="left", padx=5)
        
        # Right side buttons
        right_buttons = ctk.CTkFrame(button_frame, fg_color="transparent")
        right_buttons.pack(side="right")
        
        if self.retry_callback:
            retry_btn = ctk.CTkButton(
                right_buttons,
                text="🔄 Retry",
                command=self._retry,
                width=100,
                fg_color="#10b981",
                hover_color="#059669"
            )
            retry_btn.pack(side="left", padx=5)
        
        close_btn = ctk.CTkButton(
            right_buttons,
            text="Close",
            command=self._close,
            width=100
        )
        close_btn.pack(side="left", padx=(5, 0))
    
    def _get_severity_icon(self) -> str:
        """Get icon emoji based on severity."""
        icons = {
            ErrorSeverity.INFO: "ℹ️",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.CRITICAL: "🛑"
        }
        return icons.get(self.severity, "❌")
    
    def _get_severity_color(self) -> str:
        """Get color based on severity."""
        colors = {
            ErrorSeverity.INFO: "#3b82f6",     # Blue
            ErrorSeverity.WARNING: "#f59e0b",  # Amber
            ErrorSeverity.ERROR: "#ef4444",    # Red
            ErrorSeverity.CRITICAL: "#dc2626"  # Dark red
        }
        return colors.get(self.severity, "#ef4444")
    
    def _copy_to_clipboard(self):
        """Copy error details to clipboard."""
        try:
            # Build comprehensive error report
            report_lines = [
                f"Error Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 60,
                f"Category: {self.category.value}",
                f"Severity: {self.severity.value.upper()}",
                "",
                "Message:",
                self.error_message,
                ""
            ]
            
            if self.suggestions:
                report_lines.append("Suggestions:")
                for i, suggestion in enumerate(self.suggestions, 1):
                    report_lines.append(f"  {i}. {suggestion}")
                report_lines.append("")
            
            if self.details:
                report_lines.append("Technical Details:")
                report_lines.append(self.details)
            
            report = "\n".join(report_lines)
            
            # Copy to clipboard
            self.clipboard_clear()
            self.clipboard_append(report)
            
            # Show feedback
            self._show_feedback("✓ Copied to clipboard", success=True)
            
            logger.info("Error details copied to clipboard")
            
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
            self._show_feedback("✗ Copy failed", success=False)
    
    def _view_logs(self):
        """Open log viewer."""
        try:
            if self.view_logs_callback:
                self.view_logs_callback()
            logger.info("Log viewer opened from error dialog")
        except Exception as e:
            logger.error(f"Failed to open log viewer: {e}")
    
    def _retry(self):
        """Retry the failed operation."""
        try:
            if self.retry_callback:
                self._close()
                self.retry_callback()
            logger.info("Retry requested from error dialog")
        except Exception as e:
            logger.error(f"Retry failed: {e}")
            # Show new error dialog
            ErrorDialog(
                self.parent,
                "Retry Failed",
                str(e),
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.ERROR
            )
    
    def _close(self):
        """Close the dialog."""
        self.grab_release()
        self.destroy()
    
    def _show_feedback(self, message: str, success: bool = True):
        """Show temporary feedback message."""
        # Create overlay
        overlay = ctk.CTkFrame(
            self,
            fg_color=("#10b981" if success else "#ef4444")
        )
        overlay.place(relx=0.5, rely=0.95, anchor="center")
        
        msg_label = ctk.CTkLabel(
            overlay,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        msg_label.pack(padx=20, pady=8)
        
        # Auto-dismiss after 2 seconds
        self.after(2000, overlay.destroy)
    
    def _log_error(self):
        """Log the error for debugging."""
        log_message = f"[{self.category.value}] {self.error_message}"
        
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif self.severity == ErrorSeverity.ERROR:
            logger.error(log_message)
        elif self.severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        if self.details:
            logger.debug(f"Error details: {self.details}")


def show_error(
    parent,
    title: str,
    message: str,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    details: Optional[str] = None,
    suggestions: Optional[List[str]] = None,
    retry_callback: Optional[Callable] = None,
    view_logs_callback: Optional[Callable] = None
):
    """
    Convenience function to show an error dialog.
    
    Args:
        parent: Parent window
        title: Dialog title
        message: Error message
        category: Error category
        severity: Error severity
        details: Technical details
        suggestions: List of suggestions
        retry_callback: Optional retry function
        view_logs_callback: Optional log viewer function
    """
    dialog = ErrorDialog(
        parent=parent,
        title=title,
        error_message=message,
        category=category,
        severity=severity,
        details=details,
        suggestions=suggestions,
        retry_callback=retry_callback,
        view_logs_callback=view_logs_callback
    )
    return dialog
