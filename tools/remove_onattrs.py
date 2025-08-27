#!/usr/bin/env python3
"""Remove inline on* attributes from HTML files in-place.
Usage: python tools/remove_onattrs.py [paths...]
If no paths are given, defaults to user_drafts/.
"""
import sys
from pathlib import Path
import re

# Use a triple-quoted raw-looking regex so we don't fight quoting inside the source
RX_ON = re.compile(r'''(?is)\s+on[a-z]+\s*=\s*(?:"[^"]*"|'[^']*')''')

paths = sys.argv[1:] or ['user_drafts']
changed = []
for p in paths:
    p = Path(p)
    if p.is_dir():
        files = list(p.rglob('*.html'))
    elif p.exists():
        files = [p]
    else:
        print(f"missing: {p}")
        continue
    for f in files:
        text = f.read_text(encoding='utf-8', errors='replace')
        new = RX_ON.sub('', text)
        if new != text:
            f.write_text(new, encoding='utf-8')
            changed.append(str(f))
            print(f'fixed: {f}')
        else:
            print(f'ok:    {f}')
print('done. changed=' + str(len(changed)))
