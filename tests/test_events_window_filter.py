def test_filter_events_window_today_only():
    from datetime import datetime, timezone, timedelta
    from bulletin_builder.event_feed import filter_events_window

    today = datetime.now(timezone.utc).date()
    tomorrow = today + timedelta(days=1)
    events = [
        {"date": today.isoformat(), "description": "Today"},
        {"date": tomorrow.isoformat(), "description": "Tomorrow"},
    ]

    out = filter_events_window(events, days=0, start_date=today)
    assert len(out) == 1
    assert out[0]["description"] == "Today"


def test_importer_respects_events_window(monkeypatch):
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
        from datetime import datetime, timezone, timedelta
        today = datetime.now(timezone.utc).date()
        tomorrow = today + timedelta(days=1)

        from bulletin_builder.app_core import importer
        importer.init(root)
        root.events_window_days = 0
        if not hasattr(root, 'sections_data'):
            root.sections_data = []

        # Make threaded calls synchronous
        monkeypatch.setattr(importer, '_submit', lambda app, fn: fn())
        root.after = lambda delay, cb: cb()

        sample = [
            {"date": today.isoformat(), "time": "9am", "description": "X"},
            {"date": tomorrow.isoformat(), "time": "9am", "description": "Y"},
        ]
        monkeypatch.setattr(importer, 'fetch_events', lambda url: sample)
        monkeypatch.setattr(importer, 'process_event_images', lambda events: None)

        import tkinter.messagebox as mb
        monkeypatch.setattr(mb, 'showinfo', lambda *a, **kw: None)
        monkeypatch.setattr(mb, 'showwarning', lambda *a, **kw: None)
        monkeypatch.setattr(mb, 'showerror', lambda *a, **kw: None)

        root.import_events_feed('http://example.com/feed')

        sec = next((s for s in root.sections_data if s.get('type') == 'community_events'), None)
        assert sec is not None
        ds = [ev.get('date') for ev in sec.get('content')]
        assert ds == [today.isoformat()]
    finally:
        try:
            root.destroy()
        except Exception:
            pass

