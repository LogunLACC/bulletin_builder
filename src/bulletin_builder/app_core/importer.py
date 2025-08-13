# -*- coding: utf-8 -*-
import csv
import io
import urllib.request
import threading
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog

from bulletin_builder.event_feed import (
    fetch_events,
    events_to_blocks,
    process_event_images,
    expand_recurring_events,
    detect_conflicts,
)

NET_TIMEOUT = 12  # seconds


def init(app):
    """Attach CSV/JSON/Feed import handlers onto app."""

    # ---------- CSV FILE ----------
    def import_csv_file():
        path = filedialog.askopenfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialdir="./user_drafts",
            title="Import Announcements CSV",
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            messagebox.showerror("Import Error", str(e))
            return
        _rows_to_sections(app, rows)

    # ---------- GOOGLE SHEET (public CSV URL) ----------
    def import_google_sheet():
        url = simpledialog.askstring("Google Sheet URL", "Enter public CSV URL:")
        if not url:
            return
        if hasattr(app, "_show_progress"):
            app._show_progress("Fetching Google Sheet…")

        def _worker():
            try:
                with urllib.request.urlopen(url, timeout=NET_TIMEOUT) as resp:
                    text = resp.read().decode("utf-8")
                reader = csv.DictReader(io.StringIO(text))
                rows = list(reader)
            except Exception as e:
                err = e  # capture
                app.after(0, lambda err=err: messagebox.showerror("Import Error", str(err)))
                if hasattr(app, "_hide_progress"):
                    app.after(0, app._hide_progress)
                return

            app.after(0, lambda: (_rows_to_sections(app, rows),
                                  hasattr(app, "_hide_progress") and app._hide_progress()))

        _submit(app, _worker)

    # ---------- EVENTS FEED (JSON/CSV URL) ----------
    def import_events_feed(url: str | None = None):
        if not url:
            url = simpledialog.askstring("Events Feed URL", "Enter events JSON/CSV URL:")
        if not url:
            return

        if hasattr(app, "_show_progress"):
            app._show_progress("Fetching events…")

        def _worker():
            try:
                raw_events = fetch_events(url)  # ensure internal timeouts inside fetch_events
            except Exception as e:
                app.after(0, lambda e=e: messagebox.showerror("Import Error", str(e)))
                if hasattr(app, "_hide_progress"):
                    app.after(0, app._hide_progress)
                return

            raw_events_local = expand_recurring_events(raw_events)

            def _apply():
                # (Optional) interactive filters by date/tags could go here
                events = events_to_blocks(raw_events_local)
                process_event_images(events)
                conflicts = detect_conflicts(events)
                if conflicts:
                    msg_lines = ["Overlapping events detected:"]
                    for a, b in conflicts:
                        msg_lines.append(
                            f"- {a.get('description','')} ({a.get('date')} {a.get('time')}) ↔ "
                            f"{b.get('description','')} ({b.get('date')} {b.get('time')})"
                        )
                    messagebox.showwarning("Event Conflicts", "\n".join(msg_lines))

                if not events:
                    messagebox.showinfo("Import Events", "No events found.")
                else:
                    app.sections_data.append({
                        "title": "Community Events",
                        "type": "community_events",
                        "content": events,
                        "layout_style": "Card",
                    })
                    if hasattr(app, "refresh_listbox_titles"):
                        app.refresh_listbox_titles()
                    if hasattr(app, "show_placeholder"):
                        app.show_placeholder()
                    if hasattr(app, "update_preview"):
                        app.update_preview()
                    if hasattr(app, "show_status_message"):
                        app.show_status_message(f"Imported {len(events)} events")

                if hasattr(app, "_hide_progress"):
                    app._hide_progress()

            app.after(0, _apply)

        _submit(app, _worker)

    # ---------- AUTO SYNC AFTER UI SHOWS ----------
    def auto_sync_events_feed():
        url = getattr(app, "events_feed_url", "")
        if not url:
            return
        # defer slightly so the window is visible, then run threaded
        app.after(300, lambda: import_events_feed(url))

    # Attach
    app.import_announcements_csv = import_csv_file
    app.import_announcements_sheet = import_google_sheet
    app.import_events_feed = import_events_feed
    app.auto_sync_events_feed = auto_sync_events_feed

    # kick off auto-sync if configured
    app.auto_sync_events_feed()


# --- INTERNAL ----------------------------------------------------------------

def _submit(app, fn):
    """Submit work to app's executor or a daemon thread."""
    if getattr(app, "_thread_executor", None):
        app._thread_executor.submit(fn)
    else:
        threading.Thread(target=fn, daemon=True).start()

def _rows_to_sections(app, rows):
    """Convert CSV rows into a section and refresh UI."""
    if not rows:
        messagebox.showinfo("Import CSV", "No rows found.")
        return
    items = []
    for r in rows:
        items.append({
            "title": (r.get("title") or r.get("name") or "").strip(),
            "description": (r.get("description") or r.get("details") or "").strip(),
            "date": (r.get("date") or r.get("start_date") or "").strip(),
            "time": (r.get("time") or r.get("start_time") or "").strip(),
            "location": (r.get("location") or r.get("venue") or "").strip(),
            "url": (r.get("url") or r.get("link") or "").strip(),
        })
    app.sections_data.append({
        "title": "Announcements",
        "type": "announcements",
        "content": items,
        "layout_style": "List",
    })
    if hasattr(app, "refresh_listbox_titles"):
        app.refresh_listbox_titles()
    if hasattr(app, "show_placeholder"):
        app.show_placeholder()
    if hasattr(app, "update_preview"):
        app.update_preview()
    if hasattr(app, "show_status_message"):
        app.show_status_message(f"Imported {len(items)} announcements")
