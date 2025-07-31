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
        return config.get("events", "feed_url", fallback="")
    return ""


def save_events_feed_url(url: str) -> None:
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    if "events" not in config:
        config["events"] = {}
    config["events"]["feed_url"] = url
    with open(CONFIG_FILE, "w") as f:
        config.write(f)
