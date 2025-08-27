"""
URL upgrade utility for preventing mixed content in generated HTML.
Automatically upgrades HTTP URLs to HTTPS for known safe hosts.
"""
import re

# Known safe hosts that support HTTPS
SAFE_HOSTS = (
    r"lakealmanorcountryclub\.com",
    r"cdn-ip\.allevents\.in",
    r"maps\.app\.goo\.gl",
    r"googleusercontent\.com",
    r"imgur\.com",
    r"allevents\.in",
    r"sierradailynews\.com",
    r"foreupsoftware\.com",
    r"us02web\.zoom\.us",
    r"hoamco\.zoom\.us",
    r"placehold\.co",
)

# Safe hosts for AVIF images (subset that we know have JPG fallbacks)
_SAFE_AVIF_HOSTS = (
    r"cdn-ip\.allevents\.in",
    r"allevents\.in",
    r"lakealmanorcountryclub\.com",
    r"googleusercontent\.com",
    r"imgur\.com",
)

# Regex pattern to match HTTP URLs in src and href attributes
_RX = re.compile(r'(?P<prefix>\b(?:src|href)\s*=\s*["\'])http://(?P<host>[^/"]+)', re.I)

# Regex pattern to match AVIF images
_RX_AVIF = re.compile(r'(?i)(?P<attr>\b(?:src|href)\s*=\s*["\'])(?P<url>https?://(?P<host>[^/"\']+)[^"\']*\.avif(?:\?[^"\']*)?)(?P<rest>["\'])')


def upgrade_http_to_https(html: str, convert_avif: bool = False) -> str:
    """
    Upgrade HTTP URLs to HTTPS for known safe hosts to prevent mixed content.

    Args:
        html: HTML string containing potential HTTP URLs

    Returns:
        HTML string with HTTP URLs upgraded to HTTPS where safe
    """
    def _sub(m):
        host = m.group('host')
        # Check if the host is in our safe list
        if any(re.search(pattern, host, re.I) for pattern in SAFE_HOSTS):
            return m.group('prefix') + "https://" + host
        # Return unchanged for unknown hosts
        return m.group(0)

    out = _RX.sub(_sub, html)
    if convert_avif:
        # Replace only .avif at the end of path or before querystring for src/href attributes
        def _to_jpg_url(match):
            # match groups: attr, url, host, rest (from _RX_AVIF)
            url = match.group('url')
            jpg = re.sub(r'(?i)\.avif(?=(?:\?|$))', '.jpg', url)
            return match.group('attr') + jpg + match.group('rest')
        out = _RX_AVIF.sub(_to_jpg_url, out)
    return out


def avif_to_jpg_email_only(html: str) -> str:
    """
    Convert AVIF image URLs to JPG for email compatibility.
    Only converts images from known safe hosts that we know have JPG fallbacks.

    Args:
        html: HTML string containing potential AVIF image URLs

    Returns:
        HTML string with AVIF URLs converted to JPG where safe
    """
    def _sub(m):
        host = m.group('host')
        url = m.group('url')
        # Check if the host is in our safe AVIF list
        if any(re.search(pattern, host, re.I) for pattern in _SAFE_AVIF_HOSTS):
            # Replace .avif extension with .jpg
            jpg_url = re.sub(r'\.avif(?=\?|$)', '.jpg', url, flags=re.I)
            return m.group('attr') + jpg_url + m.group('rest')
        # Return unchanged for unknown hosts
        return m.group(0)

    return _RX_AVIF.sub(_sub, html)


def is_secure_context() -> bool:
    """
    Check if we're in a secure context (for clipboard/service worker support).
    Since this is a desktop app, we'll consider it secure by default.
    """
    return True
