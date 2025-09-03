"""Lightweight GUI smoke script: create an announcements section, save, exit.
This script is programmatic and doesn't require manual interaction.
"""
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parents[1])

from bulletin_builder.__main__ import BulletinBuilderApp


def run():
    app = BulletinBuilderApp()
    # Ensure user_drafts dir
    Path('user_drafts').mkdir(exist_ok=True)
    app.sections_data.append({'title': 'Smoke Ann', 'type': 'announcements', 'content': []})
    app.refresh_listbox_titles()
    idx = len(app.sections_data) - 1
    app.section_listbox.selection_clear(0, 'end')
    app.section_listbox.selection_set(idx)
    app.on_section_select()
    frame = app.editor_container.winfo_children()[0]
    frame._add_item()
    frame._load_into_editor(0)
    frame.title_entry.delete(0, 'end'); frame.title_entry.insert(0, 'Smoke Title')
    frame.body_text.delete('1.0', 'end'); frame.body_text.insert('1.0', 'Smoke Body')
    frame._save_current_if_any()
    app.current_draft_path = 'user_drafts/smoke_draft.json'
    app.save_draft()
    print('Saved smoke draft:', app.current_draft_path)


if __name__ == '__main__':
    run()
