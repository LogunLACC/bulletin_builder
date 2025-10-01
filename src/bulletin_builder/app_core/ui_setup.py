import customtkinter as ctk
import tkinter as tk
from tkhtmlview import HTMLLabel
from ..ui.settings import SettingsFrame
from bulletin_builder.ui.tooltip import add_tooltip

def init(app):
    """Construct the main UI elements on the provided app instance.

    This function intentionally performs all GUI creation only when called so
    that importing this module is safe in headless/test environments.
    """

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
            for child in app.editor_container.winfo_children():
                if child is new_frame:
                    continue
                try:
                    child.grid_forget()
                except Exception:
                    pass
                child.destroy()
            # Ensure it's created with the correct parent
            if new_frame.master is not parent:
                raise RuntimeError("Editor frame must be created with parent=app.editor_container")
            parent.grid_rowconfigure(0, weight=1)
            parent.grid_columnconfigure(0, weight=1)
            new_frame.grid(row=0, column=0, sticky="nsew")
            if hasattr(app, "status_bar"):
                app.status_bar.configure(text="Editor ready.")
        app.replace_editor_frame = replace_editor_frame

    # Full menu builder -------------------------------------------------
    def _build_menus(app):
        """Attach a rich menu bar wired to known app handlers.

        This mirrors the fallback in __main__ but may include richer
        application-specific commands when available.
        """
        import tkinter as tk

        menubar = tk.Menu(app)
        file_menu = tk.Menu(menubar, tearoff=0)
        # Expose for tests and potential external customization
        try:
            app._menubar = menubar
            app._file_menu = file_menu
        except Exception:
            pass
        
        # In test mode, we want missing handlers to raise an error.
        # In production, we want silent failure to prevent crashes.
        is_test_mode = hasattr(app, "_is_test_mode") and app._is_test_mode

        def add(label, attr):
            # Defer resolution of handler until the menu item is invoked so
            # the menu shows even if the handler is attached later during init.
            def _cmd():
                if is_test_mode and not hasattr(app, attr):
                    raise AttributeError(f"Test failed: Menu handler '{attr}' not found on app instance.")

                fn = getattr(app, attr, None)
                if callable(fn):
                    return fn()
            file_menu.add_command(label=label, command=_cmd)

        # Primary file actions (new/open/save) — always visible but resolved lazily
        file_menu.add_command(label="New Draft", command=lambda: getattr(app, 'new_draft', lambda: None)())
        file_menu.add_separator()
        file_menu.add_command(label="Open Draft...", command=lambda: getattr(app, 'open_draft', lambda: None)())
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=lambda: getattr(app, 'save_draft', lambda save_as=False: None)())
        file_menu.add_command(label="Save As...", command=lambda: getattr(app, 'save_draft', lambda save_as=False: None)(save_as=True))
        file_menu.add_separator()

        add("Export Bulletin (FrontSteps)", "export_current_preview")
        add("Open in Browser", "open_in_browser")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=app.destroy)

        # Removed legacy Export submenu; only FrontSteps export remains

        menubar.add_cascade(label="File", menu=file_menu)

        # Tools menu (optional but helpful)
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Import Announcements CSV...", command=lambda: getattr(app, 'import_announcements_csv', lambda: None)())
        tools_menu.add_command(label="Import Events Feed...", command=lambda: getattr(app, 'import_events_feed', lambda: None)())
        tools_menu.add_separator()
        tools_menu.add_command(label="Run Auto Sync", command=lambda: getattr(app, 'auto_sync_events_feed', lambda *a, **k: None)(True))
        menubar.add_cascade(label="Tools", menu=tools_menu)

        try:
            app.configure(menu=menubar)
        except Exception:
            # On some lightweight widgets or tests configuring a menu can fail.
            pass

    # Attach the full menu builder to the app so __main__ can call it
    app._build_menus = lambda: _build_menus(app)

    # ---------- window + base grid ----------
    app.title("LACC Bulletin Builder")
    # Do not force geometry here; respect the startup state (often maximized)
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

    app.section_listbox.delete(0, tk.END)
    for i, sec in enumerate(getattr(app, "sections_data", [])):
        app.section_listbox.insert(tk.END, f"{i+1}. {sec.get('title','Untitled')}")

    # Smart Suggestions panel (optional)
    try:
        if hasattr(app, "build_suggestions_panel"):
            _sug_frame = app.build_suggestions_panel(left)
            _sug_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
            # Populate suggestions once UI exists
            if hasattr(app, "compute_suggestions"):
                app.after(100, app.compute_suggestions)
    except Exception:
        pass

    # Actions under the editor
    actions = ctk.CTkFrame(app.editor_container, fg_color="transparent")
    actions.grid(row=1, column=0, sticky="ew", pady=(8, 0))
    actions.grid_columnconfigure(0, weight=1)

    def _mk(btn_text, cb_attr):
        return ctk.CTkButton(
            actions, text=btn_text, **btn_style,
            command=getattr(app, cb_attr, lambda: None)
        )

    # Always pass a callable for refresh_callback, not the app instance
    refresh_cb = getattr(app, "refresh_callback", None)
    if not callable(refresh_cb):
        def refresh_cb():
            return None
    # Create the settings view container if not already created
    settings_view = ctk.CTkFrame(view_container)
    settings_view.grid(row=0, column=0, sticky="nsew")
    settings_view.grid_rowconfigure(0, weight=1)
    settings_view.grid_columnconfigure(0, weight=1)
    all_views["Settings"] = settings_view
    app.settings_view = settings_view

    app.settings_frame = SettingsFrame(
        settings_view,
        refresh_cb,
        getattr(app, "save_api_key_callback", lambda *a, **kw: None),
        getattr(app, "save_openai_key_callback", lambda *a, **kw: None),
        getattr(app, "save_events_url_callback", lambda *a, **kw: None),
    )
    # The actual form container frame (where labels/entries live)
    settings_view.grid_rowconfigure(0, weight=1)
    settings_view.grid_columnconfigure(0, weight=1)
    app.settings_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
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
    for i in range(5):
        controls.grid_columnconfigure(i, weight=(1 if i == 4 else 0))

    app.device_var = tk.StringVar(value="Desktop")
    def _on_device_change(choice):
        try:
            if hasattr(app, 'set_preview_device'):
                app.set_preview_device(choice)
            if hasattr(app, 'update_preview'):
                app.update_preview()
        except Exception:
            pass
    device_menu = ctk.CTkOptionMenu(controls, variable=app.device_var,
                                    values=["Desktop", "Tablet", "Mobile"],
                                    command=_on_device_change)
    device_menu.grid(row=0, column=0, padx=(0, 8))
    add_tooltip(device_menu, "Preview width: Desktop/Tablet/Mobile")

    app.preview_mode_var = tk.StringVar(value="Code")
    def on_preview_mode_change(choice):
        if choice == "Code":
            app.code_preview.grid(row=1, column=0, sticky="nsew")
            app.rendered_preview.grid_forget()
        else:
            app.rendered_preview.grid(row=1, column=0, sticky="nsew")
            app.code_preview.grid_forget()

    mode_menu = ctk.CTkOptionMenu(controls, variable=app.preview_mode_var,
                                  values=["Code", "Rendered"],
                                  command=on_preview_mode_change)
    mode_menu.grid(row=0, column=1, padx=(0, 8))
    add_tooltip(mode_menu, "Switch between raw HTML and rendered preview")

    update_btn = ctk.CTkButton(controls, text="Update",
                               command=getattr(app, "update_preview", lambda: None))
    update_btn.grid(row=0, column=2, padx=(0, 8))
    add_tooltip(update_btn, "Re-render preview (Ctrl+U)")

    view_btn = ctk.CTkButton(controls, text="View in Browser",
                             command=getattr(app, "open_in_browser", lambda: None))
    view_btn.grid(row=0, column=3, padx=(0, 8))
    add_tooltip(view_btn, "Open current preview in your browser")

    export_btn = ctk.CTkButton(controls, text="Export (FrontSteps)",
                               command=getattr(app, "export_current_preview", lambda: None))
    export_btn.grid(row=0, column=4, sticky="e")
    add_tooltip(export_btn, "Export body-only HTML for FrontSteps")

    # Expose a preview area reference for device width tweaks
    app.preview_area = preview_view
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
                try:
                    child.grid_forget()
                except Exception:
                    try:
                        child.pack_forget()
                    except Exception:
                        pass
                child.destroy()
            if hasattr(app, "show_section_editor"):
                app.show_section_editor()
        else:
            app.editor_container.grid_forget()
            for child in app.editor_container.winfo_children():
                try:
                    child.grid_forget()
                except Exception:
                    try:
                        child.pack_forget()
                    except Exception:
                        pass
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
