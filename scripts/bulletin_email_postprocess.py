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

import sys, re, os, pathlib

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
    try:
        from bs4 import BeautifulSoup  # type: ignore
        soup = BeautifulSoup(html, "html.parser")

        # 1) Collect in-document anchor targets from TOC (href="#section-id")
        toc_ids = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("#") and len(href) > 1:
                toc_ids.add(href[1:].strip())

        # 2) Ensure common section ids exist by trying to match headings text or sections
        #    If id doesn't exist, create on a matching section/heading.
        #    We try: exact id on any element; else attach id to a heading with matching normalized text.
        def normalize_txt(t: str) -> str:
            return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")

        existing_ids = {tag.get("id") for tag in soup.find_all(attrs={"id": True})}
        existing_ids = {i for i in existing_ids if i}

        # Build a map from normalized heading text -> element
        heading_candidates = {}
        for hx in soup.find_all(["h1","h2","h3","h4","h5","h6"]):
            txt = (hx.get_text() or "").strip()
            if not txt:
                continue
            heading_candidates[normalize_txt(txt)] = hx

        for sec_id in toc_ids:
            if sec_id in existing_ids:
                continue
            # Try to find a heading whose normalized text equals the id
            target = heading_candidates.get(sec_id)
            if target is None:
                # Try to find a section-like container to attach to (first large heading fallback)
                target = soup.find(id=sec_id)
            if target is None:
                # Fallback heuristic: attach to the first h2
                target = soup.find("h2") or soup.find("h1")
            if target is not None:
                target["id"] = sec_id
                existing_ids.add(sec_id)

        # 3) Normalize <img> tags: block, full width (within 600px table), height auto
        for img in soup.find_all("img"):
            # Replace .avif with .jpg in src
            src = img.get("src", "")
            if src.endswith(".avif"):
                img["src"] = src[:-5] + ".jpg"
            style = img.get("style", "")
            style = add_or_merge_style(style, {
                "display": "block",
                "width": "100%",
                "max-width": "600px",
                "height": "auto",
                "border": "0",
                "line-height": "0",
                "outline": "none",
                "text-decoration": "none"
            })
            img["style"] = style
            # Set width attr to 600 for good measure in some clients
            img["width"] = "600"

        # 4) Remove tiny max-width caps from containers (e.g., 320px or 340px)
        for tag in soup.find_all(True):
            style = tag.get("style", "")
            if not style:
                continue
            # replace max-width:320px/340px/360px → 600px (or remove if it's inline columns)
            style_new = re.sub(r"max-width\s*:\s*(320|340|360)px\s*;?", "max-width:600px;", style, flags=re.I)
            if style_new != style:
                tag["style"] = style_new

        return str(soup)

    except Exception:
        # Fallback: do minimal regex-based fixes if BeautifulSoup isn't available
        out = html

        # Ensure .avif -> .jpg
        out = re.sub(r'(<img[^>]+src="[^"]+)\.avif"', r'\1.jpg"', out, flags=re.I)

        # Normalize images: append/merge basic style (best-effort)
        def fix_img_style(match):
            tag = match.group(0)
            # If style exists, merge; else add a style attribute
            if 'style=' in tag:
                tag = re.sub(
                    r'style="([^"]*)"',
                    lambda m: f'style="{m.group(1)};display:block;width:100%;max-width:600px;height:auto;border:0;line-height:0;outline:none;text-decoration:none;"',
                    tag, flags=re.I
                )
            else:
                tag = tag.replace("<img", '<img style="display:block;width:100%;max-width:600px;height:auto;border:0;line-height:0;outline:none;text-decoration:none;"')
            if ' width=' not in tag:
                tag = tag.replace("<img", '<img width="600"', 1)
            return tag

        out = re.sub(r'<img\b[^>]*>', fix_img_style, out, flags=re.I)

        # Remove small max-width caps
        out = re.sub(r'max-width\s*:\s*(320|340|360)px\s*;?', 'max-width:600px;', out, flags=re.I)

        # Anchor ids: if we see a #welcome/#community-events link, add bare IDs to first H2s as fallback
        if '#welcome' in out and 'id="welcome"' not in out:
            out = out.replace("<h2", '<h2 id="welcome"', 1)
        if '#community-events' in out and 'id="community-events"' not in out:
            out = out.replace("<h2", '<h2 id="community-events"', 1)

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
