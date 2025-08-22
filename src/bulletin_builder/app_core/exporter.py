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

