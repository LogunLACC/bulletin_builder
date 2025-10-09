
def _add_if(app, menu, label, attr):
    if hasattr(app, attr):
        menu.add_command(label=label, command=getattr(app, attr))

def init(app):
    """Attach the expected file/tool handlers to the app object but do not
    build a menubar here. UI construction (menus) is handled centrally by
    `ui_setup.init` so that only one authoritative menu exists and duplicates
    are avoided.

    This function simply ensures the app exposes the common handler attributes
    so menu building code (ui_setup) can safely reference them.
    """
    # Ensure standard handlers exist (defaults are no-ops so UI items work)
    app.new_draft = getattr(app, 'new_draft', lambda: None)
    app.open_draft = getattr(app, 'open_draft', lambda: None)
    app.save_draft = getattr(app, 'save_draft', lambda save_as=False: None)
    app.import_announcements_csv = getattr(app, 'import_announcements_csv', lambda: None)
    app.import_announcements_sheet = getattr(app, 'import_announcements_sheet', lambda: None)
    app.import_events_feed = getattr(app, 'import_events_feed', lambda url=None: None)
    app.on_export_html_text_clicked = getattr(app, 'on_export_html_text_clicked', lambda: None)
    app.on_export_pdf_clicked = getattr(app, 'on_export_pdf_clicked', lambda: None)
    app.on_copy_for_email_clicked = getattr(app, 'on_copy_for_email_clicked', lambda: None)
    app.open_in_browser = getattr(app, 'open_in_browser', lambda: None)
    app.on_export_ics_clicked = getattr(app, 'on_export_ics_clicked', lambda: None)
    # No UI construction here; ui_setup.build_menus will create the actual menubar.
    return None
