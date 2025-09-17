import customtkinter as ctk
from .base_section import SectionRegistry

@SectionRegistry.register("image")
class ImageFrame(ctk.CTkFrame):
    """
    A frame for editing an 'image' section by pasting an image URL.
    """
    def __init__(self, parent, section_data: dict, refresh_callback: callable):
        print(f"[DEBUG] ImageFrame __init__ called. parent={parent}, section_data={section_data}")
        self._init_args = (parent, section_data, refresh_callback, save_component_callback)
        try:
            super().__init__(parent, fg_color="#ccccff")  # Debug: blue background
            self.section_data = section_data
            self.refresh_callback = refresh_callback

            self.grid_rowconfigure(99, weight=1)
            self.grid_columnconfigure(1, weight=1)

            title_label = ctk.CTkLabel(self, text="Section Title")
            title_label.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="w")
            self.title_entry = ctk.CTkEntry(self, font=ctk.CTkFont(size=14))
            self.title_entry.grid(row=0, column=1, padx=0, pady=(0, 10), sticky="ew")
            self.title_entry.insert(0, self.section_data.get("title", "Image"))
            self.title_entry.bind("<KeyRelease>", self._on_data_change)

            image_label = ctk.CTkLabel(self, text="Image URL")
            image_label.grid(row=1, column=0, padx=(0, 10), pady=(0, 10), sticky="w")

            self.image_url_entry = ctk.CTkEntry(self, placeholder_text="https://your-website.com/path/to/image.jpg")
            self.image_url_entry.grid(row=1, column=1, sticky="ew")
            self.image_url_entry.insert(0, self.section_data.get("src", ""))
            self.image_url_entry.bind("<KeyRelease>", self._on_data_change)

            alt_text_label = ctk.CTkLabel(self, text="Alt Text")
            alt_text_label.grid(row=2, column=0, padx=(0, 10), pady=(0, 10), sticky="w")

            self.alt_text_entry = ctk.CTkEntry(self, placeholder_text="Description for screen readers...")
            self.alt_text_entry.grid(row=2, column=1, sticky="ew")
            self.alt_text_entry.insert(0, self.section_data.get("alt", ""))
            self.alt_text_entry.bind("<KeyRelease>", self._on_data_change)

            
            # Layout fix: ensure frame expands and grid works
            self.grid_propagate(True)
            self.update_idletasks()
            print(f"[DEBUG] ImageFrame children: {[str(w) for w in self.winfo_children()]}")
            print("[DEBUG] ImageFrame __init__ completed successfully.")
        except Exception as e:
            print(f"[ERROR] Exception in ImageFrame __init__: {e}")
            raise

    def _on_data_change(self, event=None):
        self.section_data['title'] = self.title_entry.get()
        self.section_data['src'] = self.image_url_entry.get()
        self.section_data['alt'] = self.alt_text_entry.get()
        self.refresh_callback()

    def _on_save_component(self):
        self._on_data_change()
        app = self.winfo_toplevel()
        app.save_component(self.section_data)
