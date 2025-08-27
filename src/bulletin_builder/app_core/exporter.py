<<<<<<< HEAD
# --- Stub for collect_context to support GUI import ---
def collect_context(*args, **kwargs):
    """Stub: Returns an empty context dict. Replace with real logic if needed."""
    return {}
# Add a stub for _render_section_html to resolve undefined function errors
def _render_section_html(section):
  stype = section.get("type", "")
  if stype == "custom_text":
    # In web view, custom_text is in section['content']['text']
    text = ""
    content = section.get("content", {})
    if isinstance(content, dict):
      text = content.get("text", "")
    return f'<div style="font-size:15px;line-height:1.7;">{escape(text)}</div>'
  elif stype == "announcements":
    # Render announcement titles only for web stub
    items = section.get("content", []) or []
    return "<ul>" + "".join(f'<li>{escape(a.get("title", ""))}</li>' for a in items) + "</ul>"
  else:
    return f'<div>{escape(section.get("title", ""))}</div>'
# --- Imports ---
from bulletin_builder.postprocess import ensure_postprocessed
import sys
import traceback
from html import escape
import re
=======
# app_core/exporter.py

import tempfile
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox
from uuid import uuid4
from datetime import datetime
>>>>>>> origin/harden/email-sanitize-and-ci

# --- Helper: slugify a string for anchor links ---
def _slug(text):
    return re.sub(r'[^a-z0-9]+', '-', str(text).lower()).strip('-') if text else "section"

# --- Main: Render the full HTML for the bulletin (email view) ---
def render_email_html(ctx):
  try:
    print("[EXPORTER][DEBUG] render_email_html called with ctx:", ctx)
    title = ctx.get("title", "Bulletin")
    date = ctx.get("date", "")
    sections = ctx.get("sections", [])
    print(f"[EXPORTER][DEBUG] title={title}, date={date}, #sections={len(sections)}")
    sections_html = ""
    for idx, s in enumerate(sections):
      print(f"[EXPORTER][DEBUG] Rendering section {idx}: {s.get('title', '')} (type={s.get('type', '')})")
      try:
        rendered = _render_section_email(s)
        print(f"[EXPORTER][DEBUG] Section {idx} rendered length: {len(rendered)}")
        sections_html += rendered
      except Exception as sec_e:
        print(f"[EXPORTER][ERROR] Section {idx} failed: {sec_e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sections_html += f"<div style='color:red;'><b>Section error:</b> {escape(str(sec_e))}<br><pre>{escape(traceback.format_exc())}</pre></div>"
    toc = ctx.get("toc")
    if toc is None and sections:
      def _render_toc(sections):
        items = []
        for s in sections:
          t = s.get("title", "")
          if t:
            anchor = _slug(t)
            items.append(f'<li><a href="#' + anchor + '">' + escape(t) + '</a></li>')
        if items:
          return '<ul style="margin:0 0 24px 0;padding:0 0 0 18px;">' + "\n".join(items) + '</ul>'
        return ""
      toc = _render_toc(sections)
    print(f"[EXPORTER][DEBUG] toc generated: {bool(toc)}")
    html = (
      f'<body style="background:#f9f9fb;">'
      f'<center>'
      f'<table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f9f9fb" style="padding:0;margin:0;border-collapse:collapse;border:none;">'
      f'<tr>'
      f'<td align="center">'
      f'<table width="600" cellpadding="0" cellspacing="0" border="0" style="background:#fff;margin:32px 0 48px 0;padding:0 24px 24px 24px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.04);font-family:Arial,Helvetica,sans-serif;border-collapse:collapse;border:none;">'
      f'<tr><td style="padding:32px 0 0 0;text-align:center;">'
      f'<h1 style="font-size:2em;margin:0 0 8px 0;">{escape(title)}</h1>'
      f'<div style="color:#555;font-size:1.1em;margin-bottom:12px;">{escape(date)}</div>'
      f'<hr style="margin:18px 0 24px 0;border:0;border-top:1px solid #e5e7eb;">'
      f'{toc}'
      f'</td></tr>'
      f'<tr><td>'
      f'{sections_html}'
      f'</td></tr>'
      f'</table>'
      f'</td>'
      f'</tr>'
      f'</table>'
      f'</center>'
      f'</body>'
    )
    print(f"[EXPORTER][DEBUG] render_email_html returning HTML length: {len(html)}")
    # Post-process HTML for email compatibility
    html = ensure_postprocessed(html)
    return html
  except Exception as e:
    print("[EXPORTER][ERROR] render_email_html failed:", e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    html = f"<body><pre style='color:red;'>Export error: {escape(str(e))}\n{escape(traceback.format_exc())}\nCTX: {escape(str(ctx))}</pre></body>"
    html = ensure_postprocessed(html)
    return html
# Minimal init required for app import
def init(app):
  """Exporter module initialization (stub)."""
  pass
# --- Add stubs to resolve ImportError ---
def render_bulletin_html(ctx):
  """Render the full HTML for the bulletin (web view) using section renderers and helpers. Adds debug logging for errors."""
  import traceback
  import sys
  try:
    print("[EXPORTER][DEBUG] render_bulletin_html called with ctx:", ctx)
    title = ctx.get("title", "Bulletin")
    date = ctx.get("date", "")
    sections = ctx.get("sections", [])
    head_css = ctx.get("head_css", "")
    print(f"[EXPORTER][DEBUG] title={title}, date={date}, #sections={len(sections)}")
    sections_html = ""
    for idx, s in enumerate(sections):
      print(f"[EXPORTER][DEBUG] Rendering section {idx}: {s.get('title', '')} (type={s.get('type', '')})")
      try:
        rendered = _render_section_html(s)
        print(f"[EXPORTER][DEBUG] Section {idx} rendered length: {len(rendered)}")
        sections_html += rendered
      except Exception as sec_e:
        print(f"[EXPORTER][ERROR] Section {idx} failed: {sec_e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sections_html += f"<div style='color:red;'><b>Section error:</b> {escape(str(sec_e))}<br><pre>{escape(traceback.format_exc())}</pre></div>"
    toc = ctx.get("toc")
    if toc is None and sections:
      def _render_toc(sections):
        items = []
        for s in sections:
          t = s.get("title", "")
          if t:
            anchor = _slug(t)
            items.append(f'<li><a href="#' + anchor + '">' + escape(t) + '</a></li>')
        if items:
          return '<ul style="margin:0 0 24px 0;padding:0 0 0 18px;">' + "\n".join(items) + '</ul>'
        return ""
      toc = _render_toc(sections)
    print(f"[EXPORTER][DEBUG] toc generated: {bool(toc)}")
    html = f'''<body style="background:#f9f9fb;">
  <center>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f9f9fb" style="padding:0;margin:0;border-collapse:collapse;border:none;">
      <tr>
        <td align="center">
          <table width="600" cellpadding="0" cellspacing="0" border="0" style="background:#fff;margin:32px 0 48px 0;padding:0 24px 24px 24px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.04);font-family:Arial,Helvetica,sans-serif;border-collapse:collapse;border:none;">
            <tr><td style="padding:32px 0 0 0;text-align:center;">
              <h1 style="font-size:2em;margin:0 0 8px 0;">{escape(title)}</h1>
              <div style="color:#555;font-size:1.1em;margin-bottom:12px;">{escape(date)}</div>
              <hr style="margin:18px 0 24px 0;border:0;border-top:1px solid #e5e7eb;">
              {toc}
            </td></tr>
            <tr><td>
              {sections_html}
            </td></tr>
          </table>
        </td>
      </tr>
    </table>
  </center>
</body>'''
    print(f"[EXPORTER][DEBUG] render_bulletin_html returning HTML length: {len(html)}")
    html = ensure_postprocessed(html)
    return html
  except Exception as e:
    print("[EXPORTER][ERROR] render_bulletin_html failed:", e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    return f"<body><pre style='color:red;'>Export error: {escape(str(e))}\n{escape(traceback.format_exc())}\nCTX: {escape(str(ctx))}</pre></body>"
# Import escape for HTML escaping

from html import escape
from bulletin_builder.event_feed import events_to_blocks

# Helper: slugify a string for anchor links
import re
def _slug(text):
  return re.sub(r'[^a-z0-9]+', '-', str(text).lower()).strip('-') if text else "section"

# Helper: normalize and iterate events from a section
def _iter_events(section):
  content = section.get("content")
  if not content:
    return []
  return content

      # --- NEW: bulletin (web) card ---
def _render_section_email(section):
  stype = section.get("type", "")
  slug = _slug(section.get("title", "")) or "section"
  if stype == "announcements":
    items = section.get("content", []) or []
    parts = []
    for a in items:
      at = escape(a.get("title", ""))
      body = a.get("body", "")
      link = a.get("link", "") or ""
      link_text = a.get("link_text", "") or ""
      link_html = ""
      if link:
        safe_text = escape(link_text) if link_text else escape(link)
        link_html = f'<p style="margin:8px 0 0;"><a href="{escape(link)}" style="color:inherit;text-decoration:underline;">{safe_text}</a></p>'
      parts.append(
        f'<tr><td style="padding:12px 0 12px 0; font-family: Arial, Helvetica, sans-serif; font-size:14px; line-height:1.5; border-bottom:1px solid #e5e7eb;">'
        f'<strong style="font-size:16px;line-height:1.3;display:block;margin:0 0 6px 0;">{at}</strong>'
        f'<div>{body}</div>'
        f'{link_html}'
        f'</td></tr>'
      )
    if parts:
      return f'<table width="100%" cellpadding="0" cellspacing="0" border="0">{"".join(parts)}</table>'
    else:
      return '<div style="opacity:.7;font-size:14px;">No announcements.</div>'
  elif stype == "events":
    events = section.get("content", []) or []
    if events:
      cards = "".join(_event_card_email(ev) for ev in events)
    else:
      cards = '<div style="opacity:.7;font-size:14px;">No events available.</div>'
    return f'<div class="event-cards">{cards}</div>'
  elif stype == "custom_text":
    # In email view, custom_text is in section['content']['text']
    text = ""
    content = section.get("content", {})
    if isinstance(content, dict):
      text = content.get("text", "")
    return f'<div style="font-size:15px;line-height:1.7;">{escape(text)}</div>'
  else:
    return '<div style="opacity:.7;font-size:14px;">No content available.</div>'

# Add missing stub for _event_card_email
def _event_card_email(ev):
  # Minimal stub for event card rendering
  title = escape(ev.get("title", ""))
  date = escape(ev.get("date", ""))
  return f'<div style="margin-bottom:8px;"><strong>{title}</strong> <span style="color:#888;">{date}</span></div>'

<<<<<<< HEAD
=======
    def handle_data(self, data):
        if data:
            self.parts.append(data)


def _html_to_text(html: str) -> str:
    parser = _PlainTextExtractor()
    parser.feed(html)
    text = "".join(parser.parts)
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join([l for l in lines if l])

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

    def on_copy_for_email_clicked():
        app.export_button.configure(state="disabled")
        app.email_button.configure(state="disabled")
        app._show_progress("Preparing email HTML…")
        future = app._thread_executor.submit(_do_copy_for_email)
        future.add_done_callback(_on_copy_for_email_done)

    def _do_copy_for_email():
        settings = app.settings_frame.dump()
        html = app.renderer.render_html(app.sections_data, settings)
        # Apply premailer transforms (inlining) before URL upgrades
        html = transform(html)
        # Upgrade HTTP URLs to HTTPS and convert AVIF->JPG for email
        from .url_upgrade import upgrade_http_to_https
        html = upgrade_http_to_https(html, convert_avif=True)
        # Apply LACC email sanitization rules for email output
        from .sanitize import sanitize_email_html
        html = sanitize_email_html(html)
        return html

    app.on_copy_for_email_clicked = on_copy_for_email_clicked

    # --- Export HTML + plain text (threaded) ---
    def on_export_html_text_clicked():
        app.export_button.configure(state="disabled")
        app.email_button.configure(state="disabled")
        app._show_progress("Exporting HTML/Text…")
        future = app._thread_executor.submit(_do_export_html_text)
        future.add_done_callback(_on_export_html_text_done)

    def _do_export_html_text():
        settings = app.settings_frame.dump()
        html = app.renderer.render_html(app.sections_data, settings)
        # Note: Premailer transform is NOT applied here - this is for web/HTML output, not email
        # Upgrade HTTP URLs to HTTPS to prevent mixed content
        from .url_upgrade import upgrade_http_to_https
        # For web export we do not convert AVIF to JPG — preserve original formats
        html = upgrade_http_to_https(html, convert_avif=False)
        # Note: Sanitizer is NOT applied here - this is for web/HTML output, not email
        path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Documents", "*.html")],
            initialdir="./user_drafts",
            title="Export HTML and Text",
        )
        if not path:
            return None
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        txt_path = Path(path).with_suffix(".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(_html_to_text(html))
        return Path(path).name, txt_path.name

    def _on_export_html_text_done(fut):
        try:
            result = fut.result()
            if result:
                html_name, txt_name = result
                app.after(0, lambda: app.show_status_message(
                    f"Exported: {html_name} & {txt_name}"
                ))
        finally:
            app.after(0, app._hide_progress)
            app.after(0, lambda: app.export_button.configure(state="normal"))
            app.after(0, lambda: app.email_button.configure(state="normal"))

    app.on_export_html_text_clicked = on_export_html_text_clicked

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

    # --- Send test email (threaded) ---
    def on_send_test_email_clicked():
        dlg = EmailDialog(app)
        to_addr = dlg.get_email()
        if not to_addr:
            return
        app.export_button.configure(state="disabled")
        app.email_button.configure(state="disabled")
        app.send_test_button.configure(state="disabled")
        app._show_progress("Sending email…")
        future = app._thread_executor.submit(_do_send_email, to_addr)
        future.add_done_callback(_on_send_email_done)

    def _load_smtp_config():
        cfg = configparser.ConfigParser()
        if os.path.exists("config.ini"):
            cfg.read("config.ini")
            return cfg.get("smtp", {})
        return {}

    def _do_send_email(to_addr: str):
        settings = app.settings_frame.dump()
        html = app.renderer.render_html(app.sections_data, settings)
        html = transform(html)
        # Upgrade HTTP URLs to HTTPS to prevent mixed content
        from .url_upgrade import upgrade_http_to_https
        html = upgrade_http_to_https(html)
        # Convert AVIF images to JPG for email compatibility
        from .url_upgrade import avif_to_jpg_email_only
        html = avif_to_jpg_email_only(html)
        # Apply LACC email sanitization rules for email output
        from .sanitize import sanitize_email_html
        html = sanitize_email_html(html)

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
        msg["To"] = to_addr
        msg.set_content("HTML preview attached.")
        msg.add_alternative(html, subtype="html")

        with smtplib.SMTP(host, port) as s:
            if use_tls:
                try:
                    s.starttls()
                except Exception:
                    pass
            if username:
                s.login(username, password)
            s.send_message(msg)

    def _on_send_email_done(fut):
        try:
            fut.result()
            app.after(0, lambda: app.show_status_message("Test email sent!"))
        except Exception as e:
            # app.after(0, lambda: messagebox.showerror("Email Error", str(e)))
            pass
        finally:
            app.after(0, app._hide_progress)
            app.after(0, lambda: app.export_button.configure(state="normal"))
            app.after(0, lambda: app.email_button.configure(state="normal"))
            app.after(0, lambda: app.send_test_button.configure(state="normal"))

    app.on_send_test_email_clicked = on_send_test_email_clicked
>>>>>>> origin/harden/email-sanitize-and-ci
