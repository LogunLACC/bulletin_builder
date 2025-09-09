from bulletin_builder.bulletin_renderer import BulletinRenderer
from bulletin_builder.postprocess import ensure_postprocessed


def test_announcements_button_vml_and_color():
    sections = [
        {
            "type": "announcements",
            "title": "Announcements",
            "body": "Body",
            "link": "https://example.com/more",
            "link_text": "Read More",
        }
    ]
    settings = {"colors": {"primary": "#123456"}}
    html = BulletinRenderer().render_html(sections, settings)
    assert "<v:roundrect" in html
    # non-MSO anchor color and VML fillcolor should reflect the theme color
    assert "#123456" in html


def test_inline_style_prefixes_and_idempotent():
    src = """
    <html><body>
      <table><tr><td>Cell <a href="#">link</a></td></tr></table>
      <img src="x.jpg">
    </body></html>
    """
    out1 = ensure_postprocessed(src)
    # tables
    assert "border-collapse:collapse" in out1 and "border-spacing:0" in out1
    # td
    assert "border:none" in out1
    # a/img
    assert "margin:0" in out1 and "padding:0" in out1
    # idempotent
    out2 = ensure_postprocessed(out1)
    assert out1 == out2
