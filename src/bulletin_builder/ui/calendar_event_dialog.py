import customtkinter as ctk
import tkinter as tk
from datetime import datetime

class CalendarEventDialog(ctk.CTkToplevel):
    """Dialog to collect basic calendar event details."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("New Calendar Event")
        self.geometry("400x380")
        self.transient(parent)
        self.grab_set()
        self.result = None

        frm = ctk.CTkFrame(self)
        frm.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(frm, text="Title:").pack(anchor="w")
        self.title_entry = ctk.CTkEntry(frm)
        self.title_entry.pack(fill="x", pady=(0,10))

        ctk.CTkLabel(frm, text="Date (YYYY-MM-DD):").pack(anchor="w")
        self.date_entry = ctk.CTkEntry(frm)
        self.date_entry.pack(fill="x", pady=(0,10))

        ctk.CTkLabel(frm, text="Start Time (HH:MM)").pack(anchor="w")
        self.start_entry = ctk.CTkEntry(frm)
        self.start_entry.pack(fill="x", pady=(0,10))

        ctk.CTkLabel(frm, text="End Time (HH:MM)").pack(anchor="w")
        self.end_entry = ctk.CTkEntry(frm)
        self.end_entry.pack(fill="x", pady=(0,10))

        ctk.CTkLabel(frm, text="Location:").pack(anchor="w")
        self.location_entry = ctk.CTkEntry(frm)
        self.location_entry.pack(fill="x", pady=(0,10))

        ctk.CTkLabel(frm, text="Description:").pack(anchor="w")
        self.desc_entry = ctk.CTkEntry(frm)
        self.desc_entry.pack(fill="x", pady=(0,20))

        btnf = ctk.CTkFrame(frm)
        btnf.pack(fill="x", side="bottom")
        ctk.CTkButton(btnf, text="OK", command=self.on_ok).pack(side="right")
        ctk.CTkButton(btnf, text="Cancel", command=self.destroy, fg_color="gray50", hover_color="gray40").pack(side="right", padx=(0,10))

        self.title_entry.focus_set()
        self.wait_window()

    def on_ok(self):
        title = self.title_entry.get().strip()
        date_str = self.date_entry.get().strip()
        start_str = self.start_entry.get().strip()
        end_str = self.end_entry.get().strip()
        if not title or not date_str or not start_str:
            # tk.messagebox.showwarning("Input Error", "Title, date, and start time are required.", parent=self)
            return
        try:
            start_dt = datetime.strptime(f"{date_str} {start_str}", "%Y-%m-%d %H:%M")
            if end_str:
                end_dt = datetime.strptime(f"{date_str} {end_str}", "%Y-%m-%d %H:%M")
            else:
                end_dt = start_dt
        except Exception:
            # tk.messagebox.showwarning("Input Error", "Invalid date or time format.", parent=self)
            return
        self.result = {
            "title": title,
            "start": start_dt,
            "end": end_dt,
            "location": self.location_entry.get().strip(),
            "description": self.desc_entry.get().strip()
        }
        self.destroy()

    def get_data(self):
        return self.result
