from pathlib import Path
from bulletin_builder.postprocess.bulletin_email_postprocess import process_html

p = Path('tmp_export')
if not p.exists():
    print('tmp_export does not exist')
    raise SystemExit(2)

files = sorted(p.glob('*email*.html'))
if not files:
    print('No email files found in tmp_export')
    raise SystemExit(0)

for f in files:
    try:
        html = f.read_text(encoding='utf-8')
    except Exception as e:
        print('Failed to read', f, e)
        continue
    fixed = process_html(html)
    out = f.with_name(f.stem + '_fixed.html')
    out.write_text(fixed, encoding='utf-8')
    print('WROTE', out)
