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

    def __init__(self, parent, refresh_callback: callable, save_api_key_callback: callable, save_openai_key_callback: callable, save_events_url_callback: callable):
        super().__init__(parent, fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.refresh_callback = refresh_callback
        self.save_api_key_callback = save_api_key_callback
        self.save_openai_key_callback = save_openai_key_callback
        self.save_events_url_callback = save_events_url_callback
        # Build all controls
        self._build_widgets()
        self.pack_propagate(False)
        self.grid_propagate(True)
        # Populate entries from persisted config
        try:
            # older code path may call a method that doesn't exist in some branches
            self._populate_from_config()
        except Exception:
            pass
        # Force CTkEntry placeholders to draw at startup when empty
        try:
            self.after(50, self._refresh_placeholders)
        except Exception:
            pass

    def _build_widgets(self):
        from pathlib import Path
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
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

        ctk.CTkLabel(self, text="Events Feed URL:").grid(row=7, column=0, sticky="w", pady=(0,5))
        self.events_feed_entry = ctk.CTkEntry(self)
        self.events_feed_entry.grid(row=7, column=1, sticky="ew", pady=(0,5))

        # Appearance Mode
        ctk.CTkLabel(self, text="Appearance:").grid(row=8, column=0, sticky="w", pady=(0,5))
        self.appearance_option = ctk.CTkOptionMenu(
            self,
            values=["Light", "Dark", "Hybrid"],
            command=self._on_appearance_changed,
        )
        # initialize with current mode
        try:
            current = ctk.get_appearance_mode()
        except Exception:
            current = "Dark"
        self.appearance_option.set(current)
        self.appearance_option.grid(row=8, column=1, sticky="ew", pady=(0,5))

        # Events Window (optional filter for upcoming events)
        ctk.CTkLabel(self, text="Events Window:").grid(row=9, column=0, sticky="w", pady=(0,5))
        self._events_window_values = [
            "All",
            "Today only",
            "3 days",
            "7 days",
            "14 days",
            "30 days",
        ]
        self.events_window_menu = ctk.CTkOptionMenu(
            self,
            values=self._events_window_values,
            command=self._on_events_window_changed,
        )
        self.events_window_menu.grid(row=9, column=1, sticky="ew", pady=(0,5))

        self.grid_columnconfigure(1, weight=1)

    def load_data(self, settings_data: dict, google_key: str, openai_key: str, events_url: str):
        """Populate all fields, falling back to sensible defaults."""
        settings_data = settings_data or {}
        colors = settings_data.get("colors", {})

        # Defaults
        default_title     = "LACC Bulletin"
        default_date      = date.today().strftime("%A, %B %d, %Y")
        default_primary   = "#103040"
        default_secondary = "#506070"
        default_theme     = self.themes[0] if getattr(self, "themes", None) else "default.css"
        default_appearance = "Dark"

        # Bulletin Title & Date
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, settings_data.get("bulletin_title") or default_title)
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, settings_data.get("bulletin_date") or default_date)

        # Theme
        theme = settings_data.get("theme_css") or default_theme
        if theme in getattr(self, "themes", []):
            self.theme_menu.set(theme)
        else:
            self.theme_menu.set(default_theme)

        # Appearance Mode
        try:
            current_mode = ctk.get_appearance_mode()
        except Exception:
            current_mode = default_appearance
        appearance = settings_data.get("appearance_mode") or current_mode or default_appearance
        try:
            if appearance == "Hybrid":
                ctk.set_appearance_mode("Light")
                app = self.winfo_toplevel()
                for panel_name in ("left_panel", "right_panel"):
                    panel = getattr(app, panel_name, None)
                    if panel:
                        try:
                            panel.configure(fg_color="#222222")
                        except Exception:
                            pass
            else:
                ctk.set_appearance_mode(appearance)
                app = self.winfo_toplevel()
                for panel_name in ("left_panel", "right_panel"):
                    panel = getattr(app, panel_name, None)
                    if panel:
                        try:
                            panel.configure(fg_color=None)
                        except Exception:
                            pass
        except Exception:
            pass
        self.appearance_option.set(appearance)

        # Colors
        self.primary_color_entry.delete(0, "end")
        self.primary_color_entry.insert(0, colors.get("primary") or default_primary)
        self.secondary_color_entry.delete(0, "end")
        self.secondary_color_entry.insert(0, colors.get("secondary") or default_secondary)

        # API Key (also persist immediately)
        self.google_api_entry.delete(0, "end")
        self.google_api_entry.insert(0, google_key or "")
        try:
            self.save_api_key_callback(self.google_api_entry.get())
        except Exception:
            pass

        self.openai_api_entry.delete(0, "end")
        self.openai_api_entry.insert(0, openai_key or "")
        try:
            self.save_openai_key_callback(self.openai_api_entry.get())
        except Exception:
            pass

        self.events_feed_entry.delete(0, "end")
        self.events_feed_entry.insert(0, events_url or "")
        try:
            self.save_events_url_callback(self.events_feed_entry.get())
        except Exception:
            pass

        # Events Window selection
        default_events_window_days = None  # All
        wnd_days = settings_data.get("events_window_days", default_events_window_days)
        label = self._map_events_window_days_to_label(wnd_days)
        try:
            self.events_window_menu.set(label)
        except Exception:
            pass
        # Reflect to app attribute for importer usage
        try:
            app = self.winfo_toplevel()
            setattr(app, 'events_window_days', None if label == 'All' else self._label_to_days(label))
        except Exception:
            pass

        # Fire a preview refresh
        try:
            self.refresh_callback()
        except Exception:
            pass

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
            "events_feed_url": self.events_feed_entry.get(),
            "appearance_mode": self.appearance_option.get(),
            "events_window_days": None if self.events_window_menu.get() == 'All' else self._label_to_days(self.events_window_menu.get()),
        }

    def _suggest_subject(self):
        app = self.winfo_toplevel()
        content_parts = []
        
        for sec in getattr(app, "sections_data", []):
            # Add the title, which is always a string
            title = sec.get("title", "")
            if title:
                content_parts.append(title)

            # Get the body, which might be a string or a dictionary
            body_content = sec.get("body", sec.get("content"))

            # IMPORTANT: Only append the body if it's a string
            if isinstance(body_content, str):
                content_parts.append(body_content)
            # If body_content is a dictionary or another type, it's skipped.

        # Now, content_parts is guaranteed to contain only strings
        prompt_text = "\n".join(content_parts)
        
        try:
            suggestions = app.generate_subject_lines(prompt_text)
            if suggestions:
                # messagebox.showinfo("Subject Suggestions", "\n".join(suggestions), parent=self)
                pass
        except Exception:
            pass

    def _on_appearance_changed(self, mode: str):
        """Apply the selected appearance mode immediately."""
        try:
            if mode == "Hybrid":
                # Hybrid: Light for main/editor, Dark for side panels (or vice versa)
                # For now, set app-wide to Light, then manually darken side panels if possible
                ctk.set_appearance_mode("Light")
                app = self.winfo_toplevel()
                # Try to set side panels to dark (if accessible)
                for panel_name in ("left_panel", "right_panel"):
                    panel = getattr(app, panel_name, None)
                    if panel:
                        try:
                            panel.configure(fg_color="#222222")
                        except Exception:
                            pass
            else:
                ctk.set_appearance_mode(mode)
                app = self.winfo_toplevel()
                for panel_name in ("left_panel", "right_panel"):
                    panel = getattr(app, panel_name, None)
                    if panel:
                        try:
                            panel.configure(fg_color=None)
                        except Exception:
                            pass
        except Exception:
            pass

    # ----- Events Window helpers -----
    def _map_events_window_days_to_label(self, days):
        try:
            if days is None:
                return "All"
            if int(days) == 0:
                return "Today only"
            n = int(days)
            return f"{n} days"
        except Exception:
            return "All"

    def _label_to_days(self, label: str) -> int:
        label = (label or '').strip().lower()
        if label.startswith('today'):
            return 0
        try:
            return int(label.split()[0])
        except Exception:
            return 0

    def _on_events_window_changed(self, label: str):
        try:
            app = self.winfo_toplevel()
            if label == 'All':
                setattr(app, 'events_window_days', None)
            else:
                setattr(app, 'events_window_days', self._label_to_days(label))
            if callable(self.refresh_callback):
                self.refresh_callback()
        except Exception:
            pass
