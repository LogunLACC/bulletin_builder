from bulletin_builder.postprocess import process_html
import os
import customtkinter as ctk
from bulletin_builder.app_core.loader import init_app
from bulletin_builder.app_core.config import (
    save_api_key,
    save_openai_key,
    save_events_feed_url,
    load_window_state,
    save_window_state,
)
from tkinter import filedialog, messagebox
from bulletin_builder.app_core.exporter import collect_context, render_bulletin_html, render_email_html

# Force PyInstaller to include these dynamically-imported modules
import bulletin_builder.app_core.importer  # noqa: F401
import bulletin_builder.app_core.suggestions  # noqa: F401

import argparse
from bulletin_builder.wysiwyg_editor import launch_gui


class BulletinBuilderApp(ctk.CTk):
    """
    Main application window for the LACC Bulletin Builder.
    Relies on app_core modules for UI setup, draft I/O, exporter, and preview.
    """
    def __init__(self):
        super().__init__()
        # Window title and initial fullscreen/maximized
        try:
            self.title("LACC Bulletin Builder")
        except Exception:
            pass
        # Restore last window placement/state; default to maximized
        self._desired_start_state = 'zoomed'
        try:
            geo, st = load_window_state()
            if geo:
                self.geometry(geo)
            if st:
                self._desired_start_state = st
            # Apply desired state now, but also re-assert after UI builds
            self.state(self._desired_start_state)
        except Exception:
            try:
                self.state('zoomed')
            except Exception:
                pass
        # Expose config savers for SettingsFrame
        self.save_api_key_to_config = save_api_key
        self.save_openai_key_to_config = save_openai_key
        self.save_events_url_to_config = save_events_feed_url

        # Wire up all subsystems (core_init, handlers, drafts, sections, exporter, preview, UI)
        from bulletin_builder.app_core.core_init import init as core_init
        core_init(self)
        init_app(self)

        # Persist window state on close
        try:
            def _on_close():
                try:
                    # If maximized, still save geometry from normal state
                    st = self.state()
                    if st == 'zoomed':
                        # Temporarily de-maximize to read geometry, then restore
                        self.state('normal')
                        geo = self.geometry()
                        save_window_state(geo, st)
                        self.state('zoomed')
                    else:
                        save_window_state(self.geometry(), st)
                except Exception:
                    pass
                self.destroy()
            self.protocol("WM_DELETE_WINDOW", _on_close)
        except Exception:
            pass

        # Try the menu builder that init_app should have attached; otherwise fall back
        if hasattr(self, "_build_menus"):
            self._build_menus()
        else:
            print("[warn] _build_menus not attached by init_app; building minimal menus locally.")
            self._build_menus = self._build_menus_fallback  # expose for consistency
            self._build_menus()

        # Some widget creation paths can reset the window out of maximized.
        # Re-assert desired state once idle to keep fullscreen/maximized.
        try:
            self.after(200, lambda: self.state(self._desired_start_state))
        except Exception:
            pass

    def _build_menus_fallback(self):
        """
        Minimal, safe menu bar that wires only the known handlers if present.
        Won't reference PDF. Runs entirely in main thread.
        """
        import tkinter as tk  # local import to keep this file clean
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)

        # Helper: add a menu item only if the handler exists
        def add(label, attr):
            if hasattr(self, attr):
                file_menu.add_command(label=label, command=getattr(self, attr))

        add("Export HTML & Text...", "on_export_html_text_clicked")
        add("Copy Email-Ready HTML", "on_copy_for_email_clicked")
        add("Copy FrontSteps HTML", "on_copy_for_frontsteps_clicked")
        add("Open in Browser", "open_in_browser")
        file_menu.add_separator()
        add("Import Announcements CSV...", "import_announcements_csv")
        file_menu.add_separator()
        add("Export Calendar (.ics)...", "on_export_ics_clicked")
        add("Send Test Email...", "on_send_test_email_clicked")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)

        # --- Export submenu ---
        export_menu = tk.Menu(file_menu, tearoff=0)
        export_menu.add_command(label="Bulletin HTML...", command=self.export_bulletin_html)
        export_menu.add_command(label="Email HTML...", command=self.export_email_html)
        file_menu.add_cascade(label="Export", menu=export_menu)

        menubar.add_cascade(label="File", menu=file_menu)
        self.configure(menu=menubar)

    def refresh_listbox_titles(self):
        """Fallback implementation replaced during init_app."""
        pass

def export_bulletin_html(self):
    try:
        ctx = collect_context(self)
        html = render_bulletin_html(ctx)
        default = f'{ctx["title"].replace(" ","_")}_{ctx["date"].replace(",","").replace(" ","_")}.html'
        path = filedialog.asksaveasfilename(
            defaultextension=".html",
            initialfile=default,
            filetypes=[("HTML", "*.html")],
            title="Export Bulletin HTML",
            parent=self,
        )
        if not path: return
        html = process_html(html)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        if hasattr(self, "show_status_message"):
            self.show_status_message(f"Exported Bulletin HTML: {path}")
        else:
            messagebox.showinfo("Export", f"Saved: {path}", parent=self)
    except Exception as e:
        messagebox.showerror("Export Error", str(e), parent=self)

def export_email_html(self):
    from bulletin_builder.postprocess import process_html
    try:
        ctx = collect_context(self)
        html = render_email_html(ctx)
        html = process_html(html)
        default = f'{ctx["title"].replace(" ","_")}_{ctx["date"].replace(",","").replace(" ","_")}_email.html'
        path = filedialog.asksaveasfilename(
            defaultextension=".html",
            initialfile=default,
            filetypes=[("HTML", "*.html")],
            title="Export Email HTML",
            parent=self,
        )
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        if hasattr(self, "show_status_message"):
            self.show_status_message(f"Exported Email HTML  {path}")
        else:
            messagebox.showinfo("Export", f"Saved: {path}", parent=self)
    except Exception as e:
        messagebox.showerror("Export Error", str(e), parent=self)


def main():
    parser = argparse.ArgumentParser(description="Bulletin Builder Launcher")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode (no GUI)")
    args = parser.parse_args()
    # Default to launching GUI once; prevents duplicate creation when called via different entrypoints
    launch_gui()
    return

    if args.cli:
        print("ðŸ“° Bulletin Builder CLI is running!")
        launch_gui()
    else:
        print("ðŸ“° CLI mode coming soon! Use '--gui' to launch the editor.")


if __name__ == '__main__':
    # Ensure required directories exist
    for d in [
        'templates/partials',
        'templates/themes',
        'user_drafts',
        'assets'
    ]:
        os.makedirs(d, exist_ok=True)

    # Prevent duplicate launch if another entrypoint already opened the GUI
    if os.environ.get('BB_LAUNCHED') != '1':
        os.environ['BB_LAUNCHED'] = '1'
    main()
