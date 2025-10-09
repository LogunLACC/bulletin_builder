# Note: The following features are now implemented in dedicated modules:
# - Email Best Practices: see best_practices.py for interactive checklist/wizard
# - PDF Export: see pdf_exporter.py for full PDF export functionality  
# - HTML/CSS Linting: see export_validator.py for comprehensive email safety validation
# - Email Analytics: Skipped per user preference (Task 6 in roadmap)
# - Batch Sending: Skipped per user preference (Task 9 in roadmap)
# - Image Optimization: Skipped per user preference (Task 8 in roadmap)

# Simulate rendering in major email clients
def simulate_email_preview(html):
  previews = {
    "Gmail": f"<div style='border:2px solid #d93025;padding:8px'><h3>Gmail Preview</h3>{html}</div>",
    "Outlook": f"<div style='border:2px solid #0078d4;padding:8px'><h3>Outlook Preview</h3>{html}</div>",
    "Apple Mail": f"<div style='border:2px solid #34c759;padding:8px'><h3>Apple Mail Preview</h3>{html}</div>",
    "Mobile": f"<div style='border:2px solid #ff9500;padding:8px;max-width:375px'><h3>Mobile Preview</h3>{html}</div>",
  }
  for client, preview_html in previews.items():
    print(f"\n--- {client} ---\n{preview_html}\n")
from bulletin_builder.exporters.frontsteps_exporter import build_frontsteps_html
import os
import tempfile
import webbrowser

from tkinter import messagebox

# DKIM/SPF/DMARC guidance for email deliverability
def show_email_auth_guidance():
  guidance = (
    "To maximize deliverability, configure your domain with DKIM, SPF, and DMARC records.\n"
    "- DKIM: Add a TXT record for your sending domain with your public key.\n"
    "- SPF: Add a TXT record listing authorized sending servers.\n"
    "- DMARC: Add a policy record to enforce authentication.\n"
    "See your email provider's documentation for details.\n"
  )
  print(guidance)

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

  def export_frontsteps_html(html_content: str):
    """Given HTML content, sanitize it for FrontSteps and copy to clipboard."""
    try:
      frontsteps_html = build_frontsteps_html(html_content)

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
  
  # PDF export handler
  def on_export_pdf_clicked():
    """Export bulletin to PDF format."""
    try:
      from tkinter import filedialog, messagebox
      import os
      
      # Check if PDF exporter is available
      if not hasattr(app, 'export_to_pdf'):
        messagebox.showerror(
          "PDF Export Unavailable",
          "PDF export requires the 'weasyprint' library.\n\n"
          "Install with: pip install weasyprint",
          parent=app
        )
        return
      
      # Get the HTML content
      if hasattr(app, 'render_bulletin_html'):
        # Get context
        ctx = {}
        if hasattr(app, 'get_export_context'):
          ctx = app.get_export_context()
        html_content = app.render_bulletin_html(ctx)
      else:
        messagebox.showerror("Export Error", "Cannot render bulletin HTML", parent=app)
        return
      
      # Ask user where to save
      default_name = "LACC_Bulletin.pdf"
      if hasattr(app, 'current_draft_path') and app.current_draft_path:
        draft_name = os.path.splitext(os.path.basename(app.current_draft_path))[0]
        default_name = f"{draft_name}.pdf"
      
      output_path = filedialog.asksaveasfilename(
        title="Export to PDF",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        initialfile=default_name,
        parent=app
      )
      
      if not output_path:
        return  # User cancelled
      
      # Export to PDF
      success, message = app.export_to_pdf(html_content, output_path)
      
      if success:
        messagebox.showinfo("PDF Export Successful", message, parent=app)
        if hasattr(app, 'show_status_message'):
          app.show_status_message("PDF exported successfully", duration=2000)
      else:
        messagebox.showerror("PDF Export Failed", message, parent=app)
        if hasattr(app, 'show_status_message'):
          app.show_status_message("PDF export failed", duration=2000)
      
    except Exception as e:
      try:
        messagebox.showerror('PDF Export Error', str(e), parent=app)
      except Exception:
        print('PDF Export Error:', e)
  
  app.on_export_pdf_clicked = on_export_pdf_clicked
  
  # The main handler is now on the app, this is the worker function
  app.export_frontsteps_html = export_frontsteps_html