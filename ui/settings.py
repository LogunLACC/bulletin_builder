import customtkinter as ctk
from datetime import date

class SettingsFrame(ctk.CTkFrame):
    """
    A frame for editing global bulletin settings:
      • Bulletin Title
      • Bulletin Date
      • Theme (CSS file)
      • Primary / Secondary colors
      • Google AI API Key
    """

    def __init__(self, parent, refresh_callback: callable, save_api_key_callback: callable):
        super().__init__(parent, fg_color="transparent")
        self.refresh_callback = refresh_callback
        self.save_api_key_callback = save_api_key_callback

        # Build all controls
        self._build_widgets()

    def _build_widgets(self):
        import os
        # Title
        ctk.CTkLabel(self, text="Bulletin Title:").grid(row=0, column=0, sticky="w", pady=(0,5))
        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=(0,5))
        # Date
        ctk.CTkLabel(self, text="Bulletin Date:").grid(row=1, column=0, sticky="w", pady=(0,5))
        self.date_entry = ctk.CTkEntry(self)
        self.date_entry.grid(row=1, column=1, sticky="ew", pady=(0,5))
        # Theme dropdown
        ctk.CTkLabel(self, text="Theme:").grid(row=2, column=0, sticky="w", pady=(0,5))
        themes_dir = os.path.join("templates", "themes")
        try:
            self.themes = sorted([f for f in os.listdir(themes_dir) if f.endswith(".css")])
        except Exception:
            self.themes = []
        self.theme_menu = ctk.CTkOptionMenu(self, values=self.themes)
        self.theme_menu.grid(row=2, column=1, sticky="ew", pady=(0,5))
        # Colors
        ctk.CTkLabel(self, text="Primary Color:").grid(row=3, column=0, sticky="w", pady=(0,5))
        self.primary_color_entry = ctk.CTkEntry(self)
        self.primary_color_entry.grid(row=3, column=1, sticky="ew", pady=(0,5))
        ctk.CTkLabel(self, text="Secondary Color:").grid(row=4, column=0, sticky="w", pady=(0,5))
        self.secondary_color_entry = ctk.CTkEntry(self)
        self.secondary_color_entry.grid(row=4, column=1, sticky="ew", pady=(0,5))
        # API Key
        ctk.CTkLabel(self, text="Google AI API Key:").grid(row=5, column=0, sticky="w", pady=(0,5))
        self.google_api_entry = ctk.CTkEntry(self, show="*")
        self.google_api_entry.grid(row=5, column=1, sticky="ew", pady=(0,5))

        self.grid_columnconfigure(1, weight=1)

    def load_data(self, settings_data: dict, api_key: str):
        """Populate all fields, falling back to sensible defaults."""
        settings_data = settings_data or {}
        colors = settings_data.get("colors", {})

        # Defaults
        default_title     = "LACC Bulletin"
        default_date      = date.today().strftime("%A, %B %d, %Y")
        default_primary   = "#103040"
        default_secondary = "#506070"

        # Bulletin Title & Date
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, settings_data.get("bulletin_title", default_title))
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, settings_data.get("bulletin_date", default_date))

        # Theme
        theme = settings_data.get("theme_css", self.themes[0] if self.themes else "default.css")
        if theme in self.themes:
            self.theme_menu.set(theme)

        # Colors
        self.primary_color_entry.delete(0, "end")
        self.primary_color_entry.insert(0, colors.get("primary", default_primary))
        self.secondary_color_entry.delete(0, "end")
        self.secondary_color_entry.insert(0, colors.get("secondary", default_secondary))

        # API Key (also persist immediately)
        self.google_api_entry.delete(0, "end")
        self.google_api_entry.insert(0, api_key or "")
        self.save_api_key_callback(self.google_api_entry.get())

        # Fire a preview refresh
        self.refresh_callback()

    def dump(self) -> dict:
        """Read out current settings to embed in drafts or exports."""
        return {
            "bulletin_title": self.title_entry.get(),
            "bulletin_date":   self.date_entry.get(),
            "theme_css":       self.theme_menu.get(),
            "colors": {
                "primary":   self.primary_color_entry.get(),
                "secondary": self.secondary_color_entry.get(),
            },
            "google_api_key": self.google_api_entry.get(),
        }
