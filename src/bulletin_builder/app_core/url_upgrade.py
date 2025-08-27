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

# Regex pattern to match HTTP URLs in src and href attributes
_RX = re.compile(r'(?P<prefix>\b(?:src|href)\s*=\s*["\'])http://(?P<host>[^/"]+)', re.I)


def upgrade_http_to_https(html: str) -> str:
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

    return _RX.sub(_sub, html)


def is_secure_context() -> bool:
    """
    Check if we're in a secure context (for clipboard/service worker support).
    Since this is a desktop app, we'll consider it secure by default.
    """
    return True
