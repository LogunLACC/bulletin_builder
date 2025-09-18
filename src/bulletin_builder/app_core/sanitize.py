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


def validate_email_html(html: str) -> list[str]:
    """
    Lightweight validator for email HTML compliance. Returns a list of
    human-readable issues (warnings) without mutating input.
    """
    issues: list[str] = []

    # 1) Forbidden wrappers/elements
    if re.search(r'(?is)<\/?(html|head|style|script|link|iframe|svg|form)\b', html):
        issues.append("Forbidden wrapper or element present (html/head/style/script/link/iframe/svg/form).")

    # 2) Anchors must have margin:0; padding:0; at least somewhere
    for m in re.finditer(r'(?is)<a\b([^>]*)>', html):
        attrs = m.group(1)
        st = re.search(r'(?is)style\s*=\s*"([^"]*)"', attrs)
        if not st:
            issues.append("<a> missing style attribute.")
        else:
            s = st.group(1).replace(" ", "")
            if not ("margin:0;" in s and "padding:0;" in s):
                issues.append("<a> style missing margin:0; padding:0;.")

    # 3) Images: absolute URLs and resets
    for m in re.finditer(r'(?is)<img\b([^>]*)>', html):
        attrs = m.group(1)
        src = re.search(r'(?is)\bsrc\s*=\s*"([^"]*)"', attrs)
        if not src or not re.match(r'(?i)^https?://', src.group(1) or ""):
            issues.append("<img> src should be absolute http(s) URL.")
        st = re.search(r'(?is)style\s*=\s*"([^"]*)"', attrs)
        if not st:
            issues.append("<img> missing style attribute.")
        else:
            s = st.group(1).replace(" ", "")
            if not ("margin:0;" in s and "padding:0;" in s):
                issues.append("<img> style missing margin:0; padding:0;.")

    # 4) Tables/td basics
    for m in re.finditer(r'(?is)<table\b([^>]*)>', html):
        attrs = m.group(1)
        st = re.search(r'(?is)style\s*=\s*"([^"]*)"', attrs)
        if not st or "border-collapse:collapse" not in (st.group(1) or ""):
            issues.append("<table> style should include border-collapse:collapse.")
    for m in re.finditer(r'(?is)<td\b([^>]*)>', html):
        attrs = m.group(1)
        st = re.search(r'(?is)style\s*=\s*"([^"]*)"', attrs)
        if not st or "border:none" not in (st.group(1) or ""):
            issues.append("<td> style should include border:none.")

    # 5) Absolute hrefs
    for m in re.finditer(r'(?is)\bhref\s*=\s*"([^"]*)"', html):
        url = m.group(1) or ""
        if url.startswith("#"):
            # Internal anchors are acceptable but may be discouraged for paste-in editors
            continue
        if not re.match(r'(?i)^https?://', url):
            issues.append("href should be absolute http(s) URL.")

    return issues


