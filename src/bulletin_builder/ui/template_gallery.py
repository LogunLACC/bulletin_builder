import customtkinter as ctk
from tkhtmlview import HTMLLabel
from pathlib import Path

class TemplateGallery(ctk.CTkToplevel):
    """Simple gallery to choose bulletin layout templates."""
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Template Gallery")
        self.geometry("650x500")
        self.transient(app)
        self.grab_set()

        container = ctk.CTkScrollableFrame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        tpl_dir = Path(__file__).resolve().parents[1] / "templates" / "gallery"
        for tpl_path in sorted(tpl_dir.glob("*.html")):
            frame = ctk.CTkFrame(container)
            frame.pack(fill="x", pady=10)

            html = self.app.renderer.render_html([], {"bulletin_title": tpl_path.stem}, template_name=tpl_path.name)
            preview = HTMLLabel(frame, html=html, width=300, height=150, background="white")
            preview.pack(side="left", padx=10)

            btn = ctk.CTkButton(frame, text=f"Use '{tpl_path.stem}'", command=lambda n=tpl_path.name: self.apply_template(n))
            btn.pack(side="left", padx=10, pady=10)

    def apply_template(self, name: str):
        self.app.renderer.set_template(name)
        self.app.show_status_message(f"Template applied: {name}")
        self.app.update_preview()
        self.destroy()
