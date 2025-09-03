import json
from pathlib import Path
from bulletin_builder.app_core import exporter

p = Path('user_drafts/TestEverything.json')
if not p.exists():
    print('ERROR: TestEverything.json not found at', p)
    raise SystemExit(2)

ctx = json.loads(p.read_text(encoding='utf-8'))
out_dir = Path('tmp_export')
out_dir.mkdir(exist_ok=True)

email_html = exporter.render_email_html(ctx)
web_html = exporter.render_bulletin_html(ctx)

email_path = out_dir / 'TestEverything_email.html'
web_path = out_dir / 'TestEverything_web.html'

email_path.write_text(email_html, encoding='utf-8')
web_path.write_text(web_html, encoding='utf-8')

print('WROTE', email_path)
print('WROTE', web_path)
