# Batch send and scheduling (stub)
def batch_send_emails(email_list, rate_limit=10):
  print(f"Batch sending {len(email_list)} emails with rate limit {rate_limit}/min (stub).")
  # In production, implement actual sending and error recovery
# Image optimization for email safety
def optimize_email_images(html):
  # Stub: In production, use Pillow or similar to compress/convert images
  print("Images optimized for email (stub).")
  return html
# Best Practices for Email wizard/checklist
def show_email_best_practices():
  checklist = [
    "Use alt text for all images.",
    "Keep subject lines clear and concise.",
    "Avoid large attachments; use links instead.",
    "Test your email in multiple clients.",
    "Use inline CSS, not <style> tags.",
    "Check for spam trigger words.",
    "Include a plain-text version if possible.",
  ]
  print("Email Best Practices:\n" + '\n'.join(f"- {item}" for item in checklist))
# Email analytics: open/click tracking (opt-in)
def add_email_analytics(html, pixel_url=None):
  if pixel_url:
    html += f"<img src='{pixel_url}' width='1' height='1' style='display:none' alt='analytics'/>"
  print("Analytics pixel added.")
  return html
# Export to PDF for compliance and archiving
def export_email_to_pdf(html, output_path):
  # Stub: In production, use a library like WeasyPrint or xhtml2pdf
  with open(output_path, 'w', encoding='utf-8') as f:
    f.write(f"PDF export placeholder for:\n{html}")
  print(f"Exported PDF to {output_path}")
# Live HTML/CSS linting for email-safe code
def lint_email_html_css(html):
  warnings = []
  if '<style>' in html:
    warnings.append("Avoid <style> tags; use inline CSS for email safety.")
  if 'position:' in html:
    warnings.append("'position' CSS may not be supported in email clients.")
  if 'float:' in html:
    warnings.append("'float' CSS may cause layout issues in email clients.")
  if warnings:
    print("HTML/CSS Lint Warnings:\n" + '\n'.join(warnings))
  else:
    print("No major HTML/CSS lint warnings.")
# Accessibility and spam validation for email export
def validate_email_export(html):
  issues = []
  if 'alt=""' in html or 'alt=' not in html:
    issues.append("Missing alt text on images.")
  if 'style="color:' in html and 'contrast' not in html:
    issues.append("Check color contrast for accessibility.")
  if 'FREE' in html.upper():
    issues.append("Potential spam trigger: 'FREE'.")
  if issues:
    print("Accessibility/Spam Issues:\n" + '\n'.join(issues))
  else:
    print("No major accessibility or spam issues detected.")
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

  def on_export_frontsteps_clicked():
    """Copy FrontSteps-safe body-only HTML to clipboard."""
    try:
      ctx = _collect_context()
      # build_frontsteps_html expects a string of HTML, not a context dict.
      # I need to render the bulletin to HTML first.
      # I'll use the existing render_bulletin_html function from the preview module.
      from bulletin_builder.app_core.preview import render_bulletin_html
      html = render_bulletin_html(ctx)
      
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
  app.on_export_frontsteps_clicked = on_export_frontsteps_clicked