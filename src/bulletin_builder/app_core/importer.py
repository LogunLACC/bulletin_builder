import csv
import io
import urllib.request
from tkinter import filedialog, messagebox, simpledialog

from ..event_feed import fetch_events, events_to_blocks, process_event_images


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

    def import_events_feed():
        url = simpledialog.askstring('Events Feed URL', 'Enter events JSON/CSV URL:')
        if not url:
            return
        try:
            raw_events = fetch_events(url)
        except Exception as e:
            messagebox.showerror('Import Error', str(e))
            return
        events = events_to_blocks(raw_events)
        process_event_images(events)
        if not events:
            messagebox.showinfo('Import Events', 'No events found.')
            return
        app.sections_data.append({
            'title': 'Community Events',
            'type': 'community_events',
            'content': events,
            'layout_style': 'Card'
        })
        app.refresh_listbox_titles()
        app.show_placeholder()
        app.update_preview()
        app.show_status_message(f"Imported {len(events)} events")

    app.import_announcements_csv = import_csv_file
    app.import_announcements_sheet = import_google_sheet
    app.import_events_feed = import_events_feed
