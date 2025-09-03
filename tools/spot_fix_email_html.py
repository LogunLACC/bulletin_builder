#!/usr/bin/env python3
"""
Spot-fix legacy EMAIL HTML files in place:
  - Convert known-safe .avif[?query] -> .jpg
  - (Optionally) enforce basic style starts if missing
"""
import sys
import re
from pathlib import Path

RX = re.compile(r'(?i)(?P<attr>\b(?:src|href)\s*=\s*["\'])(?P<url>https?://(?P<host>[^/"\']+)[^"\']*\.avif(?:\?[^"\']*)?)(?P<rest>["\'])')
SAFE_HOSTS = ("cdn-ip.allevents.in","allevents.in","lakealmanorcountryclub.com","googleusercontent.com","imgur.com")

def avif_to_jpg_email_only(html: str) -> str:
    def _sub(m):
        host = m.group('host').lower()
        if not any(h in host for h in SAFE_HOSTS):
            return m.group(0)
        u = m.group('url')
        if '.avif?' in u.lower():
            base, q = u.rsplit('.avif', 1)
            return f'{m.group("attr")}{base}.jpg{q}{m.group("rest")}'
        return f'{m.group("attr")}{u[:-5]}.jpg{m.group("rest")}'
    return RX.sub(_sub, html)

def touch_up_styles(html: str) -> str:
    # Light-handed: only fix obvious misses
    html = re.sub(r'(?is)<a\b(?![^>]*\bstyle=)', r'<a style="margin:0; padding:0;"', html)
    html = re.sub(r'(?is)<img\b(?![^>]*\bstyle=)', r'<img style="margin:0; padding:0; border:none;"', html)
    html = re.sub(r'(?is)<table\b(?![^>]*\bstyle=)', r'<table style="border-collapse: collapse;"', html)
    html = re.sub(r'(?is)<td\b(?![^>]*\bstyle=)', r'<td style="border:none;"', html)
    return html

def main(paths):
    changed = 0
    for p in paths:
        path = Path(p)
        if not path.exists(): 
            print(f"!! missing: {p}")
            continue
        src = path.read_text(encoding="utf-8", errors="replace")
        out = avif_to_jpg_email_only(src)
        out = touch_up_styles(out)
        if out != src:
            path.write_text(out, encoding="utf-8")
            print(f"fixed: {p}")
            changed += 1
        else:
            print(f"ok:    {p}")
    print(f"done. changed={changed}/{len(paths)}")
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: tools/spot_fix_email_html.py user_drafts/foo.html [...]")
        sys.exit(2)
    main(sys.argv[1:])
