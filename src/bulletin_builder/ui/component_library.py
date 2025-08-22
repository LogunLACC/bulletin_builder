import json
from pathlib import Path
import tkinter as tk
import customtkinter as ctk

COMP_DIR = Path("components")


class ComponentLibrary(ctk.CTkToplevel):
    """Simple list of saved components that can be inserted."""

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Component Library")
        self.geometry("400x400")
        self.transient(app)
        self.grab_set()

        self.listbox = tk.Listbox(
            self,
            bg="#2B2B2B",
            fg="white",
            selectbackground="#1F6AA5",
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
        )
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Insert", command=self.insert_selected).pack(side="right")
        ctk.CTkButton(
            btn_frame,
            text="Close",
            command=self.destroy,
            fg_color="gray50",
            hover_color="gray40",
        ).pack(side="right", padx=(0, 10))

        self._paths = []
        self.load_components()

    def load_components(self):
        self.listbox.delete(0, tk.END)
        self._paths = []
        if not COMP_DIR.exists():
            return
        for path in sorted(COMP_DIR.glob("*.json")):
            self.listbox.insert(tk.END, path.stem)
            self._paths.append(path)
    # In-memory cache for loaded component JSON files
    _component_cache = {}

    def load_components(self):
        self.listbox.delete(0, tk.END)
        self._paths = []
        if not COMP_DIR.exists():
            return
        for path in sorted(COMP_DIR.glob("*.json")):
            self.listbox.insert(tk.END, path.stem)
            self._paths.append(path)
    def insert_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        path = self._paths[sel[0]]
        cache = self._component_cache
        if path in cache:
            data = cache[path]
        else:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                cache[path] = data
                # LRU: pop oldest if over 32
                if len(cache) > 32:
                    cache.pop(next(iter(cache)))
            except Exception:
                return
        self.app.insert_component(data)
        self.destroy()
