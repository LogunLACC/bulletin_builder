import re
from src.exporters.frontsteps_exporter import build_frontsteps_html

MOCK = """
<!DOCTYPE html>
<html>
<head><title>preview</title></head>
<body>
  <div class="header">
    <h1>ClubLife Weekly</h1>
    <ul>
      <li><a href="#club-announcements">Club Announcements</a></li>
      <li><a href="#club-events">Club Events</a></li>
      <li><a href="#community-events">Community Events</a></li>
    </ul>
  </div>

  <section id="club-announcements">
    <h2>Club Announcements</h2>
    <article>
      <strong>Friday, Sept 19 2025</strong>
      <ul>
        <li>5:00 am – 6:30 am</li>
        <li>2:00 pm – 4:30 pm</li>
      </ul>
    </article>
    <article>
      <p>Thanks for coming to the Town Hall. Here's the deck.</p>
      <a href="https://example.com/deck" style="padding:12px; display:inline-block; background:#0067b8; color:#fff; border-radius:6px;">View Deck</a>
    </article>
  </section>

  <section id="club-events">
    <h2>Club Events</h2>
    <table><tr><td>card</td></tr></table>
    <a href="#club-events">back</a>
    <img src="x.jpg">
  </section>

  <section id="community-events"><h2>Community Events</h2></section>
</body>
</html>
"""

def test_body_only_and_rules():
    html = build_frontsteps_html(MOCK)
    print(html)

    # Body-only (no wrappers)
    assert '<!DOCTYPE' not in html and '<head' not in html and '<body' not in html

    # Demoted semantics (no <section>/<article>)
    assert '<section' not in html and '<article' not in html

    # TOC anchors replaced with spans
    assert '<a href="#club-announcements"' not in html
    assert re.search(r'<span[^>]*>Club Announcements</span>', html)

    # List normalization (no UL>UL duplicates)
    assert html.count('<ul>') == html.count('</ul>')
    assert '<ul><ul>' not in html

    # Buttons simplified to minimal anchor link
    assert 'text-decoration:underline' in html
    assert 'background:' not in re.search(r'<a[^>]*>', html).group(0)

    # Style rules applied
    assert re.search(r'<a[^>]*style="margin:0; padding:0;', html)
    assert re.search(r'<img[^>]*style="margin:0; padding:0;', html)
    assert 'border-collapse:collapse' in html
    assert re.search(r'<td[^>]*style="border:none;', html)

    # IDs preserved and internal href normalized (even though TOC anchors were removed)
    assert 'id="club-announcements"' in html
    assert 'href="#club-events"' in html