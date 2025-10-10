"""
Unit tests for CLI configuration validation command.
"""

import pytest
import tempfile
import os
from pathlib import Path


class TestCLIValidation:
    """Test CLI configuration validation functionality."""

    def test_validate_valid_config(self):
        """Test validation of a valid config file."""
        from bulletin_builder.cli import validate_config_command
        
        # Create a valid config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[meta]\nversion = 2.0\n")
            f.write("[smtp]\n")
            f.write("host = smtp.gmail.com\n")
            f.write("port = 587\n")
            f.write("username = user@example.com\n")
            f.write("password = securepass123\n")
            f.write("from_addr = Bulletin <user@example.com>\n")
            f.write("use_tls = true\n")
            temp_path = f.name
        
        try:
            # Should return 0 (success)
            exit_code = validate_config_command(temp_path)
            assert exit_code == 0
        finally:
            os.unlink(temp_path)

    def test_validate_config_with_errors(self):
        """Test validation of config file with errors."""
        from bulletin_builder.cli import validate_config_command
        
        # Create config with missing SMTP credentials
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[meta]\nversion = 2.0\n")
            f.write("[smtp]\n")
            f.write("host = smtp.gmail.com\n")
            f.write("port = 587\n")
            # Missing username and password
            temp_path = f.name
        
        try:
            # Should return 1 (errors found)
            exit_code = validate_config_command(temp_path)
            assert exit_code == 1
        finally:
            os.unlink(temp_path)

    def test_validate_config_with_warnings_only(self):
        """Test validation of config file with only warnings."""
        from bulletin_builder.cli import validate_config_command
        
        # Create config with HTTP URL (warning, not error)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[meta]\nversion = 2.0\n")
            f.write("[smtp]\n")
            f.write("host = smtp.gmail.com\n")
            f.write("port = 587\n")
            f.write("username = user@example.com\n")
            f.write("password = securepass123\n")
            f.write("[events]\n")
            f.write("feed_url = http://example.com/events.ics\n")  # HTTP instead of HTTPS
            temp_path = f.name
        
        try:
            # Should return 0 (warnings don't fail validation)
            exit_code = validate_config_command(temp_path)
            assert exit_code == 0
        finally:
            os.unlink(temp_path)

    def test_validate_missing_config(self):
        """Test validation of non-existent config file."""
        from bulletin_builder.cli import validate_config_command
        
        # Use a path that doesn't exist
        exit_code = validate_config_command("nonexistent_config_file.ini")
        
        # Should return 2 (file not found)
        assert exit_code == 2

    def test_validate_old_version_config(self):
        """Test validation of config that needs migration."""
        from bulletin_builder.cli import validate_config_command
        
        # Create old version config (1.0)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            # No [meta] section (version 1.0)
            f.write("[smtp]\n")
            f.write("host = smtp.gmail.com\n")
            f.write("port = 587\n")
            f.write("username = user@example.com\n")
            f.write("password = securepass123\n")
            temp_path = f.name
        
        try:
            # Should automatically migrate and validate
            exit_code = validate_config_command(temp_path)
            
            # Should succeed (migration happens automatically)
            assert exit_code == 0
            
            # Config should now be version 2.0
            from bulletin_builder.app_core.settings_manager import ConfigManager
            import configparser
            parser = configparser.ConfigParser()
            parser.read(temp_path)
            assert parser.get("meta", "version") == "2.0"
            
            # Backup should have been created
            backup_files = list(Path(temp_path).parent.glob("*.backup_*"))
            assert len(backup_files) > 0
            
            # Clean up backup
            for backup in backup_files:
                backup.unlink()
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
