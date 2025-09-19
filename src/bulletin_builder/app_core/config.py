"""Utility functions for persisting API keys in config.ini."""

import configparser
import os

CONFIG_FILE = "config.ini"


def _load_key(section: str) -> str:
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        return config.get(section, "api_key", fallback="")
    return ""


def _save_key(section: str, api_key: str) -> None:
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    if section not in config:
        config[section] = {}
    config[section]["api_key"] = api_key
    with open(CONFIG_FILE, "w") as f:
        config.write(f)


def load_api_key() -> str:
    """Backward compatibility for Google API key."""
    return _load_key("google")


def save_api_key(api_key: str) -> None:
    """Backward compatibility for Google API key."""
    _save_key("google", api_key)


def load_google_api_key() -> str:
    return _load_key("google")


def save_google_api_key(api_key: str) -> None:
    _save_key("google", api_key)


def load_openai_key() -> str:
    return _load_key("openai")


def save_openai_key(api_key: str) -> None:
    _save_key("openai", api_key)


def load_events_feed_url() -> str:
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        url = config.get("events", "feed_url", fallback="")
        return url.strip().strip('"\'')
    return ""


def save_events_feed_url(url: str) -> None:
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    if "events" not in config:
        config["events"] = {}
    # Always save stripped URL
    config["events"]["feed_url"] = url.strip().strip('"\'')
    with open(CONFIG_FILE, "w") as f:
        config.write(f)


def load_events_auto_import() -> bool:
    """Read the auto-import flag for events feed. Defaults to False."""
    import configparser
    import os
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        try:
            return config.getboolean("events", "auto_import", fallback=False)
        except Exception:
            return False
    return False


def save_events_auto_import(enabled: bool) -> None:
    """Persist the auto-import flag for events feed."""
    import configparser
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    if "events" not in config:
        config["events"] = {}
    config["events"]["auto_import"] = "true" if enabled else "false"
    with open(CONFIG_FILE, "w") as f:
        config.write(f)


# -------- Window placement & state -----------------------------------------
def load_window_state() -> tuple[str, str]:
    """Return (geometry, state) from config.

    geometry: standard Tk geometry string like 'WxH+X+Y' or ''
    state: one of '', 'zoomed', 'normal', 'iconic'
    """
    import configparser
    import os
    cfg = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        cfg.read(CONFIG_FILE)
        geo = cfg.get("window", "geometry", fallback="")
        state = cfg.get("window", "state", fallback="")
        return geo, state
    return "", ""


def save_window_state(geometry: str, state: str) -> None:
    import configparser
    cfg = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        cfg.read(CONFIG_FILE)
    if "window" not in cfg:
        cfg["window"] = {}
    if geometry:
        cfg["window"]["geometry"] = geometry
    if state:
        cfg["window"]["state"] = state
    with open(CONFIG_FILE, "w") as f:
        cfg.write(f)


# -------- Close behavior toggles -------------------------------------------
def load_confirm_on_close(default: bool = True) -> bool:
    import configparser
    import os
    cfg = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        cfg.read(CONFIG_FILE)
        try:
            return cfg.getboolean("window", "confirm_on_close", fallback=default)
        except Exception:
            return default
    return default


def save_confirm_on_close(enabled: bool) -> None:
    import configparser
    cfg = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        cfg.read(CONFIG_FILE)
    if "window" not in cfg:
        cfg["window"] = {}
    cfg["window"]["confirm_on_close"] = "true" if enabled else "false"
    with open(CONFIG_FILE, "w") as f:
        cfg.write(f)


def load_autosave_on_close(default: bool = True) -> bool:
    import configparser
    import os
    cfg = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        cfg.read(CONFIG_FILE)
        try:
            return cfg.getboolean("window", "autosave_on_close", fallback=default)
        except Exception:
            return default
    return default


def save_autosave_on_close(enabled: bool) -> None:
    import configparser
    cfg = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        cfg.read(CONFIG_FILE)
    if "window" not in cfg:
        cfg["window"] = {}
    cfg["window"]["autosave_on_close"] = "true" if enabled else "false"
    with open(CONFIG_FILE, "w") as f:
        cfg.write(f)
