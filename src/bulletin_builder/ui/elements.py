from __future__ import annotations
import customtkinter as ctk
import tkinter as tk
from typing import Any, Dict

from .base_section import SectionRegistry


@SectionRegistry.register("elements")
class ElementsFrame(ctk.CTkFrame):
    """Editor for element-based sections: H1, H2, Paragraph, Image, Two/Three Column.

    Stores section.content as a list of dicts with keys:
      - type: 'h1'|'h2'|'p'|'img'|'row2'|'row3'
      - text, color, size (for text types)
      - src, alt (for images)
      - cells: list[dict] for row2/row3 with same text keys
    """
    def __init__(self, master, section=None, refresh_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.section: Dict[str, Any] = section or {"content": []}
        if not isinstance(self.section.get("content"), list):
            self.section["content"] = []
        self.refresh_callback = refresh_callback or (lambda: None)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Left: elements list
        self.listbox = tk.Listbox(self, activestyle="none", exportselection=False, height=12)
        self.listbox.grid(row=0, column=0, sticky="nsw", padx=(0, 8), pady=(0, 8))
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        # Simple drag-to-reorder
        self.listbox.bind('<Button-1>', self._on_press)
        self.listbox.bind('<B1-Motion>', self._on_drag)
        self.listbox.bind('<ButtonRelease-1>', self._on_release)
        self._drag_from = None

        # Right: editor panel
        editor = ctk.CTkFrame(self, fg_color="transparent")
        editor.grid(row=0, column=1, sticky="nsew")
        editor.grid_columnconfigure(1, weight=1)
        self._editor = editor

        # Toolbar
        bar = ctk.CTkFrame(editor, fg_color="transparent")
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        def btn(label, cmd, col):
            b = ctk.CTkButton(bar, text=label, command=cmd)
            b.grid(row=0, column=col, padx=4)
        btn("H1", lambda: self._add({"type": "h1", "text": "Heading 1", "size": 24, "color": "#103040"}), 0)
        btn("H2", lambda: self._add({"type": "h2", "text": "Heading 2", "size": 20, "color": "#103040"}), 1)
        btn("Paragraph", lambda: self._add({"type": "p", "text": "Paragraph text.", "size": 16, "color": "#506070"}), 2)
        btn("Image", lambda: self._add({"type": "img", "src": "https://placehold.co/600x300", "alt": "Image"}), 3)
        btn("Two-Column", lambda: self._add({"type": "row2", "cells": [{"text": "Left"}, {"text": "Right"}]}), 4)
        btn("Three-Column", lambda: self._add({"type": "row3", "cells": [{"text": "One"}, {"text": "Two"}, {"text": "Three"}]}), 5)

        # Up/Down/Duplicate/Delete
        bar2 = ctk.CTkFrame(editor, fg_color="transparent")
        bar2.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        ctk.CTkButton(bar2, text="Up", command=lambda: self._move(-1)).grid(row=0, column=0, padx=4)
        ctk.CTkButton(bar2, text="Down", command=lambda: self._move(+1)).grid(row=0, column=1, padx=4)
        ctk.CTkButton(bar2, text="Duplicate", command=self._dup).grid(row=0, column=2, padx=4)
        ctk.CTkButton(bar2, text="Delete", command=self._del).grid(row=0, column=3, padx=4)

        # Form fields
        r = 2
        ctk.CTkLabel(editor, text="Type:").grid(row=r, column=0, sticky="e")
        self.type_var = tk.StringVar()
        self.type_entry = ctk.CTkEntry(editor, textvariable=self.type_var)
        self.type_entry.grid(row=r, column=1, sticky="ew")
        r += 1
        ctk.CTkLabel(editor, text="Text:").grid(row=r, column=0, sticky="e")
        self.text_entry = ctk.CTkEntry(editor)
        self.text_entry.grid(row=r, column=1, sticky="ew")
        r += 1
        ctk.CTkLabel(editor, text="Color:").grid(row=r, column=0, sticky="e")
        self.color_entry = ctk.CTkEntry(editor)
        self.color_entry.grid(row=r, column=1, sticky="ew")
        r += 1
        ctk.CTkLabel(editor, text="Size:").grid(row=r, column=0, sticky="e")
        self.size_entry = ctk.CTkEntry(editor)
        self.size_entry.grid(row=r, column=1, sticky="ew")
        r += 1
        ctk.CTkLabel(editor, text="Image URL:").grid(row=r, column=0, sticky="e")
        self.src_entry = ctk.CTkEntry(editor)
        self.src_entry.grid(row=r, column=1, sticky="ew")
        r += 1
        ctk.CTkLabel(editor, text="Alt Text:").grid(row=r, column=0, sticky="e")
        self.alt_entry = ctk.CTkEntry(editor)
        self.alt_entry.grid(row=r, column=1, sticky="ew")
        r += 1

        ctk.CTkButton(editor, text="Save Element", command=self._save_current).grid(row=r, column=1, sticky="e", pady=(6, 0))

        self._refresh_list()

    # --- Toolbar actions ---
    def _add(self, item: Dict[str, Any]):
        self.section["content"].append(item)
        self._refresh_list(select=len(self.section["content"]) - 1)
        self._save_section()

    def _move(self, delta: int):
        sel = self._selected_index()
        if sel is None:
            return
        idx = sel + delta
        if not (0 <= idx < len(self.section["content"])):
            return
        a = self.section["content"]
        a[sel], a[idx] = a[idx], a[sel]
        self._refresh_list(select=idx)
        self._save_section()

    def _dup(self):
        sel = self._selected_index()
        if sel is None:
            return
        item = dict(self.section["content"][sel])
        self.section["content"].insert(sel + 1, item)
        self._refresh_list(select=sel + 1)
        self._save_section()

    def _del(self):
        sel = self._selected_index()
        if sel is None:
            return
        del self.section["content"][sel]
        self._refresh_list(select=min(sel, len(self.section["content"]) - 1))
        self._save_section()

    # --- Listbox and form ---
    def _selected_index(self) -> int | None:
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    def _refresh_list(self, select: int | None = None):
        self.listbox.delete(0, "end")
        for item in self.section["content"]:
            label = item.get("type", "?").upper()
            if item.get("type") in ("h1", "h2", "p"):
                t = item.get("text", "").strip()
                if t:
                    label += f": {t[:24]}"
            elif item.get("type") == "img":
                label += " (image)"
            elif item.get("type") in ("row2", "row3"):
                label += " (columns)"
            self.listbox.insert("end", label)
        if select is not None and 0 <= select < self.listbox.size():
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(select)
            self.listbox.activate(select)
            self._load_into_editor(select)

    def _on_select(self, _=None):
        idx = self._selected_index()
        if idx is None:
            return
        self._load_into_editor(idx)

    def _load_into_editor(self, idx: int):
        item = self.section["content"][idx]
        self.type_var.set(item.get("type", ""))
        self.text_entry.delete(0, "end"); self.text_entry.insert(0, item.get("text", ""))
        self.color_entry.delete(0, "end"); self.color_entry.insert(0, item.get("color", ""))
        self.size_entry.delete(0, "end"); self.size_entry.insert(0, str(item.get("size", "")))
        self.src_entry.delete(0, "end"); self.src_entry.insert(0, item.get("src", ""))
        self.alt_entry.delete(0, "end"); self.alt_entry.insert(0, item.get("alt", ""))

    def _save_current(self):
        idx = self._selected_index()
        if idx is None:
            return
        item = self.section["content"][idx]
        item["type"] = self.type_var.get().strip().lower() or item.get("type", "p")
        if item["type"] in ("h1", "h2", "p"):
            item["text"] = self.text_entry.get()
            item["color"] = self.color_entry.get() or item.get("color", "#506070")
            try:
                item["size"] = int(self.size_entry.get())
            except Exception:
                item["size"] = item.get("size", 16)
        elif item["type"] == "img":
            item["src"] = self.src_entry.get()
            item["alt"] = self.alt_entry.get()
        self._refresh_list(select=idx)
        self._save_section()

    def _save_section(self):
        try:
            app = self.winfo_toplevel()
            if hasattr(app, "update_section_data"):
                app.update_section_data({"content": self.section["content"]})
            if callable(self.refresh_callback):
                self.refresh_callback()
        except Exception:
            pass

    # --- Drag reorder helpers ---
    def _on_press(self, event):
        self._drag_from = self.listbox.nearest(event.y)

    def _on_drag(self, event):
        idx = self.listbox.nearest(event.y)
        if 0 <= idx < self.listbox.size():
            self.listbox.selection_clear(0, 'end')
            self.listbox.selection_set(idx)
            self.listbox.activate(idx)

    def _on_release(self, event):
        if self._drag_from is None:
            return
        to = self.listbox.nearest(event.y)
        frm = self._drag_from
        self._drag_from = None
        if to == frm or not (0 <= to < len(self.section["content"])):
            return
        a = self.section["content"]
        item = a.pop(frm)
        a.insert(to, item)
        self._refresh_list(select=to)
        self._save_section()

