from bulletin_builder.app_core.sanitize import sanitize_email_html

def test_no_tagname_corruption_when_inserting_style():
    src = '<a href="#">X</a><img src="x.png"><td class="c">y</td><table><tr><td>z</td></tr></table>'
    out = sanitize_email_html(src)
    assert "<astyle=" not in out.lower()
    assert "<imgstyle=" not in out.lower()
    assert "<tdstyle=" not in out.lower()
    assert '<a style="margin:0; padding:0;' in out.lower()
    assert '<img style="margin:0; padding:0;' in out.lower()
    assert ' style="border:none;' in out.lower()  # td
    assert 'border-collapse:collapse' in out.lower()  # table

def test_strip_event_handlers_in_email():
    src = '<img src="x" onerror="alert(1)" onload="x()" style="color:red">'
    out = sanitize_email_html(src)
    assert 'onerror=' not in out.lower()
    assert 'onload=' not in out.lower()

def test_idempotence_simple_inserts():
    src = '<a style="padding:0; margin:0; color:#000" href="#">X</a>'
    out1 = sanitize_email_html(src)
    out2 = sanitize_email_html(out1)
    assert out1 == out2
