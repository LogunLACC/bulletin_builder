"""
Email HTML sanitizer for LACC formatting rules.
"""

import re

_WS_SEMI = re.compile(r'\s*;\s*')
_LOWER = lambda s: (s or "").strip().lower()

def _prepend_rule(style: str, rule: str) -> str:
    """Ensure `rule` is the very first declaration; remove later duplicates by property name."""
    style = (style or "").strip().strip('"').strip("'")
    # Split existing decls
    decls = [d.strip() for d in _WS_SEMI.split(style) if d.strip()]
    want_props = {d.split(':',1)[0].strip().lower() for d in _WS_SEMI.split(rule) if d.strip()}
    # Remove any existing decl with same prop (case-insensitive)
    filtered = []
    for d in decls:
        k = d.split(':',1)[0].strip().lower()
        if k not in want_props:
            filtered.append(d)
    merged = rule.rstrip(';')
    if filtered:
        merged += '; ' + '; '.join(filtered)
    return merged + ';'

def _ensure_contains(style: str, fragment: str) -> str:
    s = _LOWER(style)
    f = _LOWER(fragment).rstrip(';')
    if f in s:
        return style
    return style.rstrip().rstrip(';') + ('; ' if style.strip() else '') + fragment.rstrip(';') + ';'

def sanitize_email_html(html: str) -> str:
    # 0) Strip <!doctype>, <head>â€¦</head>, all <link rel="stylesheet"...>, and all <script ...>â€¦</script>
    html = re.sub(r'<!doctype[^>]*>\s*', '', html, flags=re.I)
    html = re.sub(r'<head\b[^>]*>.*?</head>', '', html, flags=re.I|re.S)
    html = re.sub(r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*>\s*', '', html, flags=re.I)
    html = re.sub(r'<script\b[^>]*>.*?</script>\s*', '', html, flags=re.I|re.S)
    html = re.sub(r'<style\b[^>]*>.*?</style>\s*', '', html, flags=re.I|re.S)

    # 0b) Remove any on* event handlers (email safety)
    # Remove attributes such as onerror="..." or onclick='...'
    html = re.sub(r'''(?is)\s+on[a-z]+\s*=\s*(?:"[^"]*"|'[^']*')''', '', html)

        # 1) Ensure a/img/table/td have a style attribute when missing (NOTE THE LEADING SPACE)
    html = re.sub(r'(<a\b)(?![^>]*style=)',   r'\1 style="margin:0; padding:0;"', html, flags=re.I)
    html = re.sub(r'(<img\b)(?![^>]*style=)', r'\1 style="margin:0; padding:0;"', html, flags=re.I)
    html = re.sub(r'(<table\b)(?![^>]*style=)', r'\1 style="border-collapse:collapse;"', html, flags=re.I)
    html = re.sub(r'(<td\b)(?![^>]*style=)',  r'\1 style="border:none;"', html, flags=re.I)
# 2) Prepend/normalize when style already exists; keep enforced rules first, dedupe props
    html = re.sub(r'(<a\b[^>]*style=")([^"]*)"',  lambda m: f'{m.group(1)}{_prepend_rule(m.group(2), "margin:0; padding:0")}"',  html, flags=re.I)
    html = re.sub(r'(<img\b[^>]*style=")([^"]*)"', lambda m: f'{m.group(1)}{_prepend_rule(m.group(2), "margin:0; padding:0")}"', html, flags=re.I)
    html = re.sub(
        r'(<table\b[^>]*style=")([^"]*)"',
        lambda m: f'{m.group(1)}{_ensure_contains(m.group(2), "border-collapse:collapse")}"',
        html,
        flags=re.I,
    )
    html = re.sub(r'(<td\b[^>]*style=")([^"]*)"',   lambda m: f'{m.group(1)}{_prepend_rule(m.group(2), "border:none")}"',       html, flags=re.I)

    # 3) Ensure table attribute defaults for email clients
    def _ensure_table_attrs(m):
        attrs = m.group(1)
        def _has(attr):
            return re.search(rf'(?i)\b{attr}\s*=\s*(?:"[^"]*"|\'[^\']*\'|\S+)', attrs) is not None
        if not _has('cellpadding'):
            attrs += ' cellpadding="0"'
        if not _has('cellspacing'):
            attrs += ' cellspacing="0"'
        if not _has('border'):
            attrs += ' border="0"'
        return '<table' + attrs + '>'

    html = re.sub(r'(?is)<table([^>]*)>', _ensure_table_attrs, html)

    return html


