"""Minimal, safe exporter helpers for headless import and tests.

This file provides conservative rendering helpers used by the app and
by test/export scripts. It intentionally avoids GUI-only imports at
module import time.
"""

from html import escape
import re
import traceback


import os
from bulletin_builder.postprocess import ensure_postprocessed
from bulletin_builder.actions_log import log_action


def _slug(text: str) -> str:
  return re.sub(r'[^a-z0-9]+', '-', str(text).lower()).strip('-') if text else "section"


def _event_card_email(ev: dict) -> str:
  """Render a compact email-friendly event line.

  Falls back from `title` to `description` (and a few common aliases) and
  shows date with optional time. Includes a simple More Info link when present.
  """
  raw_title = (
    ev.get("title")
    or ev.get("description")
    or ev.get("name")
    or ev.get("event")
    or ""
  )
  title = escape(raw_title)
  date_txt = escape(ev.get("date", ""))
  time_txt = (ev.get("time") or "").strip()
  when = date_txt + (f" at {escape(time_txt)}" if time_txt else "")
  link = (ev.get("link") or "").strip()
  more = f' <a href="{escape(link)}" style="color:#1a73e8;text-decoration:underline;">More Info</a>' if link else ""
  if not title and not when:
    title = "Event"
  return (
    '<div style="margin-bottom:8px;">'
    f'<strong>{title}</strong> '
    f'<span style="color:#888;">{when}</span>'
    f'{more}'
    '</div>'
  )


def _event_card_email_rich(ev: dict) -> str:
  img = (ev.get("image_url") or ev.get("image") or "").strip()
  link = (ev.get("link") or ev.get("url") or "").strip()
  title = escape((ev.get("title") or ev.get("description") or ev.get("name") or ev.get("event") or "").strip())
  date_txt = escape((ev.get("date") or "").strip())
  time_txt = (ev.get("time") or "").strip()
  when = date_txt + (f" at {escape(time_txt)}" if time_txt else "")
  img_html = ""
  if img:
    # simple image block (full width)
    img_html = (
      '<tr>'
      '<td style="border:none;padding:0;">'
      f'<a href="{escape(link or img)}" style="margin:0; padding:0; text-decoration:none;">'
      f'<img src="{escape(img)}" alt="{title}" style="width:100%; height:auto; margin:0; padding:0; display:block; border-radius:8px 8px 0 0;" />'
      '</a>'
      '</td>'
      '</tr>'
    )
  btn_html = f'<a href="{escape(link)}" style="display:inline-block; background-color:#103040; color:#fff; padding:6px 12px; border-radius:4px; text-decoration:none;">More Info</a>' if link else ""
  return (
    '<table cellpadding="0" cellspacing="0" width="100%" style="border-collapse:collapse; border:1px solid #ddd; border-radius:8px; margin:0 0 12px 0;">'
    f'{img_html}'
    '<tr><td style="border:none; padding:20px;">'
    f'<strong style="font-size:1.1em; color:#333;">{title}</strong><br>'
    f'<span style="font-size:1em; color:#103040; font-weight:bold;">{when}</span>'
    '</td></tr>'
    f'<tr><td style="border:none; padding:0 20px 20px 20px; text-align:center;">{btn_html}</td></tr>'
    '</table>'
  )


def _render_section_email(section: dict) -> str:
  stype = section.get("type", "")
  title = (section.get("title") or "").strip()
  slug = _slug(title) if title else ""
  header_html = f'<div id="{slug}" style="margin:0; padding:0"><h2>{escape(title)}</h2></div>' if title else ""

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
        f'<div>{escape(body)}</div>'
        f'{link_html}'
        f'</td></tr>'
      )
    content_html = (
      f'<table width="100%" cellpadding="0" cellspacing="0" border="0">{"".join(parts)}</table>'
      if parts else '<div style="opacity:.7;font-size:14px;">No announcements.</div>'
    )
    return header_html + content_html

  elif stype in ("events", "community_events", "lacc_events"):
    events = section.get("content", []) or []
    if events:
      cards = "".join(_event_card_email_rich(ev) for ev in events)
    else:
      cards = '<div style="opacity:.7;font-size:14px;">No events available.</div>'
    return header_html + f'<div class="event-cards">{cards}</div>'

  elif stype == "custom_text":
    text = ""
    content = section.get("content", {})
    if isinstance(content, dict):
      text = content.get("text", "")
    return header_html + f'<div style="font-size:15px;line-height:1.7;">{escape(text)}</div>'

  else:
    return header_html + '<div style="opacity:.7;font-size:14px;">No content available.</div>'


def _render_section_html(section: dict) -> str:
  # Web-focused rendering (simpler than email card layout)
  stype = section.get("type", "")
  if stype == "custom_text":
    content = section.get("content", {})
    text = content.get("text", "") if isinstance(content, dict) else str(content or "")
    return f"<div style=\"font-size:15px;line-height:1.7;\">{escape(text)}</div>"
  if stype == "announcements":
    items = section.get("content", []) or []
    parts = []
    for a in items:
      title = escape(a.get("title", ""))
      body = escape(a.get("body", ""))
      parts.append(f"<div style=\"margin-bottom:12px;\"><strong>{title}</strong><div>{body}</div></div>")
    return "".join(parts) if parts else '<div style="opacity:.7;font-size:14px;">No announcements.</div>'
  if stype == "events":
    events = section.get("content", []) or []
    return "".join(_event_card_email(ev) for ev in events) if events else '<div style="opacity:.7;font-size:14px;">No events available.</div>'
  return '<div style="opacity:.7;font-size:14px;">No content available.</div>'


def render_email_html(ctx: dict) -> str:
  """Render a conservative, email-ready HTML output for a bulletin context."""
  try:
    try:
      log_action("render_email_html", {"title": ctx.get("title"), "sections": len(ctx.get("sections", []))})
    except Exception:
      pass
    title = ctx.get("title", "Bulletin")
    date = ctx.get("date", "")
    sections = ctx.get("sections", [])

    sections_html = ""
    for s in sections:
      try:
        sections_html += _render_section_email(s)
      except Exception as exc:
        sections_html += f"<div style='color:red;'><b>Section error:</b> {escape(str(exc))}</div>"

    toc = ""
    if sections:
      items = []
      for s in sections:
        t = s.get("title", "")
        if t:
          items.append('<li><a href="#' + _slug(t) + '">' + escape(t) + '</a></li>')
      toc = '<ul style="margin:0 0 24px 0;padding:0 0 0 18px;">' + "\n".join(items) + '</ul>' if items else ""

    html = (
      f'<body style="background:#f9f9fb;">'
      f'<center>'
      f'<table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f9f9fb" style="padding:0;margin:0;border-collapse:collapse;border:none;">'
      f'<tr><td align="center">'
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
      f'</td></tr>'
      f'</table>'
      f'</center>'
      f'</body>'
    )
    # Make URLs email-safe (HTTPS + AVIF->JPG where possible)
    try:
      from bulletin_builder.app_core.url_upgrade import upgrade_http_to_https
      html = upgrade_http_to_https(html, convert_avif=True)
    except Exception:
      pass
    return ensure_postprocessed(html)
  except Exception as e:
    tb = traceback.format_exc()
    return ensure_postprocessed(f"<body><pre style='color:red;'>Export error: {escape(str(e))}\n{escape(tb)}</pre></body>")


def render_bulletin_html(ctx: dict) -> str:
  """Render a simple web-friendly HTML for the bulletin."""
  try:
    title = ctx.get("title", "Bulletin")
    sections = ctx.get("sections", [])

    sections_html = ""
    for s in sections:
      try:
        sections_html += _render_section_html(s)
      except Exception as exc:
        sections_html += f"<div style='color:red;'><b>Section error:</b> {escape(str(exc))}</div>"

    toc = ""
    if sections:
      items = []
      for s in sections:
        t = s.get("title", "")
        if t:
          items.append('<li><a href="#' + _slug(t) + '">' + escape(t) + '</a></li>')
      toc = '<ul>' + "\n".join(items) + '</ul>' if items else ""

    html = (
      f"<body><center><div style=\"max-width:800px;\">"
      f"<h1 style=\"font-size:2em;margin:0 0 8px 0;\">{escape(title)}</h1>"
      f"{toc}{sections_html}</div></center></body>"
    )
    return ensure_postprocessed(html)
  except Exception as e:
    tb = traceback.format_exc()
    return f"<body><pre style='color:red;'>Export error: {escape(str(e))}\n{escape(tb)}</pre></body>"


def collect_context(*args, **kwargs) -> dict:
  """Fallback collect_context used in headless contexts/tests.

  Real GUI app will provide a richer implementation.
  """
  return {}


def init(app):
  """Attach lightweight exporter menu handlers onto the app.

  Handlers are conservative and non-destructive: they render HTML using the
  existing renderers and either save to disk, copy to clipboard (if a GUI
  root is available), or write a harmless temporary file. All operations are
  best-effort and wrapped in try/except to remain safe in headless tests.
  """
  import tempfile
  import webbrowser
  from tkinter import filedialog, messagebox, simpledialog

  def _collect_context():
    try:
      # Prefer a GUI-aware collect_context on the app if present
      if hasattr(app, 'collect_context') and callable(app.collect_context):
        return app.collect_context()
      # Fallback to renderer + settings
      settings = app.settings_frame.dump() if hasattr(app, 'settings_frame') else {}
      return {'title': settings.get('bulletin_title','Bulletin'), 'date': settings.get('bulletin_date',''), 'sections': getattr(app,'sections_data',[]), 'settings': settings}
    except Exception:
      return {'title': 'Bulletin', 'date': '', 'sections': getattr(app,'sections_data',[]), 'settings': {}}

  def on_export_html_text_clicked():
    try:
      ctx = _collect_context()
      html = render_bulletin_html(ctx)
      default = f"{ctx.get('title','bulletin').replace(' ','_')}.html"
      path = filedialog.asksaveasfilename(defaultextension='.html', initialfile=default, title='Export Bulletin HTML', parent=app)
      if not path:
        return
      with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
      # Offer a plain-text copy (very small best-effort conversion)
      text_path = path.rsplit('.',1)[0] + '.txt'
      text = re.sub(r'<[^>]+>', '', html)
      with open(text_path, 'w', encoding='utf-8') as f:
        f.write(text)
      if hasattr(app, 'show_status_message'):
        app.show_status_message(f'Exported HTML: {path}')
      else:
        messagebox.showinfo('Export', f'Exported HTML: {path}', parent=app)
    except Exception as e:
      try:
        messagebox.showerror('Export Error', str(e), parent=app)
      except Exception:
        print('Export Error', e)

  def on_copy_for_email_clicked():
    try:
      ctx = _collect_context()
      html = render_email_html(ctx)
      # Copy to clipboard if app root has clipboard methods, else write to temp file and open
      if hasattr(app, 'clipboard_clear') and hasattr(app, 'clipboard_append'):
        app.clipboard_clear()
        app.clipboard_append(html)
        if hasattr(app, 'show_status_message'):
          app.show_status_message('Email HTML copied to clipboard')
        else:
          messagebox.showinfo('Copied', 'Email-ready HTML copied to clipboard', parent=app)
      else:
        fd, tmp = tempfile.mkstemp(suffix='.html')
        os.close(fd)
        with open(tmp, 'w', encoding='utf-8') as f:
          f.write(html)
        webbrowser.open(tmp)
    except Exception as e:
      try:
        messagebox.showerror('Copy Error', str(e), parent=app)
      except Exception:
        print('Copy Error', e)

  def on_copy_for_frontsteps_clicked():
    """Copy full template-rendered HTML (with head/style) for FrontSteps.

    Uses the main template renderer to produce visually identical output to
    the in-app preview. Leaves head/style intact for better paste fidelity
    into web editors like FrontSteps. Upgrades URLs and converts AVIF to JPG
    where possible to avoid mixed-content or unsupported formats.
    """
    try:
      # Render via template engine
      try:
        from bulletin_builder.bulletin_renderer import BulletinRenderer
        settings = getattr(app, 'settings_frame', None)
        settings_dict = settings.dump() if settings and hasattr(settings, 'dump') else {}
        br = BulletinRenderer()
        html = br.render_html(sections_data=getattr(app, 'sections_data', []), settings=settings_dict)
      except Exception as e:
        html = f"<html><body><p>Render error: {e}</p></body></html>"

      # Make URLs safer for email/web paste
      try:
        from bulletin_builder.app_core.url_upgrade import upgrade_http_to_https
        html = upgrade_http_to_https(html, convert_avif=True)
      except Exception:
        pass

      # Prefer clipboard; fallback to writing a temp file and opening it
      if hasattr(app, 'clipboard_clear') and hasattr(app, 'clipboard_append'):
        app.clipboard_clear()
        app.clipboard_append(html)
        if hasattr(app, 'show_status_message'):
          app.show_status_message('FrontSteps HTML copied to clipboard')
      else:
        fd, tmp = tempfile.mkstemp(suffix='.html')
        os.close(fd)
        with open(tmp, 'w', encoding='utf-8') as f:
          f.write(html)
        webbrowser.open(tmp)
    except Exception as e:
      try:
        messagebox.showerror('Copy Error', str(e), parent=app)
      except Exception:
        print('Copy FrontSteps Error', e)

  def on_export_ics_clicked():
    try:
      # Basic ICS exporter: include event titles as SUMMARY only when events present
      sections = getattr(app, 'sections_data', []) or []
      events = []
      for s in sections:
        if s.get('type') in ('community_events', 'events'):
          events.extend(s.get('content') or [])
      if not events:
        messagebox.showinfo('Export ICS', 'No events found to export.')
        return
      ics_lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//LACC//BulletinBuilder//EN']
      for ev in events:
        title = ev.get('title', ev.get('description','Event'))
        ics_lines += ['BEGIN:VEVENT', f'SUMMARY:{title}', 'END:VEVENT']
      ics_lines.append('END:VCALENDAR')
      default = 'events.ics'
      path = filedialog.asksaveasfilename(defaultextension='.ics', initialfile=default, title='Export Events (.ics)', parent=app)
      if not path:
        return
      with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(ics_lines))
      if hasattr(app, 'show_status_message'):
        app.show_status_message(f'Exported events: {path}')
      else:
        messagebox.showinfo('Export', f'Exported events: {path}', parent=app)
    except Exception as e:
      try:
        messagebox.showerror('Export Error', str(e), parent=app)
      except Exception:
        print('ICS Export Error', e)

  def on_send_test_email_clicked():
    try:
      recipient = simpledialog.askstring('Send Test Email', 'Enter test recipient email address:', parent=app)
      if not recipient:
        return
      ctx = _collect_context()
      html = render_email_html(ctx)
      # For safety, write to a temporary file and open in browser
      fd, tmp = tempfile.mkstemp(suffix='.html')
      os.close(fd)
      with open(tmp, 'w', encoding='utf-8') as f:
        f.write(html)
      webbrowser.open(tmp)
      if hasattr(app, 'show_status_message'):
        app.show_status_message(f'Test email prepared for {recipient} (opened in browser)')
    except Exception as e:
      try:
        messagebox.showerror('Send Error', str(e), parent=app)
      except Exception:
        print('Send Error', e)

  # Attach to app
  app.on_export_html_text_clicked = on_export_html_text_clicked
  app.on_copy_for_email_clicked = on_copy_for_email_clicked
  app.on_copy_for_frontsteps_clicked = on_copy_for_frontsteps_clicked
  app.on_export_ics_clicked = on_export_ics_clicked
  app.on_send_test_email_clicked = on_send_test_email_clicked
  
  # Optional explicit exports used by UI export submenu
  def export_bulletin_html():
    try:
      ctx = _collect_context()
      html = render_bulletin_html(ctx)
      default = f"{ctx.get('title','Bulletin').replace(' ','_')}.html"
      path = filedialog.asksaveasfilename(defaultextension='.html', initialfile=default, title='Export Bulletin HTML', parent=app)
      if not path:
        return
      with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
      if hasattr(app, 'show_status_message'):
        app.show_status_message(f"Exported Bulletin HTML: {path}")
    except Exception as e:
      try:
        messagebox.showerror('Export Error', str(e), parent=app)
      except Exception:
        print('Export Error', e)

  def export_email_html():
    try:
      ctx = _collect_context()
      html = render_email_html(ctx)
      default = f"{ctx.get('title','Bulletin').replace(' ','_')}_email.html"
      path = filedialog.asksaveasfilename(defaultextension='.html', initialfile=default, title='Export Email HTML', parent=app)
      if not path:
        return
      with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
      if hasattr(app, 'show_status_message'):
        app.show_status_message(f"Exported Email HTML: {path}")
    except Exception as e:
      try:
        messagebox.showerror('Export Error', str(e), parent=app)
      except Exception:
        print('Export Error', e)

  app.export_bulletin_html = export_bulletin_html
  app.export_email_html = export_email_html
  return None
