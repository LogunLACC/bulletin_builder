import customtkinter as ctk
import tkinter as tk
from tkhtmlview import HTMLLabel
<<<<<<< HEAD
from bulletin_builder.ui.settings import SettingsFrame
from bulletin_builder.ui.tooltip import ToolTip

def _build_menus(app):
    """Attach the full application menubar to the root window."""
    import tkinter as tk
    menubar = tk.Menu(app)

    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="New", command=getattr(app, "new_draft", lambda: None))
    file_menu.add_command(label="Open...", command=getattr(app, "open_draft", lambda: None))
    file_menu.add_command(label="Save", command=getattr(app, "save_draft", lambda: None))
    file_menu.add_command(label="Save As...", command=getattr(app, "save_draft_as", lambda: None))
    file_menu.add_separator()
    # --- Export submenu ---
    export_menu = tk.Menu(file_menu, tearoff=0)
    export_menu.add_command(label="Bulletin HTML…", command=getattr(app, "export_bulletin_html", lambda: None))
    export_menu.add_command(label="Email HTML…", command=getattr(app, "export_email_html", lambda: None))
    file_menu.add_cascade(label="Export", menu=export_menu)
    file_menu.add_command(label="Exit", command=app.quit)
    menubar.add_cascade(label="File", menu=file_menu)

    # Tools menu
    tools_menu = tk.Menu(menubar, tearoff=0)
    tools_menu.add_command(label="Import Announcements CSV", command=getattr(app, "import_announcements_csv", lambda: None))
    tools_menu.add_command(label="Import Events Feed (Custom URL)", command=getattr(app, "import_events_feed", lambda: None))
    def import_events_feed_default():
        url = getattr(app, "events_feed_url", None)
        if not url:
            from bulletin_builder.app_core.config import load_events_feed_url
            url = load_events_feed_url()
        if not url:
            from tkinter import messagebox
            messagebox.showerror("No Events Feed URL", "No default events feed URL is set in settings or config.")
            return
        app.import_events_feed(url)
    tools_menu.add_command(label="Import Events Feed (Default URL)", command=import_events_feed_default)
    tools_menu.add_command(label="Export HTML + Text", command=getattr(app, "on_export_html_text_clicked", lambda: None))
    tools_menu.add_command(label="Export Event .ics", command=getattr(app, "on_export_ics_clicked", lambda: None))
    menubar.add_cascade(label="Tools", menu=tools_menu)

    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="About", command=getattr(app, "show_about_dialog", lambda: None))
    menubar.add_cascade(label="Help", menu=help_menu)

    app.config(menu=menubar)
    app.menubar = menubar

=======
from pathlib import Path
from ..ui.settings import SettingsFrame
>>>>>>> origin/harden/email-sanitize-and-ci

def init(app):
    """Stable, two-column Content view + clean tab switching."""

    # ---------- safety shims ----------
    if not hasattr(app, "save_component"):
        def _noop_save_component(*_a, **_kw):
            if hasattr(app, "status_bar"):
                app.status_bar.configure(text="(Info) Save as Component not implemented yet.")
        app.save_component = _noop_save_component

    if not hasattr(app, "replace_editor_frame"):
        def replace_editor_frame(new_frame):
            parent = app.editor_container
            # Do not destroy the new frame we're keeping
            for child in list(parent.winfo_children()):
                if child is new_frame:
                    continue
                try: child.grid_forget()
                except Exception:
                    try: child.pack_forget()
                    except Exception: pass
                child.destroy()
            # Ensure it's created with the correct parent
            if new_frame.master is not parent:
                raise RuntimeError("Editor frame must be created with parent=app.editor_container")
            parent.grid_rowconfigure(0, weight=1)
            parent.grid_columnconfigure(0, weight=1)
            try:
                new_frame.grid(row=0, column=0, sticky="nsew")
            except Exception:
                new_frame.pack(fill="both", expand=True)
            if hasattr(app, "status_bar"):
                app.status_bar.configure(text="Editor ready.")
        app.replace_editor_frame = replace_editor_frame

    # Attach the full menu builder to the app so __main__ can call it
    app._build_menus = lambda: _build_menus(app)

    # ---------- window + base grid ----------
    app.title("LACC Bulletin Builder")
    app.geometry("1200x800")
<<<<<<< HEAD
=======
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
>>>>>>> origin/harden/email-sanitize-and-ci
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    # status bar (single instance)
    if not hasattr(app, "status_bar"):
        app.status_bar = ctk.CTkLabel(app, text="", anchor="w")
        app.status_bar.grid(row=1, column=0, sticky="ew", padx=10)

    # ---------- right panel (create FIRST) ----------
    if not hasattr(app, "right_panel") or app.right_panel is None:
        app.right_panel = ctk.CTkFrame(app, fg_color="#e0e0e0")
        app.right_panel.grid(row=0, column=0, sticky="nsew", padx=0, pady=10)
        app.right_panel.grid_rowconfigure(0, weight=1)
        app.right_panel.grid_columnconfigure(0, weight=1)

    tab_bar = ctk.CTkFrame(app.right_panel, fg_color="#e5e5e5")
    tab_bar.grid(row=0, column=0, sticky="ew")
    view_container = ctk.CTkFrame(app.right_panel, fg_color="#f4f4f4")
    view_container.grid(row=1, column=0, sticky="nsew")
    app.right_panel.grid_rowconfigure(0, weight=0)
    app.right_panel.grid_rowconfigure(1, weight=1)
    app.right_panel.grid_columnconfigure(0, weight=1)
    tab_bar.grid(row=0, column=0, sticky="ew")
    view_container.grid(row=1, column=0, sticky="nsew")
    view_container.grid_rowconfigure(0, weight=1)
    view_container.grid_columnconfigure(0, weight=1)

    tab_names = ["Content", "Settings", "Preview"]
    app._tab_buttons = {}
    def on_tab_click(name: str):
        for n, b in app._tab_buttons.items():
            b.configure(state=("disabled" if n == name else "normal"))
        show_view(name)

    for i, name in enumerate(tab_names):
        btn = ctk.CTkButton(tab_bar, text=name, width=110, command=lambda n=name: on_tab_click(n))
        btn.grid(row=0, column=i, padx=4, pady=4)
        app._tab_buttons[name] = btn

    # ---------- view container ----------
    all_views = {}

    # =========================
    # CONTENT VIEW (2 columns)
    # =========================
    # --- Parent grid (Content page) ---
    content_view = ctk.CTkFrame(view_container)
    content_view.grid(row=0, column=0, sticky="nsew")
    content_view.grid_rowconfigure(0, weight=1)
    content_view.grid_columnconfigure(0, weight=0)                 # left nav fixed
    content_view.grid_columnconfigure(1, weight=1)                 # editor grows
    # Nuke any stray widgets in unexpected columns (prevents pink wall)
    for w in content_view.grid_slaves():
        if int(w.grid_info().get("column", 0)) >= 2:
            w.grid_forget()
            w.destroy()
    all_views["Content"] = content_view
    app.content_view = content_view

    # Editor container (this is where AnnouncementsFrame lives)
    app.editor_container = ctk.CTkFrame(content_view)
    app.editor_container.grid(row=0, column=1, sticky="nsew", padx=(0,12), pady=(8,8))
    app.editor_container.grid_rowconfigure(0, weight=1)
    app.editor_container.grid_columnconfigure(0, weight=1)

    # Left navigation container
    left = ctk.CTkFrame(content_view, fg_color="#232b36")
    left.grid(row=0, column=0, sticky="nsew", padx=(12,8), pady=(8,8))
    # Give the left column a sane width but don't overgrow
    content_view.grid_columnconfigure(0, minsize=360)
    left.grid_rowconfigure(1, weight=1)

    button_frame = ctk.CTkFrame(left, fg_color="transparent")
    button_frame.grid(row=0, column=0, sticky="ew", pady=8)

    btn_style = dict(font=("Segoe UI", 14, "bold"), height=40,
                     corner_radius=10, fg_color="#1F6AA5",
                     hover_color="#155a8a", text_color="#FFFFFF")
    for label, cmd, col in [
        ("Add", getattr(app, "add_section_dialog", lambda: None), 0),
        ("Remove", getattr(app, "remove_section", lambda: None), 1),
        ("Move Up", getattr(app, "move_section_up", lambda: None), 2),
        ("Move Down", getattr(app, "move_section_down", lambda: None), 3),
    ]:
        b = ctk.CTkButton(button_frame, text=label, command=cmd, **btn_style)
        b.grid(row=0, column=col, padx=4, pady=2, sticky="ew")
        b.configure(border_width=2, border_color="#FFD700")

    # Listbox
    if hasattr(app, "section_listbox"):
        app.section_listbox.destroy()
    app.section_listbox = tk.Listbox(
        left, bg="#232b36", fg="#FFFFFF",
        selectbackground="#1F6AA5", selectforeground="#FFFFFF",
        borderwidth=0, highlightthickness=2, font=("Segoe UI", 14),
        relief="flat", highlightbackground="#1F6AA5",
        highlightcolor="#FFD700", activestyle="none", takefocus=True,
    )
    app.section_listbox.grid(row=1, column=0, sticky="nsew", pady=(6, 10))
    app.section_listbox.bind(
        "<<ListboxSelect>>",
        lambda e: getattr(app, "on_section_select", lambda *_: None)(e)
    )

<<<<<<< HEAD
    app.section_listbox.delete(0, tk.END)
    for i, sec in enumerate(getattr(app, "sections_data", [])):
        app.section_listbox.insert(tk.END, f"{i+1}. {sec.get('title','Untitled')}")
=======
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
>>>>>>> origin/harden/email-sanitize-and-ci

    # Actions under the editor
    actions = ctk.CTkFrame(app.editor_container, fg_color="transparent")
    actions.grid(row=1, column=0, sticky="ew", pady=(8, 0))
    actions.grid_columnconfigure(0, weight=1)

<<<<<<< HEAD
    def _mk(btn_text, cb_attr):
        return ctk.CTkButton(
            actions, text=btn_text, **btn_style,
            command=getattr(app, cb_attr, lambda: None)
        )
=======
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
>>>>>>> origin/harden/email-sanitize-and-ci

    # Use grid instead of pack for all action buttons
    _mk("Copy for Email", "on_copy_for_email_clicked").grid(row=0, column=0, sticky="ew", pady=(0, 6))
    _mk("Send Test Email...", "on_send_test_email_clicked").grid(row=1, column=0, sticky="ew", pady=(0, 6))
    _mk("Export HTML + Text...", "on_export_html_text_clicked").grid(row=2, column=0, sticky="ew", pady=(0, 6))
    _mk("Export Event .ics", "on_export_ics_clicked").grid(row=3, column=0, sticky="ew", pady=(0, 2))

    if hasattr(app, "build_suggestions_panel"):
        sugg = app.build_suggestions_panel(app.editor_container)
        sugg.grid(row=2, column=0, sticky="ew", pady=(8, 0))

    # =========================
    # SETTINGS VIEW (single column)
    # =========================
    settings_view = ctk.CTkFrame(view_container)
    settings_view.grid(row=0, column=0, sticky="nsew")
    settings_view.grid_rowconfigure(0, weight=1)
    settings_view.grid_columnconfigure(0, weight=1)
    all_views["Settings"] = settings_view
    app.settings_view = settings_view

<<<<<<< HEAD
    # Always pass a callable for refresh_callback, not the app instance
    refresh_cb = getattr(app, "refresh_callback", None)
    if not callable(refresh_cb):
        refresh_cb = lambda: None
    app.settings_frame = SettingsFrame(
        settings_view,
        refresh_cb,
        getattr(app, "save_api_key_callback", lambda *a, **kw: None),
        getattr(app, "save_openai_key_callback", lambda *a, **kw: None),
        getattr(app, "save_events_url_callback", lambda *a, **kw: None),
    )
    # The actual form container frame (where labels/entries live)
    app.settings_frame.grid(row=0, column=0, sticky="nw", padx=12, pady=12)
    # Always load latest config and fallback to defaults
    from bulletin_builder.app_core.config import load_google_api_key, load_openai_key, load_events_feed_url
    def _settings_load_defaults():
        # Try to load config values, fallback to sensible defaults
        settings_data = getattr(app, "settings_data", {}) or {}
        google_key = load_google_api_key() or ""
        openai_key = load_openai_key() or ""
        events_url = load_events_feed_url() or ""
        app.events_feed_url = events_url  # Always update the app's attribute
        app.settings_frame.load_data(settings_data, google_key, openai_key, events_url)
    _settings_load_defaults()

    # =========================
    # PREVIEW VIEW (single column)
    # =========================
    preview_view = ctk.CTkFrame(view_container)
    preview_view.grid(row=0, column=0, sticky="nsew")
    preview_view.grid_rowconfigure(1, weight=1)
    preview_view.grid_columnconfigure(0, weight=1)
    all_views["Preview"] = preview_view
    app.preview_view = preview_view

    controls = ctk.CTkFrame(preview_view)
    controls.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 8))
    for i in range(4): controls.grid_columnconfigure(i, weight=(1 if i == 3 else 0))

    app.device_var = tk.StringVar(value="Desktop")
    ctk.CTkOptionMenu(controls, variable=app.device_var,
                      values=["Desktop", "Mobile"]).grid(row=0, column=0, padx=(0, 8))

    app.preview_mode_var = tk.StringVar(value="Code")
    def on_preview_mode_change(choice):
        if choice == "Code":
            app.code_preview.grid(row=1, column=0, sticky="nsew")
            app.rendered_preview.grid_forget()
        else:
            app.rendered_preview.grid(row=1, column=0, sticky="nsew")
            app.code_preview.grid_forget()

    ctk.CTkOptionMenu(controls, variable=app.preview_mode_var,
                      values=["Code", "Rendered"],
                      command=on_preview_mode_change).grid(row=0, column=1, padx=(0, 8))
    ctk.CTkButton(controls, text="Update",
                  command=getattr(app, "update_preview", lambda: None)).grid(row=0, column=2, padx=(0, 8))
    ctk.CTkButton(controls, text="View in Browser",
                  command=getattr(app, "open_in_browser", lambda: None)).grid(row=0, column=3, sticky="e")

    app.rendered_preview = HTMLLabel(preview_view, html="", background="#f4f4f4")
    app.code_preview = tk.Text(preview_view, wrap="word", bg="#f4f4f4", fg="#222", font=("Consolas", 12))
    app.code_preview.insert("1.0", "Ready. Build your bulletin to preview here.")
    app.code_preview.grid(row=1, column=0, sticky="nsew")

    def ensure_preview_visible():
        if not app.code_preview.winfo_ismapped() and not app.rendered_preview.winfo_ismapped():
            app.code_preview.grid(row=1, column=0, sticky="nsew")
    app.ensure_preview_visible = ensure_preview_visible

    # ---------- view switching ----------
    def show_view(name: str):
        for v in all_views.values():
            v.grid_forget()
        if name == "Content":
            app.editor_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
            for child in app.editor_container.winfo_children():
                try: child.grid_forget()
                except Exception:
                    try: child.pack_forget()
                    except Exception: pass
                child.destroy()
            if hasattr(app, "show_section_editor"):
                app.show_section_editor()
        else:
            app.editor_container.grid_forget()
            for child in app.editor_container.winfo_children():
                try: child.grid_forget()
                except Exception:
                    try: child.pack_forget()
                    except Exception: pass
                child.destroy()
        all_views[name].grid(row=0, column=0, sticky="nsew")

    # ---------- prime state ----------
    # populate list and select first AFTER editor exists
    if app.section_listbox.size() > 0 and hasattr(app, "on_section_select"):
        app.section_listbox.selection_set(0)
        app.section_listbox.activate(0)
        app.on_section_select(None)

    on_tab_click("Content")  # show Content + disable its tab

    # ---------- shortcuts ----------
    app.bind("<Control-s>", lambda e: getattr(app, "save_draft", lambda: None)())
    app.bind("<Control-S>", lambda e: getattr(app, "save_draft", lambda: None)())
    app.bind("<Control-Shift-S>", lambda e: getattr(app, "save_draft_as", getattr(app, "save_draft", lambda: None))())
    app.bind("<Control-o>", lambda e: getattr(app, "open_draft", lambda: None)())
    app.bind("<Control-n>", lambda e: getattr(app, "new_draft", lambda: None)())
=======
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
>>>>>>> origin/harden/email-sanitize-and-ci
