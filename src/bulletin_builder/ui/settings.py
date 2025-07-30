import customtkinter as ctk
import tkinter.messagebox as messagebox
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

    def __init__(self, parent, refresh_callback: callable, save_api_key_callback: callable, save_openai_key_callback: callable):
        super().__init__(parent, fg_color="transparent")
        self.refresh_callback = refresh_callback
        self.save_api_key_callback = save_api_key_callback
        self.save_openai_key_callback = save_openai_key_callback

        # Build all controls
        self._build_widgets()

    def _build_widgets(self):
        import os
        from pathlib import Path
        # Title
        ctk.CTkLabel(self, text="Bulletin Title:").grid(row=0, column=0, sticky="w", pady=(0,5))
        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=(0,5))
        ctk.CTkButton(
            self, text="Suggest Subject", command=self._suggest_subject
        ).grid(row=0, column=2, padx=(5,0), pady=(0,5))
        # Date
        ctk.CTkLabel(self, text="Bulletin Date:").grid(row=1, column=0, sticky="w", pady=(0,5))
        self.date_entry = ctk.CTkEntry(self)
        self.date_entry.grid(row=1, column=1, sticky="ew", pady=(0,5))
        # Theme dropdown
        ctk.CTkLabel(self, text="Theme:").grid(row=2, column=0, sticky="w", pady=(0,5))
        themes_dir = Path(__file__).resolve().parents[1] / "templates" / "themes"
        try:
            self.themes = sorted([f.name for f in themes_dir.iterdir() if f.suffix == ".css"])
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

        ctk.CTkLabel(self, text="OpenAI API Key:").grid(row=6, column=0, sticky="w", pady=(0,5))
        self.openai_api_entry = ctk.CTkEntry(self, show="*")
        self.openai_api_entry.grid(row=6, column=1, sticky="ew", pady=(0,5))

        # Appearance Mode
        ctk.CTkLabel(self, text="Appearance:").grid(row=7, column=0, sticky="w", pady=(0,5))
        self.appearance_option = ctk.CTkOptionMenu(
            self,
            values=["Light", "Dark"],
            command=self._on_appearance_changed,
        )
        # initialize with current mode
        try:
            current = ctk.get_appearance_mode()
        except Exception:
            current = "Dark"
        self.appearance_option.set(current)
        self.appearance_option.grid(row=7, column=1, sticky="ew", pady=(0,5))

        self.grid_columnconfigure(1, weight=1)

    def load_data(self, settings_data: dict, google_key: str, openai_key: str):
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

        # Appearance Mode
        try:
            current_mode = ctk.get_appearance_mode()
        except Exception:
            current_mode = "Dark"
        appearance = settings_data.get("appearance_mode", current_mode)
        try:
            ctk.set_appearance_mode(appearance)
        except Exception:
            pass
        self.appearance_option.set(appearance)

        # Colors
        self.primary_color_entry.delete(0, "end")
        self.primary_color_entry.insert(0, colors.get("primary", default_primary))
        self.secondary_color_entry.delete(0, "end")
        self.secondary_color_entry.insert(0, colors.get("secondary", default_secondary))

        # API Key (also persist immediately)
        self.google_api_entry.delete(0, "end")
        self.google_api_entry.insert(0, google_key or "")
        self.save_api_key_callback(self.google_api_entry.get())

        self.openai_api_entry.delete(0, "end")
        self.openai_api_entry.insert(0, openai_key or "")
        self.save_openai_key_callback(self.openai_api_entry.get())

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
            "openai_api_key": self.openai_api_entry.get(),
            "appearance_mode": self.appearance_option.get(),
        }

    def _suggest_subject(self):
        app = self.winfo_toplevel()
        content_parts = []
        for sec in getattr(app, "sections_data", []):
            content_parts.append(sec.get("title", ""))
            content_parts.append(sec.get("body", sec.get("content", "")))
        prompt_text = "\n".join(content_parts)
        suggestions = app.generate_subject_lines(prompt_text)
        if suggestions:
            messagebox.showinfo("Subject Suggestions", "\n".join(suggestions), parent=self)

    def _on_appearance_changed(self, mode: str):
        """Apply the selected appearance mode immediately."""
        try:
            ctk.set_appearance_mode(mode)
        except Exception:
            pass
