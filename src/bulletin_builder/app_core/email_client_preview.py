"""
Email Client Preview Simulation Module

Provides email client-specific preview modes to simulate how bulletins will render
in Gmail, Outlook, Apple Mail, and mobile clients.
"""

import tkinter as tk
from tkinter import ttk


# Email client rendering constraints and quirks
EMAIL_CLIENT_STYLES = {
    "Gmail": {
        "name": "Gmail (Desktop)",
        "description": "Gmail strips <style> tags, supports most inline CSS, limited web fonts",
        "max_width": 650,
        "constraints": [
            "• Strips <style> tags and external stylesheets",
            "• Supports inline CSS with some limitations",
            "• May not display custom web fonts reliably",
            "• Converts some CSS properties",
            "• Good support for media queries on mobile"
        ],
        "wrapper_style": "border: 2px solid #d93025; padding: 10px; background: #fff;",
        "info_color": "#d93025"
    },
    "Outlook": {
        "name": "Outlook (Desktop)",
        "description": "Uses Word rendering engine, limited CSS support, table-based layouts work best",
        "max_width": 600,
        "constraints": [
            "• Uses Microsoft Word rendering engine",
            "• Very limited CSS support (no float, position, etc.)",
            "• Background images often not supported",
            "• Table-based layouts are most reliable",
            "• Padding/margins may be inconsistent"
        ],
        "wrapper_style": "border: 2px solid #0078d4; padding: 10px; background: #fff;",
        "info_color": "#0078d4"
    },
    "Apple Mail": {
        "name": "Apple Mail",
        "description": "Best CSS support, WebKit-based, handles modern HTML/CSS well",
        "max_width": 600,
        "constraints": [
            "• Excellent CSS support (WebKit-based)",
            "• Handles modern HTML5/CSS3 features",
            "• Good support for web fonts",
            "• Media queries work well",
            "• Generally most reliable client"
        ],
        "wrapper_style": "border: 2px solid #34c759; padding: 10px; background: #fff;",
        "info_color": "#34c759"
    },
    "Mobile": {
        "name": "Mobile (Generic)",
        "description": "Narrow viewport, touch targets, simplified layouts",
        "max_width": 375,
        "constraints": [
            "• Narrow viewport (typically 320-414px)",
            "• Touch targets should be 44x44px minimum",
            "• Font size should be 14px+ for readability",
            "• Single column layouts work best",
            "• Consider thumb-friendly spacing"
        ],
        "wrapper_style": "border: 2px solid #ff9500; padding: 8px; background: #fff;",
        "info_color": "#ff9500"
    },
    "Standard": {
        "name": "Standard Preview",
        "description": "Default bulletin preview without client-specific constraints",
        "max_width": 800,
        "constraints": [
            "• Full-featured HTML/CSS rendering",
            "• Desktop browser preview",
            "• No email client limitations applied"
        ],
        "wrapper_style": "border: 1px solid #ccc; padding: 10px; background: #fff;",
        "info_color": "#666"
    }
}


def show_email_client_info(parent, client_name="Gmail"):
    """
    Display information about a specific email client's rendering characteristics.
    
    Args:
        parent: Parent window for the dialog
        client_name: Name of the email client (Gmail, Outlook, Apple Mail, Mobile, Standard)
    """
    client_info = EMAIL_CLIENT_STYLES.get(client_name, EMAIL_CLIENT_STYLES["Standard"])
    
    # Create info dialog
    dialog = tk.Toplevel(parent)
    dialog.title(f"{client_info['name']} - Rendering Information")
    dialog.geometry("500x400")
    dialog.transient(parent)
    dialog.grab_set()
    
    # Header with client name
    header_frame = tk.Frame(dialog, bg=client_info["info_color"], pady=10)
    header_frame.pack(fill=tk.X)
    
    tk.Label(
        header_frame,
        text=client_info['name'],
        font=("Arial", 16, "bold"),
        bg=client_info["info_color"],
        fg="white"
    ).pack()
    
    # Content frame
    content_frame = tk.Frame(dialog, padx=20, pady=20)
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # Description
    tk.Label(
        content_frame,
        text=client_info['description'],
        font=("Arial", 10),
        wraplength=450,
        justify=tk.LEFT
    ).pack(anchor=tk.W, pady=(0, 15))
    
    # Max width info
    tk.Label(
        content_frame,
        text=f"Preview Width: {client_info['max_width']}px",
        font=("Arial", 10, "bold")
    ).pack(anchor=tk.W, pady=(0, 10))
    
    # Constraints
    tk.Label(
        content_frame,
        text="Rendering Constraints:",
        font=("Arial", 10, "bold")
    ).pack(anchor=tk.W, pady=(0, 5))
    
    constraints_text = "\n".join(client_info['constraints'])
    tk.Label(
        content_frame,
        text=constraints_text,
        font=("Courier", 9),
        justify=tk.LEFT,
        wraplength=450
    ).pack(anchor=tk.W, padx=10)
    
    # Close button
    tk.Button(
        dialog,
        text="Close",
        command=dialog.destroy,
        width=15
    ).pack(pady=10)
    
    # Center dialog
    dialog.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")


def get_client_max_width(client_name):
    """Get the maximum preview width for a given email client."""
    return EMAIL_CLIENT_STYLES.get(client_name, EMAIL_CLIENT_STYLES["Standard"])["max_width"]


def get_client_wrapper_style(client_name):
    """Get the CSS wrapper style for simulating a specific email client."""
    return EMAIL_CLIENT_STYLES.get(client_name, EMAIL_CLIENT_STYLES["Standard"])["wrapper_style"]


def init(app):
    """
    Initialize email client preview simulation on the app instance.
    
    Args:
        app: The main application instance
    """
    # Add email client selection variable if not exists
    if not hasattr(app, 'email_client_var'):
        try:
            app.email_client_var = tk.StringVar(value="Standard")
        except RuntimeError:
            # Tk root not available yet, will be created by UI setup
            pass
    
    # Store available clients
    app.available_email_clients = list(EMAIL_CLIENT_STYLES.keys())
    
    # Add method to show client info
    app.show_email_client_info = lambda client=None: show_email_client_info(
        app, 
        client or (app.email_client_var.get() if hasattr(app, 'email_client_var') else "Standard")
    )
    
    # Add method to get current client's max width
    def _get_current_width():
        if hasattr(app, 'email_client_var'):
            return get_client_max_width(app.email_client_var.get())
        return 800  # Default to Standard
    
    app.get_current_client_width = _get_current_width
    
    # Add method to get current client's wrapper style
    def _get_current_wrapper():
        if hasattr(app, 'email_client_var'):
            return get_client_wrapper_style(app.email_client_var.get())
        return get_client_wrapper_style("Standard")
    
    app.get_current_client_wrapper = _get_current_wrapper
