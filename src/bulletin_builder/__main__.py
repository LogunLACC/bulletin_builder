import os
import customtkinter as ctk
from bulletin_builder.app_core.loader import init_app
from bulletin_builder.app_core.config import (
    save_api_key,
    save_openai_key,
    save_events_feed_url,
)

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

        # Expose config savers for SettingsFrame
        self.save_api_key_to_config = save_api_key
        self.save_openai_key_to_config = save_openai_key
        self.save_events_url_to_config = save_events_feed_url

        # --- Provide stubs BEFORE init_app (menu wiring may reference them) ---
        if not hasattr(self, "import_announcements_csv"):
            def _stub_import_csv(*_a, **_k):
                print("[info] Import Announcements CSV not wired yet.")
            self.import_announcements_csv = _stub_import_csv

        # PDF removed: keep harmless no-ops in case any legacy wiring still references them
        if not hasattr(self, "export_pdf"):
            def _no_pdf(*_a, **_k):
                print("[info] PDF export removed.")
            self.export_pdf = _no_pdf

        if not hasattr(self, "on_export_pdf_clicked"):
            def _no_pdf_click(*_a, **_k):
                print("[info] PDF export removed.")
            self.on_export_pdf_clicked = _no_pdf_click
        # ---------------------------------------------------------------------

        # Wire up all subsystems (core_init, handlers, drafts, sections, preview, UI)
        init_app(self)

        # Try the menu builder that init_app should have attached; otherwise fall back
        if hasattr(self, "_build_menus"):
            self._build_menus()
        else:
            print("[warn] _build_menus not attached by init_app; building minimal menus locally.")
            self._build_menus = self._build_menus_fallback  # expose for consistency
            self._build_menus()

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

        add("Export HTML & Text…", "on_export_html_text_clicked")
        add("Copy Email-Ready HTML", "on_copy_for_email_clicked")
        add("Open in Browser", "open_in_browser")
        file_menu.add_separator()
        add("Import Announcements CSV…", "import_announcements_csv")
        file_menu.add_separator()
        add("Export Calendar (.ics)…", "on_export_ics_clicked")
        add("Send Test Email…", "on_send_test_email_clicked")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)

        menubar.add_cascade(label="File", menu=file_menu)
        self.configure(menu=menubar)

    def refresh_listbox_titles(self):
        """Fallback implementation replaced during init_app."""
        pass


def main():
    parser = argparse.ArgumentParser(description="Bulletin Builder CLI")
    parser.add_argument("--gui", action="store_true", help="Launch the WYSIWYG editor")
    args = parser.parse_args()

    if args.gui:
        print("📰 Bulletin Builder CLI is running!")
        launch_gui()
    else:
        print("📰 CLI mode coming soon! Use '--gui' to launch the editor.")


if __name__ == '__main__':
    # Ensure required directories exist
    for d in [
        'templates/partials',
        'templates/themes',
        'user_drafts',
        'assets'
    ]:
        os.makedirs(d, exist_ok=True)

    app = BulletinBuilderApp()
    app.mainloop()
