import tkinter as tk


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

    menubar.add_cascade(label="File", menu=filemenu)
    app.config(menu=menubar)
