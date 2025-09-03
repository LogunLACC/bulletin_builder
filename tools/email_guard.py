#!/usr/bin/env python3
import sys
import subprocess
import re
import pathlib
import fnmatch
from typing import List

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATTERNS = [
    (re.compile(r"(?is)\s+on[a-z]+\s*="), 'Inline on* attributes are not allowed in email HTML.'),
    (re.compile(r"(?i)\.avif(?=(?:\?|$))"), 'AVIF is not allowed in email HTML.'),
    (re.compile(r"(?is)(?:src|href)\s*=\s*\"http://"), 'http:// links would trigger mixed-content warnings.'),
]


def changed_files() -> List[pathlib.Path]:
    try:
        base = subprocess.check_output(["git", "merge-base", "HEAD", "origin/main"], text=True).strip()
    except Exception:
        base = 'HEAD~1'
    out = subprocess.check_output(["git", "diff", "--name-only", f"{base}...HEAD"], text=True)
    return [ROOT / f.strip() for f in out.splitlines() if f.strip()]


def _apply_globs(paths: List[pathlib.Path], includes: List[str], excludes: List[str]) -> List[pathlib.Path]:
    if not includes:
        matched = set(paths)
    else:
        matched = set()
        for g in includes:
            for p in paths:
                if fnmatch.fnmatch(str(p.as_posix()), g):
                    matched.add(p)
    # apply excludes
    if excludes:
        for g in excludes:
            for p in list(matched):
                if fnmatch.fnmatch(str(p.as_posix()), g):
                    matched.discard(p)
    return sorted(matched)


def scan(paths: List[pathlib.Path]):
    violations = []
    for p in paths:
        if not p.exists() or p.suffix.lower() not in {'.html', '.htm'}:
            continue
        text = p.read_text(errors='replace')
        # Heuristic: only guard email-like outputs or templates
        is_emaily = ('Copy for Email' in text) or ('<table' in text and '<head' not in text) or ('email' in p.name.lower())
        if not is_emaily:
            continue
        for rx, msg in PATTERNS:
            if rx.search(text):
                violations.append((str(p.relative_to(ROOT)), msg))
    return violations


def _all_html_files() -> List[pathlib.Path]:
    return list(ROOT.rglob('*.html'))


def _parse_args(argv):
    includes = []
    excludes = []
    changed_only = False
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == '--include' and i + 1 < len(argv):
            includes.append(argv[i + 1])
            i += 2
        elif a == '--exclude' and i + 1 < len(argv):
            excludes.append(argv[i + 1])
            i += 2
        elif a == '--changed-only':
            changed_only = True
            i += 1
        else:
            # ignore unknown
            i += 1
    return includes, excludes, changed_only


if __name__ == '__main__':
    includes, excludes, changed_only = _parse_args(sys.argv)
    base_paths = changed_files() if changed_only else _all_html_files()
    paths = _apply_globs(base_paths, includes, excludes)
    viols = scan(paths)
    if viols:
        print('\nEmail guard violations:')
        for f, msg in viols:
            print(f" - {f}: {msg}")
        sys.exit(1)
    print('email_guard: OK')
