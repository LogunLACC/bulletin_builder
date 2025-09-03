#!/usr/bin/env python3
"""
Fail if `datetime.utcnow(` is used in the codebase.

Intended for use as a pre-commit hook (language: system).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    # Scan project source and scripts/tools
    paths = [ROOT / "src", ROOT / "scripts", ROOT / "tools"]
    pattern = re.compile(r'\bdatetime\.utcnow\s*\(')
    # Note: pattern also catches aliasing like: from datetime import datetime; datetime.utcnow(

    failures: list[str] = []
    for base in paths:
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if pattern.search(text):
                rel = p.relative_to(ROOT)
                failures.append(str(rel))

    if failures:
        print("Found forbidden datetime.utcnow() usage in:")
        for f in failures:
            print(f" - {f}")
        print("Use timezone-aware: datetime.now(datetime.UTC) instead.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
