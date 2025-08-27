import re

# This mirrors the fixed pattern behavior: .avif with optional ?query
RX = re.compile(r'(?i)(?P<attr>\b(?:src|href)\s*=\s*["\'])(?P<url>https?://(?P<host>[^/"\']+)[^"\']*\.avif(?:\?[^"\']*)?)(?P<rest>["\'])')

SAFE_HOSTS = ("cdn-ip.allevents.in","allevents.in","lakealmanorcountryclub.com","googleusercontent.com","imgur.com")

def rewrite(url):
    def sub(m):
        host = m.group('host').lower()
        if not any(h in host for h in SAFE_HOSTS):
            return m.group(0)
        u = m.group('url')
        if '.avif?' in u.lower():
            base, q = u.rsplit('.avif', 1)
            return f"{m.group('attr')}{base}.jpg{q}{m.group('rest')}"
        else:
            return f"{m.group('attr')}{u[:-5]}.jpg{m.group('rest')}"
    return RX.sub(sub, url)

def test_avif_no_query():
    html = '<img src="https://cdn-ip.allevents.in/pic.avif">'
    out = rewrite(html)
    assert '.avif' not in out.lower()
    assert '.jpg' in out.lower()

def test_avif_with_query():
    html = '<img src="https://cdn-ip.allevents.in/pic.avif?v=123&x=y">'
    out = rewrite(html)
    assert '.avif' not in out.lower()
    assert '.jpg?v=123&x=y' in out.lower()
