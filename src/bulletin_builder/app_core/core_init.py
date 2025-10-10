# app_core/core_init.py

import customtkinter as ctk
from pathlib import Path
from typing import Any
import concurrent.futures

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


def init(app: Any) -> None:
    """
    Initialize core application components and attributes.
    
    Sets up:
    - Section data structures
    - API keys (Google, OpenAI)
    - Bulletin renderer with templates
    - Progress indicators
    - Background thread executor
    - AI callback system
    
    Args:
        app: Application instance to initialize
    """
    # --- Base attributes ---
    app.sections_data = []
    app.current_draft_path = None
    app.current_editor_frame = None
    app.active_editor_index = None

    # --- load & configure AI keys ---
    app.google_api_key = load_api_key()
    app.openai_api_key = load_openai_key()
    app.events_feed_url = load_events_feed_url()

    # Configure OpenAI when key available
    if app.openai_api_key and app.openai_api_key != "REPLACE ME WITH YOUR OPENAI API KEY":
        openai.api_key = app.openai_api_key

    # --- Renderer setup ---
    tpl_dir = Path(__file__).parent.parent / "templates"
    app.renderer = BulletinRenderer(templates_dir=tpl_dir, template_name='main_layout.html')
    
    # Add render_bulletin_html method that uses the real renderer
    def render_bulletin_html(ctx: dict) -> str:
        """Render bulletin HTML using the template renderer."""
        return app.renderer.render(ctx)
    
    app.render_bulletin_html = render_bulletin_html
    
    # Add collect_context method for gathering render context
    def collect_context() -> dict:
        """Collect all context needed for rendering."""
        settings = app.settings_frame.dump() if hasattr(app, 'settings_frame') else {}
        return {
            'title': settings.get('bulletin_title', 'Bulletin'),
            'date': settings.get('bulletin_date', ''),
            'sections': getattr(app, 'sections_data', []),
            'settings': settings
        }
    
    app.collect_context = collect_context

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
        return "AI response temporarily disabled"

    app.ai_callback = ai_callback

    def generate_subject_lines(content: str) -> list[str]:
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
            lines = [line.strip("-•* ") for line in text.splitlines() if line.strip()]
            return lines
        except Exception:
            return []

    app.generate_subject_lines = generate_subject_lines

    # --- Status message helper ---
    def show_status_message(msg: str, duration_ms: int = 2000):
        try:
            if hasattr(app, "status_bar"):
                app.status_bar.configure(text=msg or "")
                if duration_ms and duration_ms > 0:
                    app.after(duration_ms, lambda: app.status_bar.configure(text=""))
        except Exception:
            pass

    app.show_status_message = show_status_message
