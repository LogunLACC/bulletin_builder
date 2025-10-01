def test_click_file_menu_export(monkeypatch, tmp_path):
    """Build the menu and invoke a real File->Export HTML & Text... entry.

    Skips if Tk is unavailable. Uses monkeypatch to avoid real dialogs.
    """
    import pytest
    try:
        import tkinter as tk
    except Exception as e:
        pytest.skip(f"Tk not importable: {e}")

    try:
        root = tk.Tk()
        # Add required handler stubs for menu tests
        root.export_current_preview = lambda: None
        root.destroy = lambda: None
    except Exception as e:
        pytest.skip(f"Tk not available: {e}")

    try:
        # Wire handlers and build menus
        from bulletin_builder.app_core import exporter, preview, ui_setup, importer
        exporter.init(root)
        preview.init(root)
        importer.init(root)
        ui_setup.init(root)

        # Minimal settings/context
        if not hasattr(root, 'sections_data'):
            root.sections_data = []
        if not hasattr(root, 'settings_frame'):
            class _Settings:
                def dump(self):
                    return {'bulletin_title': 'Test', 'bulletin_date': '2025-01-01'}
            root.settings_frame = _Settings()

        # Stub dialogs to a temp path
        out_html = tmp_path / 'menu_out.html'
        out_email = tmp_path / 'menu_email.html'
        import tkinter.filedialog as fd
        import tkinter.messagebox as mb
        def _choose_path(**kw):
            title = kw.get('title', '') or ''
            if 'Email' in title:
                return str(out_email)
            return str(out_html)
        monkeypatch.setattr(fd, 'asksaveasfilename', _choose_path)
        monkeypatch.setattr(mb, 'showinfo', lambda *a, **kw: None)
        monkeypatch.setattr(mb, 'showerror', lambda *a, **kw: None)

        assert hasattr(root, '_build_menus')
        root._build_menus()

        # Resolve the attached menubar and File menu
        # Prefer direct reference if exposed by builder
        file_menu = getattr(root, '_file_menu', None)
        if file_menu is None:
            menubar = root.nametowidget(root['menu'])
            # Fallback: locate the first cascade as File menu
            end = menubar.index('end') or 0
            file_menu = None
            for i in range(end + 1):
                if menubar.type(i) == 'cascade':
                    try:
                        mname = menubar.entrycget(i, 'menu')
                        file_menu = menubar.nametowidget(mname)
                        break
                    except Exception:
                        continue
        assert file_menu is not None

        # Find and invoke the "Export Bulletin (FrontSteps)" command
        target_idx = None
        end = file_menu.index('end') or 0
        for i in range(end + 1):
            if file_menu.type(i) != 'command':
                continue
            if (file_menu.entrycget(i, 'label') or '').startswith('Export Bulletin (FrontSteps)'):
                target_idx = i
                break
        assert target_idx is not None, 'Menu item not found'
        file_menu.invoke(target_idx)
    finally:
        try:
            root.destroy()
        except Exception:
            pass
