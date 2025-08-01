import customtkinter as ctk
from .base_section import SectionRegistry

@SectionRegistry.register("lacc_events")
@SectionRegistry.register("community_events")
@SectionRegistry.register("events") # For backward compatibility
class EventsFrame(ctk.CTkFrame):
    """
    A frame for editing an 'events' section, with a single layout style for the whole section.
    """
    def __init__(self, parent, section_data: dict, refresh_callback: callable, save_component_callback: callable):
        super().__init__(parent, fg_color="transparent")
        self.section_data = section_data
        self.refresh_callback = refresh_callback
        self.save_component_callback = save_component_callback

        if not isinstance(self.section_data.get('content'), list):
            self.section_data['content'] = []
        if 'layout_style' not in self.section_data:
            self.section_data['layout_style'] = 'Card'

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_frame.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(top_frame, text="Section Title")
        title_label.grid(row=0, column=0, padx=(0, 10))
        
        self.title_entry = ctk.CTkEntry(top_frame, font=ctk.CTkFont(size=14))
        self.title_entry.grid(row=0, column=1, sticky="ew")
        self.title_entry.insert(0, self.section_data.get("title", "Events"))
        self.title_entry.bind("<KeyRelease>", self._on_data_change)

        save_comp_button = ctk.CTkButton(top_frame, text="Save as Component", command=self._on_save_component)
        save_comp_button.grid(row=0, column=2, padx=(10, 0))

        style_frame = ctk.CTkFrame(self, fg_color="transparent")
        style_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        style_label = ctk.CTkLabel(style_frame, text="Layout Style:")
        style_label.pack(side="left", padx=(0, 10))

        self.style_selector = ctk.CTkSegmentedButton(
            style_frame,
            values=["Card", "Grid"],
            command=self.on_style_change
        )
        self.style_selector.set(self.section_data.get('layout_style', 'Card'))
        self.style_selector.pack(side="left")

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Event Items")
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        add_event_button = ctk.CTkButton(self, text="Add New Event", command=self.add_event_item)
        add_event_button.grid(row=3, column=0, sticky="ew", pady=(10, 0))

        self.rebuild_event_list()

    def on_style_change(self, value):
        self.section_data['layout_style'] = value
        self._on_data_change()

    def rebuild_event_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        for i, event_item in enumerate(self.section_data['content']):
            self.create_event_entry_widget(event_item, i)

    def create_event_entry_widget(self, event_item_data, index):
        entry_frame = ctk.CTkFrame(self.scrollable_frame)
        entry_frame.grid(row=index, column=0, sticky="ew", pady=5, padx=5)
        entry_frame.grid_columnconfigure(0, weight=1)

        text_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        text_frame.grid(row=0, column=0, sticky="ew", pady=5)
        text_frame.grid_columnconfigure(2, weight=1)

        date_entry = ctk.CTkEntry(text_frame, placeholder_text="Date (e.g., July 4)")
        date_entry.grid(row=0, column=0, padx=5, pady=5)
        date_entry.insert(0, event_item_data.get("date", ""))
        date_entry.bind("<KeyRelease>", lambda e, i=index: self.update_event_data(i, "date", e.widget.get()))

        time_entry = ctk.CTkEntry(text_frame, placeholder_text="Time (e.g., 7:00 PM)")
        time_entry.grid(row=0, column=1, padx=5, pady=5)
        time_entry.insert(0, event_item_data.get("time", ""))
        time_entry.bind("<KeyRelease>", lambda e, i=index: self.update_event_data(i, "time", e.widget.get()))

        desc_entry = ctk.CTkEntry(text_frame, placeholder_text="Event Description")
        desc_entry.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        desc_entry.insert(0, event_item_data.get("description", ""))
        desc_entry.bind("<KeyRelease>", lambda e, i=index: self.update_event_data(i, "description", e.widget.get()))

        remove_button = ctk.CTkButton(text_frame, text="X", width=30, command=lambda i=index: self.remove_event_item(i))
        remove_button.grid(row=0, column=3, padx=5, pady=5)
        
        image_url_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        image_url_frame.grid(row=1, column=0, sticky="ew", pady=5)
        image_url_frame.grid_columnconfigure(0, weight=1)

        image_url_entry = ctk.CTkEntry(image_url_frame, placeholder_text="Image URL (optional)")
        image_url_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        image_url_entry.insert(0, event_item_data.get("image_url", ""))
        image_url_entry.bind("<KeyRelease>", lambda e, i=index: self.update_event_data(i, "image_url", e.widget.get()))

        link_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        link_frame.grid(row=2, column=0, sticky="ew", pady=5)
        link_frame.grid_columnconfigure(0, weight=1)

        link_entry = ctk.CTkEntry(link_frame, placeholder_text="More Info Link (optional)")
        link_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        link_entry.insert(0, event_item_data.get("link", ""))
        link_entry.bind("<KeyRelease>", lambda e, i=index: self.update_event_data(i, "link", e.widget.get()))

        map_entry = ctk.CTkEntry(link_frame, placeholder_text="Map Link (optional)")
        map_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        map_entry.insert(0, event_item_data.get("map_link", ""))
        map_entry.bind("<KeyRelease>", lambda e, i=index: self.update_event_data(i, "map_link", e.widget.get()))

    def add_event_item(self):
        self.section_data['content'].append({
            "date": "",
            "time": "",
            "description": "",
            "image_url": "",
            "link": "",
            "map_link": "",
        })
        self.rebuild_event_list()
        self._on_data_change()

    def remove_event_item(self, index):
        self.section_data['content'].pop(index)
        self.rebuild_event_list()
        self._on_data_change()

    def update_event_data(self, index, key, value):
        while len(self.section_data['content']) <= index:
            self.section_data['content'].append({})
        self.section_data['content'][index][key] = value
        self._on_data_change()

    def _on_data_change(self, event=None):
        self.section_data['title'] = self.title_entry.get()
        self.refresh_callback()
        
    def _on_save_component(self):
        self._on_data_change()
        self.save_component_callback(self.section_data)
