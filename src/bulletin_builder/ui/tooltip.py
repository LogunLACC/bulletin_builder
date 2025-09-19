import tkinter as tk

class ToolTip:
    def __init__(self, widget, text: str, delay_ms: int = 400):
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self._after_id = None
        self._tip = None
        widget.bind("<Enter>", self._on_enter, add=True)
        widget.bind("<Leave>", self._on_leave, add=True)
        widget.bind("<Motion>", self._on_motion, add=True)

    def _on_enter(self, _):
        self._schedule()

    def _on_leave(self, _):
        self._cancel()
        self._hide()

    def _on_motion(self, _):
        # Restart timer on movement to avoid flicker
        self._cancel()
        self._schedule()

    def _schedule(self):
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _cancel(self):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self):
        if self._tip is not None:
            return
        try:
            x, y, cx, cy = self.widget.bbox("insert") or (0, 0, 0, 0)
        except Exception:
            x, y, _cx, _cy = (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20

        self._tip = tk.Toplevel(self.widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(
            self._tip,
            text=self.text,
            justify=tk.LEFT,
            background="#111",
            foreground="#fff",
            relief=tk.SOLID,
            borderwidth=1,
            padx=6,
            pady=3,
            font=("Segoe UI", 9),
        )
        lbl.pack(ipadx=1)

    def _hide(self):
        if self._tip is not None:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None


def add_tooltip(widget, text: str, delay_ms: int = 400):
    try:
        ToolTip(widget, text, delay_ms)
    except Exception:
        pass

