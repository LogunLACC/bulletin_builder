import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tkhtmlview import HTMLLabel
from ..ui.settings import SettingsFrame
from bulletin_builder.ui.tooltip import add_tooltip

# Modern Design System - 2025 Aesthetic
DESIGN = {
    # Color Palette - Modern, Professional
    "primary": "#2563eb",      # Modern blue
    "primary_hover": "#1d4ed8", # Darker blue on hover
    "secondary": "#6366f1",     # Indigo accent
    "success": "#10b981",       # Green for positive actions
    "danger": "#ef4444",        # Red for destructive actions
    "warning": "#f59e0b",       # Amber for warnings
    
    # Backgrounds
    "bg_main": "#ffffff",       # Main background (light mode)
    "bg_surface": "#f8fafc",    # Slightly elevated surfaces
    "bg_sidebar": "#1e293b",    # Dark sidebar
    "bg_card": "#ffffff",       # Card/panel background
    
    # Text
    "text_primary": "#0f172a",  # Main text
    "text_secondary": "#64748b", # Secondary text
    "text_light": "#ffffff",    # Light text (on dark bg)
    
    # Borders & Dividers
    "border": "#e2e8f0",
    "border_hover": "#cbd5e1",
    
    # Spacing (consistent scale)
    "space_xs": 4,
    "space_sm": 8,
    "space_md": 12,
    "space_lg": 16,
    "space_xl": 24,
    
    # Border Radius
    "radius_sm": 6,
    "radius_md": 8,
    "radius_lg": 12,
    
    # Typography
    "font_family": "Segoe UI",
    "font_size_sm": 12,
    "font_size_base": 14,
    "font_size_lg": 16,
    "font_size_xl": 18,
}

def _show_about_dialog(app):
    """Display a simple About dialog with app version and info."""
    messagebox.showinfo(
        "About Bulletin Builder",
        "LACC Bulletin Builder v0.1.1\n\n"
        "Smart desktop builder for community email bulletins.\n\n"
        "© 2025 Lake Almanor Country Club",
        parent=app
    )

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

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="Email Deliverability Guide (DKIM/SPF/DMARC)",
            command=lambda: getattr(app, 'show_email_auth_guidance', lambda: None)()
        )
        help_menu.add_separator()
        help_menu.add_command(label="About", command=lambda: _show_about_dialog(app))
        menubar.add_cascade(label="Help", menu=help_menu)

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

    # Modern status bar at bottom
    if not hasattr(app, "status_bar"):
        app.status_bar = ctk.CTkLabel(
            app, 
            text="Ready",
            anchor="w",
            fg_color=DESIGN["bg_card"],
            text_color=DESIGN["text_secondary"],
            font=(DESIGN["font_family"], 12),
            height=28,
            corner_radius=0
        )
        app.status_bar.grid(row=1, column=0, sticky="ew", padx=0, pady=0)

    # ---------- right panel (create FIRST) ----------
    if not hasattr(app, "right_panel") or app.right_panel is None:
        app.right_panel = ctk.CTkFrame(app, fg_color="#e0e0e0")
        app.right_panel.grid(row=0, column=0, sticky="nsew", padx=0, pady=10)
        app.right_panel.grid_rowconfigure(0, weight=1)
        app.right_panel.grid_columnconfigure(0, weight=1)

    # Modern Tab Bar with clean design
    tab_bar = ctk.CTkFrame(app.right_panel, fg_color=DESIGN["bg_surface"], height=56)
    tab_bar.grid(row=0, column=0, sticky="ew")
    tab_bar.grid_propagate(False)
    
    view_container = ctk.CTkFrame(app.right_panel, fg_color=DESIGN["bg_main"])
    view_container.grid(row=1, column=0, sticky="nsew")
    app.right_panel.grid_rowconfigure(0, weight=0)
    app.right_panel.grid_rowconfigure(1, weight=1)
    app.right_panel.grid_columnconfigure(0, weight=1)
    view_container.grid_rowconfigure(0, weight=1)
    view_container.grid_columnconfigure(0, weight=1)

    tab_names = ["Content", "Settings", "Preview"]
    app._tab_buttons = {}
    
    # Forward declaration - will be defined after views are created
    show_view_fn = None
    
    def on_tab_click(name: str):
        for n, b in app._tab_buttons.items():
            if n == name:
                # Active tab - solid primary color
                b.configure(
                    fg_color=DESIGN["primary"],
                    hover_color=DESIGN["primary"],
                    text_color=DESIGN["text_light"],
                    border_width=0
                )
            else:
                # Inactive tabs - transparent with subtle hover
                b.configure(
                    fg_color="transparent",
                    hover_color=DESIGN["bg_card"],
                    text_color=DESIGN["text_secondary"],
                    border_width=0
                )
        if show_view_fn:
            show_view_fn(name)

    for i, name in enumerate(tab_names):
        btn = ctk.CTkButton(
            tab_bar,
            text=name,
            width=120,
            height=40,
            corner_radius=DESIGN["radius_md"],
            font=(DESIGN["font_family"], DESIGN["font_size_lg"], "normal"),
            fg_color="transparent",
            hover_color=DESIGN["bg_card"],
            text_color=DESIGN["text_secondary"],
            border_width=0,
            command=lambda n=name: on_tab_click(n)
        )
        btn.grid(row=0, column=i, padx=DESIGN["space_sm"], pady=DESIGN["space_sm"])
        app._tab_buttons[name] = btn
    
    # Set first tab as active
    on_tab_click("Content")

    # ---------- view container ----------
    all_views = {}

    # =========================
    # CONTENT VIEW (2 columns) - Modern Layout
    # =========================
    content_view = ctk.CTkFrame(view_container, fg_color=DESIGN["bg_main"])
    content_view.grid(row=0, column=0, sticky="nsew")
    content_view.grid_rowconfigure(0, weight=1)
    content_view.grid_columnconfigure(0, weight=0)  # left nav fixed
    content_view.grid_columnconfigure(1, weight=1)  # editor grows
    
    # Clean up any stray widgets
    for w in content_view.grid_slaves():
        if int(w.grid_info().get("column", 0)) >= 2:
            w.grid_forget()
            w.destroy()
    all_views["Content"] = content_view
    app.content_view = content_view

    # Modern Editor Container with subtle border
    app.editor_container = ctk.CTkFrame(
        content_view,
        fg_color=DESIGN["bg_card"],
        corner_radius=DESIGN["radius_lg"],
        border_width=1,
        border_color=DESIGN["border"]
    )
    app.editor_container.grid(row=0, column=1, sticky="nsew", padx=DESIGN["space_lg"], pady=DESIGN["space_lg"])
    app.editor_container.grid_rowconfigure(0, weight=1)
    app.editor_container.grid_columnconfigure(0, weight=1)

    # Modern Left Sidebar with dark theme
    left = ctk.CTkFrame(
        content_view,
        fg_color=DESIGN["bg_sidebar"],
        corner_radius=DESIGN["radius_lg"]
    )
    left.grid(row=0, column=0, sticky="nsew", padx=(DESIGN["space_lg"], DESIGN["space_sm"]), pady=DESIGN["space_lg"])
    content_view.grid_columnconfigure(0, minsize=340)
    left.grid_rowconfigure(1, weight=1)

    # Modern Button Group
    button_frame = ctk.CTkFrame(left, fg_color="transparent")
    button_frame.grid(row=0, column=0, sticky="ew", padx=DESIGN["space_md"], pady=DESIGN["space_md"])
    
    # Evenly space buttons
    for col in range(4):
        button_frame.grid_columnconfigure(col, weight=1)

    # Modern button style
    modern_btn_style = {
        "font": (DESIGN["font_family"], DESIGN["font_size_base"], "normal"),
        "height": 36,
        "corner_radius": DESIGN["radius_md"],
        "fg_color": DESIGN["primary"],
        "hover_color": DESIGN["primary_hover"],
        "text_color": DESIGN["text_light"],
        "border_width": 0
    }
    
    button_configs = [
        ("+ Add", getattr(app, "add_section_dialog", lambda: None), 0, DESIGN["success"]),
        ("Remove", getattr(app, "remove_section", lambda: None), 1, DESIGN["danger"]),
        ("↑ Up", getattr(app, "move_section_up", lambda: None), 2, DESIGN["primary"]),
        ("↓ Down", getattr(app, "move_section_down", lambda: None), 3, DESIGN["primary"]),
    ]
    
    for label, cmd, col, color in button_configs:
        b = ctk.CTkButton(
            button_frame,
            text=label,
            command=cmd,
            **{**modern_btn_style, "fg_color": color, "hover_color": color}
        )
        b.grid(row=0, column=col, padx=2, pady=0, sticky="ew")

    # Modern Listbox with better styling
    if hasattr(app, "section_listbox"):
        app.section_listbox.destroy()
    app.section_listbox = tk.Listbox(
        left,
        bg=DESIGN["bg_sidebar"],
        fg=DESIGN["text_light"],
        selectbackground=DESIGN["primary"],
        selectforeground=DESIGN["text_light"],
        borderwidth=0,
        highlightthickness=1,
        highlightbackground=DESIGN["border"],
        highlightcolor=DESIGN["primary"],
        font=(DESIGN["font_family"], DESIGN["font_size_base"]),
        relief="flat",
        activestyle="none",
        takefocus=True,
    )
    app.section_listbox.grid(row=1, column=0, sticky="nsew", padx=DESIGN["space_md"], pady=(DESIGN["space_sm"], DESIGN["space_md"]))
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

    # Actions under the editor - removed (not currently used)
    
    # Refresh callback for settings
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
    # PREVIEW VIEW - Modern Clean Design
    # =========================
    preview_view = ctk.CTkFrame(view_container, fg_color=DESIGN["bg_main"])
    preview_view.grid(row=0, column=0, sticky="nsew")
    preview_view.grid_rowconfigure(1, weight=1)
    preview_view.grid_columnconfigure(0, weight=1)
    all_views["Preview"] = preview_view
    app.preview_view = preview_view

    # Modern Controls Bar with better spacing
    controls = ctk.CTkFrame(
        preview_view,
        fg_color=DESIGN["bg_surface"],
        corner_radius=DESIGN["radius_md"],
        height=52
    )
    controls.grid(row=0, column=0, sticky="ew", padx=DESIGN["space_lg"], pady=(DESIGN["space_lg"], DESIGN["space_md"]))
    controls.grid_propagate(False)
    for i in range(7):
        controls.grid_columnconfigure(i, weight=(1 if i == 6 else 0), pad=DESIGN["space_sm"])

    # Modern dropdown style
    dropdown_style = {
        "corner_radius": DESIGN["radius_md"],
        "fg_color": DESIGN["bg_card"],
        "button_color": DESIGN["primary"],
        "button_hover_color": DESIGN["primary_hover"],
        "dropdown_fg_color": DESIGN["bg_card"],
        "font": (DESIGN["font_family"], DESIGN["font_size_base"]),
        "height": 36
    }
    
    # Modern button style for controls
    control_btn_style = {
        "corner_radius": DESIGN["radius_md"],
        "fg_color": DESIGN["primary"],
        "hover_color": DESIGN["primary_hover"],
        "font": (DESIGN["font_family"], DESIGN["font_size_base"]),
        "height": 36,
        "border_width": 0
    }

    app.device_var = tk.StringVar(value="Desktop")
    def _on_device_change(choice):
        try:
            if hasattr(app, 'set_preview_device'):
                app.set_preview_device(choice)
            if hasattr(app, 'update_preview'):
                app.update_preview()
        except Exception:
            pass
    
    device_menu = ctk.CTkOptionMenu(
        controls,
        variable=app.device_var,
        values=["Desktop", "Tablet", "Mobile"],
        command=_on_device_change,
        **dropdown_style
    )
    device_menu.grid(row=0, column=0, padx=DESIGN["space_sm"], pady=DESIGN["space_sm"], sticky="ew")
    add_tooltip(device_menu, "Preview width: Desktop/Tablet/Mobile")

    # Email client simulation selector
    if not hasattr(app, 'email_client_var'):
        app.email_client_var = tk.StringVar(value="Standard")
    
    def _on_client_change(choice):
        try:
            if hasattr(app, 'update_preview'):
                app.update_preview()
        except Exception:
            pass
    
    client_menu = ctk.CTkOptionMenu(
        controls,
        variable=app.email_client_var,
        values=["Standard", "Gmail", "Outlook", "Apple Mail", "Mobile"],
        command=_on_client_change,
        **dropdown_style
    )
    client_menu.grid(row=0, column=1, padx=DESIGN["space_sm"], pady=DESIGN["space_sm"], sticky="ew")
    add_tooltip(client_menu, "Simulate email client rendering")
    
    # Info button for client details
    info_btn = ctk.CTkButton(
        controls,
        text="ℹ",
        width=36,
        **{**control_btn_style, "fg_color": DESIGN["secondary"], "hover_color": DESIGN["secondary"]},
        command=lambda: getattr(app, 'show_email_client_info', lambda: None)()
    )
    info_btn.grid(row=0, column=2, padx=DESIGN["space_sm"], pady=DESIGN["space_sm"])
    add_tooltip(info_btn, "Show email client rendering details")

    app.preview_mode_var = tk.StringVar(value="Code")
    def on_preview_mode_change(choice):
        if choice == "Code":
            app.code_preview.grid(row=1, column=0, sticky="nsew")
            app.rendered_preview.grid_forget()
        else:
            app.rendered_preview.grid(row=1, column=0, sticky="nsew")
            app.code_preview.grid_forget()

    mode_menu = ctk.CTkOptionMenu(
        controls,
        variable=app.preview_mode_var,
        values=["Code", "Rendered"],
        command=on_preview_mode_change,
        **dropdown_style
    )
    mode_menu.grid(row=0, column=3, padx=DESIGN["space_sm"], pady=DESIGN["space_sm"], sticky="ew")
    add_tooltip(mode_menu, "Switch between raw HTML and rendered preview")

    update_btn = ctk.CTkButton(
        controls,
        text="↻ Update",
        **control_btn_style,
        command=getattr(app, "update_preview", lambda: None)
    )
    update_btn.grid(row=0, column=4, padx=DESIGN["space_sm"], pady=DESIGN["space_sm"], sticky="ew")
    add_tooltip(update_btn, "Re-render preview (Ctrl+U)")

    view_btn = ctk.CTkButton(
        controls,
        text="🌐 Browser",
        **control_btn_style,
        command=getattr(app, "open_in_browser", lambda: None)
    )
    view_btn.grid(row=0, column=5, padx=DESIGN["space_sm"], pady=DESIGN["space_sm"], sticky="ew")
    add_tooltip(view_btn, "Open current preview in your browser")

    export_btn = ctk.CTkButton(
        controls,
        text="📤 Export",
        **{**control_btn_style, "fg_color": DESIGN["success"], "hover_color": DESIGN["success"]},
        command=getattr(app, "export_current_preview", lambda: None)
    )
    export_btn.grid(row=0, column=6, padx=DESIGN["space_sm"], pady=DESIGN["space_sm"], sticky="e")
    add_tooltip(export_btn, "Export body-only HTML for FrontSteps")

    # Modern Preview Area with better styling
    app.preview_area = preview_view
    
    # HTML rendered preview with modern styling
    app.rendered_preview = HTMLLabel(preview_view, html="", background=DESIGN["bg_card"])
    
    # Code preview with modern monospace styling
    app.code_preview = tk.Text(
        preview_view,
        wrap="word",
        bg=DESIGN["bg_card"],
        fg=DESIGN["text_primary"],
        font=("Consolas", 13),
        borderwidth=0,
        highlightthickness=1,
        highlightbackground=DESIGN["border"],
        highlightcolor=DESIGN["primary"],
        padx=DESIGN["space_md"],
        pady=DESIGN["space_md"],
        insertbackground=DESIGN["primary"]
    )
    app.code_preview.insert("1.0", "Ready. Build your bulletin to preview here.")
    app.code_preview.grid(row=1, column=0, sticky="nsew", padx=DESIGN["space_lg"], pady=(0, DESIGN["space_lg"]))

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
        
        all_views.get(name, content_view).grid(row=0, column=0, sticky="nsew")
    
    # Assign to the forward reference so tab clicks work
    show_view_fn = show_view

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
    
    # Modern status message system
    def show_status_message(message: str, duration: int = 3000, type: str = "info"):
        """Show a temporary status message with modern styling."""
        if hasattr(app, "status_bar"):
            # Color code by message type
            if type == "success":
                app.status_bar.configure(text=f"✓ {message}", text_color=DESIGN["success"])
            elif type == "error":
                app.status_bar.configure(text=f"✗ {message}", text_color=DESIGN["danger"])
            elif type == "warning":
                app.status_bar.configure(text=f"⚠ {message}", text_color=DESIGN["warning"])
            else:
                app.status_bar.configure(text=message, text_color=DESIGN["text_secondary"])
            
            # Auto-clear after duration
            if duration > 0:
                app.after(duration, lambda: app.status_bar.configure(text="Ready", text_color=DESIGN["text_secondary"]))
    
    app.show_status_message = show_status_message
