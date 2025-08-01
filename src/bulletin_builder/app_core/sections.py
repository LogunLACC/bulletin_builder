import customtkinter as ctk
import tkinter as tk
from ..ui.base_section import SectionRegistry

class AddSectionDialog(ctk.CTkToplevel):
    """Modal dialog to capture title and type for a new section."""
    def __init__(self, parent, section_types):
        super().__init__(parent)
        self.title("Add New Section")
        self.geometry("400x220")
        self.transient(parent)
        self.grab_set()
        self.result = None

        frm = ctk.CTkFrame(self)
        frm.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(frm, text="Section Title:").pack(anchor="w")
        self.title_entry = ctk.CTkEntry(frm)
        self.title_entry.pack(fill="x", pady=(0,10))

        ctk.CTkLabel(frm, text="Section Type:").pack(anchor="w")
        self.type_menu = ctk.CTkOptionMenu(frm, values=section_types)
        self.type_menu.pack(fill="x", pady=(0,20))

        btnf = ctk.CTkFrame(frm)
        btnf.pack(fill="x", side="bottom")
        ctk.CTkButton(btnf, text="OK", command=self.on_ok).pack(side="right")
        ctk.CTkButton(btnf, text="Cancel", command=self.destroy, fg_color="gray50", hover_color="gray40").pack(side="right", padx=(0,10))

        self.title_entry.focus_set()
        self.wait_window()

    def on_ok(self):
        title = self.title_entry.get().strip()
        sec_type = self.type_menu.get()
        if not title:
            tk.messagebox.showwarning("Input Error", "Please enter a title.", parent=self)
            return
        self.result = (title, sec_type)
        self.destroy()

    def get_input(self):
        return self.result


def init(app):
    # --- Add Section ---
    def add_section_dialog():
        types = SectionRegistry.available_types()
        dlg = AddSectionDialog(app, types)
        result = dlg.get_input()
        if result:
            title, sec_type = result
            app.sections_data.append({'title': title, 'type': sec_type, 'content': {}})
            app.refresh_listbox_titles()
            app.show_placeholder()

    # --- Remove Section ---
    def remove_section():
        sel = app.section_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        del app.sections_data[idx]
        app.refresh_listbox_titles()
        app.show_placeholder()

    # --- Section Selection ---
    def on_section_select(event=None):
        sel = app.section_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        section = app.sections_data[idx]
        app.clear_editor_panel()
        FrameCls = SectionRegistry.get_frame(section['type'])
        # AnnouncementsFrame may require extra callbacks
        params = [app.right_panel, section, app.refresh_listbox_titles, app.save_component]
        if section['type'] == 'announcements':
            params.append(app.ai_callback)
        frame = FrameCls(*params)
        frame.pack(fill='both', expand=True)
        app.current_editor_frame = frame
        app.active_editor_index = idx

    # --- Update Data ---
    def update_section_data(updated):
        if app.active_editor_index is not None:
            app.sections_data[app.active_editor_index].update(updated)
            app.update_preview()

    # --- Refresh Listbox Titles ---
    def refresh_listbox_titles(event=None):
        sel = app.section_listbox.curselection()
        app.section_listbox.delete(0, tk.END)
        for i, sec in enumerate(app.sections_data):
            title = sec.get('title', 'Untitled')
            app.section_listbox.insert(tk.END, f"{i+1}. {title}")
        for idx in sel:
            app.section_listbox.selection_set(idx)
        if hasattr(app, 'compute_suggestions'):
            app.compute_suggestions()

    # Bind methods
    app.add_section_dialog = add_section_dialog
    app.remove_section = remove_section
    app.on_section_select = on_section_select
    app.update_section_data = update_section_data
    app.refresh_listbox_titles = refresh_listbox_titles
