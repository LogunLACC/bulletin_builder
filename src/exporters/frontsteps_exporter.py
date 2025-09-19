import re
from bs4 import BeautifulSoup


def build_frontsteps_html(state_html: str) -> str:
    """
    Takes full HTML of the bulletin preview and returns body-only HTML ready for FrontSteps.
    Applies email-safe inline rules.
    """
    soup = BeautifulSoup(state_html, 'html.parser')

    # Extract body
    body = soup.body or soup

    # Replace semantic containers with <div>
    for tag in body.find_all(['section', 'article', 'header', 'footer', 'main', 'aside', 'nav']):
        tag.name = 'div'

    # Strip picture/source, keep <img>
    for pic in body.find_all('picture'):
        img = pic.find('img')
        if img:
            pic.replace_with(img)
        else:
            pic.decompose()
    for src in body.find_all('source'):
        src.decompose()

    # Helper to prefix inline style
    def prefix_style(el, required: str):
        style = (el.get('style') or '').strip()
        if not style.lower().startswith(required.lower()):
            el['style'] = f"{required} {style}".strip()

    # Enforce rules
    for a in body.find_all('a'):
        prefix_style(a, 'margin:0; padding:0;')
    for img in body.find_all('img'):
        prefix_style(img, 'margin:0; padding:0;')
    for table in body.find_all('table'):
        if 'style' in table.attrs:
            if 'border-collapse' not in table['style']:
                table['style'] = f"border-collapse:collapse; border-spacing:0; {table['style']}"
        else:
            table['style'] = 'border-collapse:collapse; border-spacing:0;'
    for td in body.find_all('td'):
        prefix_style(td, 'border:none;')

    # Unescape encoded tags if any
    html = str(body)
    html = html.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

    # Remove <!DOCTYPE>, <head>, <html>, <body> wrappers
    html = re.sub(r'(?is)^.*?<body[^>]*>', '', html)
    html = re.sub(r'(?is)</body>.*$', '', html)

    return html.strip()

