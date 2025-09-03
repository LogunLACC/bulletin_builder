def test_menu_builder_does_not_raise():
    """Basic smoke test: ensure ui_setup.init can attach a menu and call it.

    This uses a real Tk root but performs minimal interactions and then destroys
    the root to avoid leaving windows open in CI.
    """
    import tkinter as tk
    from bulletin_builder.app_core import ui_setup

    try:
        root = tk.Tk()
    except Exception as e:
        # In CI or headless environments tk may not be installed/configured.
        # Skip the test to avoid false negatives. Local devs should run GUI tests
        # on machines with a working Tk installation.
        import pytest

        pytest.skip(f"Tk not available: {e}")
    try:
        # init will attach many attributes; we only need it to set up the menu
        ui_setup.init(root)
        assert hasattr(root, "_build_menus")
        # calling the attached builder should not raise
        root._build_menus()
    finally:
        root.destroy()
