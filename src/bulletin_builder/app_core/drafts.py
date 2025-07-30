import json
from pathlib import Path
from tkinter import filedialog, messagebox
from datetime import date

def init(app):
    def _default_settings():
        return {
            'bulletin_title': 'LACC Bulletin',
            'bulletin_date': date.today().strftime('%A, %B %d, %Y'),
            'theme_css': 'default.css',
            'colors': {'primary':'#103040','secondary':'#506070'},
            'google_api_key': app.google_api_key
        }

    def new_draft():
        if messagebox.askyesno('New Draft','Discard current draft and start new?'):
            app.sections_data.clear()
            app.current_draft_path = None
            if hasattr(app.settings_frame,'load_data'):
                app.settings_frame.load_data(_default_settings(), app.google_api_key)
            app.refresh_listbox_titles()
            app.show_placeholder()
            app.update_preview()
    def open_draft():
        path = filedialog.askopenfilename(
            defaultextension='.json', filetypes=[('Drafts','*.json')],
            initialdir='./user_drafts', title='Open Draft'
        )
        if not path: return
        try:
            data = json.loads(Path(path).read_text(encoding='utf-8'))
        except Exception as e:
            messagebox.showerror('Open Error',str(e)); return
        app.sections_data[:] = data.get('sections',[])
        app.current_draft_path = path
        settings = data.get('settings', _default_settings())
        if hasattr(app.settings_frame,'load_data'):
            app.settings_frame.load_data(settings, settings.get('google_api_key',app.google_api_key))
        app.refresh_listbox_titles()
        app.show_placeholder()
        app.update_preview()
    def save_draft(save_as=False):
        if not app.current_draft_path or save_as:
            path = filedialog.asksaveasfilename(
                defaultextension='.json', filetypes=[('Drafts','*.json')],
                initialdir='./user_drafts', title='Save Draft As'
            )
            if not path: return
            app.current_draft_path = path
        payload = {
            'sections': app.sections_data,
            'settings': app.settings_frame.dump()
        }
        try:
            Path(app.current_draft_path).write_text(json.dumps(payload,indent=2), encoding='utf-8')
            app.show_status_message(f"Draft saved: {Path(app.current_draft_path).name}")
        except Exception as e:
            messagebox.showerror('Save Error',str(e))

    app.new_draft  = new_draft
    app.open_draft = open_draft
    app.save_draft = save_draft
