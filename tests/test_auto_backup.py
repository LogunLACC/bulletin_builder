"""
Tests for automatic draft backup and crash recovery functionality.
"""

import pytest
import json
import time
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from bulletin_builder.app_core.auto_backup import AutoBackupManager, init


class TestAutoBackupManager:
    """Test suite for AutoBackupManager class."""
    
    @pytest.fixture
    def mock_app(self):
        """Create a mock application instance."""
        app = Mock()
        app.sections_data = [
            {"title": "Test Section", "content": "Test content"}
        ]
        app.renderer = Mock()
        app.renderer.template_name = "main_layout.html"
        app.settings_frame = Mock()
        app.settings_frame.dump = Mock(return_value={
            "bulletin_title": "Test Bulletin",
            "primary_color": "#0066cc"
        })
        app.current_draft_path = None
        app.after = Mock(return_value="timer_id_123")
        app.after_cancel = Mock()
        return app
    
    @pytest.fixture
    def backup_manager(self, mock_app, tmp_path):
        """Create an AutoBackupManager instance with temporary directory."""
        manager = AutoBackupManager(mock_app, backup_dir=str(tmp_path / "backups"))
        yield manager
        # Cleanup
        try:
            manager.stop()
        except:
            pass
    
    def test_initialization(self, backup_manager, tmp_path):
        """Test that AutoBackupManager initializes correctly."""
        assert backup_manager.backup_dir == tmp_path / "backups"
        assert backup_manager.backup_dir.exists()
        assert backup_manager.max_backups == 10
        assert backup_manager.backup_interval_ms == 120000  # 2 minutes
        assert backup_manager.auto_save_id is None
    
    def test_start_creates_crash_marker(self, backup_manager):
        """Test that start() creates a crash detection marker file."""
        backup_manager.start()
        
        assert backup_manager.crash_file.exists()
        content = backup_manager.crash_file.read_text(encoding='utf-8')
        # Should contain a timestamp
        assert len(content) > 0
    
    def test_start_schedules_auto_save(self, backup_manager, mock_app):
        """Test that start() schedules automatic backups."""
        backup_manager.start()
        
        # Should have called app.after to schedule backup
        mock_app.after.assert_called_once()
        args = mock_app.after.call_args[0]
        assert args[0] == 120000  # 2 minute interval
        assert callable(args[1])  # Callback function
    
    def test_collect_draft_data(self, backup_manager, mock_app):
        """Test draft data collection for backup."""
        data = backup_manager._collect_draft_data()
        
        assert 'timestamp' in data
        assert 'sections' in data
        assert 'template_name' in data
        assert 'settings' in data
        
        assert data['sections'] == mock_app.sections_data
        assert data['template_name'] == "main_layout.html"
        assert data['settings']['bulletin_title'] == "Test Bulletin"
    
    def test_collect_draft_data_with_file_path(self, backup_manager, mock_app):
        """Test that original file path is included when available."""
        mock_app.current_draft_path = Path("user_drafts/my_draft.json")
        
        data = backup_manager._collect_draft_data()
        
        assert 'original_file' in data
        assert "my_draft.json" in data['original_file']
    
    def test_perform_auto_save_creates_backup(self, backup_manager):
        """Test that auto-save creates a backup file."""
        backup_manager._perform_auto_save()
        
        # Should have created a backup file
        backup_files = list(backup_manager.backup_dir.glob("auto_backup_*.json"))
        assert len(backup_files) == 1
        
        # Verify backup content
        backup_data = json.loads(backup_files[0].read_text(encoding='utf-8'))
        assert 'timestamp' in backup_data
        assert 'sections' in backup_data
        assert len(backup_data['sections']) > 0
    
    def test_perform_auto_save_skips_empty_content(self, backup_manager, mock_app):
        """Test that auto-save skips backup when no content exists."""
        mock_app.sections_data = []
        
        backup_manager._perform_auto_save()
        
        # Should not create backup file
        backup_files = list(backup_manager.backup_dir.glob("auto_backup_*.json"))
        assert len(backup_files) == 0
    
    def test_backup_rotation(self, backup_manager):
        """Test that old backups are removed when exceeding max_backups."""
        backup_manager.max_backups = 3
        
        # Create more backups than the limit with unique timestamps
        for i in range(5):
            # Manually create backup files with different timestamps
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{i:03d}"
            backup_file = backup_manager.backup_dir / f"auto_backup_{timestamp}.json"
            backup_data = backup_manager._collect_draft_data()
            backup_file.write_text(json.dumps(backup_data, indent=2), encoding='utf-8')
            time.sleep(0.01)  # Small delay to ensure different mtime
        
        # Run rotation
        backup_manager._rotate_backups()
        
        # Should only keep the most recent 3
        backup_files = list(backup_manager.backup_dir.glob("auto_backup_*.json"))
        assert len(backup_files) == 3
    
    def test_crash_marker_removal_on_graceful_exit(self, backup_manager):
        """Test that crash marker is removed on graceful exit."""
        backup_manager.start()
        assert backup_manager.crash_file.exists()
        
        backup_manager._on_graceful_exit()
        
        assert not backup_manager.crash_file.exists()
    
    def test_check_for_crash_returns_none_when_no_crash(self, backup_manager):
        """Test crash detection returns None when no crash occurred."""
        # No crash marker exists
        result = backup_manager.check_for_crash()
        
        assert result is None
    
    def test_check_for_crash_returns_backup_when_crash_detected(self, backup_manager):
        """Test crash detection returns backup file when crash occurred."""
        # Create a backup
        backup_manager._perform_auto_save()
        
        # Simulate crash by creating crash marker
        backup_manager._create_crash_marker()
        
        # Check for crash
        result = backup_manager.check_for_crash()
        
        assert result is not None
        assert result.exists()
        assert "auto_backup_" in result.name
    
    def test_get_available_backups(self, backup_manager):
        """Test retrieval of available backup files with metadata."""
        # Create multiple backups with unique timestamps
        for i in range(3):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{i:03d}"
            backup_file = backup_manager.backup_dir / f"auto_backup_{timestamp}.json"
            backup_data = backup_manager._collect_draft_data()
            backup_file.write_text(json.dumps(backup_data, indent=2), encoding='utf-8')
            time.sleep(0.01)
        
        backups = backup_manager.get_available_backups()
        
        assert len(backups) == 3
        for backup_info in backups:
            assert 'path' in backup_info
            assert 'name' in backup_info
            assert 'timestamp' in backup_info
            assert 'size' in backup_info
            assert isinstance(backup_info['timestamp'], datetime)
    
    def test_stop_cancels_auto_save_timer(self, backup_manager, mock_app):
        """Test that stop() cancels the auto-save timer."""
        backup_manager.start()
        backup_manager.auto_save_id = "timer_id_123"
        
        backup_manager.stop()
        
        mock_app.after_cancel.assert_called_once_with("timer_id_123")
        assert backup_manager.auto_save_id is None


class TestAutoBackupIntegration:
    """Integration tests for auto-backup system."""
    
    @pytest.fixture
    def mock_app(self):
        """Create a mock application instance."""
        app = Mock()
        app.sections_data = [{"title": "Section 1", "content": "Content 1"}]
        app.renderer = Mock()
        app.renderer.template_name = "main_layout.html"
        app.settings_frame = Mock()
        app.settings_frame.dump = Mock(return_value={})
        app.after = Mock(return_value="timer_id")
        app.after_cancel = Mock()
        return app
    
    def test_init_creates_backup_manager(self, mock_app, tmp_path):
        """Test that init() creates and attaches backup manager to app."""
        with patch('bulletin_builder.app_core.auto_backup.AutoBackupManager') as MockBackupManager:
            mock_manager = Mock()
            MockBackupManager.return_value = mock_manager
            
            result = init(mock_app)
            
            # Should create manager and attach to app
            assert hasattr(mock_app, 'backup_manager')
            assert mock_app.backup_manager == mock_manager
            
            # Should start the backup system
            mock_manager.start.assert_called_once()
    
    @patch('bulletin_builder.app_core.auto_backup._prompt_crash_recovery')
    def test_init_prompts_crash_recovery(self, mock_prompt, mock_app, tmp_path):
        """Test that init() prompts for crash recovery when crash detected."""
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        
        # Create a crash scenario
        crash_file = backup_dir / ".crash_detected"
        crash_file.write_text(datetime.now().isoformat())
        
        backup_file = backup_dir / "auto_backup_20250101_120000.json"
        backup_file.write_text(json.dumps({
            'timestamp': datetime.now().isoformat(),
            'sections': [{"title": "Test"}],
            'template_name': 'main_layout.html'
        }))
        
        last_backup = backup_dir / ".last_backup.json"
        last_backup.write_text(str(backup_file))
        
        # Initialize with crash detection
        manager = AutoBackupManager(mock_app, backup_dir=str(backup_dir))
        manager.check_for_crash()
        
        # Verify crash was detected
        crash_backup = manager.check_for_crash()
        assert crash_backup is not None


class TestBackupRecovery:
    """Test backup recovery functionality."""
    
    @pytest.fixture
    def mock_app(self):
        """Create a mock application for recovery tests."""
        app = Mock()
        app.sections_data = []
        app.renderer = Mock()
        app.settings_frame = Mock()
        app.settings_frame.load_data = Mock()
        app.refresh_listbox_titles = Mock()
        app.show_placeholder = Mock()
        app.update_preview = Mock()
        app.show_status_message = Mock()
        return app
    
    def test_restore_backup_restores_sections(self, mock_app, tmp_path):
        """Test that restore_backup correctly restores draft sections."""
        from bulletin_builder.app_core.auto_backup import _restore_backup
        
        # Create a backup file
        backup_file = tmp_path / "test_backup.json"
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'sections': [
                {"title": "Section 1", "content": "Content 1"},
                {"title": "Section 2", "content": "Content 2"}
            ],
            'template_name': 'main_layout.html',
            'settings': {
                'bulletin_title': 'Recovered Bulletin',
                'primary_color': '#ff0000'
            }
        }
        backup_file.write_text(json.dumps(backup_data), encoding='utf-8')
        
        # Restore backup
        _restore_backup(mock_app, backup_file)
        
        # Verify sections were restored
        assert len(mock_app.sections_data) == 2
        assert mock_app.sections_data[0]['title'] == "Section 1"
        
        # Verify UI refresh was called
        mock_app.refresh_listbox_titles.assert_called_once()
        mock_app.show_placeholder.assert_called_once()
        mock_app.update_preview.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
