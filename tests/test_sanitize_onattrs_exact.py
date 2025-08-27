from bulletin_builder.app_core.sanitize import sanitize_email_html

def test_onattrs_stripped_long_values():
    html = '<img onerror="alert(1)" src="x.jpg"><a onclick=\'return confirm("ok")\' href="#">x</a>'
    out = sanitize_email_html(html)
    assert 'onerror' not in out
    assert 'onclick' not in out
    assert 'alert(1)' not in out
    assert 'confirm' not in out
