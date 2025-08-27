# app_core/core_init.py
<<<<<<< HEAD

=======
>>>>>>> origin/harden/email-sanitize-and-ci
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
<<<<<<< HEAD
from bulletin_builder.ui.base_section import SectionRegistry

# ensure all UI frame classes register themselves
from bulletin_builder.ui import custom_text  # noqa:F401
from bulletin_builder.ui import events       # noqa:F401
from bulletin_builder.ui import image        # noqa:F401
from bulletin_builder.ui import announcements  # noqa:F401
=======
from ..ui.base_section import SectionRegistry


# ensure all UI frame classes register themselves
from ..ui import custom_text  # noqa:F401
from ..ui import events       # noqa:F401
from ..ui import image        # noqa:F401
from ..ui import announcements  # noqa:F401
>>>>>>> origin/harden/email-sanitize-and-ci

# Helper to list registered section types
SectionRegistry.available_types = classmethod(lambda cls: list(cls._frames.keys()))


def init(app):
<<<<<<< HEAD
    import time
    startup_times = []
    def mark(label):
        t = time.perf_counter()
        startup_times.append((label, t))
        print(f"[PROFILE] {label}: {t:.4f}s")
    mark("start")
    mark("UI helpers ready")
    mark("status bar, progress, base attrs")


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
    app.sections_data = [{
        'title': 'Welcome',
        'type': 'custom_text',
        'content': {'text': 'This is a preview section. Add your content!'}
    }]
=======
    # --- Base attributes ---
    app.sections_data = []
>>>>>>> origin/harden/email-sanitize-and-ci
    app.current_draft_path = None
    app.current_editor_frame = None
    app.active_editor_index = None

    # --- load & configure AI keys ---
    app.google_api_key = load_api_key()
    app.openai_api_key = load_openai_key()
    app.events_feed_url = load_events_feed_url()
<<<<<<< HEAD
    mark("keys loaded")

    # Defer AI API config to first use (lazy)
    def ensure_ai_config():
        if getattr(app, "_ai_configured", False):
            return
        try:
            if app.google_api_key:
                genai.configure(api_key=app.google_api_key)
            if app.openai_api_key:
                openai.api_key = app.openai_api_key
            app._ai_configured = True
            print("[PROFILE] AI APIs configured")
        except Exception as e:
            print(f"[PROFILE] AI config error: {e}")
    app.ensure_ai_config = ensure_ai_config

    # --- Renderer setup ---
    tpl_dir = Path(__file__).parent.parent / "templates"
    app.renderer = BulletinRenderer(templates_dir=tpl_dir)
    app.renderer.set_template('main_layout.html')  # If your Template Gallery changes templates later, it'll use renderer.set_template(...)
    mark("renderer ready")
=======
    # genai.configure(api_key=app.google_api_key)

    # Configure OpenAI when key available
    if app.openai_api_key and app.openai_api_key != "REPLACE ME WITH YOUR OPENAI API KEY":
        openai.api_key = app.openai_api_key    # --- Renderer setup ---
    tpl_dir = Path(__file__).parent.parent / "templates"
    app.renderer = BulletinRenderer(templates_dir=tpl_dir, template_name='main_layout.html')
>>>>>>> origin/harden/email-sanitize-and-ci

    # --- Progress indicator ---
    app.progress = ctk.CTkProgressBar(app, mode="indeterminate")
    app.progress.place(relx=0.5, rely=0.5, anchor="center")
    app.progress.lower()
    mark("progress bar ready")

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
    mark("progress helpers ready")

    # Executor for threaded background tasks like exporting
    app._thread_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
<<<<<<< HEAD
    mark("thread executor ready")

     # --- AI callback ---
    def ai_callback(prompt: str) -> str:
        app.ensure_ai_config()
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(prompt)
            return resp.text
        except Exception as e:
            messagebox.showerror("AI Error", f"AI request failed: {e}")
            return ""
=======

     # --- AI callback ---
    def ai_callback(prompt: str) -> str:
        # try:
        #     model = genai.GenerativeModel("gemini-1.5-flash")
        #     resp = model.generate_content(prompt)
        #     return resp.text
        # except Exception as e:
        #     # messagebox.showerror("AI Error", f"AI request failed: {e}")
        #     return ""
        return "AI response temporarily disabled"
>>>>>>> origin/harden/email-sanitize-and-ci

    app.ai_callback = ai_callback

    def generate_subject_lines(content: str) -> list[str]:
<<<<<<< HEAD
        app.ensure_ai_config()
        if not app.openai_api_key:
            messagebox.showwarning("OpenAI Key Missing", "Please enter your OpenAI API key in Settings.")
            return []
=======
        # if not app.openai_api_key:
        #     messagebox.showwarning("OpenAI Key Missing", "Please enter your OpenAI API key in Settings.")
        #     return []
>>>>>>> origin/harden/email-sanitize-and-ci
        try:
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
            # messagebox.showerror("AI Error", f"OpenAI request failed: {e}")
            return []

    app.generate_subject_lines = generate_subject_lines
<<<<<<< HEAD
    mark("handlers, drafts, sections, exporter, preview, UI setup")
    mark("editor container ready")
    print("[PROFILE] Startup complete. Timings:")
    t0 = startup_times[0][1]
    for label, t in startup_times:
        print(f"  {label:30s} {t-t0:8.4f}s")

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

    import os
    if os.environ.get("BB_DEBUG_RP") == "1":
        # --- BATTLE-TESTED RP/EDITOR SETUP ---
        # Always create right_panel and editor_container, even if UI setup missed it
        if hasattr(app, "right_panel"):
            app.right_panel.destroy()
        app.right_panel = ctk.CTkFrame(app, fg_color="#e0e0e0")
        app.right_panel.grid(row=0, column=1, sticky="nsew", padx=0, pady=10)
        app.right_panel.grid_rowconfigure(0, weight=1)
        app.right_panel.grid_columnconfigure(0, weight=1)
        app.grid_columnconfigure(0, weight=3)  # main content
        app.grid_columnconfigure(1, weight=3)  # right panel
        if hasattr(app, "editor_container"):
            app.editor_container.destroy()
        app.editor_container = ctk.CTkFrame(app.right_panel, fg_color="#ffcccc")  # Debug: red background
        app.editor_container.grid(row=0, column=0, sticky="nsew")
        print("[DEBUG] right_panel and editor_container created and gridded.")

        # Helper to replace the editor frame (always clears old one)
        def replace_editor_frame(new_frame):
            if not hasattr(app, "editor_container"):
                print("[ERROR] editor_container missing!")
                return
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
                    print(f"[DEBUG] Packing new editor frame: {new_frame}")
                    new_frame.pack(fill="both", expand=True)
                    new_frame.update_idletasks()
                    app.current_editor_frame = new_frame
                    print(f"[DEBUG] editor_container children: {[str(w) for w in app.editor_container.winfo_children()]}")
                except Exception as e:
                    print(f"[DEBUG] Could not pack new editor frame: {e}")
            else:
                app.current_editor_frame = None
        app.replace_editor_frame = replace_editor_frame

        from bulletin_builder.app_core import component_library
        component_library.init(app)
=======
>>>>>>> origin/harden/email-sanitize-and-ci
