def test_fallback_menu_builds_without_error():
    import pytest
    try:
        import tkinter as tk
    except Exception as e:
        pytest.skip(f"Tk not importable: {e}")

    try:
        root = tk.Tk()
    except Exception as e:
        pytest.skip(f"Tk not available: {e}")

    try:
        # Provide handlers so menu items wire cleanly
        root.on_export_html_text_clicked = lambda: None
        root.on_copy_for_email_clicked = lambda: None
        root.open_in_browser = lambda: None
        root.import_announcements_csv = lambda: None
        root.on_export_ics_clicked = lambda: None
        root.on_send_test_email_clicked = lambda: None
        root.export_bulletin_html = lambda: None
        root.export_email_html = lambda: None

        from bulletin_builder import __main__ as mainmod
        # Use the class method on a Tk root (enough for building menus)
        mainmod.BulletinBuilderApp._build_menus_fallback(root)
    finally:
        try:
            root.destroy()
        except Exception:
            pass

