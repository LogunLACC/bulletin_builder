# bulletin_email_postprocess.py
"""
Post-process exported bulletin HTML for email compatibility and style fixes.
"""
import re


def _ensure_attr(style: str, token: str) -> str:
    """Ensure a token (e.g. 'margin:0') exists in a style string; append if missing."""
    if token in style:
        return style
    if style and not style.endswith(';'):
        style = style + ';'
    return style + token + ';'


def process_html(html: str) -> str:
    """
    Post-process the exported HTML for email compatibility and style fixes.
    - Normalizes the TOC (ul) styles and TOC links
    - Inserts <hr> after TOC
    - Ensures anchors/images/tables/td have safe inline resets for email clients
    - Idempotent: safe to run multiple times.
    """

    # --- Normalize TOC <ul> styles ---
    html = re.sub(
        r'<ul(\s+class="toc")?>',
        '<ul class="toc" style="list-style:none; text-align:left; padding:0 16px 0 16px;">',
        html,
        flags=re.IGNORECASE,
    )

    # Ensure links inside TOC have consistent inline style (color + no extra spacing)
    html = re.sub(
        r'(<ul[^>]*class="toc"[^>]*>)(.*?)</ul>',
        lambda m: m.group(1)
        + re.sub(
            r'<a([^>]*)>',
            lambda a: ("<a" + a.group(1) + " style=\"color:#103040; text-decoration:none; margin:0; padding:0;\">"),
            m.group(2),
            flags=re.IGNORECASE,
        )
        + '</ul>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Insert <hr> after TOC when followed by a section/h2
    html = re.sub(
        r'(</ul>)(\s*<(section|h2)[^>]*>)',
        r"\1\n<hr style=\"border:none;border-top:1px solid #eee;margin:24px 0;\">\2",
        html,
        flags=re.IGNORECASE,
    )

    # --- Ensure anchors have reset style (add if missing, otherwise append minimal resets) ---
    # 1) Anchors that already have style attribute: append missing reset tokens
    def _fix_anchor_with_style(m):
        attrs = m.group(1)
        style_match = re.search(r'style="([^"]*)"', attrs, flags=re.IGNORECASE)
        if style_match:
            style = style_match.group(1)
            style = _ensure_attr(style, 'margin:0')
            style = _ensure_attr(style, 'padding:0')
            style = _ensure_attr(style, 'border:none')
            new_attrs = re.sub(r'style="[^"]*"', f'style="{style}"', attrs, flags=re.IGNORECASE)
            return '<a' + new_attrs + '>'
        return '<a' + attrs + '>'

    html = re.sub(r'<a([^>]*)>', _fix_anchor_with_style, html, flags=re.IGNORECASE)

    # --- Ensure images have safe inline resets ---
    def _fix_img(m):
        attrs = m.group(1)
        # find existing style
        style_match = re.search(r'style="([^"]*)"', attrs, flags=re.IGNORECASE)
        base = 'margin:0;padding:0;border:none;display:block;max-width:100%;height:auto;'
        if style_match:
            style = style_match.group(1)
            # merge but avoid duplicates
            for tok in ['margin:0', 'padding:0', 'border:none', 'display:block', 'max-width:100%', 'height:auto']:
                if tok not in style:
                    style += tok + ';'
            new_attrs = re.sub(r'style="[^"]*"', f'style="{style}"', attrs, flags=re.IGNORECASE)
            return '<img' + new_attrs + '>'
        else:
            return '<img' + attrs + f' style="{base}">'

    html = re.sub(r'<img([^>]*)>', _fix_img, html, flags=re.IGNORECASE)

    # --- Ensure table/td collapse and td border resets ---
    # Add border-collapse and border:none to tables
    def _fix_table(m):
        attrs = m.group(1)
        style_match = re.search(r'style="([^"]*)"', attrs, flags=re.IGNORECASE)
        if style_match:
            style = style_match.group(1)
            if 'border-collapse' not in style:
                style += 'border-collapse:collapse;'
            if 'border:none' not in style:
                style += 'border:none;'
            new_attrs = re.sub(r'style="[^"]*"', f'style="{style}"', attrs, flags=re.IGNORECASE)
            return '<table' + new_attrs + '>'
        else:
            return '<table' + attrs + ' style="border-collapse:collapse;border:none;">'

    html = re.sub(r'<table([^>]*)>', _fix_table, html, flags=re.IGNORECASE)

    # Ensure td have border:none if style exists or add minimal style
    def _fix_td(m):
        attrs = m.group(1)
        style_match = re.search(r'style="([^"]*)"', attrs, flags=re.IGNORECASE)
        if style_match:
            style = style_match.group(1)
            if 'border:none' not in style and 'border: none' not in style:
                style += 'border:none;'
            new_attrs = re.sub(r'style="[^"]*"', f'style="{style}"', attrs, flags=re.IGNORECASE)
            return '<td' + new_attrs + '>'
        else:
            return '<td' + attrs + ' style="border:none;">'

    html = re.sub(r'<td([^>]*)>', _fix_td, html, flags=re.IGNORECASE)

    # --- Minor cosmetic normalization: shorten multiple blank lines ---
    html = re.sub(r'\n{3,}', '\n\n', html)

    return html
