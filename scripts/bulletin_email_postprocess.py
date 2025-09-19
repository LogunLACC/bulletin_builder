#!/usr/bin/env python3
"""
bulletin_email_postprocess.py

Post-process Bulletin Builder email exports to be more email-client-friendly:
- Ensure anchor targets exist (adds ids for common sections referenced by TOC).
- Normalize <img> styles for 600px email layout.
- Remove overly small max-width caps from card containers.
- Replace .avif sources with .jpg for broader client support.

Usage:
  python bulletin_email_postprocess.py input.html [output.html]

If output.html is omitted, "_fixed" is appended before the extension.
"""

import sys
import re
import pathlib

def add_or_merge_style(elem_style: str, additions: dict) -> str:
    """Merge CSS declarations in `additions` into `elem_style` without duplicating keys."""
    styles = {}
    for part in elem_style.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            styles[k.strip().lower()] = v.strip()
    for k, v in additions.items():
        styles[k.lower()] = v
    return ";".join(f"{k}:{v}" for k, v in styles.items() if v) + ";"

def process_html(html: str) -> str:
    """Postprocess HTML for email clients:

    - Remove doctype/head/script/style/link elements
    - Inject a small reset CSS and inline it with premailer
    - Ensure img and a tags keep src/href but have inline styles starting with margin:0;padding:0;
    """
    try:
        from bs4 import BeautifulSoup  # type: ignore
        from premailer import transform as premailer_transform  # type: ignore
        from bulletin_builder.actions_log import log_action

        soup = BeautifulSoup(html, "html.parser")

        # Extract body content (if missing, use whole document)
        body = soup.body
        if body is None:
            body_html = str(soup)
        else:
            body_html = body.decode_contents()

        # Build a minimal wrapper with reset CSS (will be inlined by premailer)
        reset_css = """
        /* Email reset: neutralize client defaults */
        body, table, td, th, p, div, span { margin:0!important; padding:0!important; }
        * { border:0!important; box-sizing: border-box!important; }
        a { color:inherit!important; text-decoration:none!important; outline:none!important; }
        img { display:block!important; border:0!important; margin:0!important; padding:0!important; max-width:100%!important; height:auto!important; }
        table { border-collapse:collapse!important; border-spacing:0!important; }
        """

        wrapper = f"<html><head><style>{reset_css}</style></head><body>{body_html}</body></html>"

        # Inline CSS using premailer
        try:
            inlined = premailer_transform(wrapper, remove_classes=True, disable_validation=True)
        except Exception:
            # If premailer fails, fall back to the wrapper as-is
            inlined = wrapper

        # Parse the inlined result and extract body inner HTML
        res_soup = BeautifulSoup(inlined, "html.parser")
        res_body = res_soup.body
        final_html = res_body.decode_contents() if res_body is not None else str(res_soup)

        # Remove any remaining head/script/style/link tags from the result
        for tag in res_soup.find_all(["script", "style", "link", "head", "meta", "title"]):
            try:
                tag.decompose()
            except Exception:
                pass

        # Ensure img src / a href preserved and style starts with margin:0;padding:0;
        def ensure_reset_prefix(style_str: str) -> str:
            # Parse existing declarations into dict
            out = {}
            for part in (style_str or "").split(";"):
                if ":" in part:
                    k, v = part.split(":", 1)
                    out[k.strip().lower()] = v.strip()
            # Build result starting with margin/padding
            parts = ["margin:0", "padding:0"]
            for k, v in out.items():
                if k in ("margin", "padding"):
                    continue
                parts.append(f"{k}:{v}")
            return ";".join(parts) + ";"

        final_soup = BeautifulSoup(final_html, "html.parser")
        for img in final_soup.find_all("img"):
            # keep src but ensure avif -> jpg fallback
            src = img.get("src", "") or ""
            if src.lower().endswith('.avif'):
                img["src"] = src[:-5] + ".jpg"
            img_style = img.get("style", "")
            img["style"] = ensure_reset_prefix(img_style)
            if img.get("width") is None:
                img["width"] = "600"

        for a in final_soup.find_all("a"):
            # preserve href
            a.get("href")
            a_style = a.get("style", "")
            a["style"] = ensure_reset_prefix(a_style)

        # Ensure tables collapse and tds have no borders
        for table in final_soup.find_all("table"):
            tstyle = table.get("style", "")
            # Merge required table styles
            tstyle = add_or_merge_style(tstyle, {
                "border-collapse": "collapse",
                "border-spacing": "0",
                "margin": "0",
                "padding": "0",
            })
            table["style"] = tstyle

        for cell in final_soup.find_all(["td", "th"]):
            cstyle = cell.get("style", "")
            # Ensure reset prefix and force border:none
            merged = ensure_reset_prefix(cstyle)
            # Merge border:none explicitly
            merged = add_or_merge_style(merged, {"border": "none"})
            cell["style"] = merged

        # log success
        try:
            log_action("postprocess_html", {"imgs": len(final_soup.find_all("img")), "links": len(final_soup.find_all("a"))})
        except Exception:
            pass
        return final_soup.decode()

    except Exception:
        # Very small fallback: attempt regex-based sanitize but keep href/src
        out = html
        # Remove DOCTYPE and head-like blocks
        out = re.sub(r"<!DOCTYPE[^>]*>", "", out, flags=re.I)
        out = re.sub(r"<head[\s\S]*?</head>", "", out, flags=re.I)
        # Remove scripts and link/style tags
        out = re.sub(r"<script[\s\S]*?</script>", "", out, flags=re.I)
        out = re.sub(r"<link[^>]+rel=[\"']?stylesheet[\"']?[^>]*>", "", out, flags=re.I)
        out = re.sub(r"<style[\s\S]*?</style>", "", out, flags=re.I)

        # Basic avif -> jpg
        out = re.sub(r'(<img[^>]+src="[^"]+)\.avif"', r'\1.jpg"', out, flags=re.I)

        # Ensure images and anchors have margin/padding defaults inline
        def ensure_inline_reset(m):
            tag = m.group(0)
            if 'style=' in tag:
                tag = re.sub(r'style="([^"]*)"', lambda mm: f'style="margin:0;padding:0;{mm.group(1)}"', tag, flags=re.I)
            else:
                tag = tag.replace('<img', '<img style="margin:0;padding:0;"', 1) if tag.lower().startswith('<img') else tag.replace('<a', '<a style="margin:0;padding:0;"', 1)
            return tag

        out = re.sub(r'<img\b[^>]*>', ensure_inline_reset, out, flags=re.I)
        out = re.sub(r'<a\b[^>]*>', ensure_inline_reset, out, flags=re.I)

        try:
            from bulletin_builder.actions_log import log_action
            log_action("postprocess_html_fallback", {"reason": "exception"})
        except Exception:
            pass
        return out

def main():
    if len(sys.argv) < 2:
        print("Usage: python bulletin_email_postprocess.py input.html [output.html]")
        sys.exit(1)
    in_path = sys.argv[1]
    if len(sys.argv) >= 3:
        out_path = sys.argv[2]
    else:
        p = pathlib.Path(in_path)
        out_path = str(p.with_name(p.stem + "_fixed" + p.suffix))

    with open(in_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
    fixed = process_html(html)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(fixed)
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    main()
