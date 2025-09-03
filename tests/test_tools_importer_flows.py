import os
import io
import tkinter as tk
import pytest


def _mk_root_or_skip():
    try:
        return tk.Tk()
    except Exception as e:
        pytest.skip(f"Tk not available: {e}")


def test_import_csv_updates_announcements(monkeypatch, tmp_path):
    root = _mk_root_or_skip()
    try:
        from bulletin_builder.app_core import importer
        importer.init(root)
        if not hasattr(root, 'sections_data'):
            root.sections_data = []
        # Ensure sections_data exists for appending
        if not hasattr(root, 'sections_data'):
            root.sections_data = []

        csv_path = tmp_path / "ann.csv"
        csv_path.write_text("Title,Body,Link\nA1,Body1,http://example.com\n", encoding="utf-8")

        import tkinter.filedialog as fd
        import tkinter.messagebox as mb
        monkeypatch.setattr(fd, 'askopenfilename', lambda **kw: str(csv_path))
        monkeypatch.setattr(mb, 'showinfo', lambda *a, **kw: None)
        monkeypatch.setattr(mb, 'showerror', lambda *a, **kw: None)

        # Invoke tools menu handler
        root.import_announcements_csv()

        assert hasattr(root, 'sections_data')
        anns = next((s for s in root.sections_data if s.get('type') == 'announcements'), None)
        assert anns is not None and isinstance(anns.get('content'), list)
        assert anns['content'] and anns['content'][0]['title'] == 'A1'
    finally:
        try:
            root.destroy()
        except Exception:
            pass


def test_import_events_feed_adds_section(monkeypatch):
    root = _mk_root_or_skip()
    try:
        from bulletin_builder.app_core import importer
        importer.init(root)

        # Synchronous submit and after
        monkeypatch.setattr(importer, '_submit', lambda app, fn: fn())
        root.after = lambda delay, cb: cb()

        # Stub fetch + processing
        sample = [{
            'date': '2099-01-01',
            'time': '9am',
            'description': 'Sample Event',
            'image_url': '',
            'tags': [],
            'link': '',
            'map_link': ''
        }]
        monkeypatch.setattr(importer, 'fetch_events', lambda url: sample)
        monkeypatch.setattr(importer, 'process_event_images', lambda events: None)

        import tkinter.messagebox as mb
        monkeypatch.setattr(mb, 'showinfo', lambda *a, **kw: None)
        monkeypatch.setattr(mb, 'showwarning', lambda *a, **kw: None)
        monkeypatch.setattr(mb, 'showerror', lambda *a, **kw: None)

        root.import_events_feed('http://example.com/feed')

        sec = next((s for s in getattr(root, 'sections_data', []) if s.get('type') == 'community_events'), None)
        assert sec is not None
        assert isinstance(sec.get('content'), list)
        assert any('Sample Event' in (ev.get('description','') or ev.get('title','')) for ev in sec['content'])
    finally:
        try:
            root.destroy()
        except Exception:
            pass
