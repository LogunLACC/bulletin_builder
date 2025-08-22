"""
Email post-processor for Bulletin Builder (idempotent, email-safe).
Fixes:
  1) Edge-hugging content cells → adds side padding (12px 16px).
  2) Table of Contents <ul> → left-align, remove bullets, add side padding.
  3) Inserts a subtle <hr> after TOC (if not already present).
Safe to run multiple times.
"""
from __future__ import annotations
import re
from typing import Dict
try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:
    # Soft dependency; callers should catch if missing. We still expose a no-op fallback.
    BeautifulSoup = None

def _parse_style(style: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not style:
        return out
    for chunk in style.split(";"):
        if not chunk.strip() or ":" not in chunk:
            continue
        k, v = chunk.split(":", 1)
        out[k.strip().lower()] = v.strip()
    return out

def _style_to_str(props: Dict[str, str]) -> str:
    return ";".join(f"{k}:{v}" for k, v in props.items() if v) + (";" if props else "")

def _merge_style(existing: str, updates: Dict[str, str]) -> str:
    props = _parse_style(existing or "")
    for k, v in updates.items():
        props[k.lower()] = v
    return _style_to_str(props)

def _has_inpage_anchor(li) -> bool:
    a = li.find("a", href=True)
    return bool(a and isinstance(a.get("href"), str) and a["href"].startswith("#"))

def _fix_announcement_padding(soup) -> None:
    for td in soup.find_all("td"):
        style = (td.get("style") or "")
        if "padding" in style.lower() and re.search(r"padding\s*:\s*12px\s*0\s*12px\s*0", style, flags=re.I):
            td["style"] = _merge_style(style, {"padding": "12px 16px"})

def _normalize_toc_and_hr(soup) -> None:
    for ul in soup.find_all("ul"):
        lis = ul.find_all("li")
        if not lis or not all(_has_inpage_anchor(li) for li in lis):
            continue
        ul["style"] = _merge_style(ul.get("style", ""), {
            "margin": "0 0 24px 0",
            "padding": "0 16px",
            "list-style": "none",
            "text-align": "left",
        })
        for li in lis:
            li["style"] = _merge_style(li.get("style", ""), {"margin": "0 0 6px 0"})
        next_elem = ul.find_next_sibling()
        if not (next_elem and getattr(next_elem, "name", None) == "hr"):
            hr = soup.new_tag("hr")
            hr["style"] = "border:0;border-top:1px solid #e5e7eb;margin:16px 0;"
            ul.insert_after(hr)

def process_html(html: str) -> str:
    """
    Post-process email/preview HTML (idempotent). If bs4 is missing, returns original HTML.
    """
    if not BeautifulSoup or not html or "<html" not in html.lower():
        return html
    soup = BeautifulSoup(html, "html.parser")
    _fix_announcement_padding(soup)
    _normalize_toc_and_hr(soup)
    return str(soup)

def ensure_postprocessed(html: str) -> str:
    """Wrapper that never raises—returns original HTML on error."""
    try:
        return process_html(html)
    except Exception:
        return html
