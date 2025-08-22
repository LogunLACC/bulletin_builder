# bulletin_email_postprocess.py
"""
Post-process exported bulletin HTML for email compatibility and style fixes.
"""
import re

def process_html(html: str) -> str:
    """
    Post-process the exported HTML for email compatibility and style fixes.
    - Normalizes the TOC (ul) styles.
    - Inserts <hr> after TOC.
    - Fixes announcement padding.
    - Idempotent: safe to run multiple times.
    """
    # Normalize TOC <ul> styles
    html = re.sub(
        r'<ul(\s+class="toc")?>',
        '<ul class="toc" style="list-style:none; text-align:left; padding:0 16px 0 16px;">',
        html,
        flags=re.IGNORECASE
    )
    # Insert <hr> after TOC (after </ul> that is followed by <section or <h2)
    html = re.sub(
        r'(</ul>)(\s*<(section|h2)[^>]*>)',
        r'\1\n<hr style="border:none;border-top:1px solid #eee;margin:24px 0;">\2',
        html,
        flags=re.IGNORECASE
    )
    # Fix announcement padding: td style="padding:12px 0 12px 0;..." => padding:12px 16px;
    html = re.sub(
        r'(td[^>]+style=")padding:12px 0 12px 0;([^\"]*)"',
        r'\1padding:12px 16px;\2"',
        html,
        flags=re.IGNORECASE
    )
    return html
