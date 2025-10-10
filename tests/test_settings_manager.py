"""
Unit tests for the centralized settings manager.
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.bulletin_builder.app_core.settings_manager import (
    ConfigManager,
    AppSettings,
    SMTPConfig,
    APIKeys,
    EventsConfig,
    WindowConfig,
    ConfigurationError,
)


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write("""[smtp]
host = smtp.test.com
port = 587
username = test@example.com
password = testpass
from_addr = Test <test@example.com>
use_tls = true

[google]
api_key = test_google_key

[openai]
api_key = test_openai_key

[events]
feed_url = https://example.com/events.json
auto_import = true

[window]
geometry = 1200x800+100+100
state = normal
confirm_on_close = true
autosave_on_close = false
""")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def config_manager(temp_config_file):
    """Create a ConfigManager with temporary config file."""
    return ConfigManager(temp_config_file)


class TestConfigManager:
    """Test ConfigManager basic functionality."""

    def test_load_all_settings(self, config_manager):
        """Test loading all settings from config file."""
        settings = config_manager.load()
        
        # SMTP
        assert settings.smtp.host == "smtp.test.com"
        assert settings.smtp.port == 587
        assert settings.smtp.username == "test@example.com"
        assert settings.smtp.password == "testpass"
        assert settings.smtp.from_addr == "Test <test@example.com>"
        assert settings.smtp.use_tls is True
        
        # API Keys
        assert settings.api_keys.google == "test_google_key"
        assert settings.api_keys.openai == "test_openai_key"
        
        # Events
        assert settings.events.feed_url == "https://example.com/events.json"
        assert settings.events.auto_import is True
        
        # Window
        assert settings.window.geometry == "1200x800+100+100"
        assert settings.window.state == "normal"
        assert settings.window.confirm_on_close is True
        assert settings.window.autosave_on_close is False

    def test_save_all_settings(self, config_manager):
        """Test saving all settings to config file."""
        # Create new settings
        new_settings = AppSettings(
            smtp=SMTPConfig(
                host="smtp.new.com",
                port=465,
                username="new@example.com",
                password="newpass",
                from_addr="New <new@example.com>",
                use_tls=False,
            ),
            api_keys=APIKeys(
                google="new_google_key",
                openai="new_openai_key",
            ),
            events=EventsConfig(
                feed_url="https://new.com/events",
                auto_import=False,
            ),
            window=WindowConfig(
                geometry="1600x900+50+50",
                state="zoomed",
                confirm_on_close=False,
                autosave_on_close=True,
            ),
        )
        
        # Save and reload
        config_manager.save(new_settings)
        loaded = config_manager.load()
        
        # Verify
        assert loaded.smtp.host == "smtp.new.com"
        assert loaded.smtp.port == 465
        assert loaded.api_keys.google == "new_google_key"
        assert loaded.events.feed_url == "https://new.com/events"
        assert loaded.window.geometry == "1600x900+50+50"

    def test_load_missing_config_file(self):
        """Test loading from non-existent config file returns defaults."""
        manager = ConfigManager("/tmp/nonexistent_config_12345.ini")
        settings = manager.load()
        
        # Should return defaults
        assert settings.smtp.host == "smtp.example.com"
        assert settings.api_keys.google == ""
        assert settings.events.feed_url == ""
        assert settings.window.geometry == ""

    def test_load_invalid_config_format(self):
        """Test loading invalid config file raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("This is not valid INI format\n[[[broken")
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            with pytest.raises(ConfigurationError):
                manager.load()
        finally:
            os.unlink(temp_path)


class TestSMTPConfig:
    """Test SMTP configuration."""

    def test_smtp_is_configured(self):
        """Test SMTP is_configured method."""
        # Configured
        smtp = SMTPConfig(
            host="smtp.gmail.com",
            username="user@gmail.com",
            password="password",
        )
        assert smtp.is_configured() is True
        
        # Not configured (default host)
        smtp = SMTPConfig()
        assert smtp.is_configured() is False
        
        # Missing username
        smtp = SMTPConfig(host="smtp.gmail.com", password="pass")
        assert smtp.is_configured() is False

    def test_get_save_smtp(self, config_manager):
        """Test get and save SMTP config."""
        smtp = config_manager.get_smtp()
        assert smtp.host == "smtp.test.com"
        
        # Modify and save
        smtp.host = "smtp.modified.com"
        smtp.port = 465
        config_manager.save_smtp(smtp)
        
        # Reload and verify
        reloaded = config_manager.get_smtp()
        assert reloaded.host == "smtp.modified.com"
        assert reloaded.port == 465


class TestAPIKeys:
    """Test API keys configuration."""

    def test_api_keys_has_methods(self):
        """Test API keys has_google and has_openai methods."""
        # Has keys
        keys = APIKeys(google="key123", openai="key456")
        assert keys.has_google() is True
        assert keys.has_openai() is True
        
        # No keys
        keys = APIKeys()
        assert keys.has_google() is False
        assert keys.has_openai() is False
        
        # Placeholder keys
        keys = APIKeys(google="REPLACE_ME_GOOGLE_API_KEY")
        assert keys.has_google() is False

    def test_get_save_api_keys(self, config_manager):
        """Test get and save API keys."""
        keys = config_manager.get_api_keys()
        assert keys.google == "test_google_key"
        
        # Modify and save
        keys.google = "modified_google_key"
        keys.openai = "modified_openai_key"
        config_manager.save_api_keys(keys)
        
        # Reload and verify
        reloaded = config_manager.get_api_keys()
        assert reloaded.google == "modified_google_key"
        assert reloaded.openai == "modified_openai_key"

    def test_backward_compatible_api_key_methods(self, config_manager):
        """Test backward compatible load/save methods."""
        # Google
        assert config_manager.get_google_api_key() == "test_google_key"
        config_manager.save_google_api_key("new_google")
        assert config_manager.get_google_api_key() == "new_google"
        
        # OpenAI
        assert config_manager.get_openai_api_key() == "test_openai_key"
        config_manager.save_openai_api_key("new_openai")
        assert config_manager.get_openai_api_key() == "new_openai"


class TestEventsConfig:
    """Test events configuration."""

    def test_events_has_feed_url(self):
        """Test events has_feed_url method."""
        # Has URL
        events = EventsConfig(feed_url="https://example.com/events.json")
        assert events.has_feed_url() is True
        
        # No URL
        events = EventsConfig()
        assert events.has_feed_url() is False
        
        # Example URL
        events = EventsConfig(feed_url="http://example.com/feed")
        assert events.has_feed_url() is False

    def test_get_save_events(self, config_manager):
        """Test get and save events config."""
        events = config_manager.get_events_config()
        assert events.feed_url == "https://example.com/events.json"
        assert events.auto_import is True
        
        # Modify and save
        events.feed_url = "https://new.com/events"
        events.auto_import = False
        config_manager.save_events_config(events)
        
        # Reload and verify
        reloaded = config_manager.get_events_config()
        assert reloaded.feed_url == "https://new.com/events"
        assert reloaded.auto_import is False

    def test_backward_compatible_events_methods(self, config_manager):
        """Test backward compatible load/save methods."""
        # Feed URL
        assert config_manager.get_events_feed_url() == "https://example.com/events.json"
        config_manager.save_events_feed_url("https://new.url")
        assert config_manager.get_events_feed_url() == "https://new.url"
        
        # Auto import
        assert config_manager.get_events_auto_import() is True
        config_manager.save_events_auto_import(False)
        assert config_manager.get_events_auto_import() is False

    def test_strip_quotes_from_feed_url(self):
        """Test that quotes are stripped from feed URLs."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write('[events]\nfeed_url = "https://example.com/feed"\n')
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            url = manager.get_events_feed_url()
            # Should strip quotes
            assert url == "https://example.com/feed"
            assert '"' not in url
        finally:
            os.unlink(temp_path)


class TestWindowConfig:
    """Test window configuration."""

    def test_get_save_window(self, config_manager):
        """Test get and save window config."""
        window = config_manager.get_window_config()
        assert window.geometry == "1200x800+100+100"
        assert window.state == "normal"
        
        # Modify and save
        window.geometry = "1600x900+50+50"
        window.state = "zoomed"
        config_manager.save_window_config(window)
        
        # Reload and verify
        reloaded = config_manager.get_window_config()
        assert reloaded.geometry == "1600x900+50+50"
        assert reloaded.state == "zoomed"

    def test_backward_compatible_window_methods(self, config_manager):
        """Test backward compatible load/save methods."""
        # Window state
        geo, state = config_manager.get_window_state()
        assert geo == "1200x800+100+100"
        assert state == "normal"
        
        config_manager.save_window_state("1024x768+0+0", "zoomed")
        geo, state = config_manager.get_window_state()
        assert geo == "1024x768+0+0"
        assert state == "zoomed"
        
        # Confirm on close
        assert config_manager.get_confirm_on_close() is True
        config_manager.save_confirm_on_close(False)
        assert config_manager.get_confirm_on_close() is False
        
        # Autosave on close
        assert config_manager.get_autosave_on_close() is False
        config_manager.save_autosave_on_close(True)
        assert config_manager.get_autosave_on_close() is True


class TestValidation:
    """Test configuration validation."""

    def test_validate_valid_config(self, config_manager):
        """Test validation of valid configuration."""
        issues = config_manager.validate()
        assert len(issues) == 0

    def test_validate_smtp_missing_credentials(self):
        """Test validation catches missing SMTP credentials."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[smtp]\nhost = smtp.gmail.com\n")
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            issues = manager.validate()
            
            assert len(issues) > 0
            assert any("username" in issue.lower() for issue in issues)
            assert any("password" in issue.lower() for issue in issues)
        finally:
            os.unlink(temp_path)

    def test_validate_invalid_events_url(self):
        """Test validation catches invalid events URL."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[events]\nfeed_url = not_a_url\n")
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            issues = manager.validate()
            
            assert len(issues) > 0
            assert any("feed_url" in issue for issue in issues)
        finally:
            os.unlink(temp_path)

    def test_validate_invalid_window_geometry(self):
        """Test validation catches invalid window geometry."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[window]\ngeometry = invalid\n")
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            issues = manager.validate()
            
            assert len(issues) > 0
            assert any("geometry" in issue.lower() for issue in issues)
        finally:
            os.unlink(temp_path)

    def test_validate_invalid_window_state(self):
        """Test validation catches invalid window state."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[window]\nstate = invalid_state\n")
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            issues = manager.validate()
            
            assert len(issues) > 0
            assert any("state" in issue.lower() for issue in issues)
        finally:
            os.unlink(temp_path)


class TestUtilityMethods:
    """Test utility methods."""

    def test_export_dict(self, config_manager):
        """Test exporting settings as dictionary."""
        settings_dict = config_manager.export_dict()
        
        assert 'smtp' in settings_dict
        assert 'api_keys' in settings_dict
        assert 'events' in settings_dict
        assert 'window' in settings_dict
        
        assert settings_dict['smtp']['host'] == "smtp.test.com"
        assert settings_dict['api_keys']['google'] == "test_google_key"

    def test_reset_to_defaults(self, config_manager):
        """Test resetting configuration to defaults."""
        # Verify we have non-default values
        settings = config_manager.load()
        assert settings.smtp.host != "smtp.example.com"
        
        # Reset
        config_manager.reset_to_defaults()
        
        # Verify defaults
        settings = config_manager.load()
        assert settings.smtp.host == "smtp.example.com"
        assert settings.api_keys.google == ""
        assert settings.events.feed_url == ""


class TestGlobalInstance:
    """Test global instance management."""

    def test_get_config_manager(self):
        """Test getting global ConfigManager instance."""
        from src.bulletin_builder.app_core.settings_manager import get_config_manager
        
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        
        # Should return same instance
        assert manager1 is manager2

    def test_get_config_manager_different_path(self):
        """Test getting ConfigManager with different path creates new instance."""
        from src.bulletin_builder.app_core.settings_manager import get_config_manager
        
        manager1 = get_config_manager("config1.ini")
        manager2 = get_config_manager("config2.ini")
        
        # Should return different instances
        assert manager1 is not manager2
        assert str(manager1.config_path) != str(manager2.config_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
