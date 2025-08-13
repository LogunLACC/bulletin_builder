#!/usr/bin/env python3
# localize_images.py
"""
Usage:
  python localize_images.py bulletin.html --out updated.html --media-dir media \
      --public-prefix https://lakealmanorcountryclub.com/wp-content/uploads/2025/08/bulletin/

If you don't know the final WordPress path yet, omit --public-prefix and it'll use a relative media/ path.
"""
import argparse, base64, os, re, sys, hashlib
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from html.parser import HTMLParser
from io import BytesIO

# Pillow is used only for conversion; install with: pip install pillow
from PIL import Image

try:
    import pillow_avif  # registers AVIF with Pillow
except Exception:
    pass

LAKE_DOMAIN = "lakealmanorcountryclub.com"

def is_image_url(url: str) -> bool:
    return bool(re.search(r"\.(avif|webp|jpe?g|png|gif)(\?|$)", url, re.I))

def is_external(url: str) -> bool:
    host = urlsplit(url).netloc.lower()
    return host and LAKE_DOMAIN not in host

def extract_allevents_original(url: str) -> str | None:
    """
    Extract the original URL embedded in AllEvents 'cdn-*/s/...' links.
    Looks for a base64-like path segment starting with 'aHR0' anywhere in the URL.
    """
    try:
        path = urlsplit(url).path
        m = re.search(r"/(aHR0[0-9A-Za-z_\-]+)(?:[./]|$)", path)
        if not m:
            return None
        b64 = m.group(1)
        pad = "=" * (-len(b64) % 4)
        raw = base64.urlsafe_b64decode(b64 + pad).decode("utf-8", "ignore")
        return raw if raw.startswith("http") else None
    except Exception:
        return None

def fetch_bytes(url: str, timeout=20) -> bytes:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (image-localizer)"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()

def to_jpeg_bytes(data: bytes) -> bytes:
    im = Image.open(BytesIO(data))
    # Convert to RGB if needed (drops alpha)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    out = BytesIO()
    im.save(out, format="JPEG", quality=88, optimize=True, progressive=True)
    return out.getvalue()

def safe_name(seed: str, alt: str | None) -> str:
    base = (alt or "").strip()[:40] or urlsplit(seed).path.rsplit("/", 1)[-1]
    base = re.sub(r"[^A-Za-z0-9]+", "-", base).strip("-") or "image"
    h = hashlib.sha1(seed.encode()).hexdigest()[:8]
    return f"{base}-{h}.jpg".lower()

class Rewriter(HTMLParser):
    def __init__(self, media_dir: str, public_prefix: str | None):
        super().__init__(convert_charrefs=True)
        self.media_dir = media_dir
        self.public_prefix = public_prefix.rstrip("/") + "/" if public_prefix else None
        self.out = []
        self.downloaded = {}  # original_url -> public_path
        self.stack = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag.lower() == "img" and "src" in d and d["src"]:
            src = d["src"]
            new_src = self._localize(src, d.get("alt"))
            if new_src:
                d["src"] = new_src
        elif tag.lower() == "a" and "href" in d and d["href"] and is_image_url(d["href"]):
            href = d["href"]
            new_href = self._localize(href, None)
            if new_href:
                d["href"] = new_href

        self.out.append("<" + tag)
        for k, v in d.items():
            # keep original attribute order not guaranteed; fine for email HTML
            v = (v or "").replace('"', "&quot;")
            self.out.append(f' {k}="{v}"')
        self.out.append(">")

        self.stack.append(tag)

    def handle_endtag(self, tag):
        self.out.append(f"</{tag}>")
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_data(self, data): self.out.append(data)
    def handle_startendtag(self, tag, attrs):
        # Rare in this HTML, but handle self-closing <img/>
        d = dict(attrs)
        if tag.lower() == "img" and "src" in d and d["src"]:
            src = d["src"]
            new_src = self._localize(src, d.get("alt"))
            if new_src:
                d["src"] = new_src
        self.out.append("<" + tag)
        for k, v in d.items():
            v = (v or "").replace('"', "&quot;")
            self.out.append(f' {k}="{v}"')
        self.out.append(" />")

    def handle_comment(self, data): self.out.append(f"<!--{data}-->")
    def handle_entityref(self, name): self.out.append(f"&{name};")
    def handle_charref(self, name): self.out.append(f"&#{name};")

    def _localize(self, url: str, alt: str | None) -> str | None:
        original = url
        # only touch external images
        if not is_external(url):
            return None
        # fix Allevents avif -> original source
        if "allevents.in" in url and url.lower().endswith(".avif"):
            orig = extract_allevents_original(url)
            if orig:
                url = orig

        # If we already processed this exact URL, reuse
        if url in self.downloaded:
            return self.downloaded[url]

        # Download -> convert -> save
        try:
            data = fetch_bytes(url)
            jpg = to_jpeg_bytes(data)
            fname = safe_name(url, alt)
            os.makedirs(self.media_dir, exist_ok=True)
            local_path = os.path.join(self.media_dir, fname)
            with open(local_path, "wb") as f:
                f.write(jpg)
            public_path = (self.public_prefix + fname) if self.public_prefix else os.path.join(self.media_dir, fname).replace("\\", "/")
            self.downloaded[url] = public_path
            return public_path
        except Exception as e:
            # If anything fails, leave original URL untouched
            sys.stderr.write(f"[warn] Could not localize {url}: {e}\n")
            return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html_in", help="Path to your bulletin HTML file")
    ap.add_argument("--out", default="updated.html", help="Where to write the rewritten HTML")
    ap.add_argument("--media-dir", default="media", help="Folder to save downloaded images")
    ap.add_argument("--public-prefix", default=None,
                    help="Final public URL prefix (e.g., your WP uploads path). If omitted, uses relative media/ paths.")
    args = ap.parse_args()

    with open(args.html_in, "r", encoding="utf-8") as f:
        html = f.read()

    rewriter = Rewriter(args.media_dir, args.public_prefix)
    rewriter.feed(html)
    updated = "".join(rewriter.out)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(updated)

    print(f"Done. Saved {len(rewriter.downloaded)} images to '{args.media_dir}'.")
    for k, v in rewriter.downloaded.items():
        print(f"  {k}  ->  {v}")
    print(f"Rewritten HTML -> {args.out}")

if __name__ == "__main__":
    main()
