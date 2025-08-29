from pathlib import Path
from bulletin_builder.bulletin_renderer import BulletinRenderer
from bulletin_builder.settings import Settings
from bulletin_builder.app_core.url_upgrade import upgrade_http_to_https
from bulletin_builder.app_core.sanitize import sanitize_email_html
from premailer import transform

# Setup
templates = Path('src/bulletin_builder/templates')
if not templates.exists():
    templates = Path('templates')
renderer = BulletinRenderer(templates)
settings = Settings()
sections = []

# Render base HTML
html = renderer.render_html(sections, settings)
# Save web HTML (no premailer, no sanitize, no avif conversion)
out_dir = Path('tmp_export')
out_dir.mkdir(exist_ok=True)
web_path = out_dir / 'export_web.html'
web_html = upgrade_http_to_https(html, convert_avif=False)
web_path.write_text(web_html, encoding='utf-8')
print('web saved ->', web_path)

# Prepare email HTML
email_html = transform(html)
email_html = upgrade_http_to_https(email_html, convert_avif=True)
email_html = sanitize_email_html(email_html)
email_path = out_dir / 'export_email.html'
email_path.write_text(email_html, encoding='utf-8')
print('email saved ->', email_path)
