"""
Recovery Mode System for Bulletin Builder.

Detects startup crashes and provides recovery options including safe mode loading,
backup restoration, and graceful degradation when the application fails to start normally.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)


class RecoveryManager:
    """
    Manages crash detection and recovery operations.
    
    Provides safe mode loading, backup restoration, and recovery dialogs
    when the application crashes or fails to start normally.
    """
    
    def __init__(self, app, crash_marker_path: Optional[str] = None):
        """
        Initialize the RecoveryManager.
        
        Args:
            app: The main application instance
            crash_marker_path: Optional path to crash marker file (default: ./.crash_marker)
        """
        self.app = app
        self.crash_marker_path = Path(crash_marker_path or ".crash_marker")
        self.safe_mode = False
        self.crash_info: Optional[Dict[str, Any]] = None
        
        logger.info("RecoveryManager initialized")
    
    def detect_crash(self) -> bool:
        """
        Check if a crash marker exists from a previous session.
        
        Returns:
            bool: True if crash detected, False otherwise
        """
        if not self.crash_marker_path.exists():
            logger.debug("No crash marker found - clean startup")
            return False
        
        try:
            # Read crash marker data
            crash_data = json.loads(self.crash_marker_path.read_text(encoding='utf-8'))
            self.crash_info = crash_data
            
            crash_time = crash_data.get('timestamp', 'unknown')
            last_operation = crash_data.get('last_operation', 'unknown')
            
            logger.warning(f"Crash detected! Last session crashed at {crash_time} during: {last_operation}")
            return True
            
        except Exception as e:
            logger.error(f"Error reading crash marker: {e}")
            # If we can't read it, assume crash occurred
            self.crash_info = {
                'timestamp': 'unknown',
                'last_operation': 'unknown',
                'error': str(e)
            }
            return True
    
    def create_crash_marker(self, operation: str = "startup") -> None:
        """
        Create a crash marker file to detect abnormal termination.
        
        Args:
            operation: Description of current operation for crash context
        """
        try:
            crash_data = {
                'timestamp': datetime.now().isoformat(),
                'last_operation': operation,
                'app_version': getattr(self.app, 'version', 'unknown')
            }
            
            self.crash_marker_path.write_text(
                json.dumps(crash_data, indent=2),
                encoding='utf-8'
            )
            logger.debug(f"Crash marker created for operation: {operation}")
            
        except Exception as e:
            logger.error(f"Failed to create crash marker: {e}")
    
    def remove_crash_marker(self) -> None:
        """Remove the crash marker file on graceful exit."""
        try:
            if self.crash_marker_path.exists():
                self.crash_marker_path.unlink()
                logger.debug("Crash marker removed - graceful exit")
        except Exception as e:
            logger.error(f"Failed to remove crash marker: {e}")
    
    def update_crash_marker(self, operation: str) -> None:
        """
        Update the crash marker with current operation.
        
        Args:
            operation: Description of current operation
        """
        if self.crash_marker_path.exists():
            try:
                crash_data = json.loads(self.crash_marker_path.read_text(encoding='utf-8'))
                crash_data['last_operation'] = operation
                crash_data['last_update'] = datetime.now().isoformat()
                
                self.crash_marker_path.write_text(
                    json.dumps(crash_data, indent=2),
                    encoding='utf-8'
                )
            except Exception as e:
                logger.error(f"Failed to update crash marker: {e}")
    
    def enter_safe_mode(self) -> None:
        """
        Enter safe mode with minimal features enabled.
        
        Safe mode disables:
        - Auto-backup system
        - Plugin loading
        - Automatic imports
        - AI features
        - Network operations
        """
        self.safe_mode = True
        self.app.safe_mode = True
        
        logger.warning("Entering SAFE MODE - minimal features enabled")
        
        # Set safe mode flags
        if hasattr(self.app, 'backup_manager'):
            self.app.backup_manager.enabled = False
            logger.info("Auto-backup disabled in safe mode")
        
        # Disable AI features
        if hasattr(self.app, 'ai_helper'):
            self.app.ai_helper.enabled = False
            logger.info("AI features disabled in safe mode")
        
        # Show safe mode banner
        if hasattr(self.app, 'show_safe_mode_banner'):
            self.app.show_safe_mode_banner()
    
    def exit_safe_mode(self) -> None:
        """Exit safe mode and restore full functionality."""
        self.safe_mode = False
        self.app.safe_mode = False
        
        logger.info("Exiting safe mode - full features restored")
        
        # Re-enable features
        if hasattr(self.app, 'backup_manager'):
            self.app.backup_manager.enabled = True
        
        if hasattr(self.app, 'ai_helper'):
            self.app.ai_helper.enabled = True
        
        # Hide safe mode banner
        if hasattr(self.app, 'hide_safe_mode_banner'):
            self.app.hide_safe_mode_banner()
    
    def get_available_backups(self) -> List[Dict[str, Any]]:
        """
        Get list of available backups for recovery.
        
        Returns:
            List of backup info dictionaries with path, timestamp, size
        """
        backups = []
        
        # Check auto-backup directory
        backup_dirs = [
            Path("./backups"),
            Path("./user_drafts/AutoSave")
        ]
        
        for backup_dir in backup_dirs:
            if not backup_dir.exists():
                continue
            
            try:
                for backup_file in sorted(backup_dir.glob("*.json"), reverse=True):
                    try:
                        # Get file info
                        stat = backup_file.stat()
                        timestamp = datetime.fromtimestamp(stat.st_mtime)
                        
                        # Try to read backup to get metadata
                        backup_data = json.loads(backup_file.read_text(encoding='utf-8'))
                        
                        backups.append({
                            'path': backup_file,
                            'name': backup_file.name,
                            'timestamp': timestamp,
                            'size': stat.st_size,
                            'original_file': backup_data.get('original_file'),
                            'sections_count': len(backup_data.get('sections', [])),
                            'directory': backup_dir.name
                        })
                    except Exception as e:
                        logger.debug(f"Skipping invalid backup {backup_file}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error scanning backup directory {backup_dir}: {e}")
        
        return backups
    
    def get_draft_versions(self, draft_name: str) -> List[Dict[str, Any]]:
        """
        Get available versions for a specific draft.
        
        Args:
            draft_name: Name of the draft (without extension)
        
        Returns:
            List of version info dictionaries
        """
        versions = []
        versions_dir = Path(f"./versions/{draft_name}")
        
        if not versions_dir.exists():
            return versions
        
        try:
            for version_file in sorted(versions_dir.glob("*.json"), reverse=True):
                try:
                    stat = version_file.stat()
                    version_data = json.loads(version_file.read_text(encoding='utf-8'))
                    
                    metadata = version_data.get('metadata', {})
                    
                    versions.append({
                        'path': version_file,
                        'name': version_file.stem,
                        'timestamp': datetime.fromisoformat(metadata.get('timestamp', '1970-01-01')),
                        'version_type': metadata.get('version_type', 'manual'),
                        'comment': metadata.get('comment', ''),
                        'size': stat.st_size
                    })
                except Exception as e:
                    logger.debug(f"Skipping invalid version {version_file}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scanning versions directory: {e}")
        
        return versions
    
    def restore_backup(self, backup_path: Path) -> Tuple[bool, str]:
        """
        Restore a backup file to the application.
        
        Args:
            backup_path: Path to the backup file to restore
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            logger.info(f"Attempting to restore backup: {backup_path}")
            
            # Read backup data
            backup_data = json.loads(backup_path.read_text(encoding='utf-8'))
            
            # Restore sections
            if 'sections' in backup_data:
                self.app.sections_data = backup_data['sections']
                logger.info(f"Restored {len(backup_data['sections'])} sections")
            
            # Restore template
            if 'template_name' in backup_data and hasattr(self.app, 'renderer'):
                self.app.renderer.template_name = backup_data['template_name']
                logger.info(f"Restored template: {backup_data['template_name']}")
            
            # Restore settings
            if 'settings' in backup_data and hasattr(self.app, 'settings_frame'):
                try:
                    self.app.settings_frame.load_data(backup_data['settings'])
                    logger.info("Restored settings")
                except Exception as e:
                    logger.warning(f"Could not restore settings: {e}")
            
            # Clear current draft path (force Save As)
            self.app.current_draft_path = None
            
            # Refresh UI
            if hasattr(self.app, 'refresh_listbox_titles'):
                self.app.refresh_listbox_titles()
            
            if hasattr(self.app, 'update_preview'):
                self.app.update_preview()
            
            logger.info("Backup restored successfully")
            return True, f"Backup restored from {backup_path.name}"
            
        except Exception as e:
            error_msg = f"Failed to restore backup: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def start_fresh(self) -> Tuple[bool, str]:
        """
        Start with a fresh, empty bulletin (no data restored).
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            logger.info("Starting fresh - clearing all data")
            
            # Clear sections
            self.app.sections_data = []
            
            # Reset to default template
            if hasattr(self.app, 'renderer'):
                self.app.renderer.template_name = "main_layout.html"
            
            # Clear current draft path
            self.app.current_draft_path = None
            
            # Refresh UI
            if hasattr(self.app, 'refresh_listbox_titles'):
                self.app.refresh_listbox_titles()
            
            if hasattr(self.app, 'show_placeholder'):
                self.app.show_placeholder()
            
            logger.info("Started fresh successfully")
            return True, "Started with empty bulletin"
            
        except Exception as e:
            error_msg = f"Failed to start fresh: {str(e)}"
            logger.error(error_msg)
            return False, error_msg


def init(app) -> None:
    """
    Initialize the recovery system and check for crashes.
    
    Args:
        app: The main application instance
    """
    try:
        # Create recovery manager
        recovery_manager = RecoveryManager(app)
        app.recovery_manager = recovery_manager
        
        # Check for crash
        if recovery_manager.detect_crash():
            # Show recovery dialog
            from bulletin_builder.ui.recovery_dialog import show_recovery_dialog
            show_recovery_dialog(app, recovery_manager)
        else:
            # Create crash marker for this session
            recovery_manager.create_crash_marker("application startup")
        
        logger.info("Recovery system initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize recovery system: {e}")
        # Continue anyway - recovery is optional
