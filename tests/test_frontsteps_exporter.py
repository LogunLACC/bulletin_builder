import re
from bulletin_builder.exporters.frontsteps_exporter import build_frontsteps_html

MOCK_HTML = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
  <section><article><p>Hello</p></article></section>
  <a href='#'>toc</a>
  <a href='https://example.com'>ext</a>
  <img src='x.jpg'>
  <table><tr><td>cell</td></tr></table>
  <picture><img src='x.jpg'></picture>
  <!--[if mso]><v:roundrect>hi</v:roundrect><![endif]-->
</body>
</html>
"""


def test_export_rules():
    html = build_frontsteps_html(MOCK_HTML)

    # No doctype/head/body
    assert '<!DOCTYPE' not in html
    assert '<head' not in html
    assert '<body' not in html

    # Style rules
    assert re.search(r'<a[^>]*style=\"margin:0; padding:0;', html)
    assert re.search(r'<img[^>]*style=\"margin:0; padding:0;', html)
    assert 'border-collapse:collapse' in html
    assert 'border-spacing:0' in html
    assert 'border:none;' in html

    # No picture/source
    assert '<picture' not in html and '<source' not in html

    # MSO preserved
    assert '<!--[if mso]>' in html

    # No escaped tags
    assert '&lt;p&gt;' not in html
