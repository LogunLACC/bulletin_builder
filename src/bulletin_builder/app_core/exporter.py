# Note: The following features are now implemented in dedicated modules:
# - Email Best Practices: see best_practices.py for interactive checklist/wizard
# - PDF Export: see pdf_exporter.py for full PDF export functionality  
# - HTML/CSS Linting: see export_validator.py for comprehensive email safety validation
# - Email Analytics: Skipped per user preference (Task 6 in roadmap)
# - Batch Sending: Skipped per user preference (Task 9 in roadmap)
# - Image Optimization: Skipped per user preference (Task 8 in roadmap)

from typing import Any, Dict


def simulate_email_preview(html: str) -> None:
    """
    Simulate rendering in major email clients.
    
    Args:
        html: HTML content to preview
    """
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


def show_email_auth_guidance() -> None:
    """Display DKIM/SPF/DMARC guidance for email deliverability."""
    guidance = (
        "To maximize deliverability, configure your domain with DKIM, SPF, and DMARC records.\n"
        "- DKIM: Add a TXT record for your sending domain with your public key.\n"
        "- SPF: Add a TXT record listing authorized sending servers.\n"
        "- DMARC: Add a policy record to enforce authentication.\n"
        "See your email provider's documentation for details.\n"
    )
    print(guidance)


def init(app: Any) -> None:
    """
    Attach lightweight exporter menu handlers onto the app.
    
    Args:
        app: Application instance to attach exporter functions to
    """
    
    def _collect_context() -> Dict[str, Any]:
        """Collect context from app for rendering."""
        try:
            # Prefer a GUI-aware collect_context on the app if present
            if hasattr(app, 'collect_context') and callable(app.collect_context):
                return app.collect_context()
            # Fallback to renderer + settings
            settings = app.settings_frame.dump() if hasattr(app, 'settings_frame') else {}
            return {'title': settings.get('bulletin_title','Bulletin'), 'date': settings.get('bulletin_date',''), 'sections': getattr(app,'sections_data',[]), 'settings': settings}
        except Exception:
            return {'title': 'Bulletin', 'date': '', 'sections': getattr(app,'sections_data',[]), 'settings': {}}

    def export_frontsteps_html(html_content: str) -> None:
        """
        Given HTML content, sanitize it for FrontSteps and copy to clipboard.
        
        Args:
            html_content: HTML content to export
        """
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

    def on_copy_for_frontsteps_clicked() -> None:
        """Handler for Copy FrontSteps HTML menu item."""
        from bulletin_builder.app_core.logging_config import get_logger
        logger = get_logger(__name__)
        
        try:
            logger.info("FrontSteps export triggered")
            
            # Get the rendered bulletin HTML
            if hasattr(app, 'render_bulletin_html'):
                logger.info("Using app.render_bulletin_html")
                ctx = _collect_context()
                logger.info(f"Context collected: {list(ctx.keys())}")
                html_content = app.render_bulletin_html(ctx)
                logger.info(f"HTML rendered, length: {len(html_content)}")
                export_frontsteps_html(html_content)
            else:
                logger.error("app.render_bulletin_html not found")
                messagebox.showerror(
                    'Export Error',
                    'Bulletin rendering is not available.',
                    parent=app
                )
        except Exception as e:
            logger.error(f"FrontSteps export failed: {e}", exc_info=True)
            messagebox.showerror('Export Error', f'Failed to export: {str(e)}', parent=app)

    app.on_export_html_text_clicked = lambda: None
    app.on_copy_for_email_clicked = lambda: None
    app.on_copy_for_frontsteps_clicked = on_copy_for_frontsteps_clicked
    
    # PDF export handler
    def on_export_pdf_clicked() -> None:
        """Export bulletin to PDF format."""
        from tkinter import filedialog, messagebox
        import os
        from bulletin_builder.exceptions import PDFExportError, MissingDependencyError
        from bulletin_builder.app_core.logging_config import get_logger
        
        logger = get_logger(__name__)
        
        try:
            # Check if PDF exporter is available
            if not hasattr(app, 'export_to_pdf'):
                raise MissingDependencyError(
                    "PDF export requires the 'weasyprint' library. Install with: pip install weasyprint",
                    dependency_name="weasyprint"
                )
            
            # Get the HTML content
            if hasattr(app, 'render_bulletin_html'):
                # Get context
                ctx = {}
                if hasattr(app, 'get_export_context'):
                    ctx = app.get_export_context()
                html_content = app.render_bulletin_html(ctx)
            else:
                raise PDFExportError("Cannot render bulletin HTML - render_bulletin_html method not available")
            
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
            
            # Export to PDF - this now raises exceptions instead of returning success/message
            try:
                success, message = app.export_to_pdf(html_content, output_path)
                # If the old API returned successfully
                messagebox.showinfo("PDF Export Successful", message, parent=app)
                if hasattr(app, 'show_status_message'):
                    app.show_status_message("PDF exported successfully", duration_ms=2000)
            except (PDFExportError, MissingDependencyError):
                # These are expected, re-raise to outer handler
                raise
            
        except MissingDependencyError as e:
            logger.error(f"Missing dependency for PDF export: {e}")
            messagebox.showerror(
                "PDF Export Unavailable",
                str(e),
                parent=app
            )
            
        except PDFExportError as e:
            logger.error(f"PDF export failed: {e}")
            messagebox.showerror("PDF Export Failed", str(e), parent=app)
            if hasattr(app, 'show_status_message'):
                app.show_status_message("PDF export failed", duration_ms=2000)
            
        except Exception as e:
            logger.exception(f"Unexpected error during PDF export: {e}")
            messagebox.showerror('PDF Export Error', f"Unexpected error: {str(e)}", parent=app)
    
    app.on_export_pdf_clicked = on_export_pdf_clicked
    
    # The main handler is now on the app, this is the worker function
    app.export_frontsteps_html = export_frontsteps_html