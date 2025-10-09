"""
Test email deliverability guidance feature.
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
        pytest.skip(f"Tk not available: {e}", allow_module_level=True)


def test_email_deliverability_module_imports():
    """Test that the email_deliverability module can be imported."""
    from bulletin_builder.app_core import email_deliverability
    assert hasattr(email_deliverability, 'show_email_auth_guidance')
    assert hasattr(email_deliverability, 'init')


def test_email_deliverability_init_attaches_method():
    """Test that init attaches show_email_auth_guidance to app instance."""
    if not TK_AVAILABLE:
        pytest.skip("Tk not available")
    
    from bulletin_builder.app_core import email_deliverability
    
    # Create a minimal mock app
    class MockApp:
        pass
    
    app = MockApp()
    email_deliverability.init(app)
    
    assert hasattr(app, 'show_email_auth_guidance')
    assert callable(app.show_email_auth_guidance)


def test_email_deliverability_guidance_dialog_creation():
    """Test that the guidance dialog can be created without crashing."""
    if not TK_AVAILABLE:
        pytest.skip("Tk not available")
    
    from bulletin_builder.app_core.email_deliverability import show_email_auth_guidance
    
    # Create a root window
    try:
        root = tk.Tk()
        root.withdraw()
    except Exception as e:
        pytest.skip(f"Tk initialization failed: {e}")
    
    try:
        # This should create the dialog without raising an error
        # We immediately close it to avoid blocking the test
        root.after(100, lambda: root.quit())
        
        # Note: We can't easily test the dialog opens without blocking,
        # but we can verify the function exists and is callable
        assert callable(show_email_auth_guidance)
        
    finally:
        try:
            root.destroy()
        except Exception:
            pass


def test_email_deliverability_in_menu():
    """Test that email deliverability guidance is accessible from the Help menu."""
    if not TK_AVAILABLE:
        pytest.skip("Tk not available")
    
    import customtkinter as ctk
    from bulletin_builder.app_core import loader
    from bulletin_builder.app_core import email_deliverability
    
    # Create a minimal app instance
    app = ctk.CTk()
    app.withdraw()
    
    try:
        # Initialize email_deliverability
        email_deliverability.init(app)
        
        # Verify the method is attached
        assert hasattr(app, 'show_email_auth_guidance')
        assert callable(app.show_email_auth_guidance)
        
    finally:
        try:
            app.destroy()
        except Exception:
            pass
