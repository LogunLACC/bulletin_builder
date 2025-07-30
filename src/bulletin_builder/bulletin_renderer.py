import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown import markdown
from typing import Optional


class BulletinRenderer:
    def __init__(self, templates_dir, template_name: str = "main_layout.html"):
        """
        Initializes the renderer.
        Args:
            templates_dir (str or Path): The path to the main templates directory.
        """
        self.templates_dir = Path(templates_dir)
        self.template_name = template_name
        if not self.templates_dir.is_dir():
            raise FileNotFoundError(
                f"Templates directory not found at: {self.templates_dir}"
            )

        self.env = Environment(
            loader=FileSystemLoader(
                [
                    self.templates_dir,
                    self.templates_dir / "gallery",
                ]
            ),
            autoescape=select_autoescape(["html", "xml"]),
        )
        # Register a simple Markdown filter
        self.env.filters["markdown"] = lambda text: markdown(
            text or "", output_format="html"
        )

    def set_template(self, name: str):
        """Change the layout template used for rendering."""
        self.template_name = name

    def render_html(
        self,
        sections_data: list,
        settings: dict = None,
        template_name: Optional[str] = None,
    ) -> str:
        """
        Renders the final HTML for the bulletin, injecting theme styles.
        """
        from bulletin_builder.settings import Settings  # ✅ Import your settings class

        if settings is None:
            settings = Settings()
        elif isinstance(settings, dict):
            try:
                settings = Settings(**settings)
            except Exception as e:
                print(f"Failed to cast dict to Settings object: {e}")
                settings = Settings()

        # --- Theme Loading Logic ---
        theme_styles = ""
        theme_filename = settings.theme_css
        if theme_filename:
            theme_path = self.templates_dir / "themes" / theme_filename
            if theme_path.is_file():
                try:
                    theme_styles = theme_path.read_text(encoding="utf-8")
                except Exception as e:
                    print(f"Error reading theme file {theme_path}: {e}")
            else:
                print(f"Theme file not found: {theme_path}")

        try:
            tpl_name = template_name or self.template_name
            template = self.env.get_template(tpl_name)

            html_output = template.render(
                sections=sections_data, settings=settings, theme_styles=theme_styles
            )
            return html_output
        except Exception as e:
            print(f"Error rendering template: {e}")
            return f"<html><body><h1>Template Render Error</h1><p>{e}</p></body></html>"
