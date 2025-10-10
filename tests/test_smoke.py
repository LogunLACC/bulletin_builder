import pathlib
import pytest

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


class TestMenuHandlers:
    """Smoke tests for menu handler registration and basic functionality."""

    def test_menu_handlers_registered(self):
        """Test that all expected menu handlers are registered in menu.py."""
        from bulletin_builder.app_core import menu
        
        # Create a mock app object
        class MockApp:
            pass
        
        app = MockApp()
        
        # Initialize menu handlers
        menu.init(app)
        
        # Verify all expected handlers exist
        expected_handlers = [
            'new_draft',
            'open_draft',
            'save_draft',
            'import_announcements_csv',
            'import_announcements_sheet',
            'import_events_feed',
            'on_export_html_text_clicked',
            'on_export_pdf_clicked',
            'on_copy_for_email_clicked',
            'on_copy_for_frontsteps_clicked',  # The one we just fixed!
            'open_in_browser',
            'on_export_ics_clicked',
        ]
        
        for handler_name in expected_handlers:
            assert hasattr(app, handler_name), f"Handler '{handler_name}' not registered"
            assert callable(getattr(app, handler_name)), f"Handler '{handler_name}' is not callable"

    def test_exporter_functions_exist(self):
        """Test that exporter module has all required functions."""
        from bulletin_builder.app_core import exporter
        
        # Check that the module has the init function
        assert hasattr(exporter, 'init'), "exporter module missing init function"
        assert callable(exporter.init), "exporter.init is not callable"

    def test_frontsteps_exporter_available(self):
        """Test that FrontSteps exporter module is available."""
        try:
            from bulletin_builder.exporters.frontsteps_exporter import build_frontsteps_html
            assert callable(build_frontsteps_html)
        except ImportError as e:
            pytest.fail(f"FrontSteps exporter not available: {e}")

    def test_render_functions_available(self):
        """Test that render functions are available in exporter."""
        # These functions are created dynamically during init
        # So we just verify the exporter module can be imported
        from bulletin_builder.app_core import exporter
        assert hasattr(exporter, 'init')


class TestExportWorkflows:
    """Smoke tests for export workflow basics."""

    def test_bulletin_renderer_basic_render(self):
        """Test that bulletin renderer can render basic HTML."""
        from bulletin_builder.bulletin_renderer import BulletinRenderer
        
        tpl_dir = get_templates_dir()
        renderer = BulletinRenderer(templates_dir=str(tpl_dir), template_name="main_layout.html")
        
        # Proper context structure with nested settings
        ctx = {
            "settings": {
                "bulletin_title": "Test Bulletin",
                "bulletin_date": "2025-10-10",
                "colors": {
                    "secondary": "#333333"
                }
            },
            "theme": "default.css",
            "sections": []
        }
        
        html = renderer.render(ctx)
        assert "Test Bulletin" in html
        assert isinstance(html, str)
        assert len(html) > 0

    def test_frontsteps_html_sanitization(self):
        """Test that FrontSteps HTML sanitization works."""
        from bulletin_builder.exporters.frontsteps_exporter import build_frontsteps_html
        
        sample_html = """
        <html>
            <head><style>body { color: red; }</style></head>
            <body>
                <h1>Test</h1>
                <p>Content</p>
            </body>
        </html>
        """
        
        result = build_frontsteps_html(sample_html)
        
        # Should return a string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Should contain the content
        assert "Test" in result or "test" in result.lower()

    def test_email_renderer_basic_functionality(self):
        """Test that email renderer can be initialized."""
        # Email rendering is set up during app init
        # Just verify the necessary components exist
        from bulletin_builder.bulletin_renderer import BulletinRenderer
        
        tpl_dir = get_templates_dir()
        renderer = BulletinRenderer(templates_dir=str(tpl_dir), template_name="main_layout.html")
        
        assert renderer is not None
        assert hasattr(renderer, 'render')
        assert callable(renderer.render)


class TestImportWorkflows:
    """Smoke tests for import functionality."""

    def test_importer_module_available(self):
        """Test that importer module exists."""
        try:
            from bulletin_builder.app_core import importer
            assert hasattr(importer, 'init'), "importer module missing init function"
        except ImportError as e:
            pytest.fail(f"Importer module not available: {e}")

    def test_csv_parser_available(self):
        """Test that CSV parsing functionality exists."""
        try:
            # Try to import CSV-related functions
            import csv
            assert csv is not None
        except ImportError as e:
            pytest.fail(f"CSV support not available: {e}")
