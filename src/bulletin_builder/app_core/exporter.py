"""Minimal, safe exporter helpers for headless import and tests.

This file provides conservative rendering helpers used by the app and
by test/export scripts. It intentionally avoids GUI-only imports at
module import time.
"""

from html import escape
import re
import traceback

from pathlib import Path

from bulletin_builder.postprocess import ensure_postprocessed


def _slug(text: str) -> str:
  return re.sub(r'[^a-z0-9]+', '-', str(text).lower()).strip('-') if text else "section"


def _event_card_email(ev: dict) -> str:
  title = escape(ev.get("title", ""))
  date = escape(ev.get("date", ""))
  return f'<div style="margin-bottom:8px;"><strong>{title}</strong> <span style="color:#888;">{date}</span></div>'


def _render_section_email(section: dict) -> str:
  stype = section.get("type", "")
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
    text = ""
    content = section.get("content", {})
    if isinstance(content, dict):
      text = content.get("text", "")
    return f'<div style="font-size:15px;line-height:1.7;">{escape(text)}</div>'
  else:
    return '<div style="opacity:.7;font-size:14px;">No content available.</div>'


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
          items.append(f'<li><a href="#' + _slug(t) + '">' + escape(t) + '</a></li>')
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
          items.append(f'<li><a href="#' + _slug(t) + '">' + escape(t) + '</a></li>')
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
  """No-op init for compatibility when imported in headless contexts."""
  return None
