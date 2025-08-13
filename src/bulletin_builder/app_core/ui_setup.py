import customtkinter as ctk
import tkinter as tk
from tkhtmlview import HTMLLabel
from pathlib import Path
from bulletin_builder.ui.settings import SettingsFrame
 # Removed incorrect relative import of init
from bulletin_builder.app_core.config import (
    load_google_api_key,
    load_openai_key,
    load_events_feed_url
)

def init(app):
    """Build all UI elements and wire them to app handlers."""
    # --- Window Setup ---
    app.title("LACC Bulletin Builder")
    app.geometry("1200x800")
    # Appearance mode will be set by settings frame based on saved settings
    ctk.set_default_color_theme("blue")

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

    # Create a frame to hold the section management buttons
    button_frame = ctk.CTkFrame(lp, fg_color="transparent")
    button_frame.pack(pady=5, fill="x")
    button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1) # Make buttons expand

    # --- Content Tab ---
    content = app.tab_view.tab("Content")
    # Layout: left panel (sections), right panel (editor)
    content.grid_columnconfigure(0, weight=1, minsize=220)
    content.grid_columnconfigure(1, weight=3)
    content.grid_rowconfigure(0, weight=1)

    # Left panel: section list + controls (visually distinct)
    lp = ctk.CTkFrame(content, fg_color="#232b36", border_width=2, border_color="#1F6AA5")
    lp.grid(row=0, column=0, sticky="nsew", padx=(0,8), pady=10)

    # Create a frame to hold the section management buttons
    button_frame = ctk.CTkFrame(lp, fg_color="transparent")
    button_frame.pack(pady=5, fill="x")
    button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)  # Make buttons expand

    # --- Add/modify this section ---
    ctk.CTkButton(button_frame, text="Add", command=app.add_section_dialog).grid(row=0, column=0, padx=2)
    ctk.CTkButton(button_frame, text="Remove", command=app.remove_section).grid(row=0, column=1, padx=2)
    ctk.CTkButton(button_frame, text="Move Up", command=app.move_section_up).grid(row=0, column=2, padx=2)
    ctk.CTkButton(button_frame, text="Move Down", command=app.move_section_down).grid(row=0, column=3, padx=2)

    app.section_listbox = tk.Listbox(lp,
        bg="#232b36", fg="white",
        selectbackground="#1F6AA5", selectforeground="white",
        borderwidth=0, highlightthickness=0,
        font=("Roboto", 12),
        relief="flat",
        highlightbackground="#1F6AA5",
        highlightcolor="#1F6AA5"
    )
    app.section_listbox.pack(fill="both", expand=True, pady=10)
    app.section_listbox.bind("<<ListboxSelect>>", app.on_section_select)

    expf = ctk.CTkFrame(lp)
    expf.pack(fill="x", pady=5)
    app.email_button = ctk.CTkButton(expf, text="Copy for Email", command=app.on_copy_for_email_clicked)
    app.email_button.pack(fill="x", pady=(0,5))
    app.send_test_button = ctk.CTkButton(expf, text="Send Test Email...", command=app.on_send_test_email_clicked)
    app.send_test_button.pack(fill="x", pady=(0,5))
    app.export_html_text_button = ctk.CTkButton(expf, text="Export HTML + Text...", command=app.on_export_html_text_clicked)
    app.export_html_text_button.pack(fill="x", pady=(0,5))
    app.ics_button = ctk.CTkButton(expf, text="Export Event .ics", command=app.on_export_ics_clicked)
    app.ics_button.pack(fill="x")

    # Smart Suggestions Panel
    if hasattr(app, 'build_suggestions_panel'):
        sugg_frame = app.build_suggestions_panel(lp)
        sugg_frame.pack(fill="x", pady=5)
    else:
        print("Warning: build_suggestions_panel not found on app; skipping suggestions panel.")

    # Right panel: editor or placeholder (visually distinct)
    app.right_panel = ctk.CTkFrame(content, fg_color="#f7f9fa", border_width=1, border_color="#cccccc")
    app.right_panel.grid(row=0, column=1, sticky="nsew", padx=(0,10), pady=10)
    app.show_placeholder()

    # Status bar: always visible, full width, modern look
    app.status_bar = ctk.CTkLabel(app, text="", anchor="w", fg_color="#1F6AA5", text_color="white", height=28)
    app.status_bar.grid(row=1, column=0, sticky="ew", padx=0)

    # Load the saved keys from config.ini
    saved_google_key = load_google_api_key()
    saved_openai_key = load_openai_key()
    saved_events_url = load_events_feed_url()

    # Get the initial settings data (can be an empty dict if none exists)
    initial_settings = getattr(app, "settings", {})

    # Call load_data with the keys you just loaded from the file
    app.settings_frame.load_data(
        settings_data=initial_settings,
        google_key=saved_google_key,
        openai_key=saved_openai_key,
        events_url=saved_events_url,
    )

    # --- Preview Tab ---
    prev = app.tab_view.tab("Preview")
    ctrl = ctk.CTkFrame(prev)
    ctrl.pack(padx=10, pady=10, anchor="w")

    app.update_preview_btn = ctk.CTkButton(ctrl, text="Update Preview", command=app.update_preview)
    app.update_preview_btn.pack(side="left")

    ctk.CTkButton(ctrl, text="Open in Browser", command=app.open_in_browser).pack(side="left", padx=5)

    app.preview_mode_toggle = ctk.CTkSegmentedButton(
        ctrl, values=["Rendered", "Code"], command=app.toggle_preview_mode
    )
    app.preview_mode_toggle.set("Rendered")
    app.preview_mode_toggle.pack(side="left", padx=5)

    app.device_mode_toggle = ctk.CTkSegmentedButton(
        ctrl,
        values=["Desktop", "Tablet", "Mobile"],
        command=app.set_preview_device,
    )
    app.device_mode_toggle.set("Desktop")
    app.device_mode_toggle.pack(side="left", padx=5)

    app.preview_area = ctk.CTkFrame(prev)
    app.preview_area.pack(padx=10, pady=10)
    app.preview_area.pack_propagate(False)

    app.rendered_preview = HTMLLabel(app.preview_area, background="white")
    app.code_preview = ctk.CTkTextbox(app.preview_area, wrap="word", font=("Courier New", 12))
    # neither packed until toggle

    app.set_preview_device("Desktop")

    # --- Keyboard Shortcuts ---
    app.bind("<Control-s>", lambda e: app.save_draft())
    app.bind("<Control-S>", lambda e: app.save_draft())  # for some platforms
    app.bind("<Control-Shift-S>", lambda e: app.save_draft(save_as=True))
    app.bind("<Control-o>", lambda e: app.open_draft())
    app.bind("<Control-n>", lambda e: app.new_draft())

    if hasattr(app, "compute_suggestions"):
        app.compute_suggestions()

    # Left panel (sections / controls)
    if not hasattr(app, "left_panel"):
        app.left_panel = ctk.CTkFrame(content)
        app.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    # Right panel (created by preview.init)
    if not hasattr(app, "right_panel"):
        app.right_panel = ctk.CTkFrame(content)
        app.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    # Status bar
    if not hasattr(app, "status_bar"):
        app.status_bar = ctk.CTkLabel(app, text="", anchor="w")
        app.status_bar.grid(row=1, column=0, sticky="ew", padx=10)

    # Section list (if not already present)
    if not hasattr(app, "section_listbox"):
        app.section_listbox = tk.Listbox(app.left_panel, height=20)
        app.section_listbox.pack(fill="both", expand=True, padx=10, pady=10)

    # Primary buttons (ensure export button exists & is the HTML/TXT one)
    if not hasattr(app, "export_button"):
        app.export_button = ctk.CTkButton(
            app.left_panel,
            text="Export HTML + Text…",
            command=getattr(app, "on_export_html_text_clicked", lambda: None),
        )
        app.export_button.pack(fill="x", padx=10, pady=(0, 10))

    if not hasattr(app, "email_button"):
        app.email_button = ctk.CTkButton(
            app.left_panel,
            text="Copy Email-Ready HTML",
            command=getattr(app, "on_copy_for_email_clicked", lambda: None),
        )
        app.email_button.pack(fill="x", padx=10, pady=(0, 10))

    # --- Menus ---
    def _build_menus():
        menubar = tk.Menu(app)
        filemenu = tk.Menu(menubar, tearoff=0)

        def add(label, attr):
            if hasattr(app, attr):
                filemenu.add_command(label=label, command=getattr(app, attr))

        # Drafts
        add("New Draft", "new_draft")
        filemenu.add_separator()
        add("Open Draft…", "open_draft")
        filemenu.add_separator()
        add("Save", "save_draft")
        add("Save As…", "save_draft_as" if hasattr(app, "save_draft_as") else "save_draft")
        filemenu.add_separator()

        # Imports
        add("Import Announcements CSV…", "import_announcements_csv")
        add("Import Google Sheet (CSV)…", "import_announcements_sheet")
        add("Import Events Feed…", "import_events_feed")
        filemenu.add_separator()

        # Exports / Tools (NO PDF)
        add("Export HTML & Text…", "on_export_html_text_clicked")
        add("Copy Email-Ready HTML", "on_copy_for_email_clicked")
        add("Open in Browser", "open_in_browser")
        add("Export Calendar (.ics)…", "on_export_ics_clicked")
        filemenu.add_separator()

        # Email
        add("Send Test Email…", "on_send_test_email_clicked")
        filemenu.add_separator()

        filemenu.add_command(label="Exit", command=app.destroy)

        menubar.add_cascade(label="File", menu=filemenu)
        app.config(menu=menubar)

    app._build_menus = _build_menus
    app._build_menus()