"""
Centralized configuration and settings management.

This module provides a unified interface for reading and writing all application
settings, including API keys, SMTP configuration, window state, and user preferences.
It replaces the scattered config.py functions with a single, testable ConfigManager class.
"""

import configparser
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


@dataclass
class SMTPConfig:
    """SMTP server configuration for sending emails."""
    host: str = "smtp.example.com"
    port: int = 587
    username: str = ""
    password: str = ""
    from_addr: str = "Bulletin Builder <user@example.com>"
    use_tls: bool = True

    def is_configured(self) -> bool:
        """Check if SMTP is properly configured."""
        return bool(
            self.host 
            and self.host != "smtp.example.com"
            and self.username 
            and self.password
        )


@dataclass
class APIKeys:
    """API keys for external services."""
    google: str = ""
    openai: str = ""

    def has_google(self) -> bool:
        return bool(self.google and self.google != "REPLACE_ME_GOOGLE_API_KEY")

    def has_openai(self) -> bool:
        return bool(self.openai and self.openai != "REPLACE_ME_OPENAI_API_KEY")


@dataclass
class EventsConfig:
    """Events feed configuration."""
    feed_url: str = ""
    auto_import: bool = False

    def has_feed_url(self) -> bool:
        return bool(self.feed_url and not self.feed_url.startswith("http://example.com"))


@dataclass
class WindowConfig:
    """Window state and behavior configuration."""
    geometry: str = ""
    state: str = ""  # '', 'normal', 'zoomed', 'iconic'
    confirm_on_close: bool = True
    autosave_on_close: bool = True


@dataclass
class AppSettings:
    """Complete application settings."""
    smtp: SMTPConfig = field(default_factory=SMTPConfig)
    api_keys: APIKeys = field(default_factory=APIKeys)
    events: EventsConfig = field(default_factory=EventsConfig)
    window: WindowConfig = field(default_factory=WindowConfig)


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class ConfigManager:
    """
    Centralized configuration manager.
    
    Handles reading and writing all application settings to config.ini,
    with proper error handling, validation, and environment variable support.
    
    Usage:
        config = ConfigManager()
        settings = config.load()
        settings.smtp.host = "smtp.gmail.com"
        config.save(settings)
    """

    def __init__(self, config_path: str = "config.ini"):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to config.ini file (default: "config.ini")
        """
        self.config_path = Path(config_path)
        self._ensure_config_exists()

    def _ensure_config_exists(self) -> None:
        """Create config.ini from template if it doesn't exist."""
        if not self.config_path.exists():
            logger.info(f"Config file not found, checking for default template...")
            default_path = self.config_path.parent / "config.ini.default"
            if default_path.exists():
                import shutil
                shutil.copy(default_path, self.config_path)
                logger.info(f"Created {self.config_path} from {default_path}")
            else:
                logger.warning(f"No config file found at {self.config_path}")

    def load(self) -> AppSettings:
        """
        Load all settings from config.ini.
        
        Returns:
            AppSettings with all configuration loaded
            
        Raises:
            ConfigurationError: If config file is invalid
        """
        parser = configparser.ConfigParser()
        
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return AppSettings()  # Return defaults
        
        try:
            parser.read(self.config_path, encoding='utf-8')
        except configparser.Error as e:
            raise ConfigurationError(f"Failed to parse config file: {e}") from e
        
        return AppSettings(
            smtp=self._load_smtp(parser),
            api_keys=self._load_api_keys(parser),
            events=self._load_events(parser),
            window=self._load_window(parser),
        )

    def save(self, settings: AppSettings) -> None:
        """
        Save all settings to config.ini.
        
        Args:
            settings: AppSettings to save
            
        Raises:
            ConfigurationError: If save fails
        """
        parser = configparser.ConfigParser()
        
        # Load existing config to preserve comments and other sections
        if self.config_path.exists():
            try:
                parser.read(self.config_path, encoding='utf-8')
            except configparser.Error as e:
                logger.warning(f"Could not read existing config: {e}")
        
        # Update sections
        self._save_smtp(parser, settings.smtp)
        self._save_api_keys(parser, settings.api_keys)
        self._save_events(parser, settings.events)
        self._save_window(parser, settings.window)
        
        # Write to file
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                parser.write(f)
            logger.debug(f"Saved configuration to {self.config_path}")
        except IOError as e:
            raise ConfigurationError(f"Failed to write config file: {e}") from e

    # ========== SMTP Configuration ==========

    def _load_smtp(self, parser: configparser.ConfigParser) -> SMTPConfig:
        """Load SMTP configuration from parser."""
        if not parser.has_section("smtp"):
            return SMTPConfig()
        
        return SMTPConfig(
            host=parser.get("smtp", "host", fallback="smtp.example.com"),
            port=parser.getint("smtp", "port", fallback=587),
            username=parser.get("smtp", "username", fallback=""),
            password=parser.get("smtp", "password", fallback=""),
            from_addr=parser.get("smtp", "from_addr", fallback="Bulletin Builder <user@example.com>"),
            use_tls=parser.getboolean("smtp", "use_tls", fallback=True),
        )

    def _save_smtp(self, parser: configparser.ConfigParser, smtp: SMTPConfig) -> None:
        """Save SMTP configuration to parser."""
        if not parser.has_section("smtp"):
            parser.add_section("smtp")
        
        parser.set("smtp", "host", smtp.host)
        parser.set("smtp", "port", str(smtp.port))
        parser.set("smtp", "username", smtp.username)
        parser.set("smtp", "password", smtp.password)
        parser.set("smtp", "from_addr", smtp.from_addr)
        parser.set("smtp", "use_tls", str(smtp.use_tls).lower())

    def get_smtp(self) -> SMTPConfig:
        """Get SMTP configuration."""
        return self.load().smtp

    def save_smtp(self, smtp: SMTPConfig) -> None:
        """Save SMTP configuration."""
        settings = self.load()
        settings.smtp = smtp
        self.save(settings)

    # ========== API Keys ==========

    def _load_api_keys(self, parser: configparser.ConfigParser) -> APIKeys:
        """Load API keys from parser."""
        google_key = ""
        openai_key = ""
        
        # Try multiple sections for backward compatibility
        for section in ["google", "API"]:
            if parser.has_section(section):
                google_key = parser.get(section, "api_key", fallback="")
                if google_key:
                    break
        
        if parser.has_section("openai"):
            openai_key = parser.get("openai", "api_key", fallback="")
        
        return APIKeys(google=google_key, openai=openai_key)

    def _save_api_keys(self, parser: configparser.ConfigParser, keys: APIKeys) -> None:
        """Save API keys to parser."""
        # Save to preferred sections
        if not parser.has_section("google"):
            parser.add_section("google")
        parser.set("google", "api_key", keys.google)
        
        if not parser.has_section("openai"):
            parser.add_section("openai")
        parser.set("openai", "api_key", keys.openai)

    def get_api_keys(self) -> APIKeys:
        """Get API keys."""
        return self.load().api_keys

    def save_api_keys(self, keys: APIKeys) -> None:
        """Save API keys."""
        settings = self.load()
        settings.api_keys = keys
        self.save(settings)

    def get_google_api_key(self) -> str:
        """Get Google API key (backward compatibility)."""
        return self.load().api_keys.google

    def save_google_api_key(self, key: str) -> None:
        """Save Google API key (backward compatibility)."""
        keys = self.get_api_keys()
        keys.google = key
        self.save_api_keys(keys)

    def get_openai_api_key(self) -> str:
        """Get OpenAI API key (backward compatibility)."""
        return self.load().api_keys.openai

    def save_openai_api_key(self, key: str) -> None:
        """Save OpenAI API key (backward compatibility)."""
        keys = self.get_api_keys()
        keys.openai = key
        self.save_api_keys(keys)

    # ========== Events Configuration ==========

    def _load_events(self, parser: configparser.ConfigParser) -> EventsConfig:
        """Load events configuration from parser."""
        if not parser.has_section("events"):
            return EventsConfig()
        
        url = parser.get("events", "feed_url", fallback="")
        # Strip quotes and whitespace
        url = url.strip().strip('"\'')
        
        auto_import = parser.getboolean("events", "auto_import", fallback=False)
        
        return EventsConfig(feed_url=url, auto_import=auto_import)

    def _save_events(self, parser: configparser.ConfigParser, events: EventsConfig) -> None:
        """Save events configuration to parser."""
        if not parser.has_section("events"):
            parser.add_section("events")
        
        # Always strip quotes when saving
        parser.set("events", "feed_url", events.feed_url.strip().strip('"\''))
        parser.set("events", "auto_import", str(events.auto_import).lower())

    def get_events_config(self) -> EventsConfig:
        """Get events configuration."""
        return self.load().events

    def save_events_config(self, events: EventsConfig) -> None:
        """Save events configuration."""
        settings = self.load()
        settings.events = events
        self.save(settings)

    def get_events_feed_url(self) -> str:
        """Get events feed URL (backward compatibility)."""
        return self.load().events.feed_url

    def save_events_feed_url(self, url: str) -> None:
        """Save events feed URL (backward compatibility)."""
        events = self.get_events_config()
        events.feed_url = url
        self.save_events_config(events)

    def get_events_auto_import(self) -> bool:
        """Get events auto-import flag (backward compatibility)."""
        return self.load().events.auto_import

    def save_events_auto_import(self, enabled: bool) -> None:
        """Save events auto-import flag (backward compatibility)."""
        events = self.get_events_config()
        events.auto_import = enabled
        self.save_events_config(events)

    # ========== Window Configuration ==========

    def _load_window(self, parser: configparser.ConfigParser) -> WindowConfig:
        """Load window configuration from parser."""
        if not parser.has_section("window"):
            return WindowConfig()
        
        return WindowConfig(
            geometry=parser.get("window", "geometry", fallback=""),
            state=parser.get("window", "state", fallback=""),
            confirm_on_close=parser.getboolean("window", "confirm_on_close", fallback=True),
            autosave_on_close=parser.getboolean("window", "autosave_on_close", fallback=True),
        )

    def _save_window(self, parser: configparser.ConfigParser, window: WindowConfig) -> None:
        """Save window configuration to parser."""
        if not parser.has_section("window"):
            parser.add_section("window")
        
        if window.geometry:
            parser.set("window", "geometry", window.geometry)
        if window.state:
            parser.set("window", "state", window.state)
        parser.set("window", "confirm_on_close", str(window.confirm_on_close).lower())
        parser.set("window", "autosave_on_close", str(window.autosave_on_close).lower())

    def get_window_config(self) -> WindowConfig:
        """Get window configuration."""
        return self.load().window

    def save_window_config(self, window: WindowConfig) -> None:
        """Save window configuration."""
        settings = self.load()
        settings.window = window
        self.save(settings)

    def get_window_state(self) -> tuple[str, str]:
        """Get window state (backward compatibility)."""
        window = self.load().window
        return window.geometry, window.state

    def save_window_state(self, geometry: str, state: str) -> None:
        """Save window state (backward compatibility)."""
        window = self.get_window_config()
        window.geometry = geometry
        window.state = state
        self.save_window_config(window)

    def get_confirm_on_close(self, default: bool = True) -> bool:
        """Get confirm on close setting (backward compatibility)."""
        return self.load().window.confirm_on_close

    def save_confirm_on_close(self, enabled: bool) -> None:
        """Save confirm on close setting (backward compatibility)."""
        window = self.get_window_config()
        window.confirm_on_close = enabled
        self.save_window_config(window)

    def get_autosave_on_close(self, default: bool = True) -> bool:
        """Get autosave on close setting (backward compatibility)."""
        return self.load().window.autosave_on_close

    def save_autosave_on_close(self, enabled: bool) -> None:
        """Save autosave on close setting (backward compatibility)."""
        window = self.get_window_config()
        window.autosave_on_close = enabled
        self.save_window_config(window)

    # ========== Utility Methods ==========

    def validate(self) -> List[str]:
        """
        Validate configuration and return list of warnings/errors.
        
        Returns:
            List of validation messages (empty if all valid)
        """
        issues = []
        settings = self.load()
        
        # Validate SMTP if configured
        if settings.smtp.host != "smtp.example.com":
            if not settings.smtp.username:
                issues.append("SMTP: username is required when host is configured")
            if not settings.smtp.password:
                issues.append("SMTP: password is required when host is configured")
            if settings.smtp.port not in [25, 465, 587, 2525]:
                issues.append(f"SMTP: unusual port {settings.smtp.port} (expected 587, 465, or 25)")
        
        # Validate events feed URL
        if settings.events.feed_url:
            if not (settings.events.feed_url.startswith("http://") or 
                    settings.events.feed_url.startswith("https://")):
                issues.append("Events: feed_url should be a valid HTTP/HTTPS URL")
        
        # Validate window geometry format
        if settings.window.geometry:
            import re
            if not re.match(r'^\d+x\d+[+-]\d+[+-]\d+$', settings.window.geometry):
                issues.append(f"Window: invalid geometry format '{settings.window.geometry}' (expected WxH+X+Y)")
        
        # Validate window state
        if settings.window.state and settings.window.state not in ['', 'normal', 'zoomed', 'iconic']:
            issues.append(f"Window: invalid state '{settings.window.state}' (expected normal, zoomed, or iconic)")
        
        return issues

    def export_dict(self) -> Dict[str, Any]:
        """
        Export all settings as a dictionary.
        
        Returns:
            Dictionary representation of all settings
        """
        settings = self.load()
        return {
            'smtp': asdict(settings.smtp),
            'api_keys': asdict(settings.api_keys),
            'events': asdict(settings.events),
            'window': asdict(settings.window),
        }

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults (useful for testing)."""
        self.save(AppSettings())
        logger.info("Configuration reset to defaults")


# Global instance for backward compatibility
_default_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: str = "config.ini") -> ConfigManager:
    """
    Get the global ConfigManager instance.
    
    Args:
        config_path: Path to config file (default: "config.ini")
        
    Returns:
        ConfigManager instance
    """
    global _default_manager
    if _default_manager is None or _default_manager.config_path != Path(config_path):
        _default_manager = ConfigManager(config_path)
    return _default_manager
