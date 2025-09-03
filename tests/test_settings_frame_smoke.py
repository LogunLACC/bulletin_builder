def test_settings_frame_smoke():
    import tkinter as tk
    from bulletin_builder.ui.settings import SettingsFrame

    try:
        root = tk.Tk()
    except Exception as e:
        import pytest
        pytest.skip(f"Tk not available: {e}")
    try:
        # provide simple no-op callbacks
        f = SettingsFrame(root, lambda: None, lambda k: None, lambda k: None, lambda u: None)
        f.load_data({}, "", "", "")
        data = f.dump()
        assert isinstance(data, dict)
        assert "bulletin_title" in data
    finally:
        root.destroy()
