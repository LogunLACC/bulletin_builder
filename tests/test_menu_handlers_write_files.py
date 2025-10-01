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


def test_export_frontsteps_copies_to_clipboard(monkeypatch, tmp_path):
    from bulletin_builder.__main__ import BulletinBuilderApp
    try:
        app = BulletinBuilderApp()
    except Exception as e:
        pytest.skip(f"Tk not available: {e}")

    try:
        _ensure_minimal_ctx(app)

        # Mock clipboard and renderer
        clipboard_content = []
        def mock_clipboard_clear():
            clipboard_content.clear()
        def mock_clipboard_append(text):
            clipboard_content.append(text)

        monkeypatch.setattr(app, 'clipboard_clear', mock_clipboard_clear)
        monkeypatch.setattr(app, 'clipboard_append', mock_clipboard_append)
        monkeypatch.setattr(app, 'render_bulletin_html', lambda ctx: "<html><body>Mock Content</body></html>")
        monkeypatch.setattr(app, 'show_status_message', lambda *a, **kw: None)

        # Explicitly set export_frontsteps_html to fallback method
        from bulletin_builder.__main__ import BulletinBuilderApp
        app.export_frontsteps_html = BulletinBuilderApp.export_frontsteps_html.__get__(app)

        # Call the actual export handler
        app.export_current_preview()

        # Verify clipboard content
        assert len(clipboard_content) == 1
        assert "Mock Content" in clipboard_content[0]
        assert "<html>" not in clipboard_content[0] # Exporter should strip wrappers
    finally:
        try:
            app.destroy()
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
