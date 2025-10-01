import os
import sys
import atexit
import customtkinter as ctk
from bulletin_builder.app_core.loader import init_app
from bulletin_builder.app_core.config import (
    save_api_key,
    save_openai_key,
    save_events_feed_url,
    save_window_state,
    load_confirm_on_close,
    load_autosave_on_close,
)
import socket


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

        self.protocol("WM_DELETE_WINDOW", self._on_close)

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

    def _on_close(self):
        """Handle the window close event."""
        # 1. Check if user wants to cancel the close operation
        if self._confirm_close_is_denied():
            return

        # 2. Perform autosave if enabled
        autosave_path = self._perform_autosave()

        # 3. Show a status message if a save occurred
        if autosave_path and hasattr(self, 'show_status_message'):
            self.show_status_message(f"Autosaved to {autosave_path}", duration_ms=800)

        # 4. Finalize the closing process (with a delay for the toast)
        delay = 800 if autosave_path else 0
        self.after(delay, self._finalize_close)

    def _confirm_close_is_denied(self) -> bool:
        """Show a confirmation dialog if configured. Return True if user cancels."""
        try:
            confirm = bool(self.settings_frame.confirm_close_var.get())
        except Exception:
            confirm = load_confirm_on_close(True)

        if not confirm:
            return False

        from tkinter import messagebox
        ok = messagebox.askokcancel(
            "Exit",
            "Close the application?\nA copy of your current draft will be auto-saved to 'user_drafts/AutoSave'.",
            parent=self,
        )
        return not ok

    def _perform_autosave(self) -> str | None:
        """Saves a timestamped draft if autosave is enabled. Returns the path if saved."""
        try:
            autosave_enabled = bool(self.settings_frame.autosave_close_var.get())
        except Exception:
            autosave_enabled = load_autosave_on_close(True)

        if not autosave_enabled:
            return None

        try:
            from datetime import datetime
            from pathlib import Path
            autosave_dir = Path('user_drafts') / 'AutoSave'
            autosave_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            title = (self.settings_frame.title_entry.get().strip() or 'Draft')
            safe_title = ''.join(c for c in title if c.isalnum() or c in (' ','-','_')).rstrip()
            filename = f"{safe_title.replace(' ','_')}_{ts}.json"
            autosave_path = str(autosave_dir / filename)

            # Use a dedicated autosave method if available, otherwise fallback
            if hasattr(self, 'autosave_draft'):
                self.autosave_draft(autosave_path)
            else: # Fallback to the old, fragile way
                prev = getattr(self, 'current_draft_path', None)
                self.current_draft_path = autosave_path
                self.save_draft(save_as=False)
                self.current_draft_path = prev
            return autosave_path
        except Exception:
            return None

    def _finalize_close(self):
        """Save window state and destroy the window."""
        try:
            st = self.state()
            geo = self.geometry()
            if st == 'zoomed':
                self.state('normal') # Get geometry from normal state
                geo = self.geometry()
            save_window_state(geo, st)
        finally:
            self.destroy()

    def _build_menus_fallback(self):
        """
        Minimal, safe menu bar that wires only the known handlers if present.
        This serves as a fallback to prevent crashes if the main UI setup fails.
        """
        import tkinter as tk
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)

        if hasattr(self, "export_current_preview"):
            file_menu.add_command(label="Export Bulletin (FrontSteps)", command=self.export_current_preview)
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)
        self.configure(menu=menubar)

    def export_current_preview(self):
        """Renders the current bulletin state and passes it to the exporter."""
        try:
            if hasattr(self, 'render_bulletin_html') and hasattr(self, 'collect_context'):
                ctx = self.collect_context()
                html_content = self.render_bulletin_html(ctx)
                if hasattr(self, 'export_frontsteps_html'):
                    self.export_frontsteps_html(html_content)
        except Exception as e:
            print(f"Export failed: {e}")

    def refresh_listbox_titles(self):
        """Fallback implementation replaced during init_app."""
        pass


def run_gui():
    """Launch the main GUI with a per-process and per-machine single-instance guard."""
    # Cross-process guard (best-effort): bind localhost port
    lock_sock = None
    try:
        lock_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lock_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lock_sock.bind(('127.0.0.1', 51283))
    except OSError:
        # Port is already in use, another instance is likely running.
        # In a future task, we can send a message to the existing instance to focus it.
        from tkinter import messagebox
        messagebox.showinfo(
            "Already Running",
            "An instance of Bulletin Builder is already running.",
            icon="info"
        )
        return
    atexit.register(lock_sock.close)

    # When frozen, change CWD to the user's app data directory
    if getattr(sys, 'frozen', False):
        app_data_dir = os.path.join(os.getenv('APPDATA'), 'BulletinBuilder')
        os.makedirs(app_data_dir, exist_ok=True)
        os.chdir(app_data_dir)

    os.makedirs('user_drafts', exist_ok=True)

    app = BulletinBuilderApp()
    app.mainloop()


def main():
    """Primary application entry point."""
    try:
        from bulletin_builder.cli import main as cli_main
        # Delegate to the primary CLI entry point.
        # __main__ is for `python -m bulletin_builder`, which should behave like the installed script.
        cli_main()
    except Exception as e:
        import traceback
        with open("error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        from tkinter import messagebox
        messagebox.showerror("Fatal Error", f"A fatal error occurred:\n\n{e}\n\nSee error.log for details.")

if __name__ == "__main__":
    main()
