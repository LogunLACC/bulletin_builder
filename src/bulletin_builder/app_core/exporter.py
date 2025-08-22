# --- Imports ---
import sys
import traceback
from html import escape
import re
from bulletin_builder.postprocess.bulletin_email_postprocess import process_html

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
              {'<hr style="margin:18px 0 24px 0;border:0;border-top:2px solid #bbb;">' if toc else ''}
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
        print(f"[EXPORTER][DEBUG] render_email_html returning HTML length: {len(html)}")
        # Post-process HTML for email compatibility
        try:
            html = process_html(html)
        except Exception as exc:
            print(f"[EXPORTER][ERROR] postprocess failed: {exc}", file=sys.stderr)
        return html
    except Exception as e:
        print("[EXPORTER][ERROR] render_email_html failed:", e, file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return f"<body><pre style='color:red;'>Export error: {escape(str(e))}\n{escape(traceback.format_exc())}\nCTX: {escape(str(ctx))}</pre></body>"
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
  return events_to_blocks(content)

# Helper: render a single event card for the bulletin (web)
def _event_card_bulletin(ev):
  # Minimal, robust HTML card for a single event
  # For web: max-width:800px; for email: max-width:320px (handled below)
  img_html = f'<img src="{escape(ev.get("image_url", ""))}" alt="Event image" style="width:100%;max-width:800px;border-radius:8px 8px 0 0;">' if ev.get("image_url") else ""
  title = escape(ev.get("description", ""))
  date = escape(ev.get("date", ""))
  time = escape(ev.get("time", ""))
  link = ev.get("link", "")
  link_html = f'<a href="{escape(link)}" style="display:inline-block;margin-top:8px;color:#1a202c;text-decoration:underline;">More Info</a>' if link else ""
  return f'''<div style="background:#fff;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.06);margin:0 0 18px 0;overflow:hidden;max-width:340px;">
    {img_html}
    <div style="padding:14px 16px 12px 16px;">
      <div style="font-size:16px;font-weight:600;line-height:1.3;">{title}</div>
      <div style="font-size:14px;color:#555;margin:4px 0 0 0;">{date}{' at ' + time if time else ''}</div>
      {link_html}
    </div>
  </div>'''

# Minimal stub for _render_section_html so the app can launch
def _render_section_html(section):
  stype = section.get("type", "")
  body_html = ""

  if stype == "announcements":
    items = section.get("content", []) or []
    rows = []
    for a in items:
      at = escape(a.get("title", ""))
      body = a.get("body", "")
      link = a.get("link", "") or ""
      link_text = a.get("link_text", "") or ""
      link_html = f'<p style="margin:8px 0 0;"><a href="{escape(link)}" style="color:inherit;">{escape(link_text or link)}</a></p>' if link else ""
      rows.append(
        f"""<article style='padding:12px 0;border-bottom:1px solid rgba(0,0,0,.08);'>
            <h4 style='margin:0 0 6px 0;font-size:18px;line-height:1.25;'>{at}</h4>
            <div style='font-size:14px;line-height:1.5;margin:0;'>{body}</div>
            {link_html}
          </article>"""
      )
    body_html = "".join(rows) if rows else "<p style='opacity:.7;'>No announcements.</p>"

  elif stype in ("community_events", "upcoming_events", "event_list", "events"):
    events = list(_iter_events(section))
    if events:
      cards = "".join(_event_card_bulletin(ev) for ev in events)
    else:
      cards = '<div style="opacity:.7;font-family:Arial,Helvetica,sans-serif;font-size:14px;">No events available.</div>'
    body_html = f'<div class="event-cards">{cards}</div>'

  elif stype == "custom_text":
    text = (section.get("content") or {}).get("text", "")
    body_html = f'<div style="font-size:15px;line-height:1.7;">{text}</div>'

  else:
    body_html = "<p style='opacity:.7;'>No content available.</p>"

  title = escape(section.get("title", ""))
  slug = _slug(section.get("title", "")) or "section"
  # Deduplicate heading if present in body_html
  def strip_duplicate_section_heading(block_html: str, section_title: str) -> str:
    """
    Remove all <h1>-<h6> headings that exactly match the section title (ignoring case/whitespace)
    after the first occurrence, to avoid duplicated headings in the rendered view.
    """
    import re
    pattern = re.compile(rf'<h[1-6][^>]*>\s*{re.escape(section_title)}\s*</h[1-6]>', flags=re.I | re.S)
    matches = list(pattern.finditer(block_html))
    if not matches:
        return block_html
    # Keep the first heading, remove all subsequent
    first = matches[0]
    new_html = block_html[:first.end()] + pattern.sub('', block_html[first.end():])
    return new_html
  clean_body_html = strip_duplicate_section_heading(body_html, title)
  if title:
    return f"""
    <section id='{slug}' style='margin:0 0 32px 0;'>
      <h2 id='{slug}-h2' style='font-size:22px;margin:0 0 12px 0;font-family:inherit;font-weight:600;color:#1a202c;'>{title}</h2>
      {clean_body_html}
    </section>
    """
  else:
    return clean_body_html

# Remove all unreachable/duplicate code after this point
# -*- coding: utf-8 -*-

# ---------- required stub for app import ----------

def collect_context(*args, **kwargs):
  """Collects the current bulletin context from the BulletinBuilderApp instance for export/preview."""
  app = args[0] if args else None
  ctx = {"title": "Bulletin", "date": "", "sections": []}
  if app is not None:
    # --- DEBUG: Print all attributes and their types to help locate section data ---
    try:
      with open("app_attribute_scan.log", "w", encoding="utf-8") as f:
        f.write("[EXPORTER][DEBUG] App attributes (for section search):\n")
        for attr in dir(app):
          if attr.startswith("_"): continue
          try:
            val = getattr(app, attr)
            f.write(f"  {attr}: {type(val)}\n")
          except Exception as e:
            f.write(f"  {attr}: <error: {e}>\n")
    except Exception as log_e:
      pass
    # Try to get title and date from settings UI if present, else fallback
    title = getattr(app, 'bulletin_title', None)
    date = getattr(app, 'bulletin_date', None)
    # Try to get from settings frame if available
    if hasattr(app, 'settings_frame'):
      sf = app.settings_frame
      try:
        title = sf.title_entry.get()
        date = sf.date_entry.get()
      except Exception:
        pass
    # Try to get sections from app.sections_data if present, else fallback
    sections = getattr(app, 'sections_data', None)
    if sections is None:
      sections = getattr(app, 'sections', None)
    if sections is None and hasattr(app, 'get_sections'):
      try:
        sections = app.get_sections()
      except Exception:
        sections = []
    if sections is None:
      # Try to get from app state or fallback
      sections = []
    ctx = {
      "title": title or "Bulletin",
      "date": date or "",
      "sections": sections,
    }
  print(f"[EXPORTER][DEBUG] collect_context returning: {{'title': {ctx['title']}, 'date': {ctx['date']}, 'sections': {len(ctx['sections'])}}}")
  return ctx

  stype = section.get("type")
  title = section.get("title","")
  anchor = _slug(title) or "section"


  stype = section.get("type", "")
  body_html = ""

  if stype == "announcements":
    items = section.get("content", []) or []
    rows = []
    for a in items:
      at = escape(a.get("title", ""))
      body = a.get("body", "")
      link = a.get("link", "") or ""
      link_text = a.get("link_text", "") or ""
      link_html = f'<p style="margin:8px 0 0;"><a href="{escape(link)}" style="color:inherit;">{escape(link_text or link)}</a></p>' if link else ""
      rows.append(
        f"""<article style='padding:12px 0;border-bottom:1px solid rgba(0,0,0,.08);'>
            <h4 style='margin:0 0 6px 0;font-size:18px;line-height:1.25;'>{at}</h4>
            <div style='font-size:14px;line-height:1.5;margin:0;'>{body}</div>
            {link_html}
          </article>"""
      )
    body_html = "".join(rows) if rows else "<p style='opacity:.7;'>No announcements.</p>"

  elif stype in ("community_events", "upcoming_events", "event_list", "events"):
    # Use the new helpers for event normalization and rendering
    events = list(_iter_events(section))
    if events:
      cards = "".join(_event_card_bulletin(ev) for ev in events)
    else:
      cards = '<div style="opacity:.7;font-family:Arial,Helvetica,sans-serif;font-size:14px;">No events available.</div>'
    body_html = f'<div class="event-cards">{cards}</div>'

  elif stype == "custom_text":
    text = (section.get("content") or {}).get("text", "")
    body_html = f'<div style="font-size:15px;line-height:1.7;">{text}</div>'

  else:
    body_html = "<p style='opacity:.7;'>No content available.</p>"

  # Optionally wrap in a section container with a title
  title = escape(section.get("title", ""))
  if title:
    return f"""
    <section style='margin:0 0 32px 0;'>
      <h2 style='font-size:22px;margin:0 0 12px 0;font-family:inherit;font-weight:600;color:#1a202c;'>{title}</h2>
      {body_html}
    </section>
    """
  else:
    return body_html
    sections_html = "".join(_render_section_html(s) for s in ctx["sections"])
    toc = _render_toc(ctx["sections"])
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width">
<title>{{escape(ctx.get('title', ''))}}</title>
<style>{{head_css}}</style>
</head>
<body>
  <div class="sheet">
  <h1>{{escape(ctx.get('title', ''))}}</h1>
  <div class="date">{{escape(ctx.get('date', ''))}}</div>
    <hr>
    {{toc}}
    {{sections_html}}
  </div>
</body>
</html>"""

      # --- NEW: bulletin (web) card ---
def _render_section_email(section):
  stype = section.get("type", "")
  # Remove Announcements header duplication: do not render section title here
  slug = _slug(section.get("title", "")) or "section"
  if stype == "announcements":
    items = section.get("content", []) or []
    parts = []
    for a in items:
      at = escape(a.get("title",""))
      body = a.get("body","")
      link = a.get("link","") or ""
      link_text = a.get("link_text","") or ""
      link_html = ""
      if link:
        safe_text = escape(link_text) if link_text else escape(link)
        link_html = f'<p style="margin:8px 0 0;"><a href="{escape(link)}" style="color:inherit;text-decoration:underline;">{safe_text}</a></p>'
      parts.append(
        f"""<tr><td style="padding:12px 0 12px 0; font-family: Arial, Helvetica, sans-serif; font-size:14px; line-height:1.5; border-bottom:1px solid #e5e7eb;">
            <strong style="font-size:16px;line-height:1.3;display:block;margin:0 0 6px 0;">{at}</strong>
            <div>{body}</div>
            {link_html}
          </td></tr>"""
      )
    if parts:
      return f'<table width="100%" cellpadding="0" cellspacing="0" border="0">{"".join(parts)}</table>'
    else:
      return '<div style="opacity:.7;font-size:14px;">No announcements.</div>'
  elif stype in ("community_events", "upcoming_events", "event_list", "events"):
    events = list(_iter_events(section))
    if events:
      # For email: use max-width:320px for images
      def _event_card_email(ev):
        img_html = f'<img src="{escape(ev.get("image_url", ""))}" alt="Event image" style="width:100%;max-width:320px;border-radius:8px 8px 0 0;">' if ev.get("image_url") else ""
        title = escape(ev.get("description", ""))
        date = escape(ev.get("date", ""))
        time = escape(ev.get("time", ""))
        link = ev.get("link", "")
        link_html = f'<a href="{escape(link)}" style="display:inline-block;margin-top:8px;color:#1a202c;text-decoration:underline;">More Info</a>' if link else ""
        return f'''<div style="background:#fff;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.06);margin:0 0 18px 0;overflow:hidden;max-width:340px;">
    {img_html}
    <div style="padding:14px 16px 12px 16px;">
      <div style="font-size:16px;font-weight:600;line-height:1.3;">{title}</div>
      <div style="font-size:14px;color:#555;margin:4px 0 0 0;">{date}{' at ' + time if time else ''}</div>
      {link_html}
    </div>
  </div>'''
      cards = "".join(_event_card_email(ev) for ev in events)
    else:
      cards = '<div style="opacity:.7;font-size:14px;">No events available.</div>'
    return f'<div class="event-cards">{cards}</div>'
  elif stype == "custom_text":
    text = (section.get("content") or {}).get("text", "")
    return f'<div style="font-size:15px;line-height:1.7;">{text}</div>'
  else:
    return '<div style="opacity:.7;font-size:14px;">No content available.</div>'

