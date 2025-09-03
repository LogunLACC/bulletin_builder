def test_menu_items_are_bound_and_callable():
    """Ensure menu-targeted callbacks exist after init and are callable.

    Skips if Tk is unavailable (e.g., headless CI without Tk installed).
    """
    import tkinter as tk
    import pytest

    from bulletin_builder.app_core import exporter, preview, ui_setup, importer

    try:
        root = tk.Tk()
    except Exception as e:
        pytest.skip(f"Tk not available: {e}")
    try:
        # Bind handlers that menus expect
        exporter.init(root)
        preview.init(root)
        importer.init(root)
        ui_setup.init(root)

        # Check essential callbacks
        for name in (
            'on_export_html_text_clicked',
            'on_copy_for_email_clicked',
            'on_export_ics_clicked',
            'on_send_test_email_clicked',
            'export_bulletin_html',
            'export_email_html',
            'open_in_browser',
            'import_announcements_csv',
            'import_events_feed',
            'auto_sync_events_feed',
        ):
            fn = getattr(root, name, None)
            assert callable(fn), f"Missing or non-callable: {name}"
    finally:
        try:
            root.destroy()
        except Exception:
            pass
