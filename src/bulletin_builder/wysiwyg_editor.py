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
    def _copy_selected(self):
        item = getattr(self._context_menu, '_last_item', None)
        if item is None or item not in self._item_data:
            return
        typ, data = self._item_data[item]
        style = self._item_styles.get(item, {}).copy() if item in self._item_styles else {}
        coords = tuple(self.canvas.coords(item)[:2])
        self._clipboard = {
            'type': typ,
            'data': data,
            'style': style,
            'coords': coords
        }
        self._add_log(f"Copied {typ}")

    def _duplicate_selected(self):
        if not self._clipboard:
            # fallback: duplicate currently selected item
            item = getattr(self._context_menu, '_last_item', None)
            if item is None or item not in self._item_data:
                return
            typ, data = self._item_data[item]
            style = self._item_styles.get(item, {}).copy() if item in self._item_styles else {}
            coords = tuple(self.canvas.coords(item)[:2])
        else:
            typ = self._clipboard['type']
            data = self._clipboard['data']
            style = self._clipboard['style']
            coords = self._clipboard['coords']
        # Offset duplicate visually
        x, y = coords
        x += 30
        y += 30
        item2 = None
        if typ in ("h1", "h2", "paragraph", "text"):
            font = ("Arial", 28, "bold") if typ == "h1" else ("Arial", 20, "bold") if typ == "h2" else ("Arial", 14)
            item2 = self.canvas.create_text(x, y, text=data, anchor="nw", font=font)
        elif typ == "image":
            try:
                pil_img = Image.open(data)
                img = ImageTk.PhotoImage(pil_img)
                item2 = self.canvas.create_image(x, y, image=img, anchor="nw")
                self._images[item2] = img
            except Exception:
                return
        elif typ == "button":
            btn = ctk.CTkButton(self.canvas, text=data)
            item2 = self.canvas.create_window(x, y, window=btn, anchor="nw")
        elif typ == "2col":
            if data == "left":
                item2 = self.canvas.create_rectangle(x, y, x+200, y+150, outline="#1F6AA5", width=2, dash=(4,2))
                self._item_data[item2] = ("2col", "left")
            else:
                item2 = self.canvas.create_rectangle(x, y, x+200, y+150, outline="#1F6AA5", width=2, dash=(4,2))
                self._item_data[item2] = ("2col", "right")
        elif typ == "3col":
            item2 = self.canvas.create_rectangle(x, y, x+150, y+150, outline="#1F6AA5", width=2, dash=(4,2))
            self._item_data[item2] = ("3col", data)
        if item2 is not None:
            if typ not in ("2col", "3col"):
                self._item_data[item2] = (typ, data)
            if style:
                self._item_styles[item2] = style.copy()
            self._make_draggable(item2)
            action = HistoryAction(type="create", item=item2, item_type=typ, data=data, coords=(x, y))
            self._record_action(action)
            self._add_log(f"Duplicated {typ}")
    import concurrent.futures
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

    def __init__(self, master=None):
        super().__init__(master)
        self.title("WYSIWYG Editor")
        self.geometry("800x600")

        # Track which items are marked for TOC
        self._toc_items = set()
        # Track per-item styles
        self._item_styles = {}
        # Clipboard for copy/duplicate
        self._clipboard = None

        # Context menu for TOC, style, and element actions
        self._context_menu = tk.Menu(self, tearoff=0)
        self._context_menu.add_command(label="Add to TOC", command=self._toggle_toc_for_selected)
        self._context_menu.add_command(label="Style...", command=self._edit_style_for_selected)
        self._context_menu.add_separator()
        self._context_menu.add_command(label="Copy", command=self._copy_selected)
        self._context_menu.add_command(label="Duplicate", command=self._duplicate_selected)
        self._context_menu.add_command(label="Delete", command=self._delete_selected)

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-3>", self._on_right_click)

        sidebar = ctk.CTkFrame(self)
        sidebar.pack(side="right", fill="y", padx=5, pady=5)

        toolbar = ctk.CTkFrame(sidebar)
        toolbar.pack(fill="x")
        ctk.CTkLabel(toolbar, text="Add Elements").pack(pady=(0,2), fill="x")
        ctk.CTkButton(toolbar, text="H1 Heading", command=self.add_h1).pack(pady=2, fill="x")
        ctk.CTkButton(toolbar, text="H2 Heading", command=self.add_h2).pack(pady=2, fill="x")
        ctk.CTkButton(toolbar, text="Paragraph", command=self.add_paragraph).pack(pady=2, fill="x")
        ctk.CTkButton(toolbar, text="Image", command=self.add_image).pack(pady=2, fill="x")
        ctk.CTkButton(toolbar, text="2 Columns", command=self.add_two_column).pack(pady=2, fill="x")
        ctk.CTkButton(toolbar, text="3 Columns", command=self.add_three_column).pack(pady=2, fill="x")
        ctk.CTkLabel(toolbar, text="Other").pack(pady=(10,2), fill="x")
        ctk.CTkButton(toolbar, text="Button", command=self.add_button).pack(pady=2, fill="x")
        ctk.CTkButton(toolbar, text="Undo", command=self.undo).pack(pady=(20,2), fill="x")
        ctk.CTkButton(toolbar, text="Redo", command=self.redo).pack(pady=2, fill="x")
        ctk.CTkButton(toolbar, text="Export HTML", command=self.export_html).pack(pady=(20,0), fill="x")


        self._item_data = {}  # map canvas id -> (type, data)
        self._drag_data = {"item": None, "x": 0, "y": 0, "start": (0, 0)}
        self._images = {}  # keep PhotoImage refs
        self._history = []
        self._redo_stack = []

        # Keyboard shortcuts
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-y>", lambda e: self.redo())
        self.bind("<Control-e>", lambda e: self.export_html())

    def _delete_selected(self):
        item = getattr(self._context_menu, '_last_item', None)
        if item is None or item not in self._item_data:
            return
        self.canvas.delete(item)
        self._item_data.pop(item, None)
        self._item_styles.pop(item, None)
        self._toc_items.discard(item)
        self._images.pop(item, None)
        self._add_log("Deleted element")

    def _on_right_click(self, event):
        # Find the closest item and show context menu
        item = self.canvas.find_closest(event.x, event.y)
        if not item:
            return
        self._context_menu.entryconfig(0, label=("Remove from TOC" if item[0] in self._toc_items else "Add to TOC"))
        self._context_menu._last_item = item[0]
        self._context_menu.tk_popup(event.x_root, event.y_root)
    def _edit_style_for_selected(self):
        item = getattr(self._context_menu, '_last_item', None)
        if item is None or item not in self._item_data:
            return
        typ, _ = self._item_data[item]
        style = self._item_styles.get(item, {})
        # Only allow email-safe styles
        if typ in ("h1", "h2", "paragraph", "text"):
            font_size = simpledialog.askinteger("Font Size", "Font size (px):", initialvalue=style.get("font-size", 14), minvalue=8, maxvalue=48, parent=self)
            color = simpledialog.askstring("Font Color", "Font color (hex, e.g. #333333):", initialvalue=style.get("color", "#333333"), parent=self)
            bold = simpledialog.askstring("Bold? (yes/no)", "Bold? (yes/no):", initialvalue="yes" if style.get("font-weight") == "bold" else "no", parent=self)
            italic = simpledialog.askstring("Italic? (yes/no)", "Italic? (yes/no):", initialvalue="yes" if style.get("font-style") == "italic" else "no", parent=self)
            style = {
                "font-size": font_size,
                "color": color,
                "font-weight": "bold" if bold and bold.lower().startswith("y") else "normal",
                "font-style": "italic" if italic and italic.lower().startswith("y") else "normal",
            }
        elif typ == "image":
            width = simpledialog.askinteger("Width", "Image width (px):", initialvalue=style.get("width", 200), minvalue=20, maxvalue=1200, parent=self)
            height = simpledialog.askinteger("Height", "Image height (px):", initialvalue=style.get("height", 200), minvalue=20, maxvalue=1200, parent=self)
            style = {"width": width, "height": height}
        elif typ in ("2col", "3col"):
            border = simpledialog.askstring("Border Style", "Border CSS (e.g. 2px dashed #1F6AA5):", initialvalue=style.get("border", "2px dashed #1F6AA5"), parent=self)
            bgcolor = simpledialog.askstring("Background Color", "Background color (hex, e.g. #ffffff):", initialvalue=style.get("background-color", "#ffffff"), parent=self)
            style = {"border": border, "background-color": bgcolor}
        else:
            return
        self._item_styles[item] = style
        self._add_log(f"Style updated for {typ}")

    def _toggle_toc_for_selected(self):
        item = getattr(self._context_menu, '_last_item', None)
        if item is None:
            return
        if item in self._toc_items:
            self._toc_items.remove(item)
            self._add_log("Removed from TOC")
        else:
            self._toc_items.add(item)
            self._add_log("Added to TOC")

    def add_h1(self):
        text = simpledialog.askstring("H1 Heading", "Enter heading text:", parent=self)
        if text:
            item = self.canvas.create_text(50, 50, text=text, anchor="nw", font=("Arial", 28, "bold"))
            self._item_data[item] = ("h1", text)
            self._make_draggable(item)
            action = HistoryAction(type="create", item=item, item_type="h1", data=text, coords=(50, 50))
            self._record_action(action)

    def add_h2(self):
        text = simpledialog.askstring("H2 Heading", "Enter heading text:", parent=self)
        if text:
            item = self.canvas.create_text(50, 100, text=text, anchor="nw", font=("Arial", 20, "bold"))
            self._item_data[item] = ("h2", text)
            self._make_draggable(item)
            action = HistoryAction(type="create", item=item, item_type="h2", data=text, coords=(50, 100))
            self._record_action(action)

    def add_paragraph(self):
        text = simpledialog.askstring("Paragraph", "Enter paragraph text:", parent=self)
        if text:
            item = self.canvas.create_text(50, 150, text=text, anchor="nw", font=("Arial", 14))
            self._item_data[item] = ("paragraph", text)
            self._make_draggable(item)
            action = HistoryAction(type="create", item=item, item_type="paragraph", data=text, coords=(50, 150))
            self._record_action(action)

    def add_two_column(self):
        # Draw two rectangles as column placeholders
        col1 = self.canvas.create_rectangle(50, 220, 250, 370, outline="#1F6AA5", width=2, dash=(4,2))
        col2 = self.canvas.create_rectangle(270, 220, 470, 370, outline="#1F6AA5", width=2, dash=(4,2))
        self._item_data[col1] = ("2col", "left")
        self._item_data[col2] = ("2col", "right")
        self._make_draggable(col1)
        self._make_draggable(col2)
        action1 = HistoryAction(type="create", item=col1, item_type="2col", data="left", coords=(50, 220))
        action2 = HistoryAction(type="create", item=col2, item_type="2col", data="right", coords=(270, 220))
        self._record_action(action1)
        self._record_action(action2)

    def add_three_column(self):
        # Draw three rectangles as column placeholders
        col1 = self.canvas.create_rectangle(50, 400, 200, 550, outline="#1F6AA5", width=2, dash=(4,2))
        col2 = self.canvas.create_rectangle(220, 400, 370, 550, outline="#1F6AA5", width=2, dash=(4,2))
        col3 = self.canvas.create_rectangle(390, 400, 540, 550, outline="#1F6AA5", width=2, dash=(4,2))
        self._item_data[col1] = ("3col", "left")
        self._item_data[col2] = ("3col", "center")
        self._item_data[col3] = ("3col", "right")
        self._make_draggable(col1)
        self._make_draggable(col2)
        self._make_draggable(col3)
        action1 = HistoryAction(type="create", item=col1, item_type="3col", data="left", coords=(50, 400))
        action2 = HistoryAction(type="create", item=col2, item_type="3col", data="center", coords=(220, 400))
        action3 = HistoryAction(type="create", item=col3, item_type="3col", data="right", coords=(390, 400))
        self._record_action(action1)
        self._record_action(action2)
        self._record_action(action3)


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
            elif item_type == "h1":
                item = self.canvas.create_text(x, y, text=data, anchor="nw", font=("Arial", 28, "bold"))
                self._item_data[item] = ("h1", data)
            elif item_type == "h2":
                item = self.canvas.create_text(x, y, text=data, anchor="nw", font=("Arial", 20, "bold"))
                self._item_data[item] = ("h2", data)
            elif item_type == "paragraph":
                item = self.canvas.create_text(x, y, text=data, anchor="nw", font=("Arial", 14))
                self._item_data[item] = ("paragraph", data)
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
            elif item_type == "2col":
                # Recreate left/right column rectangles
                if data == "left":
                    item = self.canvas.create_rectangle(x, y, x+200, y+150, outline="#1F6AA5", width=2, dash=(4,2))
                    self._item_data[item] = ("2col", "left")
                else:
                    item = self.canvas.create_rectangle(x, y, x+200, y+150, outline="#1F6AA5", width=2, dash=(4,2))
                    self._item_data[item] = ("2col", "right")
            elif item_type == "3col":
                # Recreate left/center/right column rectangles
                item = self.canvas.create_rectangle(x, y, x+150, y+150, outline="#1F6AA5", width=2, dash=(4,2))
                self._item_data[item] = ("3col", data)
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
        if not path:
            return

        # Show loading indicator
        loading_text = self.canvas.create_text(400, 300, text="Loading image...", fill="gray", font=("Arial", 16, "italic"))

        def process_image():
            try:
                opt_path = optimize_image(path)
                pil_img = Image.open(opt_path)
                return (opt_path, pil_img)
            except Exception as e:
                return (None, str(e))

        def on_image_ready(future):
            self.canvas.delete(loading_text)
            opt_path, result = future.result()
            if opt_path is None:
                # Show error
                tk.messagebox.showerror("Image Error", f"Failed to load image: {result}")
                return
            img = ImageTk.PhotoImage(result)
            item = self.canvas.create_image(50, 50, image=img, anchor="nw")
            self._images[item] = img
            self._item_data[item] = ("image", opt_path)
            self._make_draggable(item)
            action = HistoryAction(type="create", item=item, item_type="image", data=opt_path, coords=(50, 50))
            self._record_action(action)

        # Run image processing in background
        future = self._executor.submit(process_image)
        self.after(100, lambda: self._poll_future(future, on_image_ready))

    def _poll_future(self, future, callback):
        if future.done():
            callback(future)
        else:
            self.after(100, lambda: self._poll_future(future, callback))

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
        toc_counter = 1
        toc_map = {}
        for item, data in self._item_data.items():
            x, y = self.canvas.coords(item)[:2]
            anchor = ""
            if item in self._toc_items:
                anchor = f" id='toc-{toc_counter}'"
                toc_map[item] = f"toc-{toc_counter}"
                toc_counter += 1
            style = self._item_styles.get(item, {})
            style_str = ""
            if data[0] in ("h1", "h2", "paragraph", "text"):
                style_str = f"font-size:{style.get('font-size', 14)}px; color:{style.get('color', '#333')}; font-weight:{style.get('font-weight', 'normal')}; font-style:{style.get('font-style', 'normal')};"
            elif data[0] == "image":
                style_str = f"width:{style.get('width', 200)}px; height:{style.get('height', 200)}px;"
            elif data[0] in ("2col", "3col"):
                style_str = f"border:{style.get('border', '2px dashed #1F6AA5')}; background-color:{style.get('background-color', '#fff')};"
            if data[0] == "text":
                html_lines.append(f"<div style='position:absolute; left:{int(x)}px; top:{int(y)}px; {style_str}'{anchor}>{data[1]}</div>")
            elif data[0] == "h1":
                html_lines.append(f"<h1 style='position:absolute; left:{int(x)}px; top:{int(y)}px; {style_str}'{anchor}>{data[1]}</h1>")
            elif data[0] == "h2":
                html_lines.append(f"<h2 style='position:absolute; left:{int(x)}px; top:{int(y)}px; {style_str}'{anchor}>{data[1]}</h2>")
            elif data[0] == "paragraph":
                html_lines.append(f"<p style='position:absolute; left:{int(x)}px; top:{int(y)}px; {style_str}'{anchor}>{data[1]}</p>")
            elif data[0] == "image":
                html_lines.append(f"<img src='{data[1]}' style='position:absolute; left:{int(x)}px; top:{int(y)}px; {style_str}'{anchor}>")
            elif data[0] == "button":
                html_lines.append(f"<button style='position:absolute; left:{int(x)}px; top:{int(y)}px;' {anchor}>{data[1]}</button>")
            elif data[0] == "2col":
                html_lines.append(f"<div style='position:absolute; left:{int(x)}px; top:{int(y)}px; width:200px; height:150px; {style_str}'{anchor}></div>")
            elif data[0] == "3col":
                html_lines.append(f"<div style='position:absolute; left:{int(x)}px; top:{int(y)}px; width:150px; height:150px; {style_str}'{anchor}></div>")
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
