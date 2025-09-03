import os, json
os.chdir(r'C:\Users\LogunJohnston\OneDrive - Lake Almanor\Documents\MyPy\GitHub\lacc-dev\Bulletin Builder')
from bulletin_builder.__main__ import BulletinBuilderApp
from pathlib import Path

# Prepare app
app = BulletinBuilderApp()
# ensure user_drafts exists
Path('user_drafts').mkdir(exist_ok=True)
# Create an announcements section and select it
app.sections_data.append({'title':'Test Announcements','type':'announcements','content':[]})
app.refresh_listbox_titles()
idx = len(app.sections_data)-1
app.section_listbox.selection_clear(0,'end')
app.section_listbox.selection_set(idx)
app.on_section_select()
frame = app.editor_container.winfo_children()[0]
print('Editor frame:', type(frame))
# Add and edit an item
frame._add_item()
frame._load_into_editor(0)
frame.title_entry.delete(0,'end'); frame.title_entry.insert(0,'Programmatic Title')
frame.body_text.delete('1.0','end'); frame.body_text.insert('1.0','Programmatic body text')
# Debug: inspect announcements and indices prior to save
print('\n[DEBUG] frame.current_index =', getattr(frame, 'current_index', None))
print('[DEBUG] frame.announcements before save =', getattr(frame, 'announcements', None))
print('[DEBUG] app.active_editor_index =', getattr(app, 'active_editor_index', None))
print('[DEBUG] app has update_section_data =', hasattr(app, 'update_section_data'))

frame._save_current_if_any()

print('[DEBUG] frame.announcements after save =', getattr(frame, 'announcements', None))
try:
	print('[DEBUG] target section before manual update =', app.sections_data[app.active_editor_index])
except Exception:
	pass

# Save draft
path = 'user_drafts/tmp_test_draft.json'
app.current_draft_path = path
app.save_draft()
print('\nSaved draft path:', path)
# Read back and print content
data = json.loads(Path(path).read_text(encoding='utf-8'))
print(json.dumps(data, indent=2))
# Also print app.sections_data for quick check
print('\nApp sections_data:', app.sections_data)
