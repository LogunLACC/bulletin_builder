import re
import os
import tempfile
import urllib.request
import concurrent.futures
from tkinter import messagebox

# Single-thread executor for preview operations
_preview_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

def init(app):
    """Bind preview methods onto the app."""
    app.update_preview      = lambda: _trigger_preview(app)
    app.toggle_preview_mode = lambda mode: _toggle_preview(app, mode)
    app.open_in_browser     = lambda: _open_in_browser(app)

def _trigger_preview(app):
    """Start rendering in background thread when user clicks Update Preview."""
    if hasattr(app, 'update_preview_btn'):
        app.update_preview_btn.configure(state="disabled")
    app._show_progress("Rendering preview…")

    future = _preview_executor.submit(_render_preview_logic, app)
    future.add_done_callback(lambda fut: _apply_preview(app, fut))

def _render_preview_logic(app):
    """Heavy work: render HTML, strip styles, download images."""
    settings = app.settings_frame.dump()
    raw_html = app.renderer.render_html(app.sections_data, settings)

    # Strip out head/style for rendered view
    body = raw_html
    lower = body.lower()
    idx = lower.find('</style>')
    if idx != -1:
        body = body[idx + len('</style>'):]

    # Download images locally (fallback to remote on error)
    def download_image(match):
        url = match.group(1)
        ext = os.path.splitext(url)[1] or '.png'
        fd, tmp_path = tempfile.mkstemp(suffix=ext)
        os.close(fd)
        try:
            urllib.request.urlretrieve(url, tmp_path)
            return f'src="{tmp_path}"'
        except Exception:
            return match.group(0)

    rendered = re.sub(
        r'src=["\'](https?://[^"\']+)["\']',
        download_image,
        body
    )

    return raw_html, rendered

def _apply_preview(app, fut):
    """Callback on main thread to apply rendered or code preview."""
    exc = fut.exception()
    if exc:
        app.after(0, lambda: messagebox.showerror("Preview Error", str(exc)))
    else:
        raw_html, rendered = fut.result()
        mode = app.preview_mode_toggle.get()

        if mode == "Rendered":
            # Try rendered → raw → code view if both fail
            for html in (rendered, raw_html):
                try:
                    app.rendered_preview.set_html(html)
                    break
                except Exception:
                    continue
            else:
                # neither worked: switch to code view
                app.preview_mode_toggle.set("Code")
                app.code_preview.pack(fill='both', expand=True)
                app.rendered_preview.pack_forget()
                app.code_preview.delete('1.0', 'end')
                app.code_preview.insert('1.0', raw_html)

        else:
            # Code view
            app.code_preview.delete('1.0', 'end')
            app.code_preview.insert('1.0', raw_html)

    # hide progress & re-enable button
    app.after(0, app._hide_progress)
    if hasattr(app, 'update_preview_btn'):
        app.after(0, lambda: app.update_preview_btn.configure(state="normal"))

def _toggle_preview(app, mode):
    """Switch between rendered and code views."""
    if mode == "Rendered":
        app.code_preview.pack_forget()
        app.rendered_preview.pack(fill='both', expand=True)
    else:
        app.rendered_preview.pack_forget()
        app.code_preview.pack(fill='both', expand=True)

def _open_in_browser(app):
    """Fall‑back open‑in‑browser implementation in case exporter didn’t bind it."""
    import webbrowser
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    html = app.renderer.render_html(app.sections_data, app.settings_frame.dump())
    tmp.write(html.encode("utf-8"))
    tmp.close()
    webbrowser.open(tmp.name)
