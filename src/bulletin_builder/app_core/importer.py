# --- Non-disruptive CSV parser helpers (append-only) -------------------
def _bb_norm(value):
    """Normalize a single CSV cell value to a stripped string (None -> '')."""
    if value is None:
        return ""
    return str(value).strip()

def _bb_norm_header(h):
    """Normalize a header name for mapping (lowercase, underscores)."""
    s = _bb_norm(h).lower()
    for ch in (" ", "-", ".", "/"):
        s = s.replace(ch, "_")
    return s

_BB_HEADER_MAP = {
    # title
    "title": "title",
    "subject": "title",
    "headline": "title",
    # body
    "body": "body",
    "message": "body",
    "text": "body",
    "content": "body",
    "description": "body",
    # link url
    "link": "link",
    "url": "link",
    "href": "link",
    "website": "link",
    # link text
    "link_text": "link_text",
    "cta": "link_text",
    "button_text": "link_text",
    "anchor": "link_text",
}

def parse_announcements_csv(text):
    """
    Parse CSV text into a list of dicts:
      {title, body, link, link_text}
    - Handles BOM
    - Detects delimiter (comma/semicolon/tab/pipe)
    - Accepts many header synonyms (case-insensitive)
    - Skips blank lines
    - Defaults link_text to 'Learn more' when link is present but text is blank
    This helper is append-only and does not modify existing import logic.
    """
    if not text:
        return []
    # Strip BOM if present
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")
    # Detect delimiter
    try:
        sample = text[:2048]
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"])
    except Exception:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    if not reader.fieldnames:
        return []
    # Build a header mapping once
    hdr_map = {}
    for raw in reader.fieldnames:
        mapped = _BB_HEADER_MAP.get(_bb_norm_header(raw))
        hdr_map[raw] = mapped  # may be None for unrecognized
    items = []
    for raw_row in reader:
        if not raw_row:
            continue
        row = {"title": "", "body": "", "link": "", "link_text": ""}
        for raw_key, value in raw_row.items():
            target = hdr_map.get(raw_key)
            if not target:
                continue
            row[target] = _bb_norm(value)
        if any(row.values()):
            if row["link"] and not row["link_text"]:
                row["link_text"] = "Learn more"
            items.append(row)
    return items
# -*- coding: utf-8 -*-
import io
import csv
import urllib.request
import threading
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
    # Bind handler callables onto the app
    app.import_announcements_csv = lambda: import_csv_file(app)
    app.import_announcements_sheet = lambda: import_google_sheet(app)
    app.import_events_feed = lambda url=None: import_events_feed(app, url)

    def auto_sync_events_feed():
        url = getattr(app, "events_feed_url", "")
        if not url:
            return
        app.after(300, lambda: import_events_feed(app, url))

    app.auto_sync_events_feed = auto_sync_events_feed
    # Kick off auto-sync if configured
    try:
        app.auto_sync_events_feed()
    except Exception:
        pass

    # ---------- CSV FILE ----------
def import_csv_file(app):
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
            text = f.read()
        # Use robust parser
        parsed = parse_announcements_csv(text)
        announcements = parsed
        _apply_announcements_to_app(app, announcements)
        print("Imported Announcements:", announcements)
        if hasattr(app, "refresh_listbox_titles"):
            app.refresh_listbox_titles()
        if hasattr(app, "show_placeholder"):
            app.show_placeholder()
        if hasattr(app, "update_preview"):
            app.update_preview()
        if hasattr(app, "show_status_message"):
            app.show_status_message(f"Imported {len(announcements)} announcements")
    except Exception as e:
        messagebox.showerror("Import Error", str(e))
        return

    # ---------- GOOGLE SHEET (public CSV URL) ----------
def import_google_sheet(app):
    url = simpledialog.askstring("Google Sheet URL", "Enter public CSV URL:")
    if not url:
        return
    url = url.strip().strip('"\'')
    if hasattr(app, "_show_progress"):
        app._show_progress("Fetching Google Sheet...")

    def _worker():
        try:
            with urllib.request.urlopen(url, timeout=NET_TIMEOUT) as resp:
                text = resp.read().decode("utf-8")
            # Reuse the robust CSV parser so headers like 'Link Text' map correctly
            parsed = parse_announcements_csv(text)
        except Exception as e:
            err = e
            app.after(0, lambda err=err: messagebox.showerror("Import Error", str(err)))
            if hasattr(app, "_hide_progress"):
                app.after(0, app._hide_progress)
            return

        def _apply():
            _apply_announcements_to_app(app, parsed)
            if hasattr(app, "_hide_progress"):
                app._hide_progress()

        app.after(0, _apply)

    _submit(app, _worker)

    # ---------- EVENTS FEED (JSON/CSV URL) ----------
def import_events_feed(app, url: str | None = None):
    if not url:
        url = simpledialog.askstring("Events Feed URL", "Enter events JSON/CSV URL:")
    if not url:
        return
    # Sanitize URL: strip whitespace and quotes
    url = url.strip().strip('"\'')
    if hasattr(app, "_show_progress"):
        app._show_progress("Fetching events...")

    def _worker():
        try:
            raw_events = fetch_events(url)  # ensure internal timeouts inside fetch_events
        except Exception as e:
            app.after(0, lambda e=e: messagebox.showerror("Import Error", str(e)))
            if hasattr(app, "_hide_progress"):
                app.after(0, app._hide_progress)
            return

        raw_events_local = expand_recurring_events(raw_events)
        events = events_to_blocks(raw_events_local)
        # Optional: restrict to a window starting today when configured
        try:
            wnd = getattr(app, 'events_window_days', None)
            if isinstance(wnd, int) and wnd >= 0:
                from bulletin_builder.event_feed import filter_events_window
                events = filter_events_window(events, days=wnd)
        except Exception:
            pass

        # Dedupe events to avoid repeated entries in UI
        try:
            from bulletin_builder.event_feed import dedupe_events
            events = dedupe_events(events)
        except Exception:
            pass
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

        def _apply():
            if not events:
                messagebox.showinfo("Import Events", "No events found.")
            else:
                if not hasattr(app, "sections_data"):
                    app.sections_data = []
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
            # Warn if outdated events were present
            # (If you want to implement outdated event detection, add logic here.)

            if hasattr(app, "_hide_progress"):
                app._hide_progress()

        app.after(0, _apply)

    _submit(app, _worker)


# --- INTERNAL ----------------------------------------------------------------

def _submit(app, fn):
    """Submit work to app's executor or a daemon thread."""
    if getattr(app, "_thread_executor", None):
        app._thread_executor.submit(fn)
    else:
        threading.Thread(target=fn, daemon=True).start()


# New: robust mapping for announcements CSV import
def _apply_announcements_to_app(app, announcements):
    """Update or create the Announcements section and refresh the UI."""
    if not hasattr(app, "sections_data"):
        app.sections_data = []
    sections = app.sections_data
    ann_section = next((s for s in sections if s.get("type") == "announcements"), None)
    if ann_section is None:
        ann_section = {"type": "announcements", "title": "Announcements", "content": []}
        sections.append(ann_section)
    ann_section["content"] = announcements
    # Make the current announcements section discoverable by any editor frame
    try:
        app._last_announcements_section = ann_section
    except Exception:
        pass
    if not announcements:
        if hasattr(app, "show_status_message"):
            app.show_status_message("No announcements were imported (0 items)")
        return
    print("Imported Announcements:", announcements)
    if hasattr(app, "refresh_listbox_titles"):
        app.refresh_listbox_titles()
    if hasattr(app, "show_placeholder"):
        app.show_placeholder()
    if hasattr(app, "update_preview"):
        app.update_preview()
    if hasattr(app, "show_status_message"):
        app.show_status_message(f"Imported {len(announcements)} announcements")
