from bulletin_builder.postprocess import ensure_postprocessed
import re, os, tempfile, urllib.request, concurrent.futures
from pathlib import Path
from tkinter import messagebox

 # Removed circular import of init
from bulletin_builder.app_core.image_utils import optimize_image

_preview_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

def init(app):
    # Bind preview API (widgets come from ui_setup)
    app.update_preview       = lambda: _trigger_preview(app)
    app.toggle_preview_mode  = lambda mode: _toggle_preview(app, mode)
    app.open_in_browser      = lambda: _open_in_browser(app)
    app.set_preview_device   = lambda device: _set_preview_device(app, device)

    def show_placeholder():
        try:
            if hasattr(app, "status_bar"):
                app.status_bar.configure(text="Waiting for content…")
            # If a code preview widget already exists, show a friendly message
            if hasattr(app, "code_preview"):
                app.code_preview.delete("1.0", "end")
                app.code_preview.insert("1.0", "Ready. Build your bulletin to preview here.")
        except Exception:
            pass
    app.show_placeholder = show_placeholder

    # First paint (safe even before ui_setup builds widgets)
    app.after(0, app.show_placeholder)

def _trigger_preview(app):
    if hasattr(app, 'update_preview_btn'):
        app.update_preview_btn.configure(state="disabled")
    if hasattr(app, "_show_progress"):
        app._show_progress("Rendering preview…")

    future = _preview_executor.submit(_render_preview_logic, app)
    future.add_done_callback(lambda fut: _apply_preview(app, fut))

def _render_preview_logic(app):
    settings = app.settings_frame.dump() if hasattr(app, "settings_frame") else {}
    context = dict(settings)
    context["sections"] = app.sections_data
    context["settings"] = settings
    raw_html = app.renderer.render(context)

    body = raw_html
    lower = body.lower()
    idx = lower.find("</style>")
    if idx != -1:
        body = body[idx + len("</style>"):]

    def download_image(match):
        url = match.group(1)
        ext = os.path.splitext(url)[1] or ".png"
        fd, tmp_path = tempfile.mkstemp(suffix=ext)
        os.close(fd)
        try:
            with urllib.request.urlopen(url, timeout=10) as resp, open(tmp_path, "wb") as out:
                out.write(resp.read())
            opt_path = optimize_image(tmp_path)
            return f'src="{opt_path}"'
        except Exception:
            return match.group(0)

    rendered = re.sub(r'src=["\'](https?://[^"\']+)["\']', download_image, body)
    return raw_html, rendered

def _apply_preview(app, fut):
    exc = fut.exception()
    if exc:
        app.after(0, lambda: messagebox.showerror("Preview Error", str(exc)))

    else:
        raw_html, rendered = fut.result()
        mode = app.preview_mode_var.get() if hasattr(app, "preview_mode_var") else "Code"



        if mode == "Rendered" and hasattr(app, "rendered_preview"):
            # Show HTMLLabel, hide code preview
            app.rendered_preview.grid(row=1, column=0, sticky="nsew")
            app.code_preview.grid_forget()
            # Try rendered → raw → fallback to code view
            for html in (rendered, raw_html):
                try:
                    app.rendered_preview.set_html(html)
                    break
                except Exception:
                    continue
            else:
                # If all HTML render attempts fail, switch UI mode to Code
                if hasattr(app, "preview_mode_var"):
                    app.preview_mode_var.set("Code")
                mode = "Code"  # fall through to code view

        if mode != "Rendered" and hasattr(app, "code_preview"):
            app.code_preview.grid(row=1, column=0, sticky="nsew")
            app.rendered_preview.grid_forget()
            app.code_preview.delete("1.0", "end")
            app.code_preview.insert("1.0", raw_html)

        if hasattr(app, "device_mode"):
            _set_preview_device(app, app.device_mode)

    if hasattr(app, "_hide_progress"):
        app.after(0, app._hide_progress)
    if hasattr(app, 'update_preview_btn'):
        app.after(0, lambda: app.update_preview_btn.configure(state="normal"))

def _toggle_preview(app, mode):
    if not all(hasattr(app, x) for x in ("rendered_preview", "code_preview")):
        return
    if mode == "Rendered":
        app.code_preview.pack_forget()
        app.rendered_preview.pack(fill="both", expand=True)
    else:
        app.rendered_preview.pack_forget()
        app.code_preview.pack(fill="both", expand=True)

def _open_in_browser(app):
    import webbrowser
    settings = app.settings_frame.dump() if hasattr(app, "settings_frame") else {}
    context = dict(settings)
    context["sections"] = app.sections_data
    context["settings"] = settings
    raw_html = app.renderer.render(context)

    # Post-process preview HTML for email compatibility
    html = ensure_postprocessed(raw_html)

    body = html
    lower = body.lower()
    idx = lower.find("</style>")
    if idx != -1:
        body = body[idx + len("</style>"):]

    def download_image(match):
        # Minimal stub: just return the original src
        return match.group(0)
    rendered = re.sub(r'src=["\'](https?://[^"\']+)["\']', download_image, body)
    return html, rendered
