"""Email HTML sanitizer to enforce LACC formatting rules."""

import re
from typing import List


def sanitize_email_html(html: str) -> str:
    """
    Sanitize HTML to enforce LACC email formatting rules:

    - <a> and <img> tags must start with style="margin:0; padding:0;"
    - <table> tags must contain border-collapse:collapse in their style
    - <td> tags must start with style="border:none;"
    - Strip <!doctype>, <head>...</head>, <link rel="stylesheet" ...>, <script>...</script>

    Args:
        html: The HTML string to sanitize

    Returns:
        The sanitized HTML string
    """
    # Strip unwanted tags
    html = _strip_unwanted_tags(html)

    # Prepend rules to <a> and <img> tags
    html = _prepend_rule(html, r'<a\s+([^>]*style="[^"]*)"[^>]*>', 'margin:0; padding:0;')
    html = _prepend_rule(html, r'<img\s+([^>]*style="[^"]*)"[^>]*>', 'margin:0; padding:0;')

    # Ensure <table> contains border-collapse:collapse
    html = _ensure_contains(html, r'<table\s+([^>]*style="[^"]*)"[^>]*>', 'border-collapse:collapse;')

    # Prepend border:none to <td> tags
    html = _prepend_rule(html, r'<td\s+([^>]*style="[^"]*)"[^>]*>', 'border:none;')

    return html


def _strip_unwanted_tags(html: str) -> str:
    """Strip unwanted tags from HTML."""
    # Strip doctype
    html = re.sub(r'<!DOCTYPE[^>]*>', '', html, flags=re.IGNORECASE)

    # Strip head tags and content
    html = re.sub(r'<head[^>]*>.*?</head>', '', html, flags=re.IGNORECASE | re.DOTALL)

    # Strip link tags
    html = re.sub(r'<link[^>]*>', '', html, flags=re.IGNORECASE)

    # Strip script tags and content
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)

    return html


def _prepend_rule(html: str, pattern: str, rule: str) -> str:
    """
    Prepend a CSS rule to existing style attributes.

    Args:
        html: The HTML string
        pattern: Regex pattern to match tags with style attributes
        rule: CSS rule to prepend

    Returns:
        HTML with rule prepended to matching style attributes
    """
    def replace_style(match):
        style_content = match.group(1)
        if not style_content.startswith(rule):
            return match.group(0).replace(style_content, rule + style_content)
        return match.group(0)

    return re.sub(pattern, replace_style, html, flags=re.IGNORECASE)


def _ensure_contains(html: str, pattern: str, rule: str) -> str:
    """
    Ensure a CSS rule is present in style attributes.

    Args:
        html: The HTML string
        pattern: Regex pattern to match tags with style attributes
        rule: CSS rule to ensure is present

    Returns:
        HTML with rule ensured in matching style attributes
    """
    def replace_style(match):
        style_content = match.group(1)
        if rule not in style_content:
            return match.group(0).replace(style_content, style_content + rule)
        return match.group(0)

    return re.sub(pattern, replace_style, html, flags=re.IGNORECASE)
