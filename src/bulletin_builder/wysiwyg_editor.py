import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
from datetime import datetime

from .image_utils import optimize_image


class HistoryAction(dict):
    """Simple dict subclass for typing convenience."""
    pass

class WysiwygEditor(ctk.CTkToplevel):
    """Simple drag-and-drop WYSIWYG bulletin editor."""
    def __init__(self, master=None):
        super().__init__(master)
        self.title("WYSIWYG Editor")
        self.geometry("800x600")

        # Keyboard shortcuts
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-y>", lambda e: self.redo())
        self.bind("<Control-e>", lambda e: self.export_html())

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        sidebar = ctk.CTkFrame(self)
        sidebar.pack(side="right", fill="y", padx=5, pady=5)

        toolbar = ctk.CTkFrame(sidebar)
        toolbar.pack(fill="x")
        ctk.CTkButton(toolbar, text="Add Text", command=self.add_text).pack(pady=5, fill="x")
        ctk.CTkButton(toolbar, text="Add Image", command=self.add_image).pack(pady=5, fill="x")
        ctk.CTkButton(toolbar, text="Add Button", command=self.add_button).pack(pady=5, fill="x")
        ctk.CTkButton(toolbar, text="Undo", command=self.undo).pack(pady=(20,5), fill="x")
        ctk.CTkButton(toolbar, text="Redo", command=self.redo).pack(pady=5, fill="x")
        ctk.CTkButton(toolbar, text="Export HTML", command=self.export_html).pack(pady=(20,0), fill="x")

        ctk.CTkLabel(sidebar, text="Changelog").pack(pady=(10,0))
        self.changelog = tk.Listbox(
            sidebar,
            bg="#2B2B2B",
            fg="white",
            selectbackground="#1F6AA5",
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            height=15,
        )
        self.changelog.pack(fill="both", expand=True, padx=5, pady=(5,0))

        self._item_data = {}  # map canvas id -> (type, data)
        self._drag_data = {"item": None, "x": 0, "y": 0, "start": (0, 0)}
        self._images = {}  # keep PhotoImage refs
        self._history = []
        self._redo_stack = []

    def _record_action(self, action: HistoryAction):
        """Push an action onto the history stack and clear redo."""
        self._history.append(action)
        self._redo_stack.clear()
        self._add_log(self._describe_action(action))

    def _describe_action(self, action: HistoryAction) -> str:
        t = action.get("type")
        if t == "create":
            return f"Added {action.get('item_type', 'item')}"
        if t == "move":
            return "Moved item"
        return t or "action"

    def _add_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.changelog.insert(tk.END, f"{timestamp} - {message}")
        self.changelog.yview_moveto(1)

    def undo(self):
        if not self._history:
            return
        action = self._history.pop()
        if action.get("type") == "create":
            item = action["item"]
            self.canvas.delete(item)
            self._item_data.pop(item, None)
            self._images.pop(item, None)
        elif action.get("type") == "move":
            self.canvas.coords(action["item"], action["old"])
        self._redo_stack.append(action)
        self._add_log("Undo " + self._describe_action(action))

    def redo(self):
        if not self._redo_stack:
            return
        action = self._redo_stack.pop()
        if action.get("type") == "create":
            item_type = action["item_type"]
            data = action["data"]
            x, y = action["coords"]
            if item_type == "text":
                item = self.canvas.create_text(x, y, text=data, anchor="nw", font=("Arial", 14))
                self._item_data[item] = ("text", data)
            elif item_type == "image":
                try:
                    pil_img = Image.open(data)
                    img = ImageTk.PhotoImage(pil_img)
                except Exception:
                    return
                item = self.canvas.create_image(x, y, image=img, anchor="nw")
                self._images[item] = img
                self._item_data[item] = ("image", data)
            elif item_type == "button":
                btn = ctk.CTkButton(self.canvas, text=data)
                item = self.canvas.create_window(x, y, window=btn, anchor="nw")
                self._item_data[item] = ("button", data)
            self._make_draggable(item)
            action["item"] = item
        elif action.get("type") == "move":
            self.canvas.coords(action["item"], action["new"])
        self._history.append(action)
        self._add_log("Redo " + self._describe_action(action))

    # --- Drag helpers ---
    def _make_draggable(self, item):
        self.canvas.tag_bind(item, "<ButtonPress-1>", self._on_drag_start)
        self.canvas.tag_bind(item, "<B1-Motion>", self._on_drag_move)
        self.canvas.tag_bind(item, "<ButtonRelease-1>", self._on_drag_end)

    def _on_drag_start(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["item"] = item
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        # store initial coords for history
        self._drag_data["start"] = tuple(self.canvas.coords(item)[:2])

    def _on_drag_move(self, event):
        item = self._drag_data.get("item")
        if item is None:
            return
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self.canvas.move(item, dx, dy)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag_end(self, event):
        item = self._drag_data.get("item")
        if not item:
            return
        start = self._drag_data.get("start")
        end = tuple(self.canvas.coords(item)[:2])
        if start != end:
            action = HistoryAction(type="move", item=item, old=start, new=end)
            self._record_action(action)
        self._drag_data = {"item": None, "x": 0, "y": 0, "start": (0, 0)}

    # --- Block creators ---
    def add_text(self):
        text = simpledialog.askstring("Text", "Enter text:", parent=self)
        if text:
            item = self.canvas.create_text(50, 50, text=text, anchor="nw", font=("Arial", 14))
            self._item_data[item] = ("text", text)
            self._make_draggable(item)
            action = HistoryAction(type="create", item=item, item_type="text", data=text, coords=(50, 50))
            self._record_action(action)

    def add_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
        if path:
            opt_path = optimize_image(path)
            try:
                pil_img = Image.open(opt_path)
                img = ImageTk.PhotoImage(pil_img)
            except Exception:
                return
            item = self.canvas.create_image(50, 50, image=img, anchor="nw")
            self._images[item] = img
            self._item_data[item] = ("image", opt_path)
            self._make_draggable(item)
            action = HistoryAction(type="create", item=item, item_type="image", data=opt_path, coords=(50, 50))
            self._record_action(action)

    def add_button(self):
        label = simpledialog.askstring("Button Label", "Enter button label:", parent=self)
        if label:
            btn = ctk.CTkButton(self.canvas, text=label)
            item = self.canvas.create_window(50, 50, window=btn, anchor="nw")
            self._item_data[item] = ("button", label)
            self._make_draggable(item)
            action = HistoryAction(type="create", item=item, item_type="button", data=label, coords=(50, 50))
            self._record_action(action)

    # --- Export ---
    def export_html(self):
        html_lines = ["<html><body style='position:relative;'>"]
        for item, data in self._item_data.items():
            x, y = self.canvas.coords(item)[:2]
            if data[0] == "text":
                html_lines.append(f"<div style='position:absolute; left:{int(x)}px; top:{int(y)}px;'>{data[1]}</div>")
            elif data[0] == "image":
                html_lines.append(f"<img src='{data[1]}' style='position:absolute; left:{int(x)}px; top:{int(y)}px;'>")
            elif data[0] == "button":
                html_lines.append(f"<button style='position:absolute; left:{int(x)}px; top:{int(y)}px;'>{data[1]}</button>")
        html_lines.append("</body></html>")
        path = filedialog.asksaveasfilename(defaultextension='.html', filetypes=[('HTML','*.html')])
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("\n".join(html_lines))

def launch_gui():
    import os
    from .__main__ import BulletinBuilderApp

    # ✅ Ensure required folders exist
    for d in [
        'templates/partials',
        'templates/themes',
        'user_drafts',
        'assets'
    ]:
        os.makedirs(d, exist_ok=True)

    # ✅ Launch the real builder
    app = BulletinBuilderApp()
    app.mainloop()
