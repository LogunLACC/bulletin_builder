# -*- coding: utf-8 -*-
import tempfile
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox
from uuid import uuid4
from datetime import datetime

import configparser
import os
import smtplib
from email.message import EmailMessage

from bulletin_builder.ui.calendar_event_dialog import CalendarEventDialog
from bulletin_builder.ui.email_dialog import EmailDialog

from premailer import transform
from html.parser import HTMLParser

# --- HELPERS -----------------------------------------------------------------

class _PlainTextExtractor(HTMLParser):
    """Simple HTML to plain text converter."""
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"br"}:
            self.parts.append("\n")
        if tag in {"p", "div", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"p", "div", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if data:
            self.parts.append(data)

def _html_to_text(html: str) -> str:
    parser = _PlainTextExtractor()
    parser.feed(html)
    text = "".join(parser.parts)
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join([l for l in lines if l])

def _load_smtp_config() -> dict:
    cfg = configparser.ConfigParser()
    if os.path.exists("config.ini"):
        cfg.read("config.ini")
        if cfg.has_section("smtp"):
            return dict(cfg["smtp"])
    return {}

# --- PUBLIC HOOK --------------------------------------------------------------

def init(app):
    """
    Attach export & email handlers onto app.
    Keep all dialogs on main thread. Push heavy work to the app's thread executor.
    """

    # ---------- Copy for Email (threaded render + premailer) ----------
    def on_copy_for_email_clicked():
        app.export_button.configure(state="disabled")
        app.email_button.configure(state="disabled")
        if hasattr(app, "_show_progress"):
            app._show_progress("Preparing email HTML…")

        def _worker():
            settings = app.settings_frame.dump()
            html = app.renderer.render_html(app.sections_data, settings)
            try:
                return transform(html)
            except Exception as e:
                raise RuntimeError(f"Premailer error: {e}") from e

        fut = app._thread_executor.submit(_worker)

        def _done(f):
            try:
                content = f.result()
                app.clipboard_clear()
                app.clipboard_append(content)
                app.show_status_message("Email-ready HTML copied!")
            except Exception as e:
                messagebox.showerror("Copy Error", str(e))
            finally:
                if hasattr(app, "_hide_progress"):
                    app._hide_progress()
                app.export_button.configure(state="normal")
                app.email_button.configure(state="normal")

        fut.add_done_callback(lambda f: app.after(0, _done, f))

    app.on_copy_for_email_clicked = on_copy_for_email_clicked

    # ---------- Export HTML + Plain Text (dialog on main, work in thread) ----------
    def on_export_html_text_clicked():
        path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Documents", "*.html")],
            initialdir="./user_drafts",
            title="Export HTML and Text",
        )
        if not path:
            return

        app.export_button.configure(state="disabled")
        app.email_button.configure(state="disabled")
        if hasattr(app, "_show_progress"):
            app._show_progress("Exporting HTML/Text…")

        def _worker(save_path: str):
            settings = app.settings_frame.dump()
            html = app.renderer.render_html(app.sections_data, settings)
            try:
                html = transform(html)
            except Exception as e:
                raise RuntimeError(f"Premailer error: {e}") from e

            p = Path(save_path)
            p.write_text(html, encoding="utf-8")
            txt_path = p.with_suffix(".txt")
            txt_path.write_text(_html_to_text(html), encoding="utf-8")
            return p.name, txt_path.name

        fut = app._thread_executor.submit(_worker, path)

        def _done(f):
            try:
                html_name, txt_name = f.result()
                app.show_status_message(f"Exported: {html_name} & {txt_name}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))
            finally:
                if hasattr(app, "_hide_progress"):
                    app._hide_progress()
                app.export_button.configure(state="normal")
                app.email_button.configure(state="normal")

        fut.add_done_callback(lambda f: app.after(0, _done, f))

    app.on_export_html_text_clicked = on_export_html_text_clicked

    # ---------- Open current bulletin in default browser ----------
    def open_in_browser():
        settings = app.settings_frame.dump()
        html = app.renderer.render_html(app.sections_data, settings)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        tmp.write(html.encode("utf-8"))
        tmp.close()
        webbrowser.open(tmp.name)

    app.open_in_browser = open_in_browser

    # ---------- Export calendar event as .ics ----------
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
        Path(path).write_text("\n".join(lines), encoding="utf-8")
        app.show_status_message(f"ICS exported: {Path(path).name}")

    app.on_export_ics_clicked = on_export_ics_clicked

    # ---------- Send test email (threaded) ----------
    def on_send_test_email_clicked():
        dlg = EmailDialog(app)
        to_addr = dlg.get_email()
        if not to_addr:
            return

        app.export_button.configure(state="disabled")
        app.email_button.configure(state="disabled")
        app.send_test_button.configure(state="disabled")
        if hasattr(app, "_show_progress"):
            app._show_progress("Sending email…")

        def _worker(addr: str):
            settings = app.settings_frame.dump()
            html = app.renderer.render_html(app.sections_data, settings)
            try:
                html = transform(html)
            except Exception as e:
                raise RuntimeError(f"Premailer error: {e}") from e

            smtp_cfg = _load_smtp_config()
            host = smtp_cfg.get("host", "localhost")
            port = int(smtp_cfg.get("port", 25))
            username = smtp_cfg.get("username", "")
            password = smtp_cfg.get("password", "")
            from_addr = smtp_cfg.get("from_addr", username or "")
            use_tls = str(smtp_cfg.get("use_tls", "true")).lower() == "true"

            msg = EmailMessage()
            msg["Subject"] = f"Preview: {settings.get('bulletin_title', 'Bulletin')}"
            msg["From"] = from_addr
            msg["To"] = addr
            msg.set_content("HTML preview attached.")
            msg.add_alternative(html, subtype="html")

            with smtplib.SMTP(host, port, timeout=15) as s:
                if use_tls:
                    try:
                        s.starttls(timeout=10)
                    except Exception:
                        pass
                if username:
                    s.login(username, password)
                s.send_message(msg)

        fut = app._thread_executor.submit(_worker, to_addr)

        def _done(f):
            try:
                f.result()
                app.show_status_message("Test email sent!")
            except Exception as e:
                messagebox.showerror("Email Error", str(e))
            finally:
                if hasattr(app, "_hide_progress"):
                    app._hide_progress()
                app.export_button.configure(state="normal")
                app.email_button.configure(state="normal")
                app.send_test_button.configure(state="normal")

        fut.add_done_callback(lambda f: app.after(0, _done, f))

    app.on_send_test_email_clicked = on_send_test_email_clicked
