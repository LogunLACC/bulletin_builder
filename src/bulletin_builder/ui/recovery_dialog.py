"""
Recovery Dialog UI for Bulletin Builder.

Provides a user-friendly dialog for crash recovery with options to:
- Load last backup
- Load a previous version
- Start fresh
- View crash logs
- Continue in safe mode
"""

import customtkinter as ctk
from pathlib import Path
from datetime import datetime
from typing import Optional, Any
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)


class RecoveryDialog(ctk.CTkToplevel):
    """
    Modal dialog for crash recovery options.
    
    Presents the user with recovery choices after a detected crash,
    showing available backups and versions with timestamps and details.
    """
    
    def __init__(self, parent, recovery_manager, **kwargs):
        """
        Initialize the Recovery Dialog.
        
        Args:
            parent: Parent window
            recovery_manager: RecoveryManager instance
            **kwargs: Additional arguments for CTkToplevel
        """
        super().__init__(parent, **kwargs)
        
        self.parent = parent
        self.recovery_manager = recovery_manager
        self.result = None  # 'backup', 'version', 'fresh', 'safe_mode', or None
        self.selected_backup: Optional[Path] = None
        self.safe_mode_enabled = ctk.BooleanVar(value=False)
        
        # Window configuration
        self.title("Recovery Mode - Bulletin Builder")
        self.geometry("700x600")
        self.resizable(False, False)
        
        # Modal behavior
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self._center_on_parent()
        
        # Create UI
        self._create_widgets()
        
        # Focus
        self.focus_set()
        
        logger.info("Recovery dialog opened")
    
    def _center_on_parent(self):
        """Center the dialog on the parent window."""
        self.update_idletasks()
        
        if self.parent:
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            dialog_width = self.winfo_width()
            dialog_height = self.winfo_height()
            
            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
            
            self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create and layout all dialog widgets."""
        # Main container with padding
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header section
        self._create_header(main_frame)
        
        # Crash info section
        self._create_crash_info(main_frame)
        
        # Options section
        self._create_options(main_frame)
        
        # Safe mode checkbox
        self._create_safe_mode_option(main_frame)
        
        # Buttons section
        self._create_buttons(main_frame)
    
    def _create_header(self, parent):
        """Create the header section with icon and title."""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Icon and title
        title_frame = ctk.CTkFrame(header_frame, fg_color="#ef4444", corner_radius=10)
        title_frame.pack(fill="x", pady=5)
        
        icon_label = ctk.CTkLabel(
            title_frame,
            text="🛑",
            font=("Segoe UI Emoji", 32),
            text_color="white"
        )
        icon_label.pack(side="left", padx=15, pady=10)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Application Crash Detected",
            font=("Segoe UI", 18, "bold"),
            text_color="white"
        )
        title_label.pack(side="left", padx=10, pady=10)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="The application did not close properly last time. You can recover your work from a backup.",
            font=("Segoe UI", 11),
            text_color="gray"
        )
        subtitle_label.pack(fill="x", pady=(5, 0))
    
    def _create_crash_info(self, parent):
        """Create the crash information section."""
        if not self.recovery_manager.crash_info:
            return
        
        info_frame = ctk.CTkFrame(parent, fg_color="#2b2b2b", corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        info_title = ctk.CTkLabel(
            info_frame,
            text="Crash Information",
            font=("Segoe UI", 13, "bold"),
            text_color="white"
        )
        info_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Crash details
        crash_info = self.recovery_manager.crash_info
        
        timestamp = crash_info.get('timestamp', 'unknown')
        if timestamp != 'unknown':
            try:
                dt = datetime.fromisoformat(timestamp)
                timestamp = dt.strftime("%B %d, %Y at %I:%M %p")
            except:
                pass
        
        details = [
            ("Time:", timestamp),
            ("Last Operation:", crash_info.get('last_operation', 'unknown')),
            ("App Version:", crash_info.get('app_version', 'unknown'))
        ]
        
        for label, value in details:
            detail_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            detail_frame.pack(fill="x", padx=15, pady=2)
            
            label_widget = ctk.CTkLabel(
                detail_frame,
                text=label,
                font=("Segoe UI", 10, "bold"),
                text_color="gray",
                width=120,
                anchor="w"
            )
            label_widget.pack(side="left")
            
            value_widget = ctk.CTkLabel(
                detail_frame,
                text=str(value),
                font=("Segoe UI", 10),
                text_color="white",
                anchor="w"
            )
            value_widget.pack(side="left", fill="x", expand=True)
        
        info_frame.pack_configure(pady=(0, 20))
    
    def _create_options(self, parent):
        """Create the recovery options section."""
        options_frame = ctk.CTkFrame(parent, fg_color="transparent")
        options_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Section title
        title_label = ctk.CTkLabel(
            options_frame,
            text="Recovery Options",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        )
        title_label.pack(fill="x", pady=(0, 10))
        
        # Get available backups
        backups = self.recovery_manager.get_available_backups()
        
        if backups:
            # Scrollable frame for backups
            scroll_frame = ctk.CTkScrollableFrame(
                options_frame,
                fg_color="#2b2b2b",
                corner_radius=10,
                height=250
            )
            scroll_frame.pack(fill="both", expand=True)
            
            # List backups
            for i, backup in enumerate(backups[:10]):  # Show up to 10 most recent
                self._create_backup_option(scroll_frame, backup, i == 0)
        else:
            # No backups available
            no_backup_label = ctk.CTkLabel(
                options_frame,
                text="⚠️ No backups available",
                font=("Segoe UI", 11),
                text_color="orange",
                anchor="w"
            )
            no_backup_label.pack(fill="x", pady=10)
    
    def _create_backup_option(self, parent, backup: dict, is_latest: bool):
        """
        Create a backup option button.
        
        Args:
            parent: Parent widget
            backup: Backup info dictionary
            is_latest: Whether this is the most recent backup
        """
        # Backup container
        backup_frame = ctk.CTkFrame(
            parent,
            fg_color="#3a3a3a" if is_latest else "#323232",
            corner_radius=8,
            border_width=2 if is_latest else 0,
            border_color="#3b82f6" if is_latest else "transparent"
        )
        backup_frame.pack(fill="x", padx=10, pady=5)
        
        # Backup info
        info_container = ctk.CTkFrame(backup_frame, fg_color="transparent")
        info_container.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        # Title with latest badge
        title_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        title_frame.pack(fill="x", anchor="w")
        
        if is_latest:
            latest_badge = ctk.CTkLabel(
                title_frame,
                text="LATEST",
                font=("Segoe UI", 8, "bold"),
                text_color="white",
                fg_color="#3b82f6",
                corner_radius=4,
                padx=8,
                pady=2
            )
            latest_badge.pack(side="left", padx=(0, 8))
        
        name_label = ctk.CTkLabel(
            title_frame,
            text=backup['name'],
            font=("Segoe UI", 11, "bold"),
            text_color="white",
            anchor="w"
        )
        name_label.pack(side="left")
        
        # Timestamp
        timestamp_str = backup['timestamp'].strftime("%B %d, %Y at %I:%M %p")
        timestamp_label = ctk.CTkLabel(
            info_container,
            text=f"📅 {timestamp_str}",
            font=("Segoe UI", 9),
            text_color="gray",
            anchor="w"
        )
        timestamp_label.pack(fill="x", pady=(2, 0))
        
        # Additional info
        info_parts = []
        if backup.get('sections_count'):
            info_parts.append(f"{backup['sections_count']} sections")
        if backup.get('original_file'):
            original = Path(backup['original_file']).name
            info_parts.append(f"from {original}")
        if backup.get('directory'):
            info_parts.append(f"in {backup['directory']}")
        
        if info_parts:
            info_text = " • ".join(info_parts)
            info_label = ctk.CTkLabel(
                info_container,
                text=f"ℹ️ {info_text}",
                font=("Segoe UI", 9),
                text_color="gray",
                anchor="w"
            )
            info_label.pack(fill="x", pady=(2, 0))
        
        # Restore button
        restore_btn = ctk.CTkButton(
            backup_frame,
            text="Restore" if not is_latest else "Restore Latest",
            width=120,
            height=35,
            fg_color="#3b82f6" if is_latest else "#4a5568",
            hover_color="#2563eb" if is_latest else "#5a6578",
            command=lambda: self._restore_backup(backup['path'])
        )
        restore_btn.pack(side="right", padx=15, pady=10)
    
    def _create_safe_mode_option(self, parent):
        """Create the safe mode checkbox option."""
        safe_mode_frame = ctk.CTkFrame(parent, fg_color="#2b2b2b", corner_radius=10)
        safe_mode_frame.pack(fill="x", pady=(0, 20))
        
        checkbox = ctk.CTkCheckBox(
            safe_mode_frame,
            text="Continue in Safe Mode (minimal features)",
            variable=self.safe_mode_enabled,
            font=("Segoe UI", 11),
            text_color="white",
            fg_color="#3b82f6",
            hover_color="#2563eb"
        )
        checkbox.pack(padx=15, pady=15)
        
        # Info label
        info_label = ctk.CTkLabel(
            safe_mode_frame,
            text="Safe mode disables auto-backup, AI features, and automatic imports to prevent further crashes.",
            font=("Segoe UI", 9),
            text_color="gray",
            wraplength=600,
            justify="left"
        )
        info_label.pack(padx=15, pady=(0, 15))
    
    def _create_buttons(self, parent):
        """Create the action buttons section."""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # Start Fresh button
        fresh_btn = ctk.CTkButton(
            button_frame,
            text="🆕 Start Fresh",
            width=150,
            height=40,
            fg_color="#4a5568",
            hover_color="#5a6578",
            command=self._start_fresh,
            font=("Segoe UI", 11)
        )
        fresh_btn.pack(side="left", padx=(0, 10))
        
        # View Logs button
        logs_btn = ctk.CTkButton(
            button_frame,
            text="📄 View Logs",
            width=150,
            height=40,
            fg_color="#4a5568",
            hover_color="#5a6578",
            command=self._view_logs,
            font=("Segoe UI", 11)
        )
        logs_btn.pack(side="left", padx=(0, 10))
        
        # Spacer
        ctk.CTkFrame(button_frame, fg_color="transparent").pack(side="left", fill="x", expand=True)
        
        # Close button
        close_btn = ctk.CTkButton(
            button_frame,
            text="✕ Close",
            width=120,
            height=40,
            fg_color="#4a5568",
            hover_color="#5a6578",
            command=self._close,
            font=("Segoe UI", 11)
        )
        close_btn.pack(side="right")
    
    def _restore_backup(self, backup_path: Path):
        """
        Restore a selected backup and close the dialog.
        
        Args:
            backup_path: Path to the backup file to restore
        """
        self.selected_backup = backup_path
        self.result = 'backup'
        
        logger.info(f"User selected to restore backup: {backup_path}")
        
        # Apply safe mode if enabled
        if self.safe_mode_enabled.get():
            self.recovery_manager.enter_safe_mode()
        
        # Close dialog
        self.grab_release()
        self.destroy()
    
    def _start_fresh(self):
        """Start with a fresh, empty bulletin."""
        self.result = 'fresh'
        
        logger.info("User selected to start fresh")
        
        # Apply safe mode if enabled
        if self.safe_mode_enabled.get():
            self.recovery_manager.enter_safe_mode()
        
        # Close dialog
        self.grab_release()
        self.destroy()
    
    def _view_logs(self):
        """Open the log viewer dialog."""
        logger.info("User requested to view logs")
        
        # Import here to avoid circular dependency
        try:
            from bulletin_builder.ui.log_viewer import LogViewerDialog
            log_dialog = LogViewerDialog(self)
            self.wait_window(log_dialog)
        except ImportError:
            # Fallback: Open logs folder
            import os
            import subprocess
            
            log_dir = Path("./logs")
            if log_dir.exists():
                if os.name == 'nt':  # Windows
                    os.startfile(log_dir)
                elif os.name == 'posix':  # macOS/Linux
                    subprocess.run(['open' if 'darwin' in os.sys.platform else 'xdg-open', log_dir])
    
    def _close(self):
        """Close the dialog without taking action."""
        self.result = None
        
        logger.info("Recovery dialog closed without action")
        
        # Apply safe mode if enabled
        if self.safe_mode_enabled.get():
            self.recovery_manager.enter_safe_mode()
        
        self.grab_release()
        self.destroy()


def show_recovery_dialog(app, recovery_manager) -> Optional[str]:
    """
    Show the recovery dialog and handle the user's choice.
    
    Args:
        app: Main application instance
        recovery_manager: RecoveryManager instance
    
    Returns:
        Result string: 'backup', 'fresh', or None
    """
    try:
        dialog = RecoveryDialog(app, recovery_manager)
        app.wait_window(dialog)
        
        # Handle the result
        if dialog.result == 'backup' and dialog.selected_backup:
            success, message = recovery_manager.restore_backup(dialog.selected_backup)
            
            if success and hasattr(app, 'show_status_message'):
                app.show_status_message(message, duration_ms=3000)
            elif not success:
                from tkinter import messagebox
                messagebox.showerror("Restore Failed", message)
            
            return 'backup'
            
        elif dialog.result == 'fresh':
            success, message = recovery_manager.start_fresh()
            
            if success and hasattr(app, 'show_status_message'):
                app.show_status_message(message, duration_ms=2000)
            elif not success:
                from tkinter import messagebox
                messagebox.showerror("Start Fresh Failed", message)
            
            return 'fresh'
        
        return None
        
    except Exception as e:
        logger.error(f"Error showing recovery dialog: {e}")
        return None
