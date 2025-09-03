from pathlib import Path
from datetime import datetime
from bulletin_builder.app_core import exporter

out = Path('tmp_export')
out.mkdir(exist_ok=True)

ctx = {
    "title": "Full Test Bulletin",
    "date": datetime.now().strftime('%B %d, %Y'),
    "sections": [
        {"type": "custom_text", "title": "Intro Text", "content": {"text": "Welcome to the full test bulletin. This section contains some <b>HTML</b> and plain text."}},
        {"type": "events", "title": "Upcoming Events", "content": [
            {"title": "Board Meeting", "date": "Mon, Sep 1", "time": "10:00 AM", "description": "Monthly board meeting.", "image_url": "https://placehold.co/600x400?text=Board"},
            {"title": "Golf Tournament", "date": "Sat, Sep 6", "time": "08:00 AM", "description": "Charity golf.", "image_url": "https://placehold.co/600x400?text=Golf"}
        ]},
        {"type": "community_events", "title": "Community", "content": [
            {"date": "Sun, Sep 7", "time": "12:00 PM", "description": "Community picnic.", "image_url": "https://placehold.co/600x400?text=Picnic"}
        ]},
        {"type": "lacc_events", "title": "LACC Events", "content": [
            {"date": "Fri, Sep 12", "time": "6:00 PM", "description": "Member social.", "image_url": "https://placehold.co/600x400?text=Social"}
        ]},
        {"type": "image", "title": "Hero Image", "content": {}, "src": "https://placehold.co/1200x400?text=Hero+Image", "alt": "Hero"},
        {"type": "announcements", "title": "Announcements", "content": [
            {"title": "Pool Closed", "body": "Pool closed for maintenance on Sep 10.", "link": "https://example.com/pool"},
            {"title": "New Menu", "body": "Our new menu launches Sep 1.", "link": "https://example.com/menu", "link_text": "See menu"}
        ]}
    ]
}

email_html = exporter.render_email_html(ctx)
web_html = exporter.render_bulletin_html(ctx)

email_path = out / 'FullTest_email.html'
web_path = out / 'FullTest_web.html'
email_path.write_text(email_html, encoding='utf-8')
web_path.write_text(web_html, encoding='utf-8')
print('WROTE', email_path)
print('WROTE', web_path)
