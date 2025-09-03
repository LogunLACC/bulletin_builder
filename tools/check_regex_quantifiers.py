import pathlib
import sys
# prefer the canonical location if present
p1 = pathlib.Path('src/sanitize.py')
p2 = pathlib.Path('src/bulletin_builder/app_core/sanitize.py')
if p1.exists():
    txt = p1.read_text()
elif p2.exists():
    txt = p2.read_text()
else:
    print("ERROR: sanitize.py not found in expected locations")
    sys.exit(1)
ok = ('(?:"[^"]*"|\'[^\']*\')' in txt) or ('(?\\:"[^\\"]*"|\\\'[^\\\']*\\\')' in txt)
if not ok:
    print("ERROR: on* stripping regex missing '*' quantifiers in sanitize.py")
    sys.exit(1)
print("regex-quantifiers-check: OK")
