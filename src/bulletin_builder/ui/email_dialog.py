import customtkinter as ctk
import tkinter as tk

class EmailDialog(ctk.CTkToplevel):
    """Dialog to capture a destination email address."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Send Test Email")
        self.geometry("400x160")
        self.transient(parent)
        self.grab_set()
        self.result = None

        frm = ctk.CTkFrame(self)
        frm.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(frm, text="Send preview to:").pack(anchor="w")
        self.email_entry = ctk.CTkEntry(frm)
        self.email_entry.pack(fill="x", pady=(0, 20))

        btnf = ctk.CTkFrame(frm)
        btnf.pack(fill="x", side="bottom")
        ctk.CTkButton(btnf, text="Send", command=self.on_ok).pack(side="right")
        ctk.CTkButton(
            btnf,
            text="Cancel",
            command=self.destroy,
            fg_color="gray50",
            hover_color="gray40",
        ).pack(side="right", padx=(0, 10))

        self.email_entry.focus_set()
        self.wait_window()

    def on_ok(self):
        addr = self.email_entry.get().strip()
        if not addr:
            tk.messagebox.showwarning(
                "Input Error", "Please enter an email address.", parent=self
            )
            return
        self.result = addr
        self.destroy()

    def get_email(self):
        return self.result
