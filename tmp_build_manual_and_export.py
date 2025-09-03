import json
from pathlib import Path
from copy import deepcopy
from bulletin_builder.app_core import exporter

p = Path('user_drafts/ManualDraft.json')
if not p.exists():
    print('ERROR: ManualDraft.json not found at', p)
    raise SystemExit(2)

raw = json.loads(p.read_text(encoding='utf-8'))
ctx = deepcopy(raw)

# Normalization (same rules as previous normalizer)
for s in ctx.get('sections', []):
    stype = s.get('type','')
    if stype == 'custom_text' and isinstance(s.get('content'), str):
        s['content'] = {'text': s['content']}
    if stype in ('community_events','lacc_events'):
        s['type'] = 'events'
    if s.get('type') == 'events':
        content = s.get('content') or []
        if isinstance(content, dict):
            content = [content]
            s['content'] = content
        new_ev = []
        for ev in content:
            title = ev.get('title') or ev.get('description') or ''
            date = ev.get('date','')
            time = ev.get('time','')
            when = (date + (' ' + time if time else '')).strip()
            collapsed = {'title': title, 'date': when}
            if ev.get('image_url'):
                collapsed['image'] = ev.get('image_url')
            new_ev.append(collapsed)
        s['content'] = new_ev
    if stype == 'announcements' and not isinstance(s.get('content'), list):
        s['content'] = []
    if stype == 'image' and 'src' in s:
        s['content'] = {'src': s.get('src'), 'alt': s.get('alt','')}

if 'title' not in ctx:
    ctx['title'] = 'Manual Draft'
if 'date' not in ctx:
    ctx['date'] = ''

out_dir = Path('tmp_export')
out_dir.mkdir(exist_ok=True)

email_html = exporter.render_email_html(ctx)
web_html = exporter.render_bulletin_html(ctx)

email_path = out_dir / 'ManualDraft_email_normalized.html'
web_path = out_dir / 'ManualDraft_web_normalized.html'
email_path.write_text(email_html, encoding='utf-8')
web_path.write_text(web_html, encoding='utf-8')
print('WROTE', email_path)
print('WROTE', web_path)
