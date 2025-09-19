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


def test_export_html_text_writes_files(monkeypatch, tmp_path):
    try:
        root = tk.Tk()
    except Exception as e:
        pytest.skip(f"Tk not available: {e}")
    try:
        from bulletin_builder.app_core import exporter
        exporter.init(root)
        _ensure_minimal_ctx(root)

        html_path = tmp_path / 'out.html'
        txt_path = tmp_path / 'out.txt'

        import tkinter.filedialog as fd
        import tkinter.messagebox as mb
        monkeypatch.setattr(fd, 'asksaveasfilename', lambda **kw: str(html_path))
        monkeypatch.setattr(mb, 'showinfo', lambda *a, **kw: None)
        monkeypatch.setattr(mb, 'showerror', lambda *a, **kw: None)

        root.on_export_html_text_clicked()

        assert html_path.exists()
        assert txt_path.exists()
    finally:
        try:
            root.destroy()
        except Exception:
            pass


def test_export_ics_writes_file(monkeypatch, tmp_path):
    try:
        root = tk.Tk()
    except Exception as e:
        pytest.skip(f"Tk not available: {e}")
    try:
        from bulletin_builder.app_core import exporter
        exporter.init(root)
        _ensure_minimal_ctx(root)

        # Provide one events section
        root.sections_data = [{
            'type': 'events',
            'content': [ {'title': 'Event A'} ]
        }]

        ics_path = tmp_path / 'events.ics'
        import tkinter.filedialog as fd
        import tkinter.messagebox as mb
        monkeypatch.setattr(fd, 'asksaveasfilename', lambda **kw: str(ics_path))
        monkeypatch.setattr(mb, 'showinfo', lambda *a, **kw: None)
        monkeypatch.setattr(mb, 'showerror', lambda *a, **kw: None)

        root.on_export_ics_clicked()

        assert ics_path.exists()
        text = ics_path.read_text(encoding='utf-8')
        assert 'BEGIN:VCALENDAR' in text
        assert 'SUMMARY:Event A' in text
    finally:
        try:
            root.destroy()
        except Exception:
            pass
