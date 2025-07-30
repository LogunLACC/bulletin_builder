import customtkinter as ctk
import tkinter as tk
from tkhtmlview import HTMLLabel
from pathlib import Path
from ..ui.settings import SettingsFrame

def init(app):
    """Build all UI elements and wire them to app handlers."""
    # --- Window Setup ---
    app.title("LACC Bulletin Builder")
    app.geometry("1200x800")
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    # --- Menu Bar ---
    menubar = tk.Menu(app)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="New Draft", command=app.new_draft)
    filemenu.add_separator()
    filemenu.add_command(label="Open Draft...", command=app.open_draft)
    filemenu.add_separator()
    filemenu.add_command(label="Save", command=app.save_draft)
    filemenu.add_command(label="Save As...", command=lambda: app.save_draft(save_as=True))
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=app.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    app.config(menu=menubar)

    # --- Main Layout (Tabs + Status Bar) ---
    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(0, weight=1)
    app.grid_rowconfigure(1, weight=0)

    app.tab_view = ctk.CTkTabview(app, anchor="w")
    app.tab_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    for name in ["Content", "Settings", "Preview"]:
        app.tab_view.add(name)

    app.status_bar = ctk.CTkLabel(app, text="", anchor="w")
    app.status_bar.grid(row=1, column=0, sticky="ew", padx=10)

    # --- Content Tab ---
    content = app.tab_view.tab("Content")
    content.grid_columnconfigure(0, weight=1)
    content.grid_columnconfigure(1, weight=3)
    content.grid_rowconfigure(0, weight=1)

    # Left panel: section list + controls
    lp = ctk.CTkFrame(content)
    lp.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    ctk.CTkButton(lp, text="Add Section", command=app.add_section_dialog).pack(pady=5)
    ctk.CTkButton(lp, text="Remove", command=app.remove_section).pack(pady=5)
    app.section_listbox = tk.Listbox(lp,
        bg="#2B2B2B", fg="white",
        selectbackground="#1F6AA5", selectforeground="white",
        borderwidth=0, highlightthickness=0,
        font=("Roboto", 12)
    )
    app.section_listbox.pack(fill="both", expand=True, pady=10)
    app.section_listbox.bind("<<ListboxSelect>>", app.on_section_select)

    expf = ctk.CTkFrame(lp)
    expf.pack(fill="x", pady=5)
    app.email_button = ctk.CTkButton(expf, text="Copy for Email", command=app.on_copy_for_email_clicked)
    app.email_button.pack(fill="x", pady=(0,5))
    app.export_button = ctk.CTkButton(expf, text="Export to PDF...", command=app.on_export_pdf_clicked)
    app.export_button.pack(fill="x")

    # Right panel: editor or placeholder
    app.right_panel = ctk.CTkFrame(content)
    app.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    app.show_placeholder()

    # --- Settings Tab ---
    sett = app.tab_view.tab("Settings")
    app.settings_frame = SettingsFrame(
        sett,
        refresh_callback=app.refresh_listbox_titles,
        save_api_key_callback=app.save_api_key_to_config
    )
    app.settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
    # Load defaults + persisted API key on startup
    app.settings_frame.load_data({}, app.google_api_key)

    # --- Preview Tab ---
    prev = app.tab_view.tab("Preview")
    ctrl = ctk.CTkFrame(prev)
    ctrl.pack(padx=10, pady=10, anchor="w")

    app.update_preview_btn = ctk.CTkButton(ctrl, text="Update Preview", command=app.update_preview)
    app.update_preview_btn.pack(side="left")

    ctk.CTkButton(ctrl, text="Open in Browser", command=app.open_in_browser).pack(side="left", padx=5)

    app.preview_mode_toggle = ctk.CTkSegmentedButton(
        ctrl, values=["Rendered","Code"], command=app.toggle_preview_mode
    )
    app.preview_mode_toggle.set("Rendered")
    app.preview_mode_toggle.pack(side="left", padx=5)

    app.rendered_preview = HTMLLabel(prev, background="white")
    app.code_preview     = ctk.CTkTextbox(prev, wrap="word", font=("Courier New",12))
    # neither packed until toggle
