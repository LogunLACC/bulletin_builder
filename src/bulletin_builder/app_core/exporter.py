# app_core/exporter.py

import tempfile
import webbrowser
from pathlib import Path
from tkinter import filedialog
from uuid import uuid4
from datetime import datetime

from ..ui.calendar_event_dialog import CalendarEventDialog

from premailer import transform
from weasyprint import HTML

def init(app):
    """
    Attach export & email handlers onto app.
    Must run before ui_setup so open_in_browser exists when the button is created.
    """
    # --- Export to PDF (threaded) ---
    def on_export_pdf_clicked():
        app.export_button.configure(state="disabled")
        app.email_button.configure(state="disabled")
        app._show_progress("Exporting PDF…")
        future = app._thread_executor.submit(_do_export_pdf)
        future.add_done_callback(_on_export_pdf_done)

    def _do_export_pdf():
        settings = app.settings_frame.dump()
        html = app.renderer.render_html(app.sections_data, settings)
        base = app.renderer.templates_dir.as_uri() + "/"
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents","*.pdf")],
            initialdir="./user_drafts",
            title="Export to PDF"
        )
        if not path:
            return None
        HTML(string=html, base_url=base).write_pdf(path)
        return Path(path).name

    def _on_export_pdf_done(fut):
        try:
            name = fut.result()
            if name:
                app.after(0, lambda: app.show_status_message(f"PDF exported: {name}"))
        finally:
            app.after(0, app._hide_progress)
            app.after(0, lambda: app.export_button.configure(state="normal"))
            app.after(0, lambda: app.email_button.configure(state="normal"))

    app.on_export_pdf_clicked = on_export_pdf_clicked

    # --- Copy for Email (threaded) ---
    def on_copy_for_email_clicked():
        app.export_button.configure(state="disabled")
        app.email_button.configure(state="disabled")
        app._show_progress("Preparing email HTML…")
        future = app._thread_executor.submit(_do_copy_for_email)
        future.add_done_callback(_on_copy_for_email_done)

    def _do_copy_for_email():
        settings = app.settings_frame.dump()
        html = app.renderer.render_html(app.sections_data, settings)
        return transform(html)

    def _on_copy_for_email_done(fut):
        try:
            content = fut.result()
            app.after(0, app.clipboard_clear)
            app.after(0, lambda: app.clipboard_append(content))
            app.after(0, lambda: app.show_status_message("Email‑ready HTML copied!"))
        finally:
            app.after(0, app._hide_progress)
            app.after(0, lambda: app.export_button.configure(state="normal"))
            app.after(0, lambda: app.email_button.configure(state="normal"))

    app.on_copy_for_email_clicked = on_copy_for_email_clicked

    # --- Open current bulletin in default browser ---
    def open_in_browser():
        settings = app.settings_frame.dump()
        html = app.renderer.render_html(app.sections_data, settings)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        tmp.write(html.encode("utf-8"))
        tmp.close()
        webbrowser.open(tmp.name)

    app.open_in_browser = open_in_browser

    # --- Export calendar event as .ics ---
    def on_export_ics_clicked():
        dlg = CalendarEventDialog(app)
        data = dlg.get_data()
        if not data:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".ics",
            filetypes=[("iCalendar Files", "*.ics")],
            initialdir="./user_drafts",
            title="Save ICS File"
        )
        if not path:
            return
        ics_content = _build_ics(data)
        with open(path, "w", encoding="utf-8") as f:
            f.write(ics_content)
        app.show_status_message(f"ICS exported: {Path(path).name}")

    def _build_ics(data: dict) -> str:
        fmt = "%Y%m%dT%H%M%S"
        start = data["start"].strftime(fmt)
        end = data["end"].strftime(fmt)
        stamp = datetime.utcnow().strftime(fmt)
        uid = uuid4()
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//LACC Bulletin Builder//EN",
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{stamp}Z",
            f"DTSTART:{start}",
            f"DTEND:{end}",
            f"SUMMARY:{data['title']}",
            f"DESCRIPTION:{data.get('description', '')}",
            f"LOCATION:{data.get('location', '')}",
            "END:VEVENT",
            "END:VCALENDAR",
        ]
        return "\n".join(lines)

    app.on_export_ics_clicked = on_export_ics_clicked
