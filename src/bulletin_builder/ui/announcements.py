# ui/announcements.py
from __future__ import annotations
import tkinter as tk
import customtkinter as ctk
from typing import Callable, Dict, List, Optional, Any
from bulletin_builder.ui.base_section import SectionRegistry

Announcement = Dict[str, Any]

def _safe_title(a: Announcement) -> str:
    t = (a.get("title") or "").strip()
    return t if t else "(untitled)"

@SectionRegistry.register("announcements")
class AnnouncementsFrame(ctk.CTkFrame):
    LAYOUT_BREAKPOINT = 1200  # px; adjust to taste

    def _apply_layout(self, mode: str):
        # Remove any prior grid placements
        for w in (self._list_panel, self._editor_panel, self._controls):
            try:
                w.grid_forget()
            except Exception:
                pass

        # Reset weights
        for r in range(0, 4):
            self.grid_rowconfigure(r, weight=0)
        for c in range(0, 3):
            self.grid_columnconfigure(c, weight=0)

        if mode == "stacked":
            # One column: [list] / [editor] / [controls]
            self.grid_columnconfigure(0, weight=1)   # single column grows
            self._list_panel.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8,4))
            self._editor_panel.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4,4))
            self._controls.grid(row=2, column=0, sticky="ew",  padx=8, pady=(4,8))
            # list grows a bit; editor grows more
            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=2)
        else:
            # Two columns: [list | editor] + [controls]
            self.grid_columnconfigure(0, weight=1, minsize=280)  # list
            self.grid_columnconfigure(1, weight=2, minsize=420)  # editor
            self._list_panel.grid(row=0, column=0, sticky="nsew", padx=(8,6), pady=(8,4))
            self._editor_panel.grid(row=0, column=1, sticky="nsew", padx=(0,12), pady=(8,4))
            self._controls.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(8,12), pady=(4,8))
            self.grid_rowconfigure(0, weight=1)

        self._layout_mode = mode

    def _on_resize(self, event=None):
        try:
            w = self.winfo_width()
        except Exception:
            return
        desired = "stacked" if w < self.LAYOUT_BREAKPOINT else "wide"
        if getattr(self, "_layout_mode", None) != desired:
            self._apply_layout(desired)
    """
    Editor for an Announcements section whose `section["content"]` is a list of:
        { "title": str, "body": str, "link": str, "link_text": str }
    """
    def __init__(self, master, section=None, section_data=None, on_dirty=None, **kwargs):
        # --- absorb router-passed custom args that may come through kwargs ---
        section = kwargs.pop("section", section)
        section_data = kwargs.pop("section_data", section_data)
        on_dirty = kwargs.pop("on_dirty", on_dirty)

        if section is None and section_data is not None:
            section = section_data

        self.on_dirty = on_dirty or (lambda: None)

        # init the CTkFrame now that kwargs are clean
        super().__init__(master, **kwargs)

        # --- build ALL UI here (panels, self.items_list, entries, self.body_text, buttons) ---
        self.section = None
        self.announcements = []
        self.current_index = None

        # Panels
        self._list_panel = ctk.CTkFrame(self)
        self._editor_panel = ctk.CTkFrame(self)
        self._controls = ctk.CTkFrame(self, fg_color="transparent")

        # Outer grid: [ list | editor ]
        self.grid_columnconfigure(0, weight=1, minsize=280)      # list column
        self.grid_columnconfigure(1, weight=2, minsize=420)      # editor column
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # Place the panels
        self._list_panel.grid(row=0, column=0, sticky="nsew", padx=(8,6), pady=(8,4))
        self._editor_panel.grid(row=0, column=1, sticky="nsew", padx=(0,12), pady=(8,4))
        self._controls.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(8,12), pady=(4,8))

        # Editor fields stretch properly
        ep = self._editor_panel
        ep.grid_columnconfigure(0, weight=0, minsize=80)         # labels
        ep.grid_columnconfigure(1, weight=1, minsize=340)        # inputs
        ep.grid_rowconfigure(3, weight=1)                        # Body grows


        # Now build the rest of the UI into these panels (move existing widget creation here)
        self._build_ui()

        # Responsive layout: bind resize event and set initial layout
        self.bind("<Configure>", self._on_resize)
        self._on_resize()

        # after widgets exist, resolve + load section safely
        if not isinstance(section, dict):
            try:
                section = self._resolve_active_section_safely()
            except Exception:
                section = None
        if not isinstance(section, dict):
            try:
                section = self._resolve_via_dynamic_importer()
            except Exception:
                section = None

        try:
            print("[DEBUG] AnnouncementsFrame __init__: section resolved?",
                  isinstance(section, dict),
                  "keys:", list(section.keys()) if isinstance(section, dict) else None)
        except Exception:
            pass

        if isinstance(section, dict):
            self.set_section(section)

    # ---------- Public API ----------
    def set_section(self, section: dict):
        self.section = section or {}
        content = self.section.get("content") or []
        # Normalize: list of items with title/body/link/link_text
        self.announcements = list(content)
        self._refresh_list(select=0 if self.announcements else None)
        if self.announcements:
            self.items_list.selection_set(0)
            self.items_list.activate(0)
            self._load_into_editor(0)
        else:
            app = self.winfo_toplevel()
            if hasattr(app, "show_status_message"):
                app.show_status_message("Announcements: 0 items (import or add new).")

    def get_content(self) -> List[Announcement]:
        """Return the edited announcements list (write back to section['content'])."""
        self._save_current_if_any()
        return self.announcements

    # ---------- UI wiring ----------
    def _build_ui(self):
        # --- Parent grid (Content page) ---
        parent = self  # AnnouncementsFrame is the parent for left + right
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=0)                 # left nav fixed
        parent.grid_columnconfigure(1, weight=1)                 # editor grows

        # Left navigation container
        self.sections_container = ctk.CTkFrame(parent)
        self.sections_container.grid(row=0, column=0, sticky="nsew", padx=(12,8), pady=(8,8))
        # Give the left column a sane width but don't overgrow
        parent.grid_columnconfigure(0, minsize=360)
        self.sections_container.grid_rowconfigure(1, weight=1)

        header = ctk.CTkLabel(self.sections_container, text="Announcements", font=ctk.CTkFont(size=14, weight="bold"))
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        self.items_list = tk.Listbox(self.sections_container, activestyle="none", exportselection=False, height=12)
        self.items_list.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.items_list.bind("<<ListboxSelect>>", self._on_select)

        btns = ctk.CTkFrame(self.sections_container)
        btns.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        for i in range(4):
            btns.grid_columnconfigure(i, weight=1)

        self.btn_add = ctk.CTkButton(btns, text="+ Add", command=self._add_item)
        self.btn_del = ctk.CTkButton(btns, text="Delete", command=self._delete_item)
        self.btn_up  = ctk.CTkButton(btns, text="↑ Up", command=lambda: self._move_item(-1))
        self.btn_dn  = ctk.CTkButton(btns, text="↓ Down", command=lambda: self._move_item(1))
        self.btn_add.grid(row=0, column=0, padx=2)
        self.btn_del.grid(row=0, column=1, padx=2)
        self.btn_up.grid(row=0, column=2, padx=2)
        self.btn_dn.grid(row=0, column=3, padx=2)

        self.count_label = ctk.CTkLabel(self.sections_container, text="", text_color="gray")
        self.count_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6,0))

        # Editor container (this is where AnnouncementsFrame lives)
        self.editor_container = ctk.CTkFrame(parent)
        self.editor_container.grid(row=0, column=1, sticky="nsew", padx=(0,12), pady=(8,8))
        for r in range(8):
            self.editor_container.grid_rowconfigure(r, weight=0)
        self.editor_container.grid_rowconfigure(7, weight=1)  # text expands
        self.editor_container.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.editor_container, text="Title").grid(row=0, column=0, sticky="w", pady=(0,4))
        self.title_entry = ctk.CTkEntry(self.editor_container)
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=(0,8))

        ctk.CTkLabel(self.editor_container, text="Link Text").grid(row=1, column=0, sticky="w", pady=(0,4))
        self.link_text_entry = ctk.CTkEntry(self.editor_container)
        self.link_text_entry.grid(row=1, column=1, sticky="ew", pady=(0,8))

        ctk.CTkLabel(self.editor_container, text="Link URL").grid(row=2, column=0, sticky="w", pady=(0,4))
        self.link_entry = ctk.CTkEntry(self.editor_container)
        self.link_entry.grid(row=2, column=1, sticky="ew", pady=(0,8))

        ctk.CTkLabel(self.editor_container, text="Body").grid(row=3, column=0, sticky="w", pady=(0,4))
        self.body_text = ctk.CTkTextbox(self.editor_container, height=220)
        self.body_text.grid(row=3, column=1, rowspan=4, sticky="nsew")


    # ---------- List management ----------
    def _refresh_list(self, select=None):
        if not hasattr(self, "items_list"):
            return  # widgets not built yet
        self.items_list.delete(0, "end")
        for i, item in enumerate(self.announcements):
            title = str(item.get("title", "")).strip()
            if not title:
                title = f"Item {i+1}"
            self.items_list.insert("end", title)
        if select is not None and self.announcements:
            self.items_list.selection_clear(0, "end")
            self.items_list.selection_set(select)
            self.items_list.activate(select)
            self._load_into_editor(select)
        else:
            self._clear_editor()

    def _on_select(self, event=None):
        try:
            sel = self.items_list.curselection()
            if sel:
                self._load_into_editor(sel[0])
            else:
                self._clear_editor()
        except Exception as e:
            print("[DEBUG] _on_select error:", e)

    def _on_field_change(self, key):
        sel = self.items_list.curselection()
        if not sel: return
        idx = sel[0]
        item = self.announcements[idx]
        if key == "title":
            item["title"] = self.title_entry.get().strip()
            # keep list title in sync
            title = item["title"] if item["title"] else f"Item {idx+1}"
            self.items_list.delete(idx)
            self.items_list.insert(idx, title)
            self.items_list.selection_set(idx)
        elif key == "link_text":
            item["link_text"] = self.link_text_entry.get().strip()
        elif key == "link":
            item["link"] = self.link_entry.get().strip()
        if hasattr(self, "on_dirty"): self.on_dirty()

    def _on_body_change(self, event=None):
        # CTkTextbox uses a 'modified' flag; clear it to avoid loops
        try:
            if self.body_text.edit_modified():
                sel = self.items_list.curselection()
                if sel:
                    idx = sel[0]
                    self.announcements[idx]["body"] = self.body_text.get("1.0", "end-1c")
                    if hasattr(self, "on_dirty"): self.on_dirty()
                self.body_text.edit_modified(False)
        except Exception:
            pass

    def _load_index(self, idx: int) -> None:
        self.current_index = idx
        a = self.announcements[idx]
        self.title_entry.delete(0, tk.END); self.title_entry.insert(0, a.get("title", ""))
        self.link_text_entry.delete(0, tk.END); self.link_text_entry.insert(0, a.get("link_text", ""))
        self.link_entry.delete(0, tk.END); self.link_entry.insert(0, a.get("link", ""))
        self.body_text.delete("1.0", tk.END); self.body_text.insert("1.0", a.get("body", ""))
        self._set_editor_enabled(True)

    def _load_into_editor(self, idx):
        item = self.announcements[idx]
        self.title_entry.delete(0, "end"); self.title_entry.insert(0, item.get("title",""))
        self.link_text_entry.delete(0, "end"); self.link_text_entry.insert(0, item.get("link_text",""))
        self.link_entry.delete(0, "end"); self.link_entry.insert(0, item.get("link",""))
        self.body_text.delete("1.0", "end"); self.body_text.insert("1.0", item.get("body",""))

    def _clear_editor(self):
        self.title_entry.delete(0, "end")
        self.link_text_entry.delete(0, "end")
        self.link_entry.delete(0, "end")
        self.body_text.delete("1.0", "end")

    def _set_editor_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for w in (self.title_entry, self.link_text_entry, self.link_entry, self.body_text, self.btn_save, self.btn_revert):
            try:
                w.configure(state=state)
            except tk.TclError:
                w.configure(state=state)

    def _add_item(self):
        self._save_current_if_any()
        self.announcements.append({"title": "", "body": "", "link": "", "link_text": ""})
        self._notify_dirty()
        self._refresh_list(select=len(self.announcements)-1)

    def _delete_item(self):
        if self.current_index is None:
            return
        del self.announcements[self.current_index]
        self._notify_dirty()
        new_idx = min(self.current_index, len(self.announcements)-1) if self.announcements else None
        self._refresh_list(select=new_idx)

    def _move_item(self, delta: int):
        if self.current_index is None:
            return
        i = self.current_index
        j = i + delta
        if j < 0 or j >= len(self.announcements):
            return
        self.announcements[i], self.announcements[j] = self.announcements[j], self.announcements[i]
        self._notify_dirty()
        self._refresh_list(select=j)

    # ---------- Save/Revert ----------
    def _save_current_if_any(self):
        if self.current_index is None:
            return
        a = self.announcements[self.current_index]
        a["title"] = self.title_entry.get().strip()
        a["link_text"] = self.link_text_entry.get().strip()
        a["link"] = self.link_entry.get().strip()
        a["body"] = self.body_text.get("1.0", tk.END).rstrip()
        # Update list title
        self.items_list.delete(self.current_index)
        self.items_list.insert(self.current_index, _safe_title(a))
        self._notify_dirty()

    def _revert_current(self):
        if self.current_index is None:
            return
        self._load_index(self.current_index)

    def _notify_dirty(self):
        if self.on_dirty:
            try:
                self.on_dirty()
            except Exception:
                pass

    def _resolve_active_section_safely(self):
        """Best-effort lookup of the currently selected 'announcements' section from the app."""
        try:
            app = self.winfo_toplevel()
        except Exception:
            app = None

        # 1) If the app exposes a getter, use it
        try:
            if app and hasattr(app, "get_active_section"):
                s = app.get_active_section()
                if isinstance(s, dict) and s.get("type") == "announcements":
                    return s
        except Exception:
            pass

        # 2) Try app.current_section_index → app.sections_data[index]
        try:
            if app and hasattr(app, "current_section_index") and hasattr(app, "sections_data"):
                idx = getattr(app, "current_section_index")
                if isinstance(idx, int) and 0 <= idx < len(app.sections_data):
                    s = app.sections_data[idx]
                    if isinstance(s, dict) and s.get("type") == "announcements":
                        return s
        except Exception:
            pass

        # 3) Try listbox selection in the content pane
        try:
            # Common names used in the app; guard each access
            lb = getattr(app, "sections_listbox", None) or getattr(app, "sections_list", None)
            data = getattr(app, "sections_data", None)
            if lb and data:
                sel = lb.curselection()
                if sel:
                    s = data[sel[0]]
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
                    section = _imp_app._last_announcements_section
                    print("[DEBUG] AnnouncementsFrame: loaded via dynamic importer fallback")
                    return section
        except Exception:
            pass
        return None
