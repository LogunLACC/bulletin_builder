"""
FrontSteps-focused HTML postprocessor.

Transforms a rendered bulletin HTML into a body-only, FrontSteps-safe
fragment that follows the key requirements from
.github/.agent_rules/bulletin_frontsteps_rules.yaml.

Key goals (best-effort, idempotent):
- Output body-only HTML (no doctype/html/head/body/style/script wrappers)
- Ensure absolute URLs for href/src (http/https only)
- Enforce inline style starts for a/img/table/td
- Normalize typography for h1–h4 minimally (explicit sizes, line-height)
- Add alt text to images and safe defaults
- Remove internal anchors and comments

Notes:
- We leverage the email renderer’s table-based structure, then further
  constrain and normalize it for FrontSteps paste-in.
- For images where intrinsic dimensions are unknown, we avoid forcing
  a potentially-wrong height attribute; width defaults to container width
  when absent. If a strict height attribute is required later, image
  dimension probing can be added.
"""

from __future__ import annotations

import re
from html import unescape


_RX_BODY = re.compile(r"(?is)<body[^>]*>(.*?)</body>")
_RX_TAG = {
    "a": re.compile(r"(?is)<a([^>]*)>(.*?)</a>"),
    "img": re.compile(r"(?is)<img([^>]*)>"),
    "table": re.compile(r"(?is)<table([^>]*)>"),
    "td": re.compile(r"(?is)<td([^>]*)>"),
    "h1": re.compile(r"(?is)<h1([^>]*)>(.*?)</h1>"),
    "h2": re.compile(r"(?is)<h2([^>]*)>(.*?)</h2>"),
    "h3": re.compile(r"(?is)<h3([^>]*)>(.*?)</h3>"),
    "h4": re.compile(r"(?is)<h4([^>]*)>(.*?)</h4>"),
    # comments
    "comment": re.compile(r"(?s)<!--.*?-->")
}

_RX_FORBIDDEN_WRAPPERS = (
    re.compile(r"(?is)<!DOCTYPE.*?>"),
    re.compile(r"(?is)<\/?(?:html|head|style|script|link|iframe|svg|form)\b[^>]*>"),
)

# Unwrap <center> tags entirely (FrontSteps prefers table alignment)
_RX_CENTER_OPEN = re.compile(r"(?is)<center\b[^>]*>")
_RX_CENTER_CLOSE = re.compile(r"(?is)</center>")

_RX_ATTR = {
    "href": re.compile(r"(?is)\bhref\s*=\s*([\"\'])(.*?)\1"),
    "src": re.compile(r"(?is)\bsrc\s*=\s*([\"\'])(.*?)\1"),
    "style": re.compile(r"(?is)\bstyle\s*=\s*([\"\'])(.*?)\1"),
    "alt": re.compile(r"(?is)\balt\s*=\s*([\"\'])(.*?)\1"),
    "width": re.compile(r"(?is)\bwidth\s*=\s*([\"\'])(.*?)\1"),
    "height": re.compile(r"(?is)\bheight\s*=\s*([\"\'])(.*?)\1"),
    "rel": re.compile(r"(?is)\brel\s*=\s*([\"\'])(.*?)\1"),
    "target": re.compile(r"(?is)\btarget\s*=\s*([\"\'])(.*?)\1"),
}


def _strip_wrappers_and_extract_body(html: str) -> str:
    m = _RX_BODY.search(html)
    if m:
        content = m.group(1)
    else:
        content = html
    # Remove any doctype/html/head/style/script/link/iframe/svg/form wrappers
    for rx in _RX_FORBIDDEN_WRAPPERS:
        content = rx.sub("", content)
    # Remove now any residual closing body/html if they slipped through
    content = re.sub(r"(?is)</?body[^>]*>", "", content)
    content = re.sub(r"(?is)</?html[^>]*>", "", content)
    # Unwrap center tags
    content = _RX_CENTER_OPEN.sub("", content)
    content = _RX_CENTER_CLOSE.sub("", content)
    # Drop HTML comments
    content = _RX_TAG["comment"].sub("", content)
    return content.strip()


def _ensure_style_prefix(style_value: str, required_prefix: str) -> str:
    style_value = (style_value or "").strip()
    # Normalize style string; ensure trailing semicolon
    if style_value and not style_value.endswith(";"):
        style_value += ";"
    # Remove any duplicate required tokens to avoid reordering oddities
    req_tokens = [t.strip() for t in required_prefix.split(";") if t.strip()]
    rest = style_value
    for tok in req_tokens:
        # remove occurrences of token followed by optional whitespace and semicolon
        rest = re.sub(rf"(?i)\b{re.escape(tok)}\s*;?\s*", "", rest)
    # Build with required tokens first, then the remaining style
    prefix = required_prefix
    if not prefix.endswith(";"):
        prefix += ";"
    merged = prefix + rest
    # Collapse multiple semicolons/spaces
    merged = re.sub(r";{2,}", ";", merged)
    merged = re.sub(r"\s+", " ", merged).strip()
    return merged


def _attrs_set(attrs: str, name: str, value: str) -> str:
    # Replace existing or append new quoted attribute
    rx = _RX_ATTR.get(name)
    if rx and rx.search(attrs):
        attrs = rx.sub(lambda m: f"{name}=\"{value}\"", attrs)
    else:
        # Trim whitespace and any stray self-close slash left by original tags
        attrs = attrs.strip()
        if attrs.endswith('/'):
            attrs = attrs[:-1].strip()
        if attrs and not attrs.endswith(" "):
            attrs += " "
        attrs += f'{name}="{value}"'
    return attrs


def _attrs_del(attrs: str, name: str) -> str:
    rx = _RX_ATTR.get(name)
    if rx:
        attrs = rx.sub("", attrs)
    return attrs


def _cleanup_attrs_spacing(attrs: str) -> str:
    # Normalize whitespace between attributes; drop any stray self-close slash
    attrs = re.sub(r"\s+", " ", attrs).strip()
    if attrs.endswith("/"):
        attrs = attrs[:-1].strip()
    return (" " + attrs) if attrs else ""


def _process_anchor(attrs: str, inner: str) -> str:
    href_m = _RX_ATTR["href"].search(attrs)
    href = href_m.group(2) if href_m else ""
    # If href is not absolute http/https, drop the link and keep text
    if not href or not re.match(r"(?i)^https?://", href):
        # Always output <span style="margin:0; padding:0; text-decoration:underline;">x</span> for any non-absolute anchor
        return f'<span style="margin:0; padding:0; text-decoration:underline;">{inner}</span>'

    # External/absolute link: enforce style start and rel/target
    style_m = _RX_ATTR["style"].search(attrs)
    if style_m:
        fixed = _ensure_style_prefix(style_m.group(2), "margin:0; padding:0; text-decoration:underline;")
        attrs = _RX_ATTR["style"].sub(lambda m: f'style="{fixed}"', attrs)
    else:
        attrs = _attrs_set(attrs, "style", "margin:0; padding:0; text-decoration:underline;")
    # Add rel/target safety
    attrs = _attrs_set(attrs, "rel", "noopener noreferrer")
    attrs = _attrs_set(attrs, "target", "_blank")
    return f"<a{_cleanup_attrs_spacing(attrs)}>{inner}</a>"


def _process_img(attrs: str) -> str:
    # Ensure style starts with img resets
    style_m = _RX_ATTR["style"].search(attrs)
    if style_m:
        fixed = _ensure_style_prefix(style_m.group(2), "margin:0; padding:0; border:none;")
        attrs = _RX_ATTR["style"].sub(lambda m: f'style="{fixed}"', attrs)
    else:
        attrs = _attrs_set(attrs, "style", "margin:0; padding:0; border:none;")

    # Ensure absolute src
    src_m = _RX_ATTR["src"].search(attrs)
    src = src_m.group(2) if src_m else ""
    if not src or not re.match(r"(?i)^https?://", src):
        # Drop src to avoid broken/relative references
        attrs = _attrs_del(attrs, "src")

    # Ensure alt attribute exists (empty if unknown)
    if not _RX_ATTR["alt"].search(attrs):
        attrs = _attrs_set(attrs, "alt", "")

    # Width/height attributes: favor width when container is 600px; try to infer height
    width_val = None
    w_m = _RX_ATTR["width"].search(attrs)
    if w_m:
        width_val = w_m.group(2)
    else:
        width_val = "600"
        attrs = _attrs_set(attrs, "width", width_val)

    # Try to infer height from src patterns like 600x400 or rs:fill:500:250
    height_val = None
    if src_m:
        s = src_m.group(2)
        m_wh = re.search(r"(?i)/(\d{2,4})x(\d{2,4})(?:\D|$)", s)
        if m_wh:
            height_val = m_wh.group(2)
        else:
            m_fill = re.search(r"(?i)rs:fill:(\d{2,4}):(\d{2,4})", s)
            if m_fill:
                height_val = m_fill.group(2)
    if height_val and height_val.isdigit():
        attrs = _attrs_set(attrs, "height", height_val)
    
    return f"<img{_cleanup_attrs_spacing(attrs)} />"


def _process_table(attrs: str) -> str:
    style_m = _RX_ATTR["style"].search(attrs)
    if style_m:
        fixed = _ensure_style_prefix(style_m.group(2), "border-collapse:collapse; border-spacing:0;")
        attrs = _RX_ATTR["style"].sub(lambda m: f'style="{fixed}"', attrs)
    else:
        attrs = _attrs_set(attrs, "style", "border-collapse:collapse; border-spacing:0;")
    return f"<table{_cleanup_attrs_spacing(attrs)}>"


def _process_td(attrs: str) -> str:
    style_m = _RX_ATTR["style"].search(attrs)
    if style_m:
        fixed = _ensure_style_prefix(style_m.group(2), "border:none;")
        attrs = _RX_ATTR["style"].sub(lambda m: f'style="{fixed}"', attrs)
    else:
        attrs = _attrs_set(attrs, "style", "border:none;")
    return f"<td{_cleanup_attrs_spacing(attrs)}>"


def _ensure_heading(tag: str, attrs: str, inner: str) -> str:
    # Apply explicit font and sizing for h1-h4
    defaults = {
        "h1": "font-family: Arial, Helvetica, sans-serif; font-weight:bold; font-size:24px; line-height:1.3; color:#103040;",
        "h2": "font-family: Arial, Helvetica, sans-serif; font-weight:bold; font-size:20px; line-height:1.3; color:#103040;",
        "h3": "font-family: Arial, Helvetica, sans-serif; font-weight:bold; font-size:18px; line-height:1.3; color:#103040;",
        "h4": "font-family: Arial, Helvetica, sans-serif; font-weight:bold; font-size:16px; line-height:1.3; color:#103040;",
    }
    style_m = _RX_ATTR["style"].search(attrs)
    if style_m:
        # Ensure the heading defaults exist (append if missing tokens)
        style = style_m.group(2)
        needed = defaults[tag]
        # Merge in a simple way without duplicating tokens
        for tok in [t.strip() for t in needed.split(";") if t.strip()]:
            if tok not in style:
                style += (";" if style and not style.endswith(";") else "") + tok
        attrs = _RX_ATTR["style"].sub(lambda m: f'style="{style}"', attrs)
    else:
        attrs = _attrs_set(attrs, "style", defaults[tag])
    return f"<{tag}{_cleanup_attrs_spacing(attrs)}>{inner}</{tag}>"


def process_frontsteps_html(html: str) -> str:
    """
    Convert an HTML document into a body-only FrontSteps-safe fragment.
    Idempotent: safe to run multiple times.
    """
    # Extract body and remove forbidden wrappers/comments
    out = _strip_wrappers_and_extract_body(html)

    # 1) Normalize anchors
    def _fix_a(m):
        return _process_anchor(m.group(1) or "", m.group(2) or "")

    out = _RX_TAG["a"].sub(_fix_a, out)

    # 2) Normalize images
    def _fix_img(m):
        return _process_img(m.group(1) or "")

    out = _RX_TAG["img"].sub(_fix_img, out)

    # 3) Enforce table/td starts
    def _fix_table(m):
        return _process_table(m.group(1) or "")

    def _fix_td(m):
        return _process_td(m.group(1) or "")

    out = _RX_TAG["table"].sub(_fix_table, out)
    out = _RX_TAG["td"].sub(_fix_td, out)

    # 4) Headings (h1–h4) explicit typography
    for tag in ("h1", "h2", "h3", "h4"):
        rx = _RX_TAG[tag]
        def _fix_h(m, t=tag):
            return _ensure_heading(t, m.group(1) or "", m.group(2) or "")
        out = rx.sub(_fix_h, out)

    # 5) Remove residual HTML comments
    out = _RX_TAG["comment"].sub("", out)

    # 6) Unescape encoded HTML blocks inside <div> that look like embedded markup (from prior escaping)
    def _unescape_div_blocks(html_text: str) -> str:
        rx_div = re.compile(r"(?is)(<div[^>]*>)(?P<inner>(?:(?!</div>).)*)</div>")
        def _maybe_unescape(m):
            head, inner = m.group(1), m.group('inner')
            # Heuristic: if inner contains many entity-encoded angle brackets and almost no real '<', unescape
            if ('&lt;' in inner or '&gt;' in inner) and inner.count('<') < 3:
                decoded = unescape(inner)
                # After decoding, run minimal sanitization: strip forbidden wrappers/center/comments again
                tmp = decoded
                for rx in _RX_FORBIDDEN_WRAPPERS:
                    tmp = rx.sub("", tmp)
                tmp = _RX_CENTER_OPEN.sub("", tmp)
                tmp = _RX_CENTER_CLOSE.sub("", tmp)
                tmp = _RX_TAG['comment'].sub("", tmp)
                return head + tmp + "</div>"
            return m.group(0)
        return rx_div.sub(_maybe_unescape, html_text)

    out = _unescape_div_blocks(out)

    # 7) Trim excess whitespace lines
    out = re.sub(r"\n{3,}", "\n\n", out)

    return out.strip()
