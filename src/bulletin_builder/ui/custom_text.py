import customtkinter as ctk
from .base_section import SectionRegistry

@SectionRegistry.register("custom_text")
class CustomTextFrame(ctk.CTkFrame):
    """
    A frame for editing a 'custom_text' section, containing a title and content.
    """
    def __init__(self, parent, section_data: dict, refresh_callback: callable):
        # Store references for potential future re-instantiation
        self._init_args = (parent, section_data, refresh_callback)
        try:
            super().__init__(parent, fg_color="transparent")
            self.section_data = section_data
            self.refresh_callback = refresh_callback

            # Debug label for section info
            self.grid_rowconfigure(99, weight=1)
            self.grid_columnconfigure(1, weight=1)

            # small helper label for accessibility (not a duplicate heading)
            # (do not duplicate <h2> — templates render section titles)

            title_label = ctk.CTkLabel(self, text="Section Title")
            title_label.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(0, 10))
            self.title_entry = ctk.CTkEntry(self, font=ctk.CTkFont(size=14))
            self.title_entry.grid(row=1, column=1, sticky="ew", padx=0, pady=(0, 10))
            self.title_entry.insert(0, self.section_data.get("title", ""))
            self.title_entry.bind("<KeyRelease>", self._on_data_change)

            content_label = ctk.CTkLabel(self, text="Content")
            content_label.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(0, 10))

            self.content_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(size=12), wrap="word")
            self.content_textbox.grid(row=2, column=1, sticky="nsew", pady=(0, 10))
            self.content_textbox.insert("1.0", self.section_data.get("content", ""))
            self.content_textbox.bind("<KeyRelease>", self._on_data_change)

        except Exception as e:
            print(f"[ERROR] Exception in CustomTextFrame __init__: {e}")
            raise

    def _on_data_change(self, event=None):
        self.section_data['title'] = self.title_entry.get()
        self.section_data['content'] = self.content_textbox.get("1.0", "end-1c")
        # Propagate changes to main sections_data
        try:
            # Resolve the top-level application instance and call the sections.update helper
            app = self.winfo_toplevel()
            from bulletin_builder.app_core.sections import update_section_data
            update_section_data(app, {'title': self.section_data['title'], 'content': self.section_data['content']})
        except Exception as e:
            print(f"[ERROR] Could not update section data: {e}")
        self.refresh_callback()

    def _on_save_component(self):
        self._on_data_change()
        # Ensure latest data is saved
        try:
            app = self.winfo_toplevel()
            from bulletin_builder.app_core.sections import update_section_data
            update_section_data(app, {'title': self.section_data['title'], 'content': self.section_data['content']})
        except Exception as e:
            print(f"[ERROR] Could not update section data on save: {e}")
        app.save_component(self.section_data)
