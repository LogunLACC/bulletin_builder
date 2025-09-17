from .bulletin_email_postprocess import process_html
from .frontsteps_postprocess import process_frontsteps_html

def ensure_postprocessed(html: str) -> str:
    """
    Apply the standard email/html post‑processing pipeline used across tests and UI:
    - Normalize TOC and insert HR after TOC
    - Enforce anchor/img/table/td inline resets and email‑safe tweaks
    - Convert simple CTA anchors (<p><a href>Text</a></p>) into VML + inline button blocks
    - Fix common announcement padding to add horizontal breathing room

    Idempotent by construction: running twice yields the same output.
    """
    from bulletin_builder.app_core.sanitize import sanitize_email_html
    import re

    out = process_html(html)
    out = sanitize_email_html(out)

    # Convert simple CTA <p><a ...>Label</a></p> into VML + styled anchor button
    def _cta_replace(m):
        attrs = m.group(1) or ""
        label = (m.group(2) or "").strip() or "More Info"
        href_m = re.search(r'(?is)\bhref\s*=\s*(["\'])(.*?)\1', attrs)
        href = href_m.group(2) if href_m else "#"
        # Make sure rel/target present
        if 'target=' not in attrs.lower():
            attrs += ' target="_blank"'
        if 'rel=' not in attrs.lower():
            attrs += ' rel="noopener"'
        # Non‑MSO anchor style
        anchor_style = (
            "margin:0; padding:0; display:inline-block; background-color:#103040; color:#ffffff; "
            "font-family:Arial, 'Helvetica Neue', Helvetica, sans-serif; font-size:16px; font-weight:bold; "
            "line-height:36px; min-height:36px; border-radius:4px; padding-left:14px; padding-right:14px; "
            "text-decoration:none; text-align:center;"
        )
        # Button block with VML for Outlook
        block = (
            '<div style="margin:0; padding:0; font-size:16px; line-height:1; display:inline-block;">'
            '<table role="presentation" style="border-collapse:collapse; border-spacing:0; margin:0 auto;" cellspacing="0" cellpadding="0">'
            '<tr><td style="border:none; padding:0; text-align:center;">'
            '<!--[if mso]>'
            f'<v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" href="{href}" arcsize="12%" stroke="f" fillcolor="#103040" style="height:36px; v-text-anchor:middle; width:120px;">'
            '<w:anchorlock/>'
            f'<center style="color:#ffffff; font-family:Arial, Helvetica, sans-serif; font-size:16px; font-weight:bold;">{label}</center>'
            '</v:roundrect>'
            '<![endif]-->'
            '<!--[if !mso]><!-- -->'
            f'<a style="{anchor_style}" href="{href}" target="_blank" rel="noopener">{label}</a>'
            '<!--<![endif]-->'
            '</td></tr></table></div>'
        )
        return block

    # Only convert when <p> contains exactly a single <a>
    out = re.sub(r'(?is)<p[^>]*>\s*<a([^>]*)>(.*?)</a>\s*</p>', _cta_replace, out)

    # Padding fix: convert paddings like 12px 0 12px 0 to 12px 16px for better readability
    out = re.sub(r'(?i)padding:\s*12px\s*0\s*12px\s*0', 'padding:12px 16px', out)

    return out

__all__ = ["process_html", "process_frontsteps_html", "ensure_postprocessed"]
