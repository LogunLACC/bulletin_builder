from scripts.bulletin_email_postprocess import process_html


def test_email_reset_preserves_links_and_inlines_styles():
    sample = '''<!DOCTYPE html>
    <html>
      <head><title>Test</title><link rel="stylesheet" href="x.css"></head>
      <body>
        <h1>Welcome</h1>
        <a href="https://example.com" style="color:blue">Click</a>
        <img src="/images/pic.avif" style="border:5px solid red;" />
        <table><tr><td style="border:1px solid #000">Cell</td></tr></table>
      </body>
    </html>'''

    out = process_html(sample)

    # Should not contain DOCTYPE or head or style/link/script tags
    assert '<!DOCTYPE' not in out.upper()
    assert '<head' not in out.lower()
    assert '<style' not in out.lower()
    assert '<script' not in out.lower()

    # href/src preserved
    assert 'href="https://example.com"' in out
    assert 'src="/images/pic.jpg"' in out or 'src="/images/pic.avif"' in out

    # styles should start with margin:0;padding:0;
    assert 'style="margin:0;padding:0' in out

    # table/td reset
    assert 'border-collapse' in out or 'border-spacing' in out
    assert 'border:none' in out
