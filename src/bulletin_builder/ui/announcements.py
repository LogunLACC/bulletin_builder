from __future__ import annotations

import tkinter as tk
import customtkinter as ctk
from typing import Any, Dict, List

from bulletin_builder.ui.base_section import SectionRegistry


@SectionRegistry.register("announcements")
class AnnouncementsFrame(ctk.CTkFrame):
    """Minimal, well-formed announcements editor focused on persistence."""

    def __init__(self, master, section=None, section_data=None, on_dirty=None, **kwargs):
        section = kwargs.pop("section", section)
        section_data = kwargs.pop("section_data", section_data)
        on_dirty = kwargs.pop("on_dirty", on_dirty)
        if section is None and section_data is not None:
            section = section_data
        self.on_dirty = on_dirty or (lambda: None)
        super().__init__(master, **kwargs)

        self.section: Dict[str, Any] | None = None
        self.announcements: List[Dict[str, Any]] = []
        self.current_index: int | None = None

        self.items_list = tk.Listbox(self, activestyle="none", exportselection=False, height=10)
        self.items_list.pack(side="left", fill="y", padx=6, pady=6)
        self.items_list.bind("<<ListboxSelect>>", self._on_select)

        right = ctk.CTkFrame(self)
        right.pack(side="left", fill="both", expand=True, padx=6, pady=6)

        self.title_entry = ctk.CTkEntry(right, placeholder_text="Announcement title…")
        self.title_entry.pack(fill="x", pady=(0, 4))

        # Optional link text + URL
        self.link_text_entry = ctk.CTkEntry(right, placeholder_text="Link title (optional)…")
        self.link_text_entry.pack(fill="x", pady=(0, 4))
        self.link_url_entry = ctk.CTkEntry(right, placeholder_text="https://example.com (optional)…")
        self.link_url_entry.pack(fill="x", pady=(0, 6))

        try:
            self.body_text = ctk.CTkTextbox(right, height=120, placeholder_text="Body (supports simple text)…")
        except Exception:
            # Older CustomTkinter versions may not support placeholder_text on CTkTextbox
            self.body_text = ctk.CTkTextbox(right, height=120)
        self.body_text.pack(fill="both", expand=True)

        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(4, 0))
        # Left-side controls
        ctk.CTkButton(btn_frame, text="+ Add", command=self._add_item).pack(side="left")
        ctk.CTkButton(btn_frame, text="Remove", command=self._delete_selected).pack(side="left", padx=(6, 0))
        ctk.CTkButton(btn_frame, text="↑ Up", width=70, command=lambda: self._move_selected(-1)).pack(side="left", padx=(6, 0))
        ctk.CTkButton(btn_frame, text="↓ Down", width=70, command=lambda: self._move_selected(1)).pack(side="left", padx=(6, 0))
        # Right-side control
        ctk.CTkButton(btn_frame, text="Save", command=self._save_current_if_any).pack(side="right")

        if isinstance(section, dict):
            self.set_section(section)
        # Ensure placeholders render immediately on first paint
        try:
            self.after(60, self._refresh_placeholders)
        except Exception:
            pass

    def set_section(self, section: Dict[str, Any]):
        self.section = section or {}
        content = self.section.get("content")
        if isinstance(content, list):
            ann = content
        elif isinstance(content, dict):
            try:
                keys = sorted(content.keys(), key=lambda x: int(x) if str(x).isdigit() else x)
                ann = [content[k] for k in keys]
            except Exception:
                ann = [content] if content else []
        elif content is None:
            ann = []
        else:
            try:
                ann = list(content)
            except Exception:
                ann = []

        norm: List[Dict[str, Any]] = []
        for x in ann:
            if isinstance(x, dict):
                norm.append({
                    "title": x.get("title", ""),
                    "body": x.get("body", ""),
                    "link": x.get("link", ""),
                    "link_text": x.get("link_text", ""),
                })
            else:
                norm.append({"title": str(x), "body": "", "link": "", "link_text": ""})
        self.announcements = norm
        self._refresh_list()

    def get_content(self) -> List[Dict[str, Any]]:
        self._save_current_if_any()
        return self.announcements

    def _refresh_list(self, select: int | None = None):
        self.items_list.delete(0, "end")
        for i, item in enumerate(self.announcements):
            title = (item.get("title") or "").strip() if isinstance(item, dict) else str(item)
            if not title:
                title = f"Item {i+1}"
            self.items_list.insert("end", title)
        if select is not None and self.announcements:
            self.items_list.selection_set(select)
            self._load_into_editor(select)
        else:
            self.current_index = None

    def _on_select(self, event=None):
        sel = self.items_list.curselection()
        if not sel:
            self.current_index = None
            return
        idx = sel[0]
        self._load_into_editor(idx)

    def _load_into_editor(self, idx: int):
        self.current_index = idx
        a = self.announcements[idx]
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, a.get("title", ""))
        try:
            self.link_text_entry.delete(0, "end")
            self.link_text_entry.insert(0, a.get("link_text", ""))
        except Exception:
            pass
        try:
            self.link_url_entry.delete(0, "end")
            self.link_url_entry.insert(0, a.get("link", ""))
        except Exception:
            pass
        try:
            self.body_text.delete("1.0", "end")
            self.body_text.insert("1.0", a.get("body", ""))
        except Exception:
            pass

    def _add_item(self):
        self._save_current_if_any()
        self.announcements.append({"title": "", "body": "", "link": "", "link_text": ""})
        self._refresh_list(select=len(self.announcements) - 1)

    def _save_current_if_any(self):
        if self.current_index is None:
            return
        a = self.announcements[self.current_index]
        a["title"] = self.title_entry.get().strip()
        try:
            a["body"] = self.body_text.get("1.0", "end-1c")
        except Exception:
            a["body"] = a.get("body", "")
        try:
            a["link_text"] = self.link_text_entry.get().strip()
        except Exception:
            a["link_text"] = a.get("link_text", "")
        try:
            a["link"] = self.link_url_entry.get().strip()
        except Exception:
            a["link"] = a.get("link", "")

        try:
            self.items_list.delete(self.current_index)
            self.items_list.insert(self.current_index, (a.get("title") or f"Item {self.current_index+1}"))
            self.items_list.selection_set(self.current_index)
        except Exception:
            pass

        try:
            app = self.winfo_toplevel()
            if app and hasattr(app, "update_section_data"):
                app.update_section_data({"content": self.announcements})
        except Exception:
            pass

        try:
            self.on_dirty()
        except Exception:
            pass

    def _refresh_placeholders(self):
        """Force placeholder drawing for empty fields on initial paint."+
        This works around a CustomTkinter quirk where placeholders sometimes
        don't render until a first focus change.
        """
        try:
            # Reconfigure with the same placeholder values to trigger redraw
            if hasattr(self.title_entry, "configure"):
                self.title_entry.configure(placeholder_text=self.title_entry.cget("placeholder_text"))
            if hasattr(self.link_text_entry, "configure"):
                self.link_text_entry.configure(placeholder_text=self.link_text_entry.cget("placeholder_text"))
            if hasattr(self.link_url_entry, "configure"):
                self.link_url_entry.configure(placeholder_text=self.link_url_entry.cget("placeholder_text"))
            if hasattr(self.body_text, "configure"):
                try:
                    self.body_text.configure(placeholder_text=self.body_text.cget("placeholder_text"))
                except Exception:
                    pass
        except Exception:
            pass

    def _delete_selected(self):
        if self.current_index is None:
            return
        idx = self.current_index
        # Remove item
        try:
            del self.announcements[idx]
        except Exception:
            return
        # Decide next selection
        if not self.announcements:
            self.current_index = None
            try:
                self.title_entry.delete(0, "end")
                self.body_text.delete("1.0", "end")
            except Exception:
                pass
            self._refresh_list()
        else:
            new_idx = min(idx, len(self.announcements) - 1)
            self._refresh_list(select=new_idx)
        # Notify app and mark dirty
        try:
            app = self.winfo_toplevel()
            if app and hasattr(app, "update_section_data"):
                app.update_section_data({"content": self.announcements})
        except Exception:
            pass
        self._notify_dirty()

    def _move_selected(self, delta: int):
        if self.current_index is None:
            return
        i = self.current_index
        j = i + int(delta)
        if j < 0 or j >= len(self.announcements):
            return
        # Save edits to current before swapping
        self._save_current_if_any()
        try:
            self.announcements[i], self.announcements[j] = self.announcements[j], self.announcements[i]
        except Exception:
            return
        self._refresh_list(select=j)
        # Notify app and mark dirty
        try:
            app = self.winfo_toplevel()
            if app and hasattr(app, "update_section_data"):
                app.update_section_data({"content": self.announcements})
        except Exception:
            pass
        self._notify_dirty()

    def _revert_current(self):
        if self.current_index is None:
            return
        try:
            content = (self.section or {}).get("content") if isinstance(self.section, dict) else None
            if isinstance(content, list) and len(content) > self.current_index:
                self.announcements[self.current_index] = dict(content[self.current_index])
                self._load_into_editor(self.current_index)
        except Exception:
            pass

    def _notify_dirty(self):
        try:
            self.on_dirty()
        except Exception:
            pass

    def _resolve_active_section_safely(self):
        try:
            app = self.winfo_toplevel()
        except Exception:
            app = None
        try:
            if app and hasattr(app, "get_active_section"):
                s = app.get_active_section()
                if isinstance(s, dict) and s.get("type") == "announcements":
                    return s
        except Exception:
            pass
        return None

    def _resolve_via_dynamic_importer(self):
        importer_mod = None
        for mod_name in ("importer", "bulletin_builder.importer", "app.importer"):
            try:
                importer_mod = __import__(mod_name, fromlist=["app"])
                break
            except Exception:
                continue
        try:
            if importer_mod and hasattr(importer_mod, "app"):
                _imp_app = getattr(importer_mod, "app")
                if hasattr(_imp_app, "_last_announcements_section"):
                    return _imp_app._last_announcements_section
        except Exception:
            pass
        return None
