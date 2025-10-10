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
from typing import Any, Optional, Dict, List, Tuple
import logging
import re

logger = logging.getLogger(__name__)


# Environment variable prefix
ENV_PREFIX = "BULLETIN_"


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

    def __init__(self, config_path: str = "config.ini", use_env_vars: bool = True):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to config.ini file (default: "config.ini")
            use_env_vars: Whether to use environment variable overrides (default: True)
        """
        self.config_path = Path(config_path)
        self.use_env_vars = use_env_vars
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

    def _get_env_var(self, *keys: str) -> Optional[str]:
        """
        Get value from environment variable.
        
        Tries multiple key formats:
        - BULLETIN_SMTP_HOST
        - BULLETIN_SMTP__HOST (with double underscore)
        
        Args:
            keys: Variable name parts (e.g., "smtp", "host")
            
        Returns:
            Environment variable value or None
        """
        if not self.use_env_vars:
            return None
        
        # Try with single underscore
        env_key = ENV_PREFIX + "_".join(k.upper() for k in keys)
        value = os.getenv(env_key)
        if value is not None:
            logger.debug(f"Using environment variable: {env_key}")
            return value
        
        # Try with double underscore separator
        env_key = ENV_PREFIX + "__".join(k.upper() for k in keys)
        value = os.getenv(env_key)
        if value is not None:
            logger.debug(f"Using environment variable: {env_key}")
            return value
        
        return None

    def _get_env_bool(self, *keys: str, default: bool = False) -> bool:
        """Get boolean from environment variable."""
        value = self._get_env_var(*keys)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')

    def _get_env_int(self, *keys: str, default: int = 0) -> Optional[int]:
        """Get integer from environment variable."""
        value = self._get_env_var(*keys)
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid integer in environment variable: {value}")
            return default

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
        """Load SMTP configuration from parser with environment variable overrides."""
        # Start with defaults or config file values
        if parser.has_section("smtp"):
            config = SMTPConfig(
                host=parser.get("smtp", "host", fallback="smtp.example.com"),
                port=parser.getint("smtp", "port", fallback=587),
                username=parser.get("smtp", "username", fallback=""),
                password=parser.get("smtp", "password", fallback=""),
                from_addr=parser.get("smtp", "from_addr", fallback="Bulletin Builder <user@example.com>"),
                use_tls=parser.getboolean("smtp", "use_tls", fallback=True),
            )
        else:
            config = SMTPConfig()
        
        # Apply environment variable overrides
        if self.use_env_vars:
            config.host = self._get_env_var("smtp", "host") or config.host
            env_port = self._get_env_int("smtp", "port")
            if env_port is not None:
                config.port = env_port
            config.username = self._get_env_var("smtp", "username") or config.username
            config.password = self._get_env_var("smtp", "password") or config.password
            config.from_addr = self._get_env_var("smtp", "from_addr") or config.from_addr
            config.use_tls = self._get_env_bool("smtp", "use_tls", default=config.use_tls)
        
        return config

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
        """Load API keys from parser with environment variable overrides."""
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
        
        # Apply environment variable overrides
        if self.use_env_vars:
            google_key = self._get_env_var("google", "api_key") or self._get_env_var("api", "google") or google_key
            openai_key = self._get_env_var("openai", "api_key") or self._get_env_var("api", "openai") or openai_key
        
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
        """Load events configuration from parser with environment variable overrides."""
        if parser.has_section("events"):
            url = parser.get("events", "feed_url", fallback="")
            # Strip quotes and whitespace
            url = url.strip().strip('"\'')
            auto_import = parser.getboolean("events", "auto_import", fallback=False)
        else:
            url = ""
            auto_import = False
        
        # Apply environment variable overrides
        if self.use_env_vars:
            url = self._get_env_var("events", "feed_url") or url
            auto_import = self._get_env_bool("events", "auto_import", default=auto_import)
        
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
        """Load window configuration from parser with environment variable overrides."""
        if parser.has_section("window"):
            config = WindowConfig(
                geometry=parser.get("window", "geometry", fallback=""),
                state=parser.get("window", "state", fallback=""),
                confirm_on_close=parser.getboolean("window", "confirm_on_close", fallback=True),
                autosave_on_close=parser.getboolean("window", "autosave_on_close", fallback=True),
            )
        else:
            config = WindowConfig()
        
        # Apply environment variable overrides (usually not used for window state)
        if self.use_env_vars:
            config.geometry = self._get_env_var("window", "geometry") or config.geometry
            config.state = self._get_env_var("window", "state") or config.state
            config.confirm_on_close = self._get_env_bool("window", "confirm_on_close", default=config.confirm_on_close)
            config.autosave_on_close = self._get_env_bool("window", "autosave_on_close", default=config.autosave_on_close)
        
        return config

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

    def validate(self) -> List[Tuple[str, str]]:
        """
        Validate configuration and return list of issues.
        
        Returns:
            List of (severity, message) tuples where severity is 'ERROR' or 'WARNING'
            Empty list if all valid
        """
        issues = []
        settings = self.load()
        
        # Validate SMTP if configured
        if settings.smtp.host and settings.smtp.host != "smtp.example.com":
            if not settings.smtp.username:
                issues.append(("ERROR", "SMTP: username is required when host is configured"))
            if not settings.smtp.password:
                issues.append(("ERROR", "SMTP: password is required when host is configured"))
            
            # Check port
            if settings.smtp.port not in [25, 465, 587, 2525]:
                issues.append(("WARNING", f"SMTP: unusual port {settings.smtp.port} (common ports: 587 for TLS, 465 for SSL, 25 for unencrypted)"))
            
            # Check TLS/SSL port mismatch
            if settings.smtp.port == 465 and settings.smtp.use_tls:
                issues.append(("WARNING", "SMTP: port 465 typically uses SSL, not TLS. Consider setting use_tls=false or using port 587"))
            if settings.smtp.port == 587 and not settings.smtp.use_tls:
                issues.append(("WARNING", "SMTP: port 587 typically requires TLS. Consider setting use_tls=true"))
            
            # Validate from_addr format
            if settings.smtp.from_addr:
                # Should match: "Name <email@example.com>" or "email@example.com"
                if not re.search(r'[^@]+@[^@]+\.[^@]+', settings.smtp.from_addr):
                    issues.append(("ERROR", f"SMTP: from_addr '{settings.smtp.from_addr}' doesn't contain a valid email address"))
        
        # Validate API keys format (basic check)
        if settings.api_keys.google and settings.api_keys.google == "REPLACE_ME_GOOGLE_API_KEY":
            issues.append(("WARNING", "Google API key is still set to placeholder value"))
        if settings.api_keys.openai and settings.api_keys.openai == "REPLACE_ME_OPENAI_API_KEY":
            issues.append(("WARNING", "OpenAI API key is still set to placeholder value"))
        
        # Validate events feed URL
        if settings.events.feed_url:
            if not (settings.events.feed_url.startswith("http://") or 
                    settings.events.feed_url.startswith("https://")):
                issues.append(("ERROR", "Events: feed_url must be a valid HTTP or HTTPS URL"))
            elif settings.events.feed_url.startswith("http://"):
                issues.append(("WARNING", "Events: feed_url uses HTTP (unencrypted). Consider using HTTPS for security"))
            
            # Check if URL looks like placeholder
            if "example.com" in settings.events.feed_url.lower():
                issues.append(("WARNING", "Events: feed_url appears to be a placeholder (contains 'example.com')"))
        
        # Validate window geometry format
        if settings.window.geometry:
            if not re.match(r'^\d+x\d+[+-]\d+[+-]\d+$', settings.window.geometry):
                issues.append(("ERROR", f"Window: invalid geometry format '{settings.window.geometry}' (expected: WIDTHxHEIGHT+X+Y, e.g., 1200x800+100+100)"))
            else:
                # Parse and validate reasonable values
                match = re.match(r'^(\d+)x(\d+)[+-](\d+)[+-](\d+)$', settings.window.geometry)
                if match:
                    width, height, x, y = map(int, match.groups())
                    if width < 640 or height < 480:
                        issues.append(("WARNING", f"Window: geometry {width}x{height} is very small (minimum 640x480 recommended)"))
                    if width > 7680 or height > 4320:  # 8K resolution
                        issues.append(("WARNING", f"Window: geometry {width}x{height} is unusually large"))
        
        # Validate window state
        valid_states = ['', 'normal', 'zoomed', 'iconic']
        if settings.window.state and settings.window.state not in valid_states:
            issues.append(("ERROR", f"Window: invalid state '{settings.window.state}' (expected: {', '.join(valid_states)})"))
        
        return issues

    def validate_and_report(self) -> bool:
        """
        Validate configuration and print issues to console.
        
        Returns:
            True if validation passed (no errors), False if errors found
        """
        issues = self.validate()
        
        if not issues:
            logger.info("✓ Configuration validation passed")
            return True
        
        has_errors = False
        for severity, message in issues:
            if severity == "ERROR":
                logger.error(f"✗ {message}")
                has_errors = True
            else:
                logger.warning(f"⚠ {message}")
        
        return not has_errors

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

    def get_supported_env_vars(self) -> Dict[str, str]:
        """
        Get dictionary of all supported environment variables with descriptions.
        
        Returns:
            Dict mapping environment variable names to descriptions
        """
        return {
            # SMTP
            "BULLETIN_SMTP_HOST": "SMTP server hostname",
            "BULLETIN_SMTP_PORT": "SMTP server port (587 for TLS, 465 for SSL)",
            "BULLETIN_SMTP_USERNAME": "SMTP username (usually email address)",
            "BULLETIN_SMTP_PASSWORD": "SMTP password or app-specific password",
            "BULLETIN_SMTP_FROM_ADDR": "From address with format: Name <email@example.com>",
            "BULLETIN_SMTP_USE_TLS": "Use TLS encryption (true/false)",
            
            # API Keys
            "BULLETIN_GOOGLE_API_KEY": "Google AI API key",
            "BULLETIN_API_GOOGLE": "Google AI API key (alternative name)",
            "BULLETIN_OPENAI_API_KEY": "OpenAI API key",
            "BULLETIN_API_OPENAI": "OpenAI API key (alternative name)",
            
            # Events
            "BULLETIN_EVENTS_FEED_URL": "Events feed URL (HTTP/HTTPS)",
            "BULLETIN_EVENTS_AUTO_IMPORT": "Auto-import events on startup (true/false)",
            
            # Window (usually not used via environment)
            "BULLETIN_WINDOW_GEOMETRY": "Window geometry (WIDTHxHEIGHT+X+Y)",
            "BULLETIN_WINDOW_STATE": "Window state (normal/zoomed/iconic)",
            "BULLETIN_WINDOW_CONFIRM_ON_CLOSE": "Confirm before closing (true/false)",
            "BULLETIN_WINDOW_AUTOSAVE_ON_CLOSE": "Auto-save on close (true/false)",
        }


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
