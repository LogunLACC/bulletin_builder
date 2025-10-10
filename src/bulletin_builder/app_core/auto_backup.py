"""
Automatic draft backup system for crash recovery and data protection.

This module provides automatic backup functionality to prevent data loss
in case of crashes or unexpected exits.
"""

import json
import atexit
import signal
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional, List
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)


class AutoBackupManager:
    """
    Manages automatic draft backups for crash recovery.
    
    Features:
    - Periodic auto-save of current work
    - Crash detection and recovery
    - Backup rotation (keeps last N backups)
    - Recovery prompt on next launch
    """
    
    def __init__(self, app: Any, backup_dir: str = "./backups", max_backups: int = 10):
        """
        Initialize the auto-backup manager.
        
        Args:
            app: The main application instance
            backup_dir: Directory to store backup files
            max_backups: Maximum number of backup files to keep
        """
        self.app = app
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.backup_interval_ms = 120000  # 2 minutes default
        self.auto_save_id: Optional[str] = None
        self.crash_file = self.backup_dir / ".crash_detected"
        self.last_backup_file = self.backup_dir / ".last_backup.json"
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"AutoBackupManager initialized: {self.backup_dir}")
    
    def start(self) -> None:
        """Start the automatic backup system."""
        # Register exit handlers for graceful shutdown
        atexit.register(self._on_graceful_exit)
        
        # Register signal handlers for crash detection
        if sys.platform != "win32":
            signal.signal(signal.SIGTERM, self._on_crash)
            signal.signal(signal.SIGINT, self._on_crash)
        
        # Create crash detection marker
        self._create_crash_marker()
        
        # Start periodic auto-save
        self._schedule_auto_save()
        
        logger.info("Auto-backup system started")
    
    def stop(self) -> None:
        """Stop the automatic backup system."""
        # Cancel scheduled auto-save
        if self.auto_save_id and hasattr(self.app, 'after_cancel'):
            try:
                self.app.after_cancel(self.auto_save_id)
                self.auto_save_id = None
            except Exception as e:
                logger.debug(f"Could not cancel auto-save timer: {e}")
        
        logger.info("Auto-backup system stopped")
    
    def _schedule_auto_save(self) -> None:
        """Schedule the next automatic backup."""
        if hasattr(self.app, 'after'):
            self.auto_save_id = self.app.after(
                self.backup_interval_ms,
                self._perform_auto_save
            )
    
    def _perform_auto_save(self) -> None:
        """Perform an automatic backup of the current draft."""
        try:
            # Only backup if there's content to save
            if not hasattr(self.app, 'sections_data') or not self.app.sections_data:
                logger.debug("Skipping auto-backup: no content")
                self._schedule_auto_save()  # Schedule next backup
                return
            
            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"auto_backup_{timestamp}.json"
            
            # Collect draft data
            payload = self._collect_draft_data()
            
            # Save backup
            backup_file.write_text(json.dumps(payload, indent=2), encoding='utf-8')
            
            # Update last backup reference
            self.last_backup_file.write_text(str(backup_file), encoding='utf-8')
            
            logger.debug(f"Auto-backup created: {backup_file.name}")
            
            # Clean up old backups
            self._rotate_backups()
            
        except Exception as e:
            logger.error(f"Auto-backup failed: {e}")
        
        finally:
            # Schedule next backup
            self._schedule_auto_save()
    
    def _collect_draft_data(self) -> Dict[str, Any]:
        """
        Collect current draft data for backup.
        
        Returns:
            Dictionary containing draft data
        """
        payload = {
            'timestamp': datetime.now().isoformat(),
            'sections': getattr(self.app, 'sections_data', []),
            'template_name': getattr(self.app.renderer, 'template_name', 'main_layout.html')
                if hasattr(self.app, 'renderer') else 'main_layout.html'
        }
        
        # Include settings if available
        if hasattr(self.app, 'settings_frame') and hasattr(self.app.settings_frame, 'dump'):
            try:
                payload['settings'] = self.app.settings_frame.dump()
            except Exception as e:
                logger.debug(f"Could not collect settings: {e}")
                payload['settings'] = {}
        
        # Include current file path if available
        if hasattr(self.app, 'current_draft_path') and self.app.current_draft_path:
            payload['original_file'] = str(self.app.current_draft_path)
        
        return payload
    
    def _rotate_backups(self) -> None:
        """Remove old backup files, keeping only the most recent max_backups."""
        try:
            # Get all backup files
            backup_files = sorted(
                self.backup_dir.glob("auto_backup_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # Remove excess backups
            for old_backup in backup_files[self.max_backups:]:
                try:
                    old_backup.unlink()
                    logger.debug(f"Removed old backup: {old_backup.name}")
                except Exception as e:
                    logger.warning(f"Could not remove old backup {old_backup.name}: {e}")
        
        except Exception as e:
            logger.error(f"Backup rotation failed: {e}")
    
    def _create_crash_marker(self) -> None:
        """Create a marker file to detect crashes."""
        try:
            self.crash_file.write_text(datetime.now().isoformat(), encoding='utf-8')
        except Exception as e:
            logger.error(f"Could not create crash marker: {e}")
    
    def _remove_crash_marker(self) -> None:
        """Remove the crash marker file on graceful exit."""
        try:
            if self.crash_file.exists():
                self.crash_file.unlink()
                logger.debug("Crash marker removed (graceful exit)")
        except Exception as e:
            logger.warning(f"Could not remove crash marker: {e}")
    
    def _on_graceful_exit(self) -> None:
        """Handler for graceful application exit."""
        logger.info("Graceful exit detected")
        self._remove_crash_marker()
        self.stop()
    
    def _on_crash(self, signum: int, frame: Any) -> None:
        """Handler for crash signals."""
        logger.warning(f"Crash signal received: {signum}")
        # Perform emergency backup
        try:
            emergency_file = self.backup_dir / f"emergency_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            payload = self._collect_draft_data()
            emergency_file.write_text(json.dumps(payload, indent=2), encoding='utf-8')
            logger.info(f"Emergency backup created: {emergency_file.name}")
        except Exception as e:
            logger.error(f"Emergency backup failed: {e}")
    
    def check_for_crash(self) -> Optional[Path]:
        """
        Check if the application crashed on last run.
        
        Returns:
            Path to last backup file if crash detected, None otherwise
        """
        if not self.crash_file.exists():
            logger.debug("No crash detected")
            return None
        
        logger.warning("Previous crash detected!")
        
        # Try to find the most recent backup
        if self.last_backup_file.exists():
            try:
                backup_path = Path(self.last_backup_file.read_text(encoding='utf-8').strip())
                if backup_path.exists():
                    logger.info(f"Found crash recovery file: {backup_path}")
                    return backup_path
            except Exception as e:
                logger.error(f"Could not read last backup reference: {e}")
        
        # Fallback: find most recent backup
        try:
            backup_files = sorted(
                self.backup_dir.glob("auto_backup_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            if backup_files:
                logger.info(f"Found crash recovery file: {backup_files[0]}")
                return backup_files[0]
        except Exception as e:
            logger.error(f"Could not find backup files: {e}")
        
        return None
    
    def get_available_backups(self) -> List[Dict[str, Any]]:
        """
        Get list of available backup files with metadata.
        
        Returns:
            List of dicts with backup info (path, timestamp, size)
        """
        backups = []
        try:
            for backup_file in sorted(
                self.backup_dir.glob("auto_backup_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            ):
                try:
                    stat = backup_file.stat()
                    backups.append({
                        'path': backup_file,
                        'name': backup_file.name,
                        'timestamp': datetime.fromtimestamp(stat.st_mtime),
                        'size': stat.st_size
                    })
                except Exception as e:
                    logger.warning(f"Could not get info for {backup_file.name}: {e}")
        
        except Exception as e:
            logger.error(f"Could not list backups: {e}")
        
        return backups


def init(app: Any) -> AutoBackupManager:
    """
    Initialize the automatic backup system for the application.
    
    Args:
        app: The main application instance
        
    Returns:
        AutoBackupManager instance
    """
    backup_manager = AutoBackupManager(app)
    app.backup_manager = backup_manager
    
    # Check for crash on startup
    crash_backup = backup_manager.check_for_crash()
    if crash_backup:
        _prompt_crash_recovery(app, crash_backup)
    
    # Start auto-backup
    backup_manager.start()
    
    return backup_manager


def _prompt_crash_recovery(app: Any, backup_file: Path) -> None:
    """
    Prompt user to recover from crash backup.
    
    Args:
        app: The main application instance
        backup_file: Path to the backup file
    """
    from tkinter import messagebox
    
    try:
        # Read backup metadata
        backup_data = json.loads(backup_file.read_text(encoding='utf-8'))
        timestamp = backup_data.get('timestamp', 'unknown time')
        original_file = backup_data.get('original_file', 'unsaved draft')
        
        message = (
            f"The application did not close properly last time.\n\n"
            f"A backup was found from {timestamp}.\n"
            f"Original file: {Path(original_file).name if original_file != 'unsaved draft' else 'unsaved draft'}\n\n"
            f"Would you like to restore this backup?"
        )
        
        if messagebox.askyesno("Crash Recovery", message, parent=app):
            _restore_backup(app, backup_file)
            logger.info("Crash recovery backup restored")
        else:
            logger.info("User declined crash recovery")
    
    except Exception as e:
        logger.error(f"Crash recovery prompt failed: {e}")


def _restore_backup(app: Any, backup_file: Path) -> None:
    """
    Restore a backup file.
    
    Args:
        app: The main application instance
        backup_file: Path to the backup file
    """
    try:
        data = json.loads(backup_file.read_text(encoding='utf-8'))
        
        # Restore sections
        if 'sections' in data:
            app.sections_data[:] = data['sections']
        
        # Restore template
        if 'template_name' in data and hasattr(app, 'renderer'):
            app.renderer.set_template(data['template_name'])
        
        # Restore settings
        if 'settings' in data and hasattr(app, 'settings_frame'):
            if hasattr(app.settings_frame, 'load_data'):
                settings = data['settings']
                app.settings_frame.load_data(
                    settings,
                    settings.get('google_api_key', ''),
                    settings.get('openai_api_key', ''),
                    settings.get('events_feed_url', ''),
                )
        
        # Mark as recovered (no current_draft_path to force Save As)
        app.current_draft_path = None
        
        # Refresh UI
        if hasattr(app, 'refresh_listbox_titles'):
            app.refresh_listbox_titles()
        if hasattr(app, 'show_placeholder'):
            app.show_placeholder()
        if hasattr(app, 'update_preview'):
            app.update_preview()
        if hasattr(app, 'show_status_message'):
            app.show_status_message("Backup restored - please save your work")
        
        logger.info(f"Backup restored from {backup_file.name}")
    
    except Exception as e:
        logger.error(f"Failed to restore backup: {e}")
        from tkinter import messagebox
        messagebox.showerror("Recovery Error", f"Could not restore backup: {str(e)}", parent=app)
