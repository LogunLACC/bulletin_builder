import os
import customtkinter as ctk
from .app_core.loader import init_app
from .app_core.config import save_api_key

class BulletinBuilderApp(ctk.CTk):
    """
    Main application window for the LACC Bulletin Builder.
    Relies on app_core modules for UI setup, draft I/O, exporter, and preview.
    """
    def __init__(self):
        super().__init__()
        # Expose save_api_key for SettingsFrame
        self.save_api_key_to_config = save_api_key

        # Wire up all subsystems (core_init, handlers, drafts, sections, exporter, preview, UI)
        init_app(self)

        # Initial state: optional test data and placeholder
        self.populate_test_data()
        self.refresh_listbox_titles()
        self.show_placeholder()

    def populate_test_data(self):
        """Optional: load some sections for testing; no-op by default."""
        pass

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
