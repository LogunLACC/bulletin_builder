
from bulletin_builder.postprocess import ensure_postprocessed


def test_toc_left_aligned_and_hr():
        src = '''
        <html><body>
            <ul>
                <li><a href="#announcements">Announcements</a></li>
                <li><a href="#events">Events</a></li>
            </ul>
            <h2 id="announcements">Announcements</h2>
        </body></html>
        '''
        out = ensure_postprocessed(src)
        assert "list-style:none" in out
        assert "text-align:left" in out
        assert "padding:0 16px" in out
        assert "<hr" in out


def test_announcement_padding_fix():
    src = '<td style="padding:12px 0 12px 0;font-family:Arial">Hello</td>'
    out = ensure_postprocessed("<html><body>"+src+"</body></html>")
    assert "padding:12px 16px" in out
