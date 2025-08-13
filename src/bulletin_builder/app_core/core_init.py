# app_core/core_init.py

import customtkinter as ctk
import tkinter.messagebox as messagebox
from pathlib import Path
import concurrent.futures

import google.generativeai as genai
import openai

from bulletin_builder.bulletin_renderer import BulletinRenderer
from bulletin_builder.app_core.config import (
    load_api_key,
    load_openai_key,
    load_events_feed_url,
)
from bulletin_builder.ui.base_section import SectionRegistry

# ensure all UI frame classes register themselves
from bulletin_builder.ui import custom_text  # noqa:F401
from bulletin_builder.ui import events       # noqa:F401
from bulletin_builder.ui import image        # noqa:F401
from bulletin_builder.ui import announcements  # noqa:F401

# Helper to list registered section types
SectionRegistry.available_types = classmethod(lambda cls: list(cls._frames.keys()))


def init(app):


    # (moved to after UI setup)

    def clear_editor_panel():
        try:
            print("[DEBUG] clear_editor_panel called")
            if hasattr(app, "editor_panel"):
                children = app.editor_panel.winfo_children()
                print(f"[DEBUG] editor_panel has {len(children)} children: {[str(w) for w in children]}")
                for w in children:
                    print(f"[DEBUG] Destroying widget: {w}")
                    w.destroy()
        except Exception as e:
            print(f"[DEBUG] Exception in clear_editor_panel: {e}")

    def build_editor_panel(section: dict | None):
        """Very simple editor stub—replace with your real widgets."""
        clear_editor_panel()
        if not hasattr(app, "editor_panel"):
            return
        title = (section or {}).get("title", "Untitled")
        ctk.CTkLabel(app.editor_panel, text=f"Editing: {title}").pack(anchor="w", padx=8, pady=8)

    if not hasattr(app, "clear_editor_panel"):
        app.clear_editor_panel = clear_editor_panel
    if not hasattr(app, "build_editor_panel"):
        app.build_editor_panel = build_editor_panel

    # --- Optional: build_suggestions_panel no-op ---
    if not hasattr(app, "build_suggestions_panel"):
        def build_suggestions_panel(_parent=None):
            frame = ctk.CTkFrame(_parent) if _parent is not None else ctk.CTkFrame(app)
            ctk.CTkLabel(frame, text="No suggestions available.").pack(padx=8, pady=8)
            return frame
        app.build_suggestions_panel = build_suggestions_panel
    # --- Status bar (bottom) ---
    if not hasattr(app, "status_bar"):
        app.status_bar = ctk.CTkLabel(app, text="", anchor="w")
        app.status_bar.grid(row=1, column=0, sticky="ew", padx=10)

    # clear any previous scheduled clear
    app._status_clear_job = None

    def show_status_message(message: str, *, level: str = "info", timeout_ms: int = 3000):
        """
        Show a transient message in the status bar.
        level: "info" | "warn" | "error" (you can style if you want)
        timeout_ms: auto-clear after this many ms; use 0/None to keep it.
        """
        try:
            prefix = {"info": "", "warn": "⚠ ", "error": "✖ "}.get(level, "")
            app.status_bar.configure(text=f"{prefix}{message}")
            # cancel previous clear, if any
            if app._status_clear_job:
                try:
                    app.after_cancel(app._status_clear_job)
                except Exception:
                    pass
                app._status_clear_job = None
            if timeout_ms:
                app._status_clear_job = app.after(timeout_ms, lambda: app.status_bar.configure(text=""))
        except Exception:
            # Last-ditch: avoid crashing if status bar isn't ready yet
            print(f"[status:{level}] {message}")

    app.show_status_message = show_status_message

    # --- Optional: progress helpers (used by exporter/importer) ---
    if not hasattr(app, "progress"):
        app.progress = ctk.CTkProgressBar(app, mode="indeterminate")
        app.progress.place(relx=0.5, rely=0.5, anchor="center")
        app.progress.lower()

    def _show_progress(msg: str = ""):
        try:
            if msg:
                app.show_status_message(msg, level="info", timeout_ms=0)
            app.progress.lift()
            app.progress.start()
            app.update_idletasks()
        except Exception:
            pass

    def _hide_progress():
        try:
            app.progress.stop()
            app.progress.lower()
            app.show_status_message("", timeout_ms=0)
            app.update_idletasks()
        except Exception:
            pass

    app._show_progress = _show_progress
    app._hide_progress = _hide_progress
    # --- Base attributes ---
    app.sections_data = []
    app.current_draft_path = None
    app.current_editor_frame = None
    app.active_editor_index = None

    # --- load & configure AI keys ---
    app.google_api_key = load_api_key()
    app.openai_api_key = load_openai_key()
    app.events_feed_url = load_events_feed_url()
    genai.configure(api_key=app.google_api_key)

    # Configure OpenAI when key available
    if app.openai_api_key:
        openai.api_key = app.openai_api_key

    # --- Renderer setup ---
    tpl_dir = Path(__file__).parent.parent / "templates"
    app.renderer = BulletinRenderer(templates_dir=tpl_dir, template_name='main_layout.html')

    # --- Progress indicator ---
    app.progress = ctk.CTkProgressBar(app, mode="indeterminate")
    app.progress.place(relx=0.5, rely=0.5, anchor="center")
    app.progress.lower()

    def _show_progress(msg: str = ""):
        try:
            if hasattr(app, "status_bar"):
                app.status_bar.configure(text=msg or "")
            app.progress.lift()
            app.progress.start()
            app.update_idletasks()
        except Exception:
            pass

    def _hide_progress():
        try:
            app.progress.stop()
            app.progress.lower()
            if hasattr(app, "status_bar"):
                app.status_bar.configure(text="")
            app.update_idletasks()
        except Exception:
            pass

    app._show_progress = _show_progress
    app._hide_progress = _hide_progress

    # Executor for threaded background tasks like exporting
    app._thread_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

     # --- AI callback ---
    def ai_callback(prompt: str) -> str:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(prompt)
            return resp.text
        except Exception as e:
            messagebox.showerror("AI Error", f"AI request failed: {e}")
            return ""

    app.ai_callback = ai_callback

    def generate_subject_lines(content: str) -> list[str]:
        if not app.openai_api_key:
            messagebox.showwarning("OpenAI Key Missing", "Please enter your OpenAI API key in Settings.")
            return []
        try:
            openai.api_key = app.openai_api_key
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You craft short, catchy email subject lines."},
                    {
                        "role": "user",
                        "content": f"Generate three catchy subject lines for this bulletin:\n{content}\nReturn each on a new line without numbering."
                    },
                ],
                temperature=0.7,
            )
            text = resp.choices[0].message.content.strip()
            lines = [l.strip("-•* ") for l in text.splitlines() if l.strip()]
            return lines
        except Exception as e:
            messagebox.showerror("AI Error", f"OpenAI request failed: {e}")
            return []

    app.generate_subject_lines = generate_subject_lines

    # --- Core UI handlers (placeholder, list-refresh, etc.) ---
    from bulletin_builder.app_core.handlers import init as handlers_init
    handlers_init(app)

    # --- Draft management (new/open/save) ---
    from bulletin_builder.app_core.drafts import init as drafts_init
    drafts_init(app)

    # --- Section CRUD & editors ---
    from bulletin_builder.app_core.sections import init as sections_init
    sections_init(app)

    # --- Export & email handlers ---
    from bulletin_builder.app_core.exporter import init as exporter_init
    exporter_init(app)

    # --- Preview rendering (background thread, image fetch) ---
    from bulletin_builder.app_core.preview import init as preview_init
    preview_init(app)

    # --- Finally: build the UI (menus, tabs, controls) ---
    from bulletin_builder.app_core.ui_setup import init as ui_setup_init
    ui_setup_init(app)

    # Now that right_panel exists, create a single editor container inside it
    if hasattr(app, "right_panel") and not hasattr(app, "editor_container"):
        app.editor_container = ctk.CTkFrame(app.right_panel, fg_color="#ffcccc")  # Debug: red background
        app.editor_container.pack(fill="both", expand=True)
        # Ensure right_panel expands using grid, not pack
        app.right_panel.grid(row=0, column=1, sticky="nsew")
        # Remove pack_propagate(False) unless explicit size is set
        app.right_panel.grid_propagate(False)
        app.editor_container.pack_propagate(True)
        app.editor_container.grid_propagate(True)

    # Helper to replace the editor frame (always clears old one)
    def replace_editor_frame(new_frame):
        if hasattr(app, "editor_container"):
            # Destroy previous editor frame if it exists
            if getattr(app, "current_editor_frame", None) is not None:
                try:
                    app.current_editor_frame.destroy()
                    print(f"[DEBUG] Destroyed previous editor frame: {app.current_editor_frame}")
                except Exception as e:
                    print(f"[DEBUG] Could not destroy previous editor frame: {e}")
                app.current_editor_frame = None
            if new_frame is not None:
                try:
                    print(f"[DEBUG] Attempting to pack new editor frame: {new_frame}, parent: {new_frame.master}, parent is editor_container: {new_frame.master is app.editor_container}")
                    print(f"[DEBUG] new_frame.winfo_exists(): {new_frame.winfo_exists()}")
                    print(f"[DEBUG] new_frame.winfo_ismapped(): {new_frame.winfo_ismapped()}")
                    if str(new_frame) and app.editor_container.winfo_ismapped():
                        new_frame.pack_forget()  # Remove any previous packing
                        new_frame.pack(fill="both", expand=True)
                        new_frame.update_idletasks()
                        app.current_editor_frame = new_frame
                        # Print geometry info for debug
                        print(f"[DEBUG] editor_container size: {app.editor_container.winfo_width()}x{app.editor_container.winfo_height()}")
                        print(f"[DEBUG] new_frame size: {new_frame.winfo_width()}x{new_frame.winfo_height()}")
                        print(f"[DEBUG] Packed new editor frame: {new_frame}")
                        print(f"[DEBUG] editor_container children: {[str(w) for w in app.editor_container.winfo_children()]}")
                    else:
                        print(f"[DEBUG] Skipping pack: frame destroyed or editor_container not mapped")
                except Exception as e:
                    print(f"[DEBUG] Could not pack new editor frame: {e}")
            else:
                app.current_editor_frame = None
    app.replace_editor_frame = replace_editor_frame

    from bulletin_builder.app_core import component_library
    component_library.init(app)
