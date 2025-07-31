import customtkinter as ctk
import tkinter as tk


class RecurringEventDialog(ctk.CTkToplevel):
    """Dialog letting user choose which recurring event dates to include."""

    def __init__(self, parent, occurrences):
        super().__init__(parent)
        self.title("Select Event Dates")
        self.geometry("420x400")
        self.transient(parent)
        self.grab_set()
        self.selected = []

        frame = ctk.CTkScrollableFrame(self, label_text="Include dates:")
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.vars = []
        for occ in occurrences:
            var = tk.BooleanVar(value=True)
            desc = f"{occ.get('date', '')} {occ.get('time', '')} - {occ.get('description', '')}"
            chk = ctk.CTkCheckBox(frame, text=desc, variable=var)
            chk.pack(anchor="w", pady=2)
            self.vars.append((var, occ))

        btnf = ctk.CTkFrame(self)
        btnf.pack(fill="x", side="bottom")
        ctk.CTkButton(btnf, text="OK", command=self.on_ok).pack(side="right")
        ctk.CTkButton(
            btnf,
            text="Cancel",
            command=self.destroy,
            fg_color="gray50",
            hover_color="gray40",
        ).pack(side="right", padx=(0, 10))

        self.wait_window()

    def on_ok(self):
        self.selected = [ev for var, ev in self.vars if var.get()]
        self.destroy()

    def get_selected(self):
        return self.selected

