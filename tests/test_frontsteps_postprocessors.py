import re
from bulletin_builder.exporters.postprocessors import frontsteps_pipeline

def test_toc_internal_anchors_become_spans():
    html = """
    <html><body>
      <ul><li><a href="#club-events">Club Events</a></li></ul>
      <h2 id="club-events">Club Events</h2>
    </body></html>
    """
    out = frontsteps_pipeline(html)
    assert '<body' not in out
    assert '<a href="#club-events"' not in out
    assert '<span>Club Events</span>' in out


def test_list_normalization():
    html = """
    <html><body>
      <p><strong>Friday</strong></p>
      <ul><li>5:00 pm</li><li>7:00 pm</li></ul>
    </body></html>
    """
    out = frontsteps_pipeline(html)
    # Expect outer UL with LI wrapping strong + inner UL
    assert '<ul><li><p><strong>Friday</strong></p><ul>' in out.replace('\n','').replace('  ','')


def test_button_simplification():
    html = """
    <html><body>
      <table role="presentation"><tr><td>
        <a href="https://x" style="display:inline-block; background-color:#103040; color:#fff;">More Info</a>
      </td></tr></table>
    </body></html>
    """
    out = frontsteps_pipeline(html)
    # Table collapsed to minimal link
    assert '<table' not in out
    assert re.search(r'<a[^>]*href="https://x"[^>]*>More Info</a>', out)
    assert 'text-decoration:underline' in out


def test_img_table_td_a_rules_and_body_only():
    html = """
    <html><body>
      <a href="#">x</a>
      <img src="x.jpg">
      <table><tr><td>y</td></tr></table>
    </body></html>
    """
    out = frontsteps_pipeline(html)
    assert '<!DOCTYPE' not in out and '<head' not in out and '<body' not in out
    assert re.search(r'<a[^>]*style="margin:0; padding:0;', out)
    assert re.search(r'<img[^>]*style="margin:0; padding:0;', out)
    assert 'border-collapse:collapse' in out and 'border-spacing:0' in out
    assert 'border:none;' in out
