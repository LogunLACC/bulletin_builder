import re
from bs4 import BeautifulSoup

MSO_OPEN = '<!--[if mso]>'
MSO_CLOSE = '<![endif]-->'
REQ_LINK_IMG = 'margin:0; padding:0;'
REQ_TABLE   = 'border-collapse:collapse; border-spacing:0;'
REQ_TD      = 'border:none;'
SEMANTIC_TAGS = ["section","article","header","footer","main","aside","nav"]
ID_SAFE_RE = re.compile(r"[^a-z0-9_\-]+")

# ---- helpers ---------------------------------------------------------------

def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'html.parser')

def _prefix_style(el, required: str):
    style = (el.get('style') or '').strip()
    if not style.lower().startswith(required.lower()):
        el['style'] = (required + (" " + style if style else "")).strip()

# ---- transforms ------------------------------------------------------------

def demote_semantics(html: str) -> str:
    soup = _soup(html)
    body = soup.body or soup
    for tag in body.find_all(SEMANTIC_TAGS):
        tag.name = 'div'
    return str(soup)

def strip_picture(html: str) -> str:
    soup = _soup(html)
    body = soup.body or soup
    for pic in body.find_all('picture'):
        img = pic.find('img')
        if img:
            pic.replace_with(img)
        else:
            pic.decompose()
    for src in body.find_all('source'):
        src.decompose()
    return str(soup)

def enforce_inline_rules(html: str) -> str:
    soup = _soup(html)
    body = soup.body or soup
    for a in body.find_all('a'):
        _prefix_style(a, REQ_LINK_IMG)
    for img in body.find_all('img'):
        _prefix_style(img, REQ_LINK_IMG)
    for table in body.find_all('table'):
        style = (table.get('style') or '').strip()
        if 'border-collapse' not in style:
            table['style'] = (REQ_TABLE + (" " + style if style else "")).strip()
    for td in body.find_all('td'):
        _prefix_style(td, REQ_TD)
    return str(soup)

def normalize_lists(html: str) -> str:
    soup = _soup(html)
    body = soup.body or soup
    processed_strongs = []
    while True:
        strong = body.find('strong')
        if not strong or strong in processed_strongs:
            break
        if strong.next_sibling and strong.next_sibling.name == 'ul':
            ul = strong.next_sibling
            li = soup.new_tag('li')
            li.append(strong)
            li.append(ul)
            new_ul = soup.new_tag('ul')
            new_ul.append(li)
            ul.replace_with(new_ul)
        processed_strongs.append(strong)
    return str(soup)

def simplify_buttons(html: str) -> str:
    soup = _soup(html)
    body = soup.body or soup
    for a in body.find_all('a'):
        if 'background' in (a.get('style') or ''):
            a['style'] = 'text-decoration:underline;'
    return str(soup)

def decode_html_entities(html: str) -> str:
    return html.replace('&lt;', '<').replace('&gt;', '>')

def minify_html(html: str) -> str:
    # Basic minify: remove newlines and extra spaces
    return re.sub(r'\n\s*', '', html).strip()

def replace_toc_anchors(html: str) -> str:
    soup = _soup(html)
    body = soup.body or soup
    for a in body.select('div.header ul li a'):
        span = soup.new_tag('span')
        span.string = a.string
        a.replace_with(span)
    return str(soup)

def run_pipeline(html: str, *, minify: bool = True) -> str:
    """Run all FrontSteps post-processing steps in order."""
    # Must be body-only HTML
    soup = _soup(html)
    body = soup.body or soup
    html = body.decode_contents()

    # Run transforms
    html = demote_semantics(html)
    html = strip_picture(html)
    html = enforce_inline_rules(html)
    html = normalize_lists(html)
    html = simplify_buttons(html)
    html = decode_html_entities(html)
    html = replace_toc_anchors(html)

    if minify:
        html = minify_html(html)
    return html