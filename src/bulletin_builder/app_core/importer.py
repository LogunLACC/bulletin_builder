import csv
import io
import urllib.request
from tkinter import filedialog, messagebox, simpledialog


def init(app):
    """Attach CSV/Google Sheets import handlers onto app."""

    def _rows_to_sections(rows):
        count = 0
        for row in rows:
            if not any(row.values()):
                continue
            app.sections_data.append({
                'title': row.get('title', '').strip(),
                'type': 'announcements',
                'body': row.get('body', '').strip(),
                'link': row.get('link', '').strip(),
                'link_text': row.get('link_text', '').strip(),
            })
            count += 1
        if count:
            app.refresh_listbox_titles()
            app.show_placeholder()
            app.update_preview()
            app.show_status_message(f"Imported {count} announcements")

    def import_csv_file():
        path = filedialog.askopenfilename(
            defaultextension='.csv', filetypes=[('CSV Files','*.csv')],
            initialdir='.', title='Import Announcements CSV'
        )
        if not path:
            return
        try:
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            messagebox.showerror('Import Error', str(e))
            return
        _rows_to_sections(rows)

    def import_google_sheet():
        url = simpledialog.askstring('Google Sheet URL', 'Enter public CSV URL:')
        if not url:
            return
        try:
            with urllib.request.urlopen(url) as resp:
                text = resp.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(text))
            rows = list(reader)
        except Exception as e:
            messagebox.showerror('Import Error', str(e))
            return
        _rows_to_sections(rows)

    app.import_announcements_csv = import_csv_file
    app.import_announcements_sheet = import_google_sheet
