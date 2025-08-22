import sys
from pathlib import Path
from bulletin_builder.postprocess import ensure_postprocessed

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/postprocess_html.py INPUT.html [OUTPUT.html]")
        raise SystemExit(2)
    inp = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else inp.with_name(inp.stem + "_postprocessed.html")
    html = inp.read_text(encoding="utf-8", errors="ignore")
    html = ensure_postprocessed(html)
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
