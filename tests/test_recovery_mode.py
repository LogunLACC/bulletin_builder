"""
Tests for recovery mode and crash detection functionality.
"""

import pytest
import json
import time
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from bulletin_builder.app_core.recovery_mode import RecoveryManager


class TestRecoveryManager:
    """Test suite for RecoveryManager class."""
    
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
        app.settings_frame.load_data = Mock()
        app.settings_frame.dump = Mock(return_value={
            "bulletin_title": "Test Bulletin"
        })
        app.current_draft_path = None
        app.refresh_listbox_titles = Mock()
        app.update_preview = Mock()
        app.show_placeholder = Mock()
        app.safe_mode = False
        app.version = "2.0"
        return app
    
    @pytest.fixture
    def recovery_manager(self, mock_app, tmp_path):
        """Create a RecoveryManager instance with temporary directory."""
        crash_marker = tmp_path / ".crash_marker"
        manager = RecoveryManager(mock_app, crash_marker_path=str(crash_marker))
        yield manager
        # Cleanup
        try:
            manager.remove_crash_marker()
        except:
            pass
    
    def test_initialization(self, recovery_manager, tmp_path):
        """Test that RecoveryManager initializes correctly."""
        assert recovery_manager.crash_marker_path == tmp_path / ".crash_marker"
        assert recovery_manager.safe_mode is False
        assert recovery_manager.crash_info is None
    
    def test_create_crash_marker(self, recovery_manager):
        """Test that crash marker is created with correct data."""
        recovery_manager.create_crash_marker("test operation")
        
        assert recovery_manager.crash_marker_path.exists()
        
        # Verify content
        crash_data = json.loads(recovery_manager.crash_marker_path.read_text(encoding='utf-8'))
        assert 'timestamp' in crash_data
        assert crash_data['last_operation'] == "test operation"
        assert crash_data['app_version'] == "2.0"
    
    def test_remove_crash_marker(self, recovery_manager):
        """Test that crash marker is removed successfully."""
        # Create marker first
        recovery_manager.create_crash_marker("test")
        assert recovery_manager.crash_marker_path.exists()
        
        # Remove it
        recovery_manager.remove_crash_marker()
        assert not recovery_manager.crash_marker_path.exists()
    
    def test_detect_crash_returns_false_when_no_marker(self, recovery_manager):
        """Test that crash detection returns False when no marker exists."""
        result = recovery_manager.detect_crash()
        
        assert result is False
        assert recovery_manager.crash_info is None
    
    def test_detect_crash_returns_true_when_marker_exists(self, recovery_manager):
        """Test that crash detection returns True when marker exists."""
        # Create a crash marker
        recovery_manager.create_crash_marker("test crash")
        
        # Create new instance to test detection
        new_manager = RecoveryManager(
            recovery_manager.app,
            crash_marker_path=str(recovery_manager.crash_marker_path)
        )
        
        result = new_manager.detect_crash()
        
        assert result is True
        assert new_manager.crash_info is not None
        assert new_manager.crash_info['last_operation'] == "test crash"
    
    def test_update_crash_marker(self, recovery_manager):
        """Test that crash marker can be updated with new operation."""
        # Create initial marker
        recovery_manager.create_crash_marker("initial operation")
        time.sleep(0.1)  # Small delay to ensure different timestamps
        
        # Update it
        recovery_manager.update_crash_marker("updated operation")
        
        # Verify update
        crash_data = json.loads(recovery_manager.crash_marker_path.read_text(encoding='utf-8'))
        assert crash_data['last_operation'] == "updated operation"
        assert 'last_update' in crash_data
    
    def test_enter_safe_mode(self, recovery_manager, mock_app):
        """Test that safe mode is entered correctly."""
        # Add backup manager and ai_helper
        mock_app.backup_manager = Mock(enabled=True)
        mock_app.ai_helper = Mock(enabled=True)
        mock_app.show_safe_mode_banner = Mock()
        
        recovery_manager.enter_safe_mode()
        
        assert recovery_manager.safe_mode is True
        assert mock_app.safe_mode is True
        assert mock_app.backup_manager.enabled is False
        assert mock_app.ai_helper.enabled is False
        mock_app.show_safe_mode_banner.assert_called_once()
    
    def test_exit_safe_mode(self, recovery_manager, mock_app):
        """Test that safe mode is exited correctly."""
        # Setup safe mode
        mock_app.backup_manager = Mock(enabled=False)
        mock_app.ai_helper = Mock(enabled=False)
        mock_app.hide_safe_mode_banner = Mock()
        recovery_manager.safe_mode = True
        mock_app.safe_mode = True
        
        recovery_manager.exit_safe_mode()
        
        assert recovery_manager.safe_mode is False
        assert mock_app.safe_mode is False
        assert mock_app.backup_manager.enabled is True
        assert mock_app.ai_helper.enabled is True
        mock_app.hide_safe_mode_banner.assert_called_once()
    
    def test_get_available_backups_returns_empty_when_no_backups(self, recovery_manager, tmp_path):
        """Test that get_available_backups returns empty list when no backups exist."""
        # Patch Path to use non-existent directories
        with patch('bulletin_builder.app_core.recovery_mode.Path') as mock_path:
            def path_factory(p):
                if p in ["./backups", "./user_drafts/AutoSave"]:
                    return tmp_path / "nonexistent"
                return Path(p)
            
            mock_path.side_effect = path_factory
            
            backups = recovery_manager.get_available_backups()
        
        assert backups == []
    
    def test_get_available_backups_finds_backups(self, recovery_manager, tmp_path):
        """Test that get_available_backups finds and returns backup files."""
        # Create backup directories
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()
        
        # Create test backups
        for i in range(3):
            backup_file = backups_dir / f"backup_{i}.json"
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'sections': [{"title": f"Section {i}"}],
                'template_name': 'main_layout.html',
                'settings': {},
                'original_file': f'draft_{i}.json'
            }
            backup_file.write_text(json.dumps(backup_data), encoding='utf-8')
            time.sleep(0.01)  # Ensure different mtimes
        
        # Patch the backup directories
        with patch('bulletin_builder.app_core.recovery_mode.Path') as mock_path:
            # Make Path("./backups") return our test directory
            def path_factory(p):
                if p == "./backups":
                    return backups_dir
                elif p == "./user_drafts/AutoSave":
                    return tmp_path / "nonexistent"
                return Path(p)
            
            mock_path.side_effect = path_factory
            
            backups = recovery_manager.get_available_backups()
        
        assert len(backups) == 3
        for backup in backups:
            assert 'path' in backup
            assert 'name' in backup
            assert 'timestamp' in backup
            assert 'size' in backup
            assert 'sections_count' in backup
            assert 'original_file' in backup
    
    def test_get_draft_versions_returns_empty_when_no_versions(self, recovery_manager):
        """Test that get_draft_versions returns empty list when no versions exist."""
        versions = recovery_manager.get_draft_versions("nonexistent_draft")
        
        assert versions == []
    
    def test_get_draft_versions_finds_versions(self, recovery_manager, tmp_path):
        """Test that get_draft_versions finds and returns version files."""
        # Create versions directory
        versions_dir = tmp_path / "versions" / "test_draft"
        versions_dir.mkdir(parents=True)
        
        # Create test versions
        for i in range(2):
            version_file = versions_dir / f"20250101_12000{i}.json"
            version_data = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'version_type': 'manual' if i == 0 else 'auto',
                    'comment': f'Version {i}'
                },
                'sections': []
            }
            version_file.write_text(json.dumps(version_data), encoding='utf-8')
        
        # Patch Path to use our test directory
        with patch('bulletin_builder.app_core.recovery_mode.Path') as mock_path:
            def path_factory(p):
                if isinstance(p, str) and p.startswith("./versions/"):
                    draft_name = p.split("/")[-1]
                    return versions_dir.parent / draft_name
                return Path(p)
            
            mock_path.side_effect = path_factory
            
            versions = recovery_manager.get_draft_versions("test_draft")
        
        assert len(versions) == 2
        for version in versions:
            assert 'path' in version
            assert 'name' in version
            assert 'timestamp' in version
            assert 'version_type' in version
            assert 'comment' in version
    
    def test_restore_backup_success(self, recovery_manager, mock_app, tmp_path):
        """Test that backup restoration works correctly."""
        # Create a backup file
        backup_file = tmp_path / "test_backup.json"
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'sections': [
                {"title": "Section 1", "content": "Content 1"},
                {"title": "Section 2", "content": "Content 2"}
            ],
            'template_name': 'custom_template.html',
            'settings': {
                'bulletin_title': 'Restored Bulletin'
            }
        }
        backup_file.write_text(json.dumps(backup_data), encoding='utf-8')
        
        # Restore backup
        success, message = recovery_manager.restore_backup(backup_file)
        
        assert success is True
        assert "restored" in message.lower()
        assert len(mock_app.sections_data) == 2
        assert mock_app.sections_data[0]['title'] == "Section 1"
        assert mock_app.renderer.template_name == 'custom_template.html'
        assert mock_app.current_draft_path is None
        mock_app.settings_frame.load_data.assert_called_once()
        mock_app.refresh_listbox_titles.assert_called_once()
        mock_app.update_preview.assert_called_once()
    
    def test_restore_backup_handles_missing_file(self, recovery_manager, tmp_path):
        """Test that restore_backup handles missing files gracefully."""
        nonexistent = tmp_path / "nonexistent.json"
        
        success, message = recovery_manager.restore_backup(nonexistent)
        
        assert success is False
        assert "failed" in message.lower()
    
    def test_restore_backup_handles_invalid_json(self, recovery_manager, tmp_path):
        """Test that restore_backup handles invalid JSON gracefully."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("not valid json", encoding='utf-8')
        
        success, message = recovery_manager.restore_backup(invalid_file)
        
        assert success is False
        assert "failed" in message.lower()
    
    def test_start_fresh_success(self, recovery_manager, mock_app):
        """Test that starting fresh clears all data correctly."""
        # Set up some data
        mock_app.sections_data = [{"title": "Test"}]
        mock_app.current_draft_path = "some_path.json"
        
        success, message = recovery_manager.start_fresh()
        
        assert success is True
        assert "empty" in message.lower() or "fresh" in message.lower()
        assert mock_app.sections_data == []
        assert mock_app.renderer.template_name == "main_layout.html"
        assert mock_app.current_draft_path is None
        mock_app.refresh_listbox_titles.assert_called_once()
        mock_app.show_placeholder.assert_called_once()


class TestRecoveryIntegration:
    """Integration tests for recovery mode system."""
    
    def test_init_creates_recovery_manager(self, tmp_path):
        """Test that init() creates and attaches recovery manager to app."""
        from bulletin_builder.app_core.recovery_mode import init
        
        mock_app = Mock()
        mock_app.safe_mode = False
        
        # Create a temp crash marker path
        crash_marker = tmp_path / ".crash_marker"
        
        with patch('bulletin_builder.app_core.recovery_mode.RecoveryManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.detect_crash.return_value = False
            mock_manager_class.return_value = mock_manager
            
            init(mock_app)
            
            assert hasattr(mock_app, 'recovery_manager')
            mock_manager.detect_crash.assert_called_once()
    
    @patch('bulletin_builder.ui.recovery_dialog.show_recovery_dialog')
    def test_init_shows_dialog_on_crash(self, mock_dialog, tmp_path):
        """Test that init() shows recovery dialog when crash detected."""
        from bulletin_builder.app_core.recovery_mode import init
        
        mock_app = Mock()
        mock_app.safe_mode = False
        
        crash_marker = tmp_path / ".crash_marker"
        crash_data = {
            'timestamp': datetime.now().isoformat(),
            'last_operation': 'test',
            'app_version': '2.0'
        }
        crash_marker.write_text(json.dumps(crash_data), encoding='utf-8')
        
        with patch('bulletin_builder.app_core.recovery_mode.RecoveryManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.detect_crash.return_value = True
            mock_manager.crash_marker_path = crash_marker
            mock_manager_class.return_value = mock_manager
            
            init(mock_app)
            
            mock_dialog.assert_called_once_with(mock_app, mock_manager)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
