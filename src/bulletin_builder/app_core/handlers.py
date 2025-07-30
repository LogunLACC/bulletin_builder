import customtkinter as ctk

def init(app):
    """
    Attach utility handlers: 
      - clear_editor_panel (for resetting the right‐hand editor)
      - show_placeholder (for initial “no section selected” UI)
      - refresh_listbox_titles (for syncing the Contents list)
      - show_status_message (status bar feedback)
      - _show_progress / _hide_progress (progress spinner)
    """

    # --- Clear the current editor panel ---
    def clear_editor_panel():
        if hasattr(app, 'current_editor_frame') and app.current_editor_frame:
            app.current_editor_frame.destroy()
        app.current_editor_frame = None
        app.active_editor_index = None
    app.clear_editor_panel = clear_editor_panel

    # --- Placeholder when no section is selected ---
    def show_placeholder(message="Select a section..."):
        # tear down any existing editor
        app.clear_editor_panel()
        placeholder = ctk.CTkLabel(
            app.right_panel, text=message, font=ctk.CTkFont(size=18)
        )
        placeholder.pack(expand=True, padx=20, pady=20)
        app.current_editor_frame = placeholder
    app.show_placeholder = show_placeholder

    # --- Refresh the section list titles ---
    def refresh_listbox_titles():
        sel = app.section_listbox.curselection()
        app.section_listbox.delete(0, 'end')
        for i, sec in enumerate(app.sections_data):
            title = sec.get('title', 'Untitled')
            app.section_listbox.insert('end', f"{i+1}. {title}")
        for i in sel:
            app.section_listbox.selection_set(i)
    app.refresh_listbox_titles = refresh_listbox_titles

    # --- Status bar messages ---
    def show_status_message(msg, duration=4000):
        app.status_bar.configure(text=msg)
        app.after(duration, lambda: app.status_bar.configure(text=""))
    app.show_status_message = show_status_message

    # --- Progress spinner controls ---
    def _show_progress(msg=None):
        if msg:
            app.show_status_message(msg)
        app.progress.start()
        app.progress.lift()
    def _hide_progress():
        app.progress.stop()
        app.progress.lower()
    app._show_progress = _show_progress
    app._hide_progress = _hide_progress

    # --- Launch the WYSIWYG editor ---
    from ..wysiwyg_editor import WysiwygEditor
    from ..ui.template_gallery import TemplateGallery

    def open_wysiwyg_editor():
        WysiwygEditor(app)

    def open_template_gallery():
        TemplateGallery(app)

    app.open_wysiwyg_editor = open_wysiwyg_editor
    app.open_template_gallery = open_template_gallery
