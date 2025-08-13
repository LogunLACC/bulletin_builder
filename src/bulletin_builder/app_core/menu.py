import tkinter as tk

def _add_if(app, menu, label, attr):
    if hasattr(app, attr):
        menu.add_command(label=label, command=getattr(app, attr))

def init(app):
    """Register the File menu items on the main application."""
    menubar = tk.Menu(app)
    filemenu = tk.Menu(menubar, tearoff=0)
    # New/Open/Save commands
    filemenu.add_command(label="New Draft", command=app.new_draft)
    filemenu.add_separator()
    filemenu.add_command(label="Open Draft...", command=app.open_draft)
    filemenu.add_separator()
    filemenu.add_command(label="Save", command=app.save_draft)
    filemenu.add_command(label="Save As...", command=lambda: app.save_draft(save_as=True))
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=app.quit)

    _add_if(app, filemenu, "Import Announcements CSV…", "import_announcements_csv")
    _add_if(app, filemenu, "Import Google Sheet (CSV)…", "import_announcements_sheet")
    _add_if(app, filemenu, "Import Events Feed…", "import_events_feed")
    filemenu.add_separator()
    _add_if(app, filemenu, "Export HTML & Text…", "on_export_html_text_clicked")
    _add_if(app, filemenu, "Copy Email-Ready HTML", "on_copy_for_email_clicked")
    _add_if(app, filemenu, "Open in Browser", "open_in_browser")
    _add_if(app, filemenu, "Export Calendar (.ics)…", "on_export_ics_clicked")
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=app.quit)

    menubar.add_cascade(label="File", menu=filemenu)
    app.config(menu=menubar)
