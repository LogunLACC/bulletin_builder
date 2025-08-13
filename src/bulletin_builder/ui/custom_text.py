import customtkinter as ctk
from .base_section import SectionRegistry

@SectionRegistry.register("custom_text")
class CustomTextFrame(ctk.CTkFrame):
    """
    A frame for editing a 'custom_text' section, containing a title and content.
    """
    def __init__(self, parent, section_data: dict, refresh_callback: callable, save_component_callback: callable):
        print(f"[DEBUG] CustomTextFrame __init__ called. parent={parent}, section_data={section_data}")
        self._init_args = (parent, section_data, refresh_callback, save_component_callback)
        try:
            super().__init__(parent, fg_color="#ccffcc")  # Debug: green background
            self.section_data = section_data
            self.refresh_callback = refresh_callback
            self.save_component_callback = save_component_callback

            # Use pack for all widgets to avoid grid/pack conflicts and ensure visibility
            title_label = ctk.CTkLabel(self, text="Section Title")
            title_label.pack(anchor="w", padx=(0, 10), pady=(0, 10))
            self.title_entry = ctk.CTkEntry(self, font=ctk.CTkFont(size=14))
            self.title_entry.pack(fill="x", padx=0, pady=(0, 10))
            self.title_entry.insert(0, self.section_data.get("title", ""))
            self.title_entry.bind("<KeyRelease>", self._on_data_change)

            content_label = ctk.CTkLabel(self, text="Content")
            content_label.pack(anchor="w", padx=(0, 10), pady=(0, 10))

            self.content_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(size=12), wrap="word")
            self.content_textbox.pack(fill="both", expand=True, pady=(0, 10))
            self.content_textbox.insert("1.0", self.section_data.get("content", ""))
            self.content_textbox.bind("<KeyRelease>", self._on_data_change)

            save_comp_button = ctk.CTkButton(self, text="Save as Component", command=self._on_save_component)
            save_comp_button.pack(anchor="e", pady=(10, 0))
            self.update_idletasks()
            print(f"[DEBUG] CustomTextFrame children: {[str(w) for w in self.winfo_children()]}")
            print("[DEBUG] CustomTextFrame __init__ completed successfully.")
        except Exception as e:
            print(f"[ERROR] Exception in CustomTextFrame __init__: {e}")
            raise

    def _on_data_change(self, event=None):
        self.section_data['title'] = self.title_entry.get()
        self.section_data['content'] = self.content_textbox.get("1.0", "end-1c")
        self.refresh_callback()

    def _on_save_component(self):
        self._on_data_change()
        self.save_component_callback(self.section_data)
