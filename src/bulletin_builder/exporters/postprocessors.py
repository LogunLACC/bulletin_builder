import re
from bs4 import BeautifulSoup

MSO_OPEN = '<!--[if mso]>'
MSO_CLOSE = '<![endif]-->'
REQ_LINK_IMG = 'margin:0; padding:0;'
REQ_TABLE = 'border-collapse:collapse; border-spacing:0;'
REQ_TD = 'border:none;'
SEMANTIC_TAGS = ["section", "article", "header", "footer", "main", "aside", "nav"]
ID_SAFE_RE = re.compile(r"[^a-z0-9_\-]+")


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'html.parser')


def _prefix_style(el, required: str):
    style = (el.get('style') or '').strip()
    if not style.lower().startswith(required.lower()):
        el['style'] = (required + (" " + style if style else "")).strip()


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


def normalize_ids_and_internal_links(html: str) -> str:
    """Normalize IDs and convert internal TOC anchors to spans (FrontSteps strips anchors)."""
    soup = _soup(html)
    body = soup.body or soup
    assigned = set()

    def safe_id(raw: str) -> str:
        base = ID_SAFE_RE.sub('-', (raw or '').lower()).strip('-') or 'section'
        i, cand = 1, base
        while cand in assigned:
            i += 1
            cand = f"{base}-{i}"
        assigned.add(cand)
        return cand

    for h in body.find_all(["h2", "h3"]):
        hid = h.get('id')
        h['id'] = safe_id(hid or h.get_text()[:64])

    # Replace <a href="#...">text</a> with <span>text</span>
    for a in body.find_all('a'):
        href = (a.get('href') or '').strip()
        if href.startswith('#'):
            span = soup.new_tag('span')
            span.string = a.get_text()
            a.replace_with(span)
    return str(soup)


def normalize_lists(html: str) -> str:
    """
    Fix a common pattern:
      <p><strong>Day</strong></p><ul>...</ul>
    -> <ul><li><strong>Day</strong><ul>...</ul></li></ul>
    """
    soup = _soup(html)
    body = soup.body or soup
    ps = list(body.find_all('p'))
    for p in ps:
        if not p.find('strong'):
            continue
        nxt = p.find_next_sibling()
        if nxt and nxt.name == 'ul':
            ul_outer = soup.new_tag('ul')
            li = soup.new_tag('li')
            li.append(p.extract())
            li.append(nxt.extract())
            ul_outer.append(li)
            nxt.insert_after(ul_outer)
    return str(soup)


def simplify_buttons(html: str) -> str:
    """Simplify button-like anchors to minimal links that FrontSteps preserves.

    - Collapse presentation tables that only wrap a single anchor
    - For anchors with heavy button styles, keep underline + inherit color
    """
    soup = _soup(html)
    body = soup.body or soup

    # Collapse simple wrapper tables around a single <a>
    for table in list(body.find_all('table')):
        anchors = table.find_all('a')
        if len(anchors) == 1 and len(table.find_all('tr')) <= 2 and len(table.find_all('td')) <= 2:
            a = anchors[0]
            new_a = soup.new_tag('a', href=a.get('href', ''))
            new_a.string = a.get_text() or 'More Info'
            new_a['style'] = 'margin:0; padding:0; text-decoration:underline; color:inherit;'
            table.replace_with(new_a)

    # Lighten heavy anchors
    for a in body.find_all('a'):
        style = (a.get('style') or '').lower()
        if 'display:inline-block' in style or 'background-color' in style:
            a['style'] = 'margin:0; padding:0; text-decoration:underline; color:inherit;'
    return str(soup)


def decode_escaped_html(html: str) -> str:
    return html.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')


def strip_wrappers(html: str) -> str:
    # Remove <!DOCTYPE>, <head>, <html>, <body> wrappers
    html = re.sub(r'(?is)^\s*<!DOCTYPE[^>]*>', '', html)
    html = re.sub(r'(?is)^.*?<body[^>]*>', '', html)
    html = re.sub(r'(?is)</body>.*$', '', html)
    html = re.sub(r'(?is)^\s*<html[^>]*>', '', html)
    html = re.sub(r'(?is)</html>\s*$', '', html)
    return html.strip()


def frontsteps_pipeline(html: str) -> str:
    html = demote_semantics(html)
    html = strip_picture(html)
    html = enforce_inline_rules(html)
    html = normalize_ids_and_internal_links(html)
    html = normalize_lists(html)
    html = simplify_buttons(html)
    html = decode_escaped_html(html)
    html = strip_wrappers(html)
    return html

