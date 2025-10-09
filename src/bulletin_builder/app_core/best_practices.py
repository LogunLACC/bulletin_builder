"""
Email Best Practices Checklist Module

Provides a pre-export checklist/wizard to guide users through email best practices.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk


class BestPracticesDialog(ctk.CTkToplevel):
    """Dialog showing email best practices checklist."""
    
    PRACTICES = [
        {
            "category": "Content Quality",
            "items": [
                "All images have descriptive alt text",
                "Subject line is clear and under 50 characters",
                "No spam trigger words (FREE, URGENT, ACT NOW, etc.)",
                "Plain text alternative is available",
                "Important information is not image-only",
            ]
        },
        {
            "category": "Design & Layout",
            "items": [
                "Layout uses tables, not flexbox/grid",
                "All styles are inline, not in <style> tags",
                "No JavaScript or external resources",
                "Mobile-friendly with proper viewport settings",
                "Colors have sufficient contrast (WCAG AA)",
            ]
        },
        {
            "category": "Technical",
            "items": [
                "HTML validates without errors",
                "Links use absolute URLs (https://)",
                "Unsubscribe link is present and visible",
                "From address is recognizable",
                "Email has been tested in preview mode",
            ]
        },
        {
            "category": "Before Sending",
            "items": [
                "Proofread all content for typos",
                "Verified all links work correctly",
                "Tested in multiple email clients",
                "Sent test email to yourself",
                "Double-checked recipient list",
            ]
        },
    ]
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Email Best Practices Checklist")
        self.geometry("700x600")
        
        # Center on parent
        self.transient(parent)
        
        # Make modal
        self.grab_set()
        
        self._create_widgets()
        
        # Center the window
        self.after(100, self._center_window)
    
    def _center_window(self):
        """Center the dialog on the parent window."""
        self.update_idletasks()
        
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header,
            text="📋 Email Best Practices Checklist",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            header,
            text="Review these best practices before sending your email",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle.pack(anchor="w", pady=(5, 0))
        
        # Scrollable content area
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create checklist sections
        for practice_group in self.PRACTICES:
            self._create_category_section(scroll_frame, practice_group)
        
        # Additional tips section
        tips_frame = ctk.CTkFrame(scroll_frame, fg_color=("#f0f0f0", "#2b2b2b"), corner_radius=8)
        tips_frame.pack(fill="x", pady=(20, 10))
        
        tips_label = ctk.CTkLabel(
            tips_frame,
            text="💡 Pro Tips",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        tips_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        tips_text = ctk.CTkLabel(
            tips_frame,
            text="• Use the Preview tab to check email client rendering\n"
                 "• Run Export Validation before sending\n"
                 "• Send a test email to multiple addresses\n"
                 "• Check spam score with online tools\n"
                 "• Keep total email size under 100KB",
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        tips_text.pack(anchor="w", padx=15, pady=(5, 15))
        
        # Bottom buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.destroy,
            width=120
        )
        close_btn.pack(side="right")
        
        print_btn = ctk.CTkButton(
            button_frame,
            text="Print Checklist",
            command=self._print_checklist,
            width=120,
            fg_color="transparent",
            border_width=2
        )
        print_btn.pack(side="right", padx=(0, 10))
    
    def _create_category_section(self, parent, practice_group):
        """Create a section for a practice category."""
        # Category frame
        category_frame = ctk.CTkFrame(parent, fg_color="transparent")
        category_frame.pack(fill="x", pady=(0, 15))
        
        # Category title
        title = ctk.CTkLabel(
            category_frame,
            text=practice_group["category"],
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 10))
        
        # Checklist items
        for item in practice_group["items"]:
            item_frame = ctk.CTkFrame(category_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=2)
            
            # Checkbox
            checkbox = ctk.CTkCheckBox(
                item_frame,
                text=item,
                font=ctk.CTkFont(size=12)
            )
            checkbox.pack(anchor="w", padx=(10, 0))
    
    def _print_checklist(self):
        """Print or save the checklist."""
        try:
            from tkinter import messagebox
            
            # Generate text version
            checklist_text = "EMAIL BEST PRACTICES CHECKLIST\n"
            checklist_text += "=" * 60 + "\n\n"
            
            for group in self.PRACTICES:
                checklist_text += f"{group['category']}\n"
                checklist_text += "-" * 60 + "\n"
                for item in group['items']:
                    checklist_text += f"☐ {item}\n"
                checklist_text += "\n"
            
            checklist_text += "PRO TIPS\n"
            checklist_text += "-" * 60 + "\n"
            checklist_text += "• Use the Preview tab to check email client rendering\n"
            checklist_text += "• Run Export Validation before sending\n"
            checklist_text += "• Send a test email to multiple addresses\n"
            checklist_text += "• Check spam score with online tools\n"
            checklist_text += "• Keep total email size under 100KB\n"
            
            # Copy to clipboard
            self.clipboard_clear()
            self.clipboard_append(checklist_text)
            
            messagebox.showinfo(
                "Checklist Copied",
                "The checklist has been copied to your clipboard.\n\n"
                "You can paste it into a text editor or document.",
                parent=self
            )
        except Exception as e:
            print(f"Error printing checklist: {e}")


def show_best_practices_checklist(app):
    """Show the best practices checklist dialog."""
    try:
        dialog = BestPracticesDialog(app)
        dialog.focus()
    except Exception as e:
        print(f"Error showing best practices dialog: {e}")
        try:
            from tkinter import messagebox
            messagebox.showerror(
                "Error",
                f"Could not show best practices checklist: {e}",
                parent=app
            )
        except:
            pass


def init(app):
    """Initialize best practices module."""
    app.show_best_practices_checklist = lambda: show_best_practices_checklist(app)
