import customtkinter as ctk
from tkinter import simpledialog
from .base_section import SectionRegistry

@SectionRegistry.register("announcements")
class AnnouncementsFrame(ctk.CTkFrame):
    """
    A frame for editing an 'announcements' section, now with AI features.
    """
    def __init__(self, parent, section_data: dict, refresh_callback: callable, save_component_callback: callable, ai_callback: callable):
        print(f"[DEBUG] AnnouncementsFrame __init__ called. parent={parent}, section_data={section_data}")
        self._init_args = (parent, section_data, refresh_callback, save_component_callback, ai_callback)
        try:
            super().__init__(parent, fg_color="transparent")
            self.section_data = section_data
            self.refresh_callback = refresh_callback
            self.save_component_callback = save_component_callback
            self.ai_callback = ai_callback

            # --- Layout Configuration ---
            self.grid_columnconfigure(1, weight=1)

            # --- Widgets ---
            title_label = ctk.CTkLabel(self, text="Title")
            title_label.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="w")
            self.title_entry = ctk.CTkEntry(self, font=ctk.CTkFont(size=14))
            self.title_entry.grid(row=0, column=1, sticky="ew", pady=10)
            self.title_entry.insert(0, self.section_data.get("title", ""))
            self.title_entry.bind("<KeyRelease>", self._on_data_change)

            body_label = ctk.CTkLabel(self, text="Body")
            body_label.grid(row=1, column=0, padx=(0, 10), pady=10, sticky="nw")
            # Layout fix: ensure frame expands and grid works
            self.grid_propagate(True)
            self.pack_propagate(False)
            self.pack(fill="both", expand=True)
            print("[DEBUG] AnnouncementsFrame __init__ completed successfully.")
        except Exception as e:
            print(f"[ERROR] Exception in AnnouncementsFrame __init__: {e}")
            raise
        
        ai_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        ai_button_frame.grid(row=2, column=1, sticky="w", pady=(0, 5))

        improve_button = ctk.CTkButton(ai_button_frame, text="Improve Writing", command=self.improve_writing)
        improve_button.pack(side="left", padx=(0, 10))
        
        generate_button = ctk.CTkButton(ai_button_frame, text="Generate from Prompt", command=self.generate_from_prompt)
        generate_button.pack(side="left")

        self.body_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(size=12), wrap="word")
        self.body_textbox.grid(row=3, column=1, sticky="nsew", pady=10)
        self.body_textbox.insert("1.0", self.section_data.get("body", ""))
        self.body_textbox.bind("<KeyRelease>", self._on_data_change)
        self.grid_rowconfigure(3, weight=1)

        link_label = ctk.CTkLabel(self, text="Link URL")
        link_label.grid(row=4, column=0, padx=(0, 10), pady=10, sticky="w")
        self.link_entry = ctk.CTkEntry(self, placeholder_text="https://example.com (optional)")
        self.link_entry.grid(row=4, column=1, sticky="ew", pady=10)
        self.link_entry.insert(0, self.section_data.get("link", ""))
        self.link_entry.bind("<KeyRelease>", self._on_data_change)

        link_text_label = ctk.CTkLabel(self, text="Link Text")
        link_text_label.grid(row=5, column=0, padx=(0, 10), pady=10, sticky="w")
        self.link_text_entry = ctk.CTkEntry(self, placeholder_text="Read More... (optional)")
        self.link_text_entry.grid(row=5, column=1, sticky="ew", pady=10)
        self.link_text_entry.insert(0, self.section_data.get("link_text", ""))
        self.link_text_entry.bind("<KeyRelease>", self._on_data_change)

        save_comp_button = ctk.CTkButton(self, text="Save as Component", command=self._on_save_component)
        save_comp_button.grid(row=6, column=1, sticky="e", pady=10)

    def improve_writing(self):
        current_text = self.body_textbox.get("1.0", "end-1c")
        if not current_text.strip():
            return
        
        prompt = f"As a professional editor, please correct the grammar and improve the clarity of the following text, but keep the core message the same. Return only the improved text:\n\n{current_text}"
        improved_text = self.ai_callback(prompt)
        
        if improved_text:
            self.body_textbox.delete("1.0", "end")
            self.body_textbox.insert("1.0", improved_text)
            self._on_data_change()

    def generate_from_prompt(self):
        prompt_dialog = ctk.CTkInputDialog(text="Enter a short prompt for the announcement:", title="Generate Announcement")
        user_prompt = prompt_dialog.get_input()

        if user_prompt:
            full_prompt = f"Write a friendly and brief announcement for an email bulletin based on the following topic. Return only the announcement text:\n\n{user_prompt}"
            generated_text = self.ai_callback(full_prompt)
            
            if generated_text:
                self.body_textbox.delete("1.0", "end")
                self.body_textbox.insert("1.0", generated_text)
                self._on_data_change()

    def _on_data_change(self, event=None):
        self.section_data['title'] = self.title_entry.get()
        self.section_data['body'] = self.body_textbox.get("1.0", "end-1c")
        self.section_data['link'] = self.link_entry.get()
        self.section_data['link_text'] = self.link_text_entry.get()
        self.refresh_callback()

    def _on_save_component(self):
        self._on_data_change()
        self.save_component_callback(self.section_data)
