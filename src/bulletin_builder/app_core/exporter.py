from bulletin_builder.exporters.frontsteps_exporter import build_frontsteps_html
import os
import tempfile
import webbrowser
from tkinter import messagebox

def init(app):
  """Attach lightweight exporter menu handlers onto the app."""

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

  def on_copy_for_frontsteps_clicked():
    """Copy FrontSteps-safe body-only HTML to clipboard."""
    try:
      ctx = _collect_context()
      # build_frontsteps_html expects a string of HTML, not a context dict.
      # I need to render the bulletin to HTML first.
      # I'll use the existing render_bulletin_html function for this.
      from bulletin_builder.app_core.preview import render_preview_html
      html = render_preview_html(ctx)
      
      frontsteps_html = build_frontsteps_html(html)

      if hasattr(app, 'clipboard_clear') and hasattr(app, 'clipboard_append'):
        app.clipboard_clear()
        app.clipboard_append(frontsteps_html)
        if hasattr(app, 'show_status_message'):
          app.show_status_message('FrontSteps HTML copied to clipboard')
      else:
        fd, tmp = tempfile.mkstemp(suffix='.html')
        os.close(fd)
        with open(tmp, 'w', encoding='utf-8') as f:
          f.write(frontsteps_html)
        webbrowser.open(tmp)
    except Exception as e:
      try:
        messagebox.showerror('Copy Error', str(e), parent=app)
      except Exception:
        print('Copy FrontSteps Error', e)

  app.on_export_html_text_clicked = lambda: None
  app.on_copy_for_email_clicked = lambda: None
  app.on_copy_for_frontsteps_clicked = on_copy_for_frontsteps_clicked