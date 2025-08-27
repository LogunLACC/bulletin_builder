#!/usr/bin/env python3
import sys, subprocess, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
PATTERNS = [
  (re.compile(r"(?is)\s+on[a-z]+\s*="), 'Inline on* attributes are not allowed in email HTML.'),
  (re.compile(r"(?i)\.avif(?=(?:\?|$))"), 'AVIF is not allowed in email HTML.'),
  (re.compile(r"(?is)(?:src|href)\s*=\s*\"http://"), 'http:// links would trigger mixed-content warnings.'),
]

def changed_files():
    try:
        base = subprocess.check_output(["git","merge-base","HEAD","origin/main"], text=True).strip()
    except Exception:
        base = 'HEAD~1'
    out = subprocess.check_output(["git","diff","--name-only",f"{base}...HEAD"], text=True)
    return [ROOT/f.strip() for f in out.splitlines() if f.strip()]

def scan(paths):
    violations = []
    for p in paths:
        if not p.exists() or p.suffix.lower() not in {'.html', '.htm'}:
            continue
        text = p.read_text(errors='replace')
        # Heuristic: only guard email-like outputs or templates
        is_emaily = ('Copy for Email' in text) or ('<table' in text and '<head' not in text) or ('email' in p.name.lower())
        if not is_emaily:
            continue
        for rx,msg in PATTERNS:
            if rx.search(text):
                violations.append((str(p.relative_to(ROOT)), msg))
    return violations

if __name__ == '__main__':
    paths = changed_files() if '--changed-only' in sys.argv else list(ROOT.rglob('*.html'))
    viols = scan(paths)
    if viols:
        print('\nEmail guard violations:')
        for f,msg in viols:
            print(f" - {f}: {msg}")
        sys.exit(1)
    print('email_guard: OK')
