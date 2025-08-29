import customtkinter as ctk
import tkinter as tk
from bulletin_builder.ui.base_section import SectionRegistry

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
            # tk.messagebox.showwarning("Input Error", "Please enter a title.", parent=self)
            return
        self.result = (title, sec_type)
        self.destroy()

    def get_input(self):
        return self.result


def add_section_dialog(app):
    types = SectionRegistry.available_types()
    dlg = AddSectionDialog(app, types)
    result = dlg.get_input()
    if result:
        title, sec_type = result
        app.sections_data.append({'title': title, 'type': sec_type, 'content': {}})
        app.refresh_listbox_titles()
        # Select the newly added section
        idx = len(app.sections_data) - 1
        app.section_listbox.selection_clear(0, tk.END)
        app.section_listbox.selection_set(idx)
        app.section_listbox.activate(idx)
        app.section_listbox.see(idx)
        # Trigger the selection event to show the editor
        app.on_section_select()

def remove_section(app):
    sel = app.section_listbox.curselection()
    if not sel:
        return
    idx = sel[0]
    del app.sections_data[idx]
    app.refresh_listbox_titles()
    app.show_placeholder()

def init(app):
    # Bind methods to the application instance only during initialization.
    app.add_section_dialog = lambda: add_section_dialog(app)
    app.remove_section = lambda: remove_section(app)
    # Bind event handlers as closures that call the module-level helpers with app
    app.on_section_select = lambda event=None: on_section_select(app, event)
    app.update_section_data = lambda updated: update_section_data(app, updated)
    app.refresh_listbox_titles = lambda event=None: refresh_listbox_titles(app, event)

# The following functions are now defined and bound inside the init(app) function.

# --- Section Selection ---
def on_section_select(app, event=None):
    print("[DEBUG] on_section_select called")
    sel = app.section_listbox.curselection()
    if not sel:
        print("[DEBUG] on_section_select: no selection")
        return
    idx = sel[0]
    section = app.sections_data[idx]
    print(f"[DEBUG] on_section_select: idx={idx}, section type={section.get('type')}, title={section.get('title')}")
    try:
        FrameCls = SectionRegistry.get_frame(section['type'])
        if section['type'] == 'announcements':
            frame = FrameCls(app.editor_container, section=section, on_dirty=app.refresh_listbox_titles)
        else:
            frame = FrameCls(app.editor_container, section, app.refresh_listbox_titles, app.save_component)
        # Do NOT call pack() or grid() on frame here; let replace_editor_frame handle it
        app.replace_editor_frame(frame)
        print(f"[DEBUG] Editor frame replaced for section {idx}")
    except Exception as e:
        print(f"[ERROR] Could not build/replace editor frame: {e}")
    app.active_editor_index = idx

# --- Update Section Data ---
def update_section_data(app, updated):
    if hasattr(app, 'active_editor_index') and app.active_editor_index is not None:
        app.sections_data[app.active_editor_index].update(updated)
        if hasattr(app, 'update_preview'):
            app.update_preview()

# --- Refresh Listbox Titles ---
def refresh_listbox_titles(app, event=None):
    sel = app.section_listbox.curselection()
    app.section_listbox.delete(0, tk.END)
    for i, sec in enumerate(app.sections_data):
        title = sec.get('title', 'Untitled')
        app.section_listbox.insert(tk.END, f"{i+1}. {title}")
