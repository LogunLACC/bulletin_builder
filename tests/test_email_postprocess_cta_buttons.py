from bulletin_builder.postprocess import ensure_postprocessed


def test_postprocess_converts_cta_anchor_to_vml_button():
    src = """
    <html><body>
      <p><a href="https://example.com/learn" target="_blank">Read More</a></p>
    </body></html>
    """
    out = ensure_postprocessed(src)
    assert "<v:roundrect" in out
    assert "Read More" in out
    assert "https://example.com/learn" in out

