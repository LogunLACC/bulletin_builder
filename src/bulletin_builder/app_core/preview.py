import re
import os
import tempfile
import urllib.request
import concurrent.futures
from typing import Any, Optional
from concurrent.futures import Future

from bulletin_builder.app_core.image_utils import optimize_image

_preview_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


def init(app: Any) -> None:
    """
    Bind preview methods onto the app.
    
    Args:
        app: Application instance to attach preview functions to
    """
    app.update_preview      = lambda: _trigger_preview(app)
    app.toggle_preview_mode = lambda mode: _toggle_preview(app, mode)
    app.open_in_browser     = lambda: _open_in_browser(app)
    app.set_preview_device  = lambda device: _set_preview_device(app, device)
    
    def _toggle_preview(app: Any, mode: str) -> None:
        """
        Switch between preview modes (e.g., Rendered/Code).
        
        Args:
            app: Application instance
            mode: Preview mode to switch to
        """
        if hasattr(app, "preview_mode_var"):
            try:
                app.preview_mode_var.set(mode)
                _trigger_preview(app)
            except Exception:
                pass

    def show_placeholder() -> None:
        """Show placeholder message in preview area."""
        try:
            if hasattr(app, "status_bar"):
                app.status_bar.configure(text="Waiting for content...")
            # If a code preview widget already exists, show a friendly message
            if hasattr(app, "code_preview"):
                app.code_preview.delete("1.0", "end")
                app.code_preview.insert("1.0", "Ready. Build your bulletin to preview here.")
        except Exception:
            pass
    app.show_placeholder = show_placeholder

    # First paint (safe even before ui_setup builds widgets)
    app.after(0, app.show_placeholder)


def _render_preview_logic(app: Any) -> str:
    """
    Render the bulletin HTML for preview.
    
    Args:
        app: Application instance
        
    Returns:
        Rendered HTML string
    """
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

    # Download images locally (fallback to remote on error)
    def download_image(match):
        url = match.group(1)
        # Extract extension from URL path only (before query string)
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        path_only = parsed_url.path
        ext = os.path.splitext(path_only)[1] or '.png'
        # Ensure extension is valid (no query string characters)
        ext = ext.split('?')[0].split('&')[0]
        fd, tmp_path = tempfile.mkstemp(suffix=ext)
        os.close(fd)
        try:
            urllib.request.urlretrieve(url, tmp_path)
            opt_path = optimize_image(tmp_path)
            return f'src="{opt_path}"'
        except Exception:
            return match.group(0)

    rendered = re.sub(r'src=["\'](https?://[^"\']+)["\']', download_image, body)
    return raw_html, rendered


def _trigger_preview(app: Any) -> None:
    """
    Submit a preview render job to the background executor and attach callback.
    
    Args:
        app: Application instance
    """
    try:
        if hasattr(app, '_show_progress'):
            app.after(0, app._show_progress)
        future = _preview_executor.submit(_render_preview_logic, app)
        # keep reference so GC doesn't collect it
        app._preview_future = future
        future.add_done_callback(lambda fut: _apply_preview(app, fut))
    except Exception:
        # Best effort synchronous fallback
        try:
            raw_html, rendered = _render_preview_logic(app)
            fut = concurrent.futures.Future()
            fut.set_result((raw_html, rendered))
            _apply_preview(app, fut)
        except Exception:
            if hasattr(app, '_hide_progress'):
                app.after(0, app._hide_progress)


def _apply_preview(app: Any, future: Future) -> None:
    """
    Apply rendered preview to the UI.
    
    Args:
        app: Application instance
        future: Future containing rendered HTML result
    """
    try:
        raw_html, rendered = future.result()
        mode = app.preview_mode_var.get() if hasattr(app, "preview_mode_var") else "Rendered"

        if mode == "Rendered" and hasattr(app, "rendered_preview"):
            # Show HTMLLabel, hide code preview
            try:
                app.rendered_preview.grid(row=1, column=0, sticky="nsew")
            except Exception:
                pass
            if hasattr(app, 'code_preview'):
                try:
                    app.code_preview.grid_forget()
                except Exception:
                    pass
            # Try rendered -> raw -> fallback to code view
            for html in (rendered, raw_html):
                try:
                    app.rendered_preview.set_html(html)
                    break
                except Exception:
                    continue
            else:
                # If all HTML render attempts fail, switch UI mode to Code
                if hasattr(app, "preview_mode_var"):
                    try:
                        app.preview_mode_var.set("Code")
                    except Exception:
                        pass
                mode = "Code"  # fall through to code view

        if mode != "Rendered" and hasattr(app, "code_preview"):
            try:
                app.code_preview.grid(row=1, column=0, sticky="nsew")
            except Exception:
                pass
            if hasattr(app, 'rendered_preview'):
                try:
                    app.rendered_preview.grid_forget()
                except Exception:
                    pass
            try:
                app.code_preview.delete("1.0", "end")
                app.code_preview.insert("1.0", raw_html)
            except Exception:
                pass

        if hasattr(app, "device_mode"):
            try:
                _set_preview_device(app, app.device_mode)
            except Exception:
                pass

    except Exception as e:
        if hasattr(app, "code_preview"):
            try:
                app.code_preview.grid(row=1, column=0, sticky="nsew")
            except Exception:
                pass
            if hasattr(app, 'rendered_preview'):
                try:
                    app.rendered_preview.grid_forget()
                except Exception:
                    pass
            try:
                app.code_preview.delete("1.0", "end")
                app.code_preview.insert("1.0", f"Preview error:\n{e}")
            except Exception:
                pass

    if hasattr(app, "_hide_progress"):
        try:
            app.after(0, app._hide_progress)
        except Exception:
            pass
    if hasattr(app, 'update_preview_btn'):
        try:
            app.after(0, lambda: app.update_preview_btn.configure(state="normal"))
        except Exception:
            pass

def _open_in_browser(app: Any) -> None:
    """
    Fall-back open-in-browser implementation in case exporter didn't bind it.
    
    Args:
        app: Application instance
    """
    import webbrowser
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    html = app.renderer.render_html(app.sections_data, app.settings_frame.dump())
    tmp.write(html.encode("utf-8"))
    tmp.close()
    webbrowser.open(tmp.name)


def _set_preview_device(app: Any, device: str) -> None:
    """
    Adjust preview width for responsive modes.
    
    Args:
        app: Application instance
        device: Device mode ('Desktop', 'Tablet', or 'Mobile')
    """
    app.device_mode = device
    
    # Get width from email client preview if available, otherwise use device defaults
    if hasattr(app, 'email_client_var') and hasattr(app, 'get_current_client_width'):
        try:
            width = app.get_current_client_width()
        except Exception:
            widths = {"Desktop": 800, "Tablet": 600, "Mobile": 375}
            width = widths.get(device, 800)
    else:
        widths = {"Desktop": 800, "Tablet": 600, "Mobile": 375}
        width = widths.get(device, 800)
    
    if hasattr(app, 'preview_area'):
        app.preview_area.configure(width=width)
