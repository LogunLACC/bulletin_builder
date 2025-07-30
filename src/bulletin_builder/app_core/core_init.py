# app_core/core_init.py
import customtkinter as ctk
import tkinter.messagebox as messagebox
from pathlib import Path
import concurrent.futures

import google.generativeai as genai

from ..bulletin_renderer import BulletinRenderer
from .config import load_api_key
from ..ui.base_section import SectionRegistry


# ensure all UI frame classes register themselves
from ..ui import custom_text  # noqa:F401
from ..ui import events       # noqa:F401
from ..ui import image        # noqa:F401
from ..ui import announcements  # noqa:F401

# Helper to list registered section types
SectionRegistry.available_types = classmethod(lambda cls: list(cls._frames.keys()))


def init(app):
    # --- Base attributes ---
    app.sections_data = []
    app.current_draft_path = None
    app.current_editor_frame = None
    app.active_editor_index = None

    # --- load & configure AI key ---
    app.google_api_key = load_api_key()
    genai.configure(api_key=app.google_api_key)

    # --- Renderer setup ---
    tpl_dir = Path(__file__).parent.parent / "templates"
    app.renderer = BulletinRenderer(templates_dir=tpl_dir)

    # --- Progress indicator ---
    app.progress = ctk.CTkProgressBar(app, mode="indeterminate")
    app.progress.place(relx=0.5, rely=0.5, anchor="center")
    app.progress.lower()

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

    # --- Core UI handlers (placeholder, list-refresh, etc.) ---
    from .handlers import init as handlers_init
    handlers_init(app)

    # --- Draft management (new/open/save) ---
    from .drafts import init as drafts_init
    drafts_init(app)

    # --- Section CRUD & editors ---
    from .sections import init as sections_init
    sections_init(app)

    # --- Export & email handlers ---
    from .exporter import init as exporter_init
    exporter_init(app)

    # --- Preview rendering (background thread, image fetch) ---
    from .preview import init as preview_init
    preview_init(app)

    # --- Finally: build the UI (menus, tabs, controls) ---
    from .ui_setup import init as ui_setup_init
    ui_setup_init(app)
