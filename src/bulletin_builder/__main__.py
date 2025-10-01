import os
import sys
import customtkinter as ctk
from bulletin_builder.app_core.loader import init_app
from bulletin_builder.app_core.config import (
    save_api_key,
    save_openai_key,
    save_events_feed_url,
    save_window_state,
)

# Force PyInstaller to include these dynamically-imported modules
import bulletin_builder.app_core.importer  # noqa: F401
import bulletin_builder.app_core.suggestions  # noqa: F401

import argparse
import socket
import atexit


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
        # Always start maximized; ignore saved geometry to prevent bounce/snap
        self._desired_start_state = 'zoomed'
        try:
            self.state('zoomed')
            self.update_idletasks()
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

        # Intercept close: confirm, optional autosave, then persist window state
        try:
            def _on_close():
                from bulletin_builder.app_core.config import (
                    load_confirm_on_close, load_autosave_on_close,
                )
                # Determine behavior from UI switches or config
                try:
                    confirm = bool(self.settings_frame.confirm_close_var.get())
                except Exception:
                    confirm = load_confirm_on_close(True)
                try:
                    autosave_enabled = bool(self.settings_frame.autosave_close_var.get())
                except Exception:
                    autosave_enabled = load_autosave_on_close(True)

                # Confirm dialog (OK/Cancel)
                if confirm:
                    try:
                        from tkinter import messagebox
                        ok = messagebox.askokcancel(
                            "Exit",
                            "Close the application?\nA copy of your current draft will be auto-saved to 'user_drafts/AutoSave'.",
                            parent=self,
                        )
                    except Exception:
                        ok = True
                    if not ok:
                        return

                autosave_path = None
                if autosave_enabled:
                    try:
                        from datetime import datetime
                        from pathlib import Path
                        autosave_dir = Path('user_drafts') / 'AutoSave'
                        autosave_dir.mkdir(parents=True, exist_ok=True)
                        ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                        title = 'Draft'
                        try:
                            title = self.settings_frame.title_entry.get().strip() or 'Draft'
                        except Exception:
                            pass
                        safe_title = ''.join(c for c in title if c.isalnum() or c in (' ','-','_')).rstrip()
                        filename = f"{safe_title.replace(' ','_')}_{ts}.json"
                        autosave_path = str(autosave_dir / filename)
                        prev = getattr(self, 'current_draft_path', None)
                        try:
                            self.current_draft_path = autosave_path
                            if hasattr(self, 'save_draft'):
                                self.save_draft(save_as=False)
                        finally:
                            self.current_draft_path = prev
                    except Exception:
                        autosave_path = None

                # Status toast then close
                if autosave_path and hasattr(self, 'show_status_message'):
                    try:
                        self.show_status_message(f"Autosaved to {autosave_path}", duration_ms=800)
                    except Exception:
                        pass

                def _finalize_close():
                    try:
                        st = self.state()
                        if st == 'zoomed':
                            self.state('normal')
                            geo = self.geometry()
                            save_window_state(geo, st)
                            self.state('zoomed')
                        else:
                            save_window_state(self.geometry(), st)
                    except Exception:
                        pass
                    self.destroy()

                # Delay slightly if we showed a toast
                try:
                    delay = 800 if autosave_path else 0
                    self.after(delay, _finalize_close)
                except Exception:
                    _finalize_close()
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

        # Re-assert maximized state after widgets map (prevents snap-to-small)
        def _ensure_maximized():
            try:
                if self.state() != 'zoomed':
                    self.state('zoomed')
            except Exception:
                pass
        try:
            self.after_idle(_ensure_maximized)
            self.after(300, _ensure_maximized)
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

        add("Export Bulletin (FrontSteps)", "on_export_frontsteps_clicked")
        add("Open in Browser", "open_in_browser")
        file_menu.add_separator()
        add("Import Announcements CSV...", "import_announcements_csv")
        file_menu.add_separator()
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)

        # Removed legacy Export submenu; only FrontSteps export remains

        menubar.add_cascade(label="File", menu=file_menu)
        self.configure(menu=menubar)

    def refresh_listbox_titles(self):
        """Fallback implementation replaced during init_app."""
        pass


def run_gui():
    """Launch the main GUI with a per-process and per-machine single-instance guard."""
    # Process-level guard
    if os.environ.get('BB_LAUNCHED') == '1':
        return
    os.environ['BB_LAUNCHED'] = '1'

    # Cross-process guard (best-effort): bind localhost port
    lock_sock = None
    try:
        lock_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lock_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lock_sock.bind(('127.0.0.1', 51283))
        lock_sock.listen(1)
        atexit.register(lambda: lock_sock and lock_sock.close())
    except Exception:
        try:
            if lock_sock:
                lock_sock.close()
        except Exception:
            pass
        return

    # When frozen, change CWD to the user's app data directory
    if getattr(sys, 'frozen', False):
        app_data_dir = os.path.join(os.getenv('APPDATA'), 'BulletinBuilder')
        os.makedirs(app_data_dir, exist_ok=True)
        os.chdir(app_data_dir)

    os.makedirs('user_drafts', exist_ok=True)

    app = BulletinBuilderApp()
    app.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Bulletin Builder Launcher")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode (no GUI)")
    parser.parse_args()

    # Default to launching GUI once; prevents duplicate creation when called via different entrypoints
    try:
        run_gui()
    except Exception as e:
        import traceback
        with open("error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        try:
            import tkinter.messagebox as mb
            mb.showerror("Error", str(e))
        except Exception:
            pass
    return
