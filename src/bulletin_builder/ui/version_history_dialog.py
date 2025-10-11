"""
Version history dialog for viewing and restoring draft versions.
"""

import customtkinter as ctk
from pathlib import Path
from typing import Callable, Optional
from datetime import datetime

from ..app_core.draft_versioning import DraftVersionManager, VersionInfo
from ..ui_core.logging_config import logger


class VersionHistoryDialog(ctk.CTkToplevel):
    """Dialog for managing draft version history."""
    
    def __init__(
        self,
        parent,
        draft_path: Path,
        on_restore: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize version history dialog.
        
        Args:
            parent: Parent window
            draft_path: Path to the draft file
            on_restore: Callback when a version is restored (receives version_id)
        """
        super().__init__(parent)
        
        self.draft_path = draft_path
        self.on_restore = on_restore
        self.manager = DraftVersionManager(draft_path)
        self.selected_version: Optional[VersionInfo] = None
        
        # Window setup
        self.title(f"Version History - {draft_path.stem}")
        self.geometry("800x600")
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.center_on_parent(parent)
        
        # Build UI
        self._create_widgets()
        
        # Load versions
        self.refresh_versions()
        
        logger.info(f"Opened version history for: {draft_path.name}")
    
    def center_on_parent(self, parent):
        """Center dialog on parent window."""
        self.update_idletasks()
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        
        dialog_w = self.winfo_width()
        dialog_h = self.winfo_height()
        
        x = parent_x + (parent_w - dialog_w) // 2
        y = parent_y + (parent_h - dialog_h) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Main container with padding
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkLabel(
            main_frame,
            text="Draft Version History",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.pack(pady=(0, 10))
        
        # Info label
        self.info_label = ctk.CTkLabel(
            main_frame,
            text="Select a version to view details or restore",
            font=ctk.CTkFont(size=12)
        )
        self.info_label.pack(pady=(0, 10))
        
        # Versions list frame
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Scrollable frame for versions
        self.versions_scroll = ctk.CTkScrollableFrame(
            list_frame,
            label_text="Available Versions"
        )
        self.versions_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Details panel
        details_frame = ctk.CTkFrame(main_frame)
        details_frame.pack(fill="x", pady=(0, 10))
        
        details_label = ctk.CTkLabel(
            details_frame,
            text="Version Details",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        details_label.pack(pady=(5, 5))
        
        self.details_text = ctk.CTkTextbox(
            details_frame,
            height=100,
            wrap="word"
        )
        self.details_text.pack(fill="x", padx=5, pady=(0, 5))
        
        # Button panel
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")
        
        # Left side buttons
        left_buttons = ctk.CTkFrame(button_frame, fg_color="transparent")
        left_buttons.pack(side="left")
        
        self.refresh_btn = ctk.CTkButton(
            left_buttons,
            text="Refresh",
            command=self.refresh_versions,
            width=100
        )
        self.refresh_btn.pack(side="left", padx=(0, 5))
        
        # Right side buttons
        right_buttons = ctk.CTkFrame(button_frame, fg_color="transparent")
        right_buttons.pack(side="right")
        
        self.delete_btn = ctk.CTkButton(
            right_buttons,
            text="Delete",
            command=self.delete_version,
            state="disabled",
            width=100,
            fg_color="#d32f2f",
            hover_color="#b71c1c"
        )
        self.delete_btn.pack(side="left", padx=5)
        
        self.restore_btn = ctk.CTkButton(
            right_buttons,
            text="Restore",
            command=self.restore_version,
            state="disabled",
            width=100
        )
        self.restore_btn.pack(side="left", padx=5)
        
        close_btn = ctk.CTkButton(
            right_buttons,
            text="Close",
            command=self.close_dialog,
            width=100
        )
        close_btn.pack(side="left", padx=(5, 0))
    
    def refresh_versions(self):
        """Reload version list."""
        # Clear existing version buttons
        for widget in self.versions_scroll.winfo_children():
            widget.destroy()
        
        # Clear selection
        self.selected_version = None
        self.update_details()
        
        # Load versions
        versions = self.manager.list_versions()
        
        if not versions:
            no_versions = ctk.CTkLabel(
                self.versions_scroll,
                text="No versions available",
                font=ctk.CTkFont(size=12)
            )
            no_versions.pack(pady=20)
            self.info_label.configure(text="No versions available")
            return
        
        # Update info label
        self.info_label.configure(text=f"{len(versions)} version(s) available")
        
        # Create button for each version
        for version in versions:
            self._create_version_button(version)
        
        logger.info(f"Refreshed version list: {len(versions)} versions")
    
    def _create_version_button(self, version: VersionInfo):
        """Create a button for a version."""
        # Container frame for version
        version_frame = ctk.CTkFrame(self.versions_scroll)
        version_frame.pack(fill="x", pady=2, padx=5)
        
        # Create button that fills the frame
        btn = ctk.CTkButton(
            version_frame,
            text="",  # Will set with compound text
            command=lambda v=version: self.select_version(v),
            anchor="w",
            height=60,
            fg_color=("gray80", "gray25")
        )
        btn.pack(fill="x", pady=2, padx=2)
        
        # Format timestamp
        try:
            timestamp = datetime.fromisoformat(version.timestamp)
            time_str = timestamp.strftime("%Y-%m-%d %I:%M:%S %p")
        except:
            time_str = version.version_id
        
        # Build display text
        auto_badge = " [AUTO]" if version.auto_created else ""
        desc = version.description or "No description"
        sections = f"{version.sections_count} section(s)"
        
        # Format size
        size_kb = version.file_size / 1024
        if size_kb < 1024:
            size_str = f"{size_kb:.1f} KB"
        else:
            size_str = f"{size_kb/1024:.1f} MB"
        
        text = f"{time_str}{auto_badge}\n{desc}\n{sections} • {size_str}"
        btn.configure(text=text)
    
    def select_version(self, version: VersionInfo):
        """Select a version and show details."""
        self.selected_version = version
        self.update_details()
        self.restore_btn.configure(state="normal")
        self.delete_btn.configure(state="normal")
        logger.info(f"Selected version: {version.version_id}")
    
    def update_details(self):
        """Update the details panel."""
        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        
        if not self.selected_version:
            self.details_text.insert("1.0", "No version selected")
            self.restore_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
        else:
            v = self.selected_version
            
            # Format timestamp
            try:
                timestamp = datetime.fromisoformat(v.timestamp)
                time_str = timestamp.strftime("%Y-%m-%d %I:%M:%S %p")
            except:
                time_str = v.version_id
            
            # Build details text
            details = f"""Version ID: {v.version_id}
Created: {time_str}
Type: {'Automatic' if v.auto_created else 'Manual'}
Description: {v.description or 'No description'}
Parent Draft: {v.parent_draft}
Sections: {v.sections_count}
File Size: {v.file_size:,} bytes
Path: {v.version_path}"""
            
            self.details_text.insert("1.0", details)
        
        self.details_text.configure(state="disabled")
    
    def restore_version(self):
        """Restore the selected version."""
        if not self.selected_version:
            return
        
        # Confirm restoration
        confirm = ctk.CTkToplevel(self)
        confirm.title("Confirm Restore")
        confirm.geometry("400x200")
        confirm.transient(self)
        confirm.grab_set()
        
        # Center on this dialog
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 200) // 2
        confirm.geometry(f"+{x}+{y}")
        
        # Warning message
        msg_frame = ctk.CTkFrame(confirm)
        msg_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        warning = ctk.CTkLabel(
            msg_frame,
            text="⚠ Restore Version?",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        warning.pack(pady=(0, 10))
        
        info = ctk.CTkLabel(
            msg_frame,
            text=f"This will replace your current draft with:\n\n"
                 f"{self.selected_version.get_display_name()}\n\n"
                 f"Your current changes will be lost unless\n"
                 f"they were saved as a version.",
            justify="center",
            wraplength=350
        )
        info.pack(pady=(0, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(msg_frame, fg_color="transparent")
        btn_frame.pack()
        
        def confirm_restore():
            confirm.destroy()
            self._do_restore()
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=confirm.destroy,
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Restore",
            command=confirm_restore,
            width=100,
            fg_color="#d32f2f",
            hover_color="#b71c1c"
        ).pack(side="left", padx=5)
    
    def _do_restore(self):
        """Actually perform the restore."""
        try:
            # Restore the version
            draft_data = self.manager.restore_version(self.selected_version.version_id)
            
            logger.info(f"Restored version: {self.selected_version.version_id}")
            
            # Call callback if provided
            if self.on_restore:
                self.on_restore(draft_data)
            
            # Show success
            self._show_message(
                "Version Restored",
                f"Successfully restored version:\n{self.selected_version.get_display_name()}",
                success=True
            )
            
            # Close dialog
            self.after(1500, self.close_dialog)
            
        except Exception as e:
            logger.error(f"Failed to restore version: {e}")
            self._show_message(
                "Restore Failed",
                f"Failed to restore version:\n{str(e)}",
                success=False
            )
    
    def delete_version(self):
        """Delete the selected version."""
        if not self.selected_version:
            return
        
        # Confirm deletion
        confirm = ctk.CTkToplevel(self)
        confirm.title("Confirm Delete")
        confirm.geometry("400x180")
        confirm.transient(self)
        confirm.grab_set()
        
        # Center on this dialog
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 180) // 2
        confirm.geometry(f"+{x}+{y}")
        
        # Warning message
        msg_frame = ctk.CTkFrame(confirm)
        msg_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        warning = ctk.CTkLabel(
            msg_frame,
            text="⚠ Delete Version?",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        warning.pack(pady=(0, 10))
        
        info = ctk.CTkLabel(
            msg_frame,
            text=f"Permanently delete this version?\n\n"
                 f"{self.selected_version.get_display_name()}\n\n"
                 f"This action cannot be undone.",
            justify="center",
            wraplength=350
        )
        info.pack(pady=(0, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(msg_frame, fg_color="transparent")
        btn_frame.pack()
        
        def confirm_delete():
            confirm.destroy()
            self._do_delete()
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=confirm.destroy,
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Delete",
            command=confirm_delete,
            width=100,
            fg_color="#d32f2f",
            hover_color="#b71c1c"
        ).pack(side="left", padx=5)
    
    def _do_delete(self):
        """Actually perform the deletion."""
        try:
            version_id = self.selected_version.version_id
            display_name = self.selected_version.get_display_name()
            
            # Delete the version
            self.manager.delete_version(version_id)
            
            logger.info(f"Deleted version: {version_id}")
            
            # Clear selection
            self.selected_version = None
            
            # Refresh list
            self.refresh_versions()
            
            # Show success
            self._show_message(
                "Version Deleted",
                f"Successfully deleted version:\n{display_name}",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Failed to delete version: {e}")
            self._show_message(
                "Delete Failed",
                f"Failed to delete version:\n{str(e)}",
                success=False
            )
    
    def _show_message(self, title: str, message: str, success: bool = True):
        """Show a temporary message overlay."""
        # Create overlay
        overlay = ctk.CTkFrame(
            self,
            fg_color=("#4caf50" if success else "#f44336")
        )
        overlay.place(relx=0.5, rely=0.5, anchor="center")
        
        title_label = ctk.CTkLabel(
            overlay,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        title_label.pack(padx=40, pady=(20, 5))
        
        msg_label = ctk.CTkLabel(
            overlay,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color="white",
            justify="center"
        )
        msg_label.pack(padx=40, pady=(5, 20))
        
        # Auto-dismiss after 2 seconds
        self.after(2000, overlay.destroy)
    
    def close_dialog(self):
        """Close the dialog."""
        self.grab_release()
        self.destroy()
