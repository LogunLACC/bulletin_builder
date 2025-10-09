"""
Test email client preview simulation feature.
"""
import pytest

try:
    import tkinter as tk
    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False

if TK_AVAILABLE:
    try:
        _root = tk.Tk()
        _root.withdraw()
        _root.destroy()
    except Exception as e:
        TK_AVAILABLE = False
        pytest.skip(f"Tk not available: {e}")


def test_email_client_preview_module_imports():
    """Test that the email_client_preview module can be imported."""
    from bulletin_builder.app_core import email_client_preview
    assert hasattr(email_client_preview, 'show_email_client_info')
    assert hasattr(email_client_preview, 'get_client_max_width')
    assert hasattr(email_client_preview, 'get_client_wrapper_style')
    assert hasattr(email_client_preview, 'init')
    assert hasattr(email_client_preview, 'EMAIL_CLIENT_STYLES')


def test_email_client_styles_defined():
    """Test that all expected email clients have style definitions."""
    from bulletin_builder.app_core.email_client_preview import EMAIL_CLIENT_STYLES
    
    expected_clients = ["Gmail", "Outlook", "Apple Mail", "Mobile", "Standard"]
    for client in expected_clients:
        assert client in EMAIL_CLIENT_STYLES
        assert "name" in EMAIL_CLIENT_STYLES[client]
        assert "description" in EMAIL_CLIENT_STYLES[client]
        assert "max_width" in EMAIL_CLIENT_STYLES[client]
        assert "constraints" in EMAIL_CLIENT_STYLES[client]
        assert "wrapper_style" in EMAIL_CLIENT_STYLES[client]
        assert "info_color" in EMAIL_CLIENT_STYLES[client]


def test_get_client_max_width():
    """Test that get_client_max_width returns expected values."""
    from bulletin_builder.app_core.email_client_preview import get_client_max_width
    
    assert get_client_max_width("Gmail") == 650
    assert get_client_max_width("Outlook") == 600
    assert get_client_max_width("Apple Mail") == 600
    assert get_client_max_width("Mobile") == 375
    assert get_client_max_width("Standard") == 800
    assert get_client_max_width("UnknownClient") == 800  # Fallback to Standard


def test_get_client_wrapper_style():
    """Test that get_client_wrapper_style returns CSS styles."""
    from bulletin_builder.app_core.email_client_preview import get_client_wrapper_style
    
    for client in ["Gmail", "Outlook", "Apple Mail", "Mobile", "Standard"]:
        style = get_client_wrapper_style(client)
        assert isinstance(style, str)
        assert "border" in style
        assert "padding" in style


def test_email_client_preview_init_attaches_methods():
    """Test that init attaches required methods to app instance."""
    from bulletin_builder.app_core import email_client_preview
    
    # Create a minimal mock app
    class MockApp:
        pass
    
    app = MockApp()
    email_client_preview.init(app)
    
    # email_client_var may not be set if Tk not available, but methods should be
    assert hasattr(app, 'available_email_clients')
    assert hasattr(app, 'show_email_client_info')
    assert hasattr(app, 'get_current_client_width')
    assert hasattr(app, 'get_current_client_wrapper')
    assert callable(app.show_email_client_info)
    assert callable(app.get_current_client_width)
    assert callable(app.get_current_client_wrapper)


def test_email_client_preview_available_clients():
    """Test that all expected clients are in available list."""
    from bulletin_builder.app_core import email_client_preview
    
    class MockApp:
        pass
    
    app = MockApp()
    email_client_preview.init(app)
    
    expected_clients = ["Gmail", "Outlook", "Apple Mail", "Mobile", "Standard"]
    for client in expected_clients:
        assert client in app.available_email_clients


def test_email_client_preview_default_selection():
    """Test that default email client is set correctly or defaults work."""
    from bulletin_builder.app_core import email_client_preview
    
    class MockApp:
        pass
    
    app = MockApp()
    email_client_preview.init(app)
    
    # Should return default width even without Tk var
    assert app.get_current_client_width() == 800  # Standard default


def test_email_client_preview_get_current_width():
    """Test that get_current_client_width returns correct width."""
    from bulletin_builder.app_core import email_client_preview
    
    class MockApp:
        pass
    
    class MockStringVar:
        def __init__(self, value="Standard"):
            self._value = value
        
        def get(self):
            return self._value
        
        def set(self, value):
            self._value = value
    
    app = MockApp()
    email_client_preview.init(app)
    
    # Manually set the var for testing
    app.email_client_var = MockStringVar("Standard")
    assert app.get_current_client_width() == 800  # Standard
    
    # Test changing client
    app.email_client_var.set("Gmail")
    assert app.get_current_client_width() == 650
    
    app.email_client_var.set("Mobile")
    assert app.get_current_client_width() == 375


def test_email_client_constraints_are_informative():
    """Test that each client has meaningful constraint information."""
    from bulletin_builder.app_core.email_client_preview import EMAIL_CLIENT_STYLES
    
    for client_name, client_info in EMAIL_CLIENT_STYLES.items():
        constraints = client_info["constraints"]
        assert isinstance(constraints, list)
        assert len(constraints) > 0, f"{client_name} should have constraints"
        
        # Each constraint should be a non-empty string
        for constraint in constraints:
            assert isinstance(constraint, str)
            assert len(constraint) > 0


def test_email_client_preview_integration_with_preview_device():
    """Test that email client preview integrates with device preview."""
    from bulletin_builder.app_core import email_client_preview
    from bulletin_builder.app_core.preview import _set_preview_device
    
    class MockApp:
        preview_area = None
        
        def configure(self, **kwargs):
            pass
    
    class MockPreviewArea:
        width = 800
        
        def configure(self, width=None):
            if width is not None:
                self.width = width
    
    class MockStringVar:
        def __init__(self, value="Standard"):
            self._value = value
        
        def get(self):
            return self._value
        
        def set(self, value):
            self._value = value
    
    app = MockApp()
    app.preview_area = MockPreviewArea()
    email_client_preview.init(app)
    
    # Manually set the var for testing
    app.email_client_var = MockStringVar("Gmail")
    
    # Test that device setting uses client width when available
    _set_preview_device(app, "Desktop")
    assert app.preview_area.width == 650  # Gmail max width, not desktop default
    
    app.email_client_var.set("Mobile")
    _set_preview_device(app, "Desktop")
    assert app.preview_area.width == 375  # Mobile max width
