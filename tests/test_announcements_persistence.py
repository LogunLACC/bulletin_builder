import os
import json


def test_announcements_persistence(tmp_path):
    """Programmatic test that edits an announcements section and verifies persistence to JSON."""
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        from bulletin_builder.__main__ import BulletinBuilderApp

        app = BulletinBuilderApp()
        # Add an announcements section and select it
        app.sections_data.append({"title": "Test Ann", "type": "announcements", "content": []})
        app.refresh_listbox_titles()
        idx = len(app.sections_data) - 1
        app.section_listbox.selection_clear(0, "end")
        app.section_listbox.selection_set(idx)
        app.on_section_select()

        frame = app.editor_container.winfo_children()[0]
        # Add a new announcement and edit title/body
        frame._add_item()
        frame._load_into_editor(0)
        frame.title_entry.delete(0, "end")
        frame.title_entry.insert(0, "PTitle")
        frame.body_text.delete("1.0", "end")
        frame.body_text.insert("1.0", "PBody")
        frame._save_current_if_any()

        # Save draft to tmp file and assert content
        path = tmp_path / "draft.json"
        app.current_draft_path = str(path)
        app.save_draft()

        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["sections"][0]["content"][0]["title"] == "PTitle"
        assert data["sections"][0]["content"][0]["body"] == "PBody"
    finally:
        os.chdir(cwd)
