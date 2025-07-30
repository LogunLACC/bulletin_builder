import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, simpledialog

class WysiwygEditor(ctk.CTkToplevel):
    """Simple drag-and-drop WYSIWYG bulletin editor."""
    def __init__(self, master=None):
        super().__init__(master)
        self.title("WYSIWYG Editor")
        self.geometry("800x600")

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        toolbar = ctk.CTkFrame(self)
        toolbar.pack(side="right", fill="y", padx=5, pady=5)
        ctk.CTkButton(toolbar, text="Add Text", command=self.add_text).pack(pady=5, fill="x")
        ctk.CTkButton(toolbar, text="Add Image", command=self.add_image).pack(pady=5, fill="x")
        ctk.CTkButton(toolbar, text="Add Button", command=self.add_button).pack(pady=5, fill="x")
        ctk.CTkButton(toolbar, text="Export HTML", command=self.export_html).pack(pady=(20,0), fill="x")

        self._item_data = {}  # map canvas id -> (type, data)
        self._drag_data = {"item": None, "x": 0, "y": 0}
        self._images = {}  # keep PhotoImage refs

    # --- Drag helpers ---
    def _make_draggable(self, item):
        self.canvas.tag_bind(item, "<ButtonPress-1>", self._on_drag_start)
        self.canvas.tag_bind(item, "<B1-Motion>", self._on_drag_move)

    def _on_drag_start(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["item"] = item
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag_move(self, event):
        item = self._drag_data.get("item")
        if item is None:
            return
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self.canvas.move(item, dx, dy)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    # --- Block creators ---
    def add_text(self):
        text = simpledialog.askstring("Text", "Enter text:", parent=self)
        if text:
            item = self.canvas.create_text(50, 50, text=text, anchor="nw", font=("Arial", 14))
            self._item_data[item] = ("text", text)
            self._make_draggable(item)

    def add_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.gif")])
        if path:
            try:
                img = tk.PhotoImage(file=path)
            except Exception:
                return
            item = self.canvas.create_image(50, 50, image=img, anchor="nw")
            self._images[item] = img
            self._item_data[item] = ("image", path)
            self._make_draggable(item)

    def add_button(self):
        label = simpledialog.askstring("Button Label", "Enter button label:", parent=self)
        if label:
            btn = ctk.CTkButton(self.canvas, text=label)
            item = self.canvas.create_window(50, 50, window=btn, anchor="nw")
            self._item_data[item] = ("button", label)
            self._make_draggable(item)

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