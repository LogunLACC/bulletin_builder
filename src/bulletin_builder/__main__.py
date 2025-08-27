import os
import customtkinter as ctk
from .app_core.loader import init_app
from .app_core.config import (
    save_api_key,
    save_openai_key,
    save_events_feed_url,
)
import argparse
from .wysiwyg_editor import launch_gui

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

        # Wire up all subsystems (core_init, handlers, drafts, sections, exporter, preview, UI)
        from .app_core.core_init import init as core_init
        core_init(self)
        init_app(self)

        # Initial state: optional test data and placeholder
        self.populate_test_data()
        self.refresh_listbox_titles()
        self.show_placeholder()

    def populate_test_data(self):
        """Optional: load some sections for testing; no-op by default."""
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
