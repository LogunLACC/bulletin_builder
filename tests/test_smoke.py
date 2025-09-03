import pathlib

def get_templates_dir():
    # Always use the known absolute path for templates
    return pathlib.Path(__file__).parent.parent / "src" / "bulletin_builder" / "templates"

def test_renderer_handles_string_and_dict():
    from bulletin_builder.bulletin_renderer import BulletinRenderer
    tpl_dir = get_templates_dir()
    r = BulletinRenderer(templates_dir=str(tpl_dir), template_name="main_layout.html")
    # minimal context
    ctx = {
        "bulletin": {"title": "t", "date": "2025-01-01"},
        "theme": "default.css",
        "settings": {"colors": {"secondary": "#333333"}},
        "sections": [
            {"type": "custom_text", "title": "A", "content": "plain string"},
            {"type": "custom_text", "title": "B", "content": {"text": "dict text"}},
        ],
    }
    html = r.render(ctx)
    assert "plain string" in html and "dict text" in html

def test_templates_exist():
    base = get_templates_dir()
    assert (base / "base.html").exists()
    assert (base / "main_layout.html").exists()
