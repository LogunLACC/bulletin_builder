import re
from bulletin_builder.postprocess.bulletin_email_postprocess import process_html

def test_toc_normalized_and_hr_inserted():
    src = '''
    <html><body>
        <ul>
            <li><a href="#announcements">Announcements</a></li>
            <li><a href="#events">Events</a></li>
        </ul>
        <h2 id="announcements">Announcements</h2>
    </body></html>
    '''
    out = process_html(src)
    assert 'list-style:none' in out
    assert 'text-align:left' in out
    assert 'padding:0 16px' in out
    assert '<hr' in out

def test_announcement_padding_fixed():
    src = '''
    <table><tr>
        <td style="padding:12px 0 12px 0;font-family:Arial">Hello</td>
    </tr></table>
    '''
    out = process_html(src)
    assert 'padding:12px 16px' in out
