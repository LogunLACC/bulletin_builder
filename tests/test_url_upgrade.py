"""
Tests for URL upgrade functionality
"""
from src.bulletin_builder.app_core.url_upgrade import upgrade_http_to_https


def test_upgrade_known_hosts():
    """Test that known safe hosts get their HTTP URLs upgraded to HTTPS"""
    html = '''<img src="http://lakealmanorcountryclub.com/a.jpg">
<a href="http://cdn-ip.allevents.in/x">link</a>
<img src="http://maps.app.goo.gl/map">
<a href="http://googleusercontent.com/img.png">image</a>'''

    out = upgrade_http_to_https(html)

    # Check that HTTP URLs were upgraded to HTTPS
    assert 'src="https://lakealmanorcountryclub.com/a.jpg"' in out
    assert 'href="https://cdn-ip.allevents.in/x"' in out
    assert 'src="https://maps.app.goo.gl/map"' in out
    assert 'href="https://googleusercontent.com/img.png"' in out

    print("✓ Known hosts upgrade test passed")


def test_skip_unknown_hosts():
    """Test that unknown hosts are not upgraded (to avoid breaking functionality)"""
    html = '''<img src="http://intranet.local/a.jpg">
<a href="http://192.168.1.100/page">local</a>
<img src="http://unknown-site.com/img.png">'''

    out = upgrade_http_to_https(html)

    # Check that unknown hosts remain HTTP
    assert out == html

    print("✓ Unknown hosts skip test passed")


def test_mixed_content_prevention():
    """Test that the upgrade prevents mixed content issues"""
    # Simulate HTML that would cause mixed content on HTTPS pages
    html = '''<html><body>
<img src="http://lakealmanorcountryclub.com/logo.png" />
<a href="http://cdn-ip.allevents.in/event">Event</a>
</body></html>'''

    upgraded = upgrade_http_to_https(html)

    # Should upgrade known hosts
    assert 'https://lakealmanorcountryclub.com/logo.png' in upgraded
    assert 'https://cdn-ip.allevents.in/event' in upgraded

    print("✓ Mixed content prevention test passed")


def test_case_insensitive_matching():
    """Test that host matching is case insensitive"""
    html = '''<img src="http://LakeAlmanorCountryClub.COM/a.jpg">
<a href="http://CDN-IP.AllEvents.IN/x">link</a>'''

    out = upgrade_http_to_https(html)

    # Should upgrade despite case differences
    assert 'https://LakeAlmanorCountryClub.COM/a.jpg' in out
    assert 'https://CDN-IP.AllEvents.IN/x' in out

    print("✓ Case insensitive matching test passed")


if __name__ == "__main__":
    test_upgrade_known_hosts()
    test_skip_unknown_hosts()
    test_mixed_content_prevention()
    test_case_insensitive_matching()
    print("✓ All URL upgrade tests passed!")
