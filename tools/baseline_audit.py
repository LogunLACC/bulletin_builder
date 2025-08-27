#!/usr/bin/env python3
"""
Baseline HTML audit for LACC Bulletin Builder (NPM-free).
Usage:
  python tools/baseline_audit.py --mode email path/to/file.html [...]
  python tools/baseline_audit.py --mode web   path/to/file.html [...]
Exit: 0 pass, 1 fail
"""
import argparse, re, sys
from pathlib import Path
from typing import List, Dict, Any

RX = {
    "doctype": re.compile(r'(?is)<!doctype'),
    "head": re.compile(r'(?is)<head\b'),
    "script": re.compile(r'(?is)<script\b'),
    "link_stylesheet": re.compile(r'(?is)<link\b[^>]*rel=["\']stylesheet["\']'),
    "on_handlers": re.compile(r'(?is)\son[a-z]+\s*='),
    "http_links": re.compile(r'(?is)(?:src|href)\s*=\s*["\'](http://[^"\']+)'),
    "a_tags": re.compile(r'(?is)<a\b[^>]*>'),
    "img_tags": re.compile(r'(?is)<img\b[^>]*>'),
    "table_tags": re.compile(r'(?is)<table\b[^>]*>'),
    "td_tags": re.compile(r'(?is)<td\b[^>]*>'),
    "style_attr": re.compile(r'(?is)\bstyle\s*=\s*["\']([^"\']*)["\']'),
    "event_title_empty": re.compile(r"(?is)<h3[^>]*class=\"[^\"]*event-card__title[^\"]*\"[^>]*>\s*</h3>"),
    "avif": re.compile(r'(?i)\.avif(\b|\")'),
}

def _style_starts(tag_html: str, starter_css: str) -> bool:
    m = RX["style_attr"].search(tag_html)
    if not m: return False
    val = m.group(1).strip().lower().replace(' ', '')
    return val.startswith(starter_css.replace(' ', '').lower())

def _table_has_collapse(tag_html: str) -> bool:
    m = RX["style_attr"].search(tag_html)
    if not m: return False
    return 'border-collapse:collapse' in m.group(1).lower().replace(' ', '')

def _td_starts_border_none(tag_html: str) -> bool:
    m = RX["style_attr"].search(tag_html)
    if not m: return False
    val = m.group(1).strip().lower().replace(' ', '')
    return val.startswith('border:none;')

def audit_one(path: Path, mode: str) -> Dict[str, Any]:
    html = path.read_text(encoding="utf-8", errors="replace")
    res: Dict[str, Any] = {"file": str(path), "mode": mode, "errors": []}

    has_doctype = bool(RX["doctype"].search(html))
    has_head = bool(RX["head"].search(html))
    has_script = bool(RX["script"].search(html))
    has_link = bool(RX["link_stylesheet"].search(html))
    has_on = bool(RX["on_handlers"].search(html))
    http_links = RX["http_links"].findall(html)
    avif = bool(RX["avif"].search(html))

    a_tags = RX["a_tags"].findall(html)
    img_tags = RX["img_tags"].findall(html)
    table_tags = RX["table_tags"].findall(html)
    td_tags = RX["td_tags"].findall(html)
    empty_titles = RX["event_title_empty"].findall(html)

    if mode == "email":
        if has_doctype: res["errors"].append("email: <!doctype> present")
        if has_head: res["errors"].append("email: <head> present")
        if has_script: res["errors"].append("email: <script> present")
        if has_link: res["errors"].append('email: <link rel="stylesheet"> present')
        if has_on: res["errors"].append("email: inline on* handlers present")
        if http_links: res["errors"].append(f"email: mixed content (http://) URLs: {len(http_links)}")
        if avif: res["errors"].append("email: AVIF images detected (poor client support)")
        if not all(_style_starts(t, "margin:0; padding:0;") for t in a_tags):
            res["errors"].append("email: <a> missing 'margin:0; padding:0;' as first styles")
        if not all(_style_starts(t, "margin:0; padding:0;") for t in img_tags):
            res["errors"].append("email: <img> missing 'margin:0; padding:0;' as first styles")
        if not all(_table_has_collapse(t) for t in table_tags):
            res["errors"].append("email: <table> missing 'border-collapse:collapse'")
        if not all(_td_starts_border_none(t) for t in td_tags):
            res["errors"].append("email: <td> styles not starting with 'border:none;'")
    elif mode == "web":
        if not has_doctype: res["errors"].append("web: <!doctype> is missing")
        if not has_head: res["errors"].append("web: <head> is missing")
        if http_links: res["errors"].append(f"web: mixed content (http://) URLs: {len(http_links)}")
        if empty_titles:
            res["errors"].append(f"web: {len(empty_titles)} empty <h3.event-card__title> elements")
    else:
        res["errors"].append(f"unknown mode: {mode}")

    res.update({
        "a_tags_total": len(a_tags),
        "img_tags_total": len(img_tags),
        "table_tags_total": len(table_tags),
        "td_tags_total": len(td_tags),
        "http_links_count": len(http_links),
        "avif_present": avif,
        "on_handlers_present": has_on,
    })
    return res

def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["email", "web"], required=True, help="Audit profile")
    ap.add_argument("paths", nargs="+", help="HTML files to audit (no directories)")
    args = ap.parse_args(argv)

    failures = 0
    for p in args.paths:
        path = Path(p)
        if not path.exists():
            print(f"!! missing: {path}")
            failures += 1
            continue
        rep = audit_one(path, args.mode)
        if rep["errors"]:
            failures += 1
            print(f"\n✗ FAIL: {rep['file']} [{rep['mode']}]")
            for e in rep["errors"]:
                print("  -", e)
        else:
            print(f"\n✓ PASS: {rep['file']} [{rep['mode']}]")
        print(f"    metrics: a={rep['a_tags_total']} img={rep['img_tags_total']} "
              f"table={rep['table_tags_total']} td={rep['td_tags_total']} "
              f"http={rep['http_links_count']} avif={rep['avif_present']} on*={rep['on_handlers_present']}")
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
#!/usr/bin/env python3
"""
Baseline HTML audit for LACC Bulletin Builder.

Usage:
  python tools/baseline_audit.py --mode email path/to/file.html [more.html ...]
  python tools/baseline_audit.py --mode web   path/to/file.html [more.html ...]

Exit codes:
  0 = all files pass for the selected mode
  1 = one or more files failed checks

This script performs audits only (no mutation). It is NPM-free and safe to run anywhere.
"""

import argparse, re, sys
from pathlib import Path
from typing import List, Dict, Any

RX = {
    "doctype": re.compile(r"(?is)<!doctype"),
    "head": re.compile(r"(?is)<head\b"),
    "script": re.compile(r"(?is)<script\b"),
    "link_stylesheet": re.compile(r"(?is)<link\b[^>]*rel=[\"\\']stylesheet[\"\\']"),
    "on_handlers": re.compile(r"(?is)\bon[a-z]+\s*="),
    "http_links": re.compile(r"(?is)(?:src|href)\s*=\s*[\"\\'](http://[^\"\\']+)"),
    "a_tags": re.compile(r"(?is)<a\b[^>]*>"),
    "img_tags": re.compile(r"(?is)<img\b[^>]*>"),
    "table_tags": re.compile(r"(?is)<table\b[^>]*>"),
    "td_tags": re.compile(r"(?is)<td\b[^>]*>"),
    "style_attr": re.compile(r"(?is)\bstyle\s*=\s*[\"\\']([^\"\\']*)[\"\\']"),
    "event_title_empty": re.compile(r"(?is)<h3[^>]*class=[\"']*event-card__title[\"']*[^>]*>\s*</h3>"),
    "avif": re.compile(r"(?i)\.avif(\b|\")"),
}

def _style_starts(tag_html: str, starter_css: str) -> bool:
    m = RX["style_attr"].search(tag_html)
    if not m: return False
    val = m.group(1).strip().lower().replace(' ', '')
    return val.startswith(starter_css.replace(' ', '').lower())

def _table_has_collapse(tag_html: str) -> bool:
    m = RX["style_attr"].search(tag_html)
    if not m: return False
    return 'border-collapse:collapse' in m.group(1).lower().replace(' ', '')

def _td_starts_border_none(tag_html: str) -> bool:
    m = RX["style_attr"].search(tag_html)
    if not m: return False
    val = m.group(1).strip().lower().replace(' ', '')
    return val.startswith('border:none;')

def audit_one(path: Path, mode: str) -> Dict[str, Any]:
    html = path.read_text(encoding="utf-8", errors="replace")
    res: Dict[str, Any] = {"file": str(path), "mode": mode, "errors": []}

    has_doctype = bool(RX["doctype"].search(html))
    has_head = bool(RX["head"].search(html))
    has_script = bool(RX["script"].search(html))
    has_link = bool(RX["link_stylesheet"].search(html))
    has_on = bool(RX["on_handlers"].search(html))
    http_links = RX["http_links"].findall(html)
    avif = bool(RX["avif"].search(html))

    a_tags = RX["a_tags"].findall(html)
    img_tags = RX["img_tags"].findall(html)
    table_tags = RX["table_tags"].findall(html)
    td_tags = RX["td_tags"].findall(html)
    empty_titles = RX["event_title_empty"].findall(html)

    if mode == "email":
        if has_doctype: res["errors"].append("email: <!doctype> present")
        if has_head: res["errors"].append("email: <head> present")
        if has_script: res["errors"].append("email: <script> present")
        if has_link: res["errors"].append('email: <link rel="stylesheet"> present')
        if has_on: res["errors"].append("email: inline on* handlers present")
        if http_links: res["errors"].append(f"email: mixed content (http://) URLs: {len(http_links)}")
        if avif: res["errors"].append("email: AVIF images detected (poor client support)")
        if not all(_style_starts(t, "margin:0; padding:0;") for t in a_tags):
            res["errors"].append("email: <a> missing 'margin:0; padding:0;' as first styles")
        if not all(_style_starts(t, "margin:0; padding:0;") for t in img_tags):
            res["errors"].append("email: <img> missing 'margin:0; padding:0;' as first styles")
        if not all(_table_has_collapse(t) for t in table_tags):
            res["errors"].append("email: <table> missing 'border-collapse:collapse'")
        if not all(_td_starts_border_none(t) for t in td_tags):
            res["errors"].append("email: <td> styles not starting with 'border:none;'")
    elif mode == "web":
        if not has_doctype: res["errors"].append("web: <!doctype> is missing")
        if not has_head: res["errors"].append("web: <head> is missing")
        if http_links: res["errors"].append(f"web: mixed content (http://) URLs: {len(http_links)}")
        if empty_titles:
            res["errors"].append(f"web: {len(empty_titles)} empty <h3.event-card__title> elements")
    else:
        res["errors"].append(f"unknown mode: {mode}")

    res.update({
        "a_tags_total": len(a_tags),
        "img_tags_total": len(img_tags),
        "table_tags_total": len(table_tags),
        "td_tags_total": len(td_tags),
        "http_links_count": len(http_links),
        "avif_present": avif,
        "on_handlers_present": has_on,
    })
    return res

def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["email", "web"], required=True, help="Audit profile")
    ap.add_argument("paths", nargs="+", help="HTML files to audit (no directories)")
    args = ap.parse_args(argv)

    failures = 0
    for p in args.paths:
        path = Path(p)
        if not path.exists():
            print(f"!! missing: {path}")
            failures += 1
            continue
        rep = audit_one(path, args.mode)
        if rep["errors"]:
            failures += 1
            print(f"\n✗ FAIL: {rep['file']} [{rep['mode']}]")
            for e in rep["errors"]:
                print("  -", e)
        else:
            print(f"\n✓ PASS: {rep['file']} [{rep['mode']}]")
        print(f"    metrics: a={rep['a_tags_total']} img={rep['img_tags_total']} "
              f"table={rep['table_tags_total']} td={rep['td_tags_total']} "
              f"http={rep['http_links_count']} avif={rep['avif_present']} on*={rep['on_handlers_present']}")
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
