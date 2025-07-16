import customtkinter as ctk
from ui.base_section import SectionRegistry

@SectionRegistry.register("custom_text")
class CustomTextFrame(ctk.CTkFrame):
    """
    A frame for editing a 'custom_text' section, containing a title and content.
    """
    def __init__(self, parent, section_data: dict, refresh_callback: callable, save_component_callback: callable):
        super().__init__(parent, fg_color="transparent")
        
        self.section_data = section_data
        self.refresh_callback = refresh_callback
        self.save_component_callback = save_component_callback

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title_label = ctk.CTkLabel(self, text="Section Title")
        title_label.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="w")
        
        self.title_entry = ctk.CTkEntry(self, font=ctk.CTkFont(size=14))
        self.title_entry.grid(row=0, column=1, padx=0, pady=(0, 10), sticky="ew")
        self.title_entry.insert(0, self.section_data.get("title", ""))
        self.title_entry.bind("<KeyRelease>", self._on_data_change)

        content_label = ctk.CTkLabel(self, text="Content")
        content_label.grid(row=1, column=0, padx=(0, 10), pady=(0, 10), sticky="nw")

        self.content_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(size=12), wrap="word")
        self.content_textbox.grid(row=1, column=1, sticky="nsew", pady=(0, 10))
        self.content_textbox.insert("1.0", self.section_data.get("content", ""))
        self.content_textbox.bind("<KeyRelease>", self._on_data_change)
        
        save_comp_button = ctk.CTkButton(self, text="Save as Component", command=self._on_save_component)
        save_comp_button.grid(row=2, column=1, sticky="e", pady=(10, 0))

    def _on_data_change(self, event=None):
        self.section_data['title'] = self.title_entry.get()
        self.section_data['content'] = self.content_textbox.get("1.0", "end-1c")
        self.refresh_callback()

    def _on_save_component(self):
        self._on_data_change()
        self.save_component_callback(self.section_data)
