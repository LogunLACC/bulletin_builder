import tkinter as tk
import pytest


def _ensure_minimal_ctx(app):
    class _Settings:
        def dump(self):
            return {
                'bulletin_title': 'Test Bulletin',
                'bulletin_date': '2025-08-20',
            }
    app.settings_frame = getattr(app, 'settings_frame', _Settings())
    app.sections_data = getattr(app, 'sections_data', [])


def test_export_frontsteps_writes_file_and_copies(monkeypatch, tmp_path):
    try:
        root = tk.Tk()
    except Exception as e:
        pytest.skip(f"Tk not available: {e}")
    try:
        from bulletin_builder.app_core import exporter
        exporter.init(root)
        _ensure_minimal_ctx(root)

        html_path = tmp_path / 'out.html'
        tmp_path / 'out.txt'

        import tkinter.filedialog as fd
        import tkinter.messagebox as mb
        monkeypatch.setattr(fd, 'asksaveasfilename', lambda **kw: str(html_path))
        monkeypatch.setattr(mb, 'showinfo', lambda *a, **kw: None)
        monkeypatch.setattr(mb, 'showerror', lambda *a, **kw: None)

        # Wire FrontSteps exporter and save path
        from bulletin_builder.app_core import exporter
        exporter.init(root)
        _ensure_minimal_ctx(root)
        frontsteps_path = tmp_path / 'out_frontsteps.html'

        import tkinter.filedialog as fd
        import tkinter.messagebox as mb
        monkeypatch.setattr(fd, 'asksaveasfilename', lambda **kw: str(frontsteps_path))
        monkeypatch.setattr(mb, 'showinfo', lambda *a, **kw: None)
        monkeypatch.setattr(mb, 'showerror', lambda *a, **kw: None)

        root.on_export_frontsteps_clicked()

        assert frontsteps_path.exists()
    finally:
        try:
            root.destroy()
        except Exception:
            pass


def test_no_ics_export_handler(monkeypatch):
    try:
        root = tk.Tk()
    except Exception as e:
        pytest.skip(f"Tk not available: {e}")
    try:
        from bulletin_builder.app_core import exporter
        exporter.init(root)
        assert not hasattr(root, 'on_export_ics_clicked')
    finally:
        try:
            root.destroy()
        except Exception:
            pass
