from bulletin_builder.postprocess import ensure_postprocessed

def test_toc_left_aligned_and_hr_and_container_padding():
    src = '''
    <html><body>
      <table role="presentation" width="640"><tr>
        <td style="text-align:center;padding:0">
          <ul>
            <li><a href="#announcements">Announcements</a></li>
            <li><a href="#events">Events</a></li>
          </ul>
        </td>
      </tr></table>
      <h2 id="announcements">Announcements</h2>
    </body></html>
    '''
    out = ensure_postprocessed(src)
    assert "list-style:none" in out
    assert "text-align:left" in out
    assert "display:block" in out and "width:100%" in out
    assert "<hr" in out
    # parent TD got side padding
    assert "padding-left:16px" in out and "padding-right:16px" in out

def test_announcement_padding_and_zero_padding_cells():
    src = '''
    <html><body>
      <table><tr>
        <td style="padding:12px 0 12px 0;font-family:Arial">A</td>
      </tr></table>
      <table><tr>
        <td style="padding:0">B</td>
      </tr></table>
    </body></html>
    '''
    out = ensure_postprocessed(src)
    assert "padding:12px 16px" in out
    assert "padding:0 16px" in out


def test_pytest_discovery():
  assert True
