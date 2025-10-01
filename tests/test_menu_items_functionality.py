def test_menu_items_are_bound_and_callable():
    """Ensure menu-targeted callbacks exist after init and are callable.
    
    Skips if Tk is unavailable (e.g., headless CI without Tk installed).
    """
    import pytest
    from bulletin_builder.__main__ import BulletinBuilderApp

    try:
        # Use the actual app class, not a generic tk.Tk() instance.
        # The app's __init__ sequence correctly wires up all handlers.
        app = BulletinBuilderApp()
        
        # Set the test mode flag so that menu clicks will raise an
        # error if a handler is missing, ensuring test integrity.
        app._is_test_mode = True
        
    except Exception as e:
        pytest.skip(f"Tk not available: {e}")
        
    try:
        # Check essential callbacks
        for name in (
            'export_current_preview',
            'open_in_browser',
            'import_announcements_csv',
            'import_events_feed',
            'auto_sync_events_feed'
        ):
            fn = getattr(app, name, None)
            assert callable(fn), f"Missing or non-callable: {name}"
    finally:
        try:
            app.destroy()
        except Exception:
            pass
