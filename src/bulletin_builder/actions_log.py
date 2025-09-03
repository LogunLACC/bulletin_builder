"""Simple action logger used by scripts and exporters to record runs.

Writes append-only timestamped entries to 'activity.log' at the repo root.
This module is intentionally tiny and has no heavy imports to avoid import cycles.
"""
from __future__ import annotations

import datetime
import pathlib


def log_action(action: str, details: str | None = None) -> None:
    """Append an action entry to activity.log in the repo root.

    Arguments:
        action: short action name
        details: optional free-form details
    """
    try:
        repo_root = pathlib.Path(__file__).resolve().parents[2]
        log_file = repo_root / "activity.log"
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with open(log_file, "a", encoding="utf-8") as f:
            line = ts + " | " + action
            if details:
                line += " | " + str(details)
            f.write(line + "\n")
    except Exception:
        # Best-effort fallback: try current working directory
        try:
            alt = pathlib.Path.cwd() / "activity.log"
            ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
            with open(alt, "a", encoding="utf-8") as f:
                f.write(ts + " | " + action + (" | " + str(details) if details else "") + "\n")
        except Exception:
            # Give up silently; logging must not break functionality
            return
