# app_core/exporter.py

import tempfile
import webbrowser
from premailer import transform
from weasyprint import HTML

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
        base = app.templates_dir.as_uri() + "/"
        path = app.file_dialog.asksaveasfilename(
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
    def on_copy_for_email_clicked():
        app.export_button.configure(state="disabled")
        app.email_button.configure(state="disabled")
        app._show_progress("Preparing email HTML…")
        future = app._thread_executor.submit(_do_copy_for_email)
        future.add_done_callback(_on_copy_for_email_done)

    def _do_copy_for_email():
        settings = app.settings_frame.dump()
        html = app.renderer.render_html(app.sections_data, settings)
        return transform(html)

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

    app.on_copy_for_email_clicked = on_copy_for_email_clicked

    # --- Open current bulletin in default browser ---
    def open_in_browser():
        settings = app.settings_frame.dump()
        html = app.renderer.render_html(app.sections_data, settings)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        tmp.write(html.encode("utf-8"))
        tmp.close()
        webbrowser.open(tmp.name)

    app.open_in_browser = open_in_browser
