import customtkinter as ctk
import tkinter as tk


def init(app):
    """Attach smart suggestion helpers to the application."""

    def build_panel(parent):
        frame = ctk.CTkFrame(parent)
        ctk.CTkLabel(frame, text="Smart Suggestions").pack(anchor="w")
        listbox = tk.Listbox(
            frame,
            bg="#2B2B2B",
            fg="white",
            selectbackground="#1F6AA5",
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            height=5,
            font=("Roboto", 10),
        )
        listbox.pack(fill="both", expand=True, pady=(5, 0))
        listbox.bind("<Double-Button-1>", apply_suggestion)
        app.suggestions_list = listbox
        return frame

    def compute_suggestions():
        suggestions = []
        events_sections = [
            sec
            for sec in app.sections_data
            if sec.get("type") in ("events", "lacc_events", "community_events")
        ]
        total_events = sum(len(sec.get("content", [])) for sec in events_sections)
        has_highlights = any(
            "Community Highlights" in sec.get("title", "") for sec in app.sections_data
        )
        if total_events >= 5 and not has_highlights:
            suggestions.append("Add a 'Community Highlights' banner")
        if not suggestions:
            suggestions.append("No suggestions")
        app.suggestions_list.delete(0, tk.END)
        for s in suggestions:
            app.suggestions_list.insert(tk.END, s)

    def apply_suggestion(event=None):
        sel = app.suggestions_list.curselection()
        if not sel:
            return
        suggestion = app.suggestions_list.get(sel[0])
        if "Community Highlights" in suggestion:
            app.sections_data.append(
                {
                    "title": "Community Highlights",
                    "type": "announcements",
                    "body": "Highlight key upcoming events here.",
                    "link": "",
                    "link_text": "",
                }
            )
            app.refresh_listbox_titles()
            app.show_placeholder()
            app.update_preview()
        compute_suggestions()

    app.compute_suggestions = compute_suggestions
    app.apply_suggestion = apply_suggestion
    app.build_suggestions_panel = build_panel
