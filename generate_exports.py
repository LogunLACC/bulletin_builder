from pathlib import Path
import json
from importlib import import_module

exporter = import_module('bulletin_builder.app_core.exporter')

# pick a draft
p = Path('user_drafts/basic.json')
if not p.exists():
    drafts = list(Path('user_drafts').glob('*.json'))
    p = drafts[0] if drafts else None

if not p:
    ctx = {'title':'Auto Export','date':'2025-08-28','sections':[{'type':'custom_text','title':'Intro','content':{'text':'Generated export'}}]}
else:
    ctx = json.loads(p.read_text(encoding='utf8'))

exports_dir = Path('exports')
exports_dir.mkdir(exist_ok=True)

b_html = exporter.render_bulletin_html(ctx)
e_html = exporter.render_email_html(ctx)

(b_html_path := exports_dir / 'bulletin_basic.html').write_text(b_html, encoding='utf8')
(e_html_path := exports_dir / 'email_basic.html').write_text(e_html, encoding='utf8')
print('Wrote', b_html_path, e_html_path)
