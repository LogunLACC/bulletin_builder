
"""
bulletin_email_postprocess.py
---------------------------------
Email-safe HTML post-processor for LACC Bulletin exports.

What it does (idempotent):
  1) Fixes announcement cells with edge-hugging text by adding side padding.
  2) Normalizes the Table of Contents: left-align, remove bullets, add side padding.
  3) Inserts a subtle <hr> after the TOC to separate it from content.
  4) Leaves everything else untouched; can be run multiple times safely.

Usage:
  - As a library: html = process_html(html)
  - As a script:  python bulletin_email_postprocess.py INPUT.html OUTPUT.html
"""
from __future__ import annotations

import re
import sys
from typing import Dict

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:  # pragma: no cover
    print("BeautifulSoup (bs4) is required for this post-processor. Please install with: pip install beautifulsoup4")
    raise

# ----------------------------
# Helpers
# ----------------------------

def _parse_style(style: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not style:
        return out
    for chunk in style.split(';'):
        if not chunk.strip():
            continue
        if ':' not in chunk:
            continue
        k, v = chunk.split(':', 1)
        out[k.strip().lower()] = v.strip()
    return out

def _style_to_str(props: Dict[str, str]) -> str:
    # Preserve deterministic order for stability
    return ';'.join(f"{k}:{v}" for k, v in props.items() if v) + (';' if props else '')

def add_or_merge_style(existing: str, updates: Dict[str, str]) -> str:
    props = _parse_style(existing or '')
    for k, v in updates.items():
        props[k.lower()] = v
    return _style_to_str(props)

def _has_inpage_anchor(li) -> bool:
    a = li.find("a", href=True)
    return bool(a and isinstance(a.get("href"), str) and a["href"].startswith("#"))

# ----------------------------
# Core transforms
# ----------------------------

def _fix_announcement_padding(soup: BeautifulSoup) -> None:
    """
    Find TDs that have padding:12px 0 12px 0 and give them side padding.
    """
    for td in soup.find_all("td"):
        style = (td.get("style") or "")
        if "padding" in style.lower() and re.search(r"padding\s*:\s*12px\s*0\s*12px\s*0", style, flags=re.I):
            td["style"] = add_or_merge_style(style, {"padding": "12px 16px"})

def _normalize_toc_and_insert_hr(soup: BeautifulSoup) -> None:
    """
    Identify a TOC <ul> (all li items link to in-page #anchors).
    Normalize style and insert a single <hr> after it if missing.
    """
    for ul in soup.find_all("ul"):
        lis = ul.find_all("li")
        if not lis:
            continue
        if not all(_has_inpage_anchor(li) for li in lis):
            continue

        # Normalize UL style: remove bullets, left-align, add side padding
        ul["style"] = add_or_merge_style(ul.get("style", ""), {
            "margin": "0 0 24px 0",
            "padding": "0 16px",        # side padding so it doesn't hug edges
            "list-style": "none",
            "text-align": "left",
        })

        # Space out each list item a bit
        for li in lis:
            li["style"] = add_or_merge_style(li.get("style", ""), {"margin": "0 0 6px 0"})

        # Insert a subtle divider <hr> after the TOC (idempotent)
        next_elem = ul.find_next_sibling()
        if not (next_elem and getattr(next_elem, "name", None) == "hr"):
            hr_tag = soup.new_tag("hr")
            hr_tag["style"] = "border:0;border-top:1px solid #e5e7eb;margin:16px 0;"
            ul.insert_after(hr_tag)

# ----------------------------
# Public API
# ----------------------------

def process_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    _fix_announcement_padding(soup)
    _normalize_toc_and_insert_hr(soup)

    return str(soup)

# ----------------------------
# CLI
# ----------------------------

def _main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python bulletin_email_postprocess.py INPUT.html [OUTPUT.html]")
        return 2
    in_path = argv[1]
    out_path = argv[2] if len(argv) > 2 else in_path.replace(".html", "_postprocessed.html")
    with open(in_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
    out = process_html(html)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Post-processed: {out_path}")
    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main(sys.argv))
