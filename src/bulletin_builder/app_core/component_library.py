import json
from pathlib import Path
from tkinter import simpledialog, messagebox

from ..ui.component_library import ComponentLibrary

COMP_DIR = Path("components")


def init(app):
    """Attach component library helpers to the app."""

    def save_component(data: dict):
        COMP_DIR.mkdir(exist_ok=True)
        name = simpledialog.askstring("Save Component", "Component name:", parent=app)
        if not name:
            return
        path = COMP_DIR / f"{name}.json"
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            # messagebox.showinfo("Component Saved", f"Saved {path.name}", parent=app)
        except Exception as e:
            # messagebox.showerror("Save Error", str(e), parent=app)
            pass

    def insert_component(data: dict):
        app.sections_data.append(data)
        app.refresh_listbox_titles()
        app.show_placeholder()
        app.update_preview()

    def open_component_library():
        ComponentLibrary(app)

    app.save_component = save_component
    app.insert_component = insert_component
    app.open_component_library = open_component_library
