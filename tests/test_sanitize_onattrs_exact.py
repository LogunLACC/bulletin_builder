from bulletin_builder.app_core.sanitize import sanitize_email_html

SAMPLE = '<img onerror="alert(1)" src="x.jpg" style="margin:0; padding:0;">'
SAMPLE2 = "<a onclick='x(1)' href='y'>y</a>"


def test_onattrs_stripped_quotes_double():
    out = sanitize_email_html(SAMPLE)
    assert 'onerror' not in out


def test_onattrs_stripped_quotes_single():
    out = sanitize_email_html(SAMPLE2)
    assert 'onclick' not in out
