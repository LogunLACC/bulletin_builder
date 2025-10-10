"""
Unit tests for the centralized settings manager.
"""

import pytest
import tempfile
import os
from pathlib import Path
from bulletin_builder.app_core.settings_manager import (
    ConfigManager,
    AppSettings,
    SMTPConfig,
    APIKeys,
    EventsConfig,
    WindowConfig,
    ConfigurationError,
    ENV_PREFIX,
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
        # Config has valid SMTP settings, should have no errors
        errors = [msg for sev, msg in issues if sev == "ERROR"]
        assert len(errors) == 0

    def test_validate_smtp_missing_credentials(self):
        """Test validation catches missing SMTP credentials."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[smtp]\nhost = smtp.gmail.com\n")
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            issues = manager.validate()
            
            assert len(issues) > 0
            # Check for errors (not just warnings)
            errors = [msg for sev, msg in issues if sev == "ERROR"]
            assert any("username" in msg.lower() for msg in errors)
            assert any("password" in msg.lower() for msg in errors)
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
            messages = [msg for sev, msg in issues]
            assert any("feed_url" in msg for msg in messages)
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
            messages = [msg for sev, msg in issues]
            assert any("geometry" in msg.lower() for msg in messages)
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
            messages = [msg for sev, msg in issues]
            assert any("state" in msg.lower() for msg in messages)
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
        from bulletin_builder.app_core.settings_manager import get_config_manager
        
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        
        # Should return same instance
        assert manager1 is manager2

    def test_get_config_manager_different_path(self):
        """Test getting ConfigManager with different path creates new instance."""
        from bulletin_builder.app_core.settings_manager import get_config_manager
        
        manager1 = get_config_manager("config1.ini")
        manager2 = get_config_manager("config2.ini")
        
        # Should return different instances
        assert manager1 is not manager2
        assert str(manager1.config_path) != str(manager2.config_path)


class TestEnvironmentVariables:
    """Test environment variable overrides."""

    def test_smtp_env_override(self, monkeypatch, temp_config_file):
        """Test SMTP configuration from environment variables."""
        # Set environment variables
        monkeypatch.setenv(f"{ENV_PREFIX}SMTP_HOST", "smtp.env.com")
        monkeypatch.setenv(f"{ENV_PREFIX}SMTP_PORT", "465")
        monkeypatch.setenv(f"{ENV_PREFIX}SMTP_USERNAME", "env@example.com")
        monkeypatch.setenv(f"{ENV_PREFIX}SMTP_PASSWORD", "envpass")
        monkeypatch.setenv(f"{ENV_PREFIX}SMTP_USE_TLS", "false")
        
        manager = ConfigManager(temp_config_file, use_env_vars=True)
        smtp = manager.get_smtp()
        
        # Environment variables should override config file
        assert smtp.host == "smtp.env.com"
        assert smtp.port == 465
        assert smtp.username == "env@example.com"
        assert smtp.password == "envpass"
        assert smtp.use_tls is False

    def test_api_keys_env_override(self, monkeypatch, temp_config_file):
        """Test API keys from environment variables."""
        monkeypatch.setenv(f"{ENV_PREFIX}GOOGLE_API_KEY", "env_google_key")
        monkeypatch.setenv(f"{ENV_PREFIX}OPENAI_API_KEY", "env_openai_key")
        
        manager = ConfigManager(temp_config_file, use_env_vars=True)
        keys = manager.get_api_keys()
        
        assert keys.google == "env_google_key"
        assert keys.openai == "env_openai_key"

    def test_events_env_override(self, monkeypatch, temp_config_file):
        """Test events configuration from environment variables."""
        monkeypatch.setenv(f"{ENV_PREFIX}EVENTS_FEED_URL", "https://env.com/events")
        monkeypatch.setenv(f"{ENV_PREFIX}EVENTS_AUTO_IMPORT", "false")
        
        manager = ConfigManager(temp_config_file, use_env_vars=True)
        events = manager.get_events_config()
        
        assert events.feed_url == "https://env.com/events"
        assert events.auto_import is False

    def test_env_bool_parsing(self, monkeypatch, temp_config_file):
        """Test boolean environment variable parsing."""
        test_cases = [
            ("true", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("FALSE", False),
            ("0", False),
            ("no", False),
            ("off", False),
        ]
        
        for value, expected in test_cases:
            monkeypatch.setenv(f"{ENV_PREFIX}SMTP_USE_TLS", value)
            manager = ConfigManager(temp_config_file, use_env_vars=True)
            smtp = manager.get_smtp()
            assert smtp.use_tls is expected, f"Failed for value: {value}"

    def test_env_disabled(self, monkeypatch, temp_config_file):
        """Test that environment variables are ignored when disabled."""
        monkeypatch.setenv(f"{ENV_PREFIX}SMTP_HOST", "smtp.env.com")
        
        manager = ConfigManager(temp_config_file, use_env_vars=False)
        smtp = manager.get_smtp()
        
        # Should use config file value, not environment
        assert smtp.host == "smtp.test.com"
        assert smtp.host != "smtp.env.com"

    def test_get_supported_env_vars(self, config_manager):
        """Test getting list of supported environment variables."""
        env_vars = config_manager.get_supported_env_vars()
        
        # Check some key variables are documented
        assert "BULLETIN_SMTP_HOST" in env_vars
        assert "BULLETIN_GOOGLE_API_KEY" in env_vars
        assert "BULLETIN_EVENTS_FEED_URL" in env_vars
        
        # Check descriptions are present
        for var, desc in env_vars.items():
            assert isinstance(desc, str)
            assert len(desc) > 0


class TestEnhancedValidation:
    """Test enhanced validation with severity levels."""

    def test_validate_returns_tuples(self, config_manager):
        """Test that validate returns (severity, message) tuples."""
        issues = config_manager.validate()
        
        # Should return list of tuples
        for issue in issues:
            assert isinstance(issue, tuple)
            assert len(issue) == 2
            severity, message = issue
            assert severity in ["ERROR", "WARNING"]
            assert isinstance(message, str)

    def test_validate_smtp_tls_port_mismatch(self):
        """Test validation catches TLS/SSL port mismatches."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            # Port 465 with TLS (should use SSL)
            f.write("[smtp]\nhost = smtp.test.com\nport = 465\nuse_tls = true\n")
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            issues = manager.validate()
            
            # Should have warning about port/TLS mismatch
            assert any("465" in msg and "SSL" in msg for sev, msg in issues)
        finally:
            os.unlink(temp_path)

    def test_validate_placeholder_values(self):
        """Test validation catches placeholder values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[google]\napi_key = REPLACE_ME_GOOGLE_API_KEY\n")
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            issues = manager.validate()
            
            # Should have warning about placeholder
            assert any("placeholder" in msg.lower() for sev, msg in issues)
        finally:
            os.unlink(temp_path)

    def test_validate_insecure_http(self):
        """Test validation warns about HTTP (not HTTPS)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[events]\nfeed_url = http://example.com/events\n")
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            issues = manager.validate()
            
            # Should have warning about HTTP
            assert any("HTTP" in msg and "unencrypted" in msg.lower() for sev, msg in issues)
        finally:
            os.unlink(temp_path)

    def test_validate_window_size_warnings(self):
        """Test validation warns about unusual window sizes."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            # Very small window
            f.write("[window]\ngeometry = 400x300+0+0\n")
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            issues = manager.validate()
            
            # Should have warning about small size
            assert any("small" in msg.lower() for sev, msg in issues)
        finally:
            os.unlink(temp_path)

    def test_validate_and_report(self, config_manager, caplog):
        """Test validate_and_report method."""
        import logging
        caplog.set_level(logging.INFO)
        
        result = config_manager.validate_and_report()
        
        # Should return True (no errors in test config)
        assert result is True


class TestConfigMigration:
    """Test configuration migration system."""

    def test_get_config_version(self):
        """Test getting config version."""
        import configparser
        from bulletin_builder.app_core.settings_manager import ConfigMigration
        
        # Config with version
        parser = configparser.ConfigParser()
        parser.add_section("meta")
        parser.set("meta", "version", "1.5")
        
        version = ConfigMigration.get_config_version(parser)
        assert version == "1.5"
        
        # Config without version (defaults to 1.0)
        parser2 = configparser.ConfigParser()
        version2 = ConfigMigration.get_config_version(parser2)
        assert version2 == "1.0"

    def test_set_config_version(self):
        """Test setting config version."""
        import configparser
        from bulletin_builder.app_core.settings_manager import ConfigMigration
        
        parser = configparser.ConfigParser()
        ConfigMigration.set_config_version(parser, "2.5")
        
        assert parser.has_section("meta")
        assert parser.get("meta", "version") == "2.5"

    def test_needs_migration(self):
        """Test checking if migration is needed."""
        import configparser
        from bulletin_builder.app_core.settings_manager import ConfigMigration
        
        # Old version needs migration
        parser1 = configparser.ConfigParser()
        parser1.add_section("meta")
        parser1.set("meta", "version", "1.0")
        assert ConfigMigration.needs_migration(parser1) is True
        
        # Current version doesn't need migration
        parser2 = configparser.ConfigParser()
        parser2.add_section("meta")
        parser2.set("meta", "version", ConfigMigration.CURRENT_VERSION)
        assert ConfigMigration.needs_migration(parser2) is False

    def test_migrate_1_0_to_2_0(self):
        """Test migration from version 1.0 to 2.0."""
        import configparser
        from bulletin_builder.app_core.settings_manager import ConfigMigration
        
        # Create a 1.0 config
        parser = configparser.ConfigParser()
        parser.add_section("smtp")
        parser.set("smtp", "host", "smtp.example.com")
        
        parser.add_section("window")
        parser.set("window", "geometry", "1024x768+0+0")
        parser.set("window", "confirm_on_close", "TRUE")  # Uppercase boolean
        
        # Apply migration
        migrated = ConfigMigration._migrate_1_0_to_2_0(parser)
        
        # Check meta section was added
        assert migrated.has_section("meta")
        
        # Check autosave_on_close was added
        assert migrated.has_option("window", "autosave_on_close")
        assert migrated.get("window", "autosave_on_close") == "true"
        
        # Check boolean normalization
        assert migrated.get("window", "confirm_on_close") == "true"

    def test_full_migration_process(self):
        """Test complete migration process."""
        import configparser
        from bulletin_builder.app_core.settings_manager import ConfigMigration
        
        # Create a 1.0 config
        parser = configparser.ConfigParser()
        parser.add_section("smtp")
        parser.set("smtp", "host", "smtp.gmail.com")
        parser.set("smtp", "use_tls", "YES")  # Mixed case boolean
        
        # Should need migration
        assert ConfigMigration.needs_migration(parser) is True
        
        # Perform migration
        migrated = ConfigMigration.migrate(parser)
        
        # Should now be at current version
        version = ConfigMigration.get_config_version(migrated)
        assert version == ConfigMigration.CURRENT_VERSION
        
        # Should not need migration anymore
        assert ConfigMigration.needs_migration(migrated) is False
        
        # Check boolean was normalized
        assert migrated.get("smtp", "use_tls") == "true"

    def test_backup_config(self):
        """Test config backup creation."""
        from bulletin_builder.app_core.settings_manager import ConfigMigration
        
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[smtp]\nhost = smtp.example.com\n")
            temp_path = Path(f.name)
        
        try:
            # Create backup
            backup_path = ConfigMigration.backup_config(temp_path)
            
            # Backup should exist
            assert backup_path.exists()
            assert "backup" in backup_path.name
            
            # Backup should have same content
            assert backup_path.read_text() == temp_path.read_text()
            
            # Clean up backup
            backup_path.unlink()
        finally:
            temp_path.unlink()

    def test_automatic_migration_on_load(self):
        """Test that ConfigManager automatically migrates old configs."""
        import configparser
        
        # Create a 1.0 config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[smtp]\nhost = smtp.example.com\nuse_tls = TRUE\n")
            f.write("[window]\ngeometry = 1024x768+0+0\n")
            temp_path = f.name
        
        try:
            # Load config (should trigger migration)
            manager = ConfigManager(temp_path)
            settings = manager.load()
            
            # Config should have been migrated
            parser = configparser.ConfigParser()
            parser.read(temp_path)
            
            # Should have version
            assert parser.has_section("meta")
            version = parser.get("meta", "version")
            assert version == "2.0"
            
            # Should have autosave_on_close
            assert parser.has_option("window", "autosave_on_close")
            
            # Backup file should exist
            backup_files = list(Path(temp_path).parent.glob("*.backup_*"))
            assert len(backup_files) > 0
            
            # Clean up backup
            for backup in backup_files:
                backup.unlink()
        finally:
            os.unlink(temp_path)

    def test_save_includes_version(self):
        """Test that saving config always includes version."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            temp_path = f.name
        
        try:
            # Save config
            manager = ConfigManager(temp_path)
            settings = AppSettings()
            manager.save(settings)
            
            # Read back
            import configparser
            parser = configparser.ConfigParser()
            parser.read(temp_path)
            
            # Should have version
            assert parser.has_section("meta")
            assert parser.get("meta", "version") == "2.0"
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
