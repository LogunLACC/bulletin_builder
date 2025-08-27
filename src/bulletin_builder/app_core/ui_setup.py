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

    tools_menu = tk.Menu(menubar, tearoff=0)
    tools_menu.add_command(label="WYSIWYG Editor", command=app.open_wysiwyg_editor)
    tools_menu.add_command(label="Template Gallery", command=app.open_template_gallery)
    tools_menu.add_command(label="Component Library", command=app.open_component_library)
    tools_menu.add_separator()
    tools_menu.add_command(label="Import Announcements CSV...", command=app.import_announcements_csv)
    tools_menu.add_command(label="Import Announcements from Sheet...", command=app.import_announcements_sheet)
    tools_menu.add_command(label="Import Events Feed...", command=app.import_events_feed)
    menubar.add_cascade(label="Tools", menu=tools_menu)

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
    app.send_test_button = ctk.CTkButton(expf, text="Send Test Email...", command=app.on_send_test_email_clicked)
    app.send_test_button.pack(fill="x", pady=(0,5))
    app.export_button = ctk.CTkButton(expf, text="Export to PDF...", command=app.on_export_pdf_clicked)
    app.export_button.pack(fill="x", pady=(0,5))
    app.export_html_text_button = ctk.CTkButton(expf, text="Export HTML + Text...", command=app.on_export_html_text_clicked)
    app.export_html_text_button.pack(fill="x", pady=(0,5))
    app.ics_button = ctk.CTkButton(expf, text="Export Event .ics", command=app.on_export_ics_clicked)
    app.ics_button.pack(fill="x")

    # Smart Suggestions Panel
    sugg_frame = app.build_suggestions_panel(lp)
    sugg_frame.pack(fill="x", pady=5)

    # Right panel: editor or placeholder
    app.right_panel = ctk.CTkFrame(content)
    app.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    app.show_placeholder()

    # --- Settings Tab ---
    sett = app.tab_view.tab("Settings")
    app.settings_frame = SettingsFrame(
        sett,
        refresh_callback=app.refresh_listbox_titles,
        save_api_key_callback=app.save_api_key_to_config,
        save_openai_key_callback=app.save_openai_key_to_config,
        save_events_url_callback=app.save_events_url_to_config,
    )
    app.settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
    # Load defaults + persisted API key on startup
    app.settings_frame.load_data({}, app.google_api_key, app.openai_api_key, app.events_feed_url)

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

    # if hasattr(app, "compute_suggestions"):
    #     app.compute_suggestions()
