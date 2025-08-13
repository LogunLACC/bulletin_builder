# -*- coding: utf-8 -*-
import customtkinter as ctk

def move_section_up(app):
    """Move the selected section up in the listbox and data model."""
    try:
        sel = app.section_listbox.curselection()
        if not sel:
            return
        idx = int(sel[0])
        if idx <= 0:
            return
        app.sections_data[idx - 1], app.sections_data[idx] = app.sections_data[idx], app.sections_data[idx - 1]
        app.refresh_listbox_titles()
        app.section_listbox.selection_clear(0, ctk.END)
        app.section_listbox.selection_set(idx - 1)
        app.section_listbox.activate(idx - 1)
        if hasattr(app, "update_preview"):
            app.update_preview()
    except Exception as e:
        print(f"Error moving section up: {e}")

def move_section_down(app):
    """Move the selected section down in the listbox and data model."""
    try:
        sel = app.section_listbox.curselection()
        if not sel:
            return
        idx = int(sel[0])
        if idx >= len(app.sections_data) - 1:
            return
        app.sections_data[idx + 1], app.sections_data[idx] = app.sections_data[idx], app.sections_data[idx + 1]
        app.refresh_listbox_titles()
        app.section_listbox.selection_clear(0, ctk.END)
        app.section_listbox.selection_set(idx + 1)
        app.section_listbox.activate(idx + 1)
        if hasattr(app, "update_preview"):
            app.update_preview()
    except Exception as e:
        print(f"Error moving section down: {e}")

def init(app):
    """Attach simple handlers that other modules (menu/ui) can call."""
    # WYSIWYG / Templates are optional; only wire if available
    try:
        from bulletin_builder.wysiwyg_editor import WysiwygEditor  # noqa
        def open_wysiwyg_editor():
            WysiwygEditor(app)
        app.open_wysiwyg_editor = open_wysiwyg_editor
    except Exception:
        pass

    try:
        from bulletin_builder.ui.template_gallery import TemplateGallery  # noqa
        def open_template_gallery():
            TemplateGallery(app)
        app.open_template_gallery = open_template_gallery
    except Exception:
        pass

    app.move_section_up = lambda: move_section_up(app)
    app.move_section_down = lambda: move_section_down(app)
