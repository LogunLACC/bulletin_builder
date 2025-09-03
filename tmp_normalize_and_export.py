import json
from pathlib import Path
from copy import deepcopy
from bulletin_builder.app_core import exporter

p = Path('user_drafts/TestEverything.json')
if not p.exists():
    print('ERROR: TestEverything.json not found at', p)
    raise SystemExit(2)

raw = json.loads(p.read_text(encoding='utf-8'))
ctx = deepcopy(raw)
if 'sections' not in ctx:
    print('No sections in JSON')
    raise SystemExit(1)

# Normalize sections for exporter expectations
for s in ctx['sections']:
    stype = s.get('type','')
    # custom_text: exporter expects content to be dict with 'text'
    if stype == 'custom_text' and isinstance(s.get('content'), str):
        s['content'] = {'text': s['content']}
    # community_events / lacc_events -> map to type 'events'
    if stype in ('community_events','lacc_events'):
        s['type'] = 'events'
    # events: ensure content is a list of events with 'title' and 'date'
    if s.get('type') == 'events':
        content = s.get('content') or []
        if isinstance(content, dict):
            content = [content]
            s['content'] = content
        new_ev = []
        for ev in content:
            # prefer existing title, else build from description
            title = ev.get('title') or ev.get('description') or ev.get('name') or ''
            # build date string
            date = ev.get('date','')
            time = ev.get('time','')
            when = (date + (' ' + time if time else '')).strip()
            collapsed = {'title': title, 'date': when}
            # copy other helpful fields if present
            if ev.get('image_url'):
                collapsed['image'] = ev.get('image_url')
            new_ev.append(collapsed)
        s['content'] = new_ev
    # announcements: ensure content is list
    if stype == 'announcements' and not isinstance(s.get('content'), list):
        s['content'] = []
    # image: exporter doesn't support image in email; move src into content for web renderer
    if stype == 'image' and 'src' in s:
        s['content'] = {'src': s.get('src'), 'alt': s.get('alt','')}

# add title/date if missing
if 'title' not in ctx:
    ctx['title'] = 'Test Export'
if 'date' not in ctx:
    ctx['date'] = 'August 29, 2025'

out_dir = Path('tmp_export')
out_dir.mkdir(exist_ok=True)
email_html = exporter.render_email_html(ctx)
web_html = exporter.render_bulletin_html(ctx)

email_path = out_dir / 'TestEverything_email_normalized.html'
web_path = out_dir / 'TestEverything_web_normalized.html'
email_path.write_text(email_html, encoding='utf-8')
web_path.write_text(web_html, encoding='utf-8')
print('WROTE', email_path)
print('WROTE', web_path)
