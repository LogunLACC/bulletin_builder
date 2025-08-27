from src.bulletin_builder.app_core.sanitize import sanitize_email_html
from pathlib import Path

p = Path(__file__).parent / 'sanitize_input.html'
html = p.read_text(encoding='utf-8')
print(sanitize_email_html(html))
