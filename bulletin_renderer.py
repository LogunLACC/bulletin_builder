import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

class BulletinRenderer:
    def __init__(self, templates_dir):
        """
        Initializes the renderer.
        Args:
            templates_dir (str or Path): The path to the main templates directory.
        """
        self.templates_dir = Path(templates_dir)
        if not self.templates_dir.is_dir():
            raise FileNotFoundError(f"Templates directory not found at: {self.templates_dir}")

        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def render_html(self, sections_data: list, settings: dict = None) -> str:
        """
        Renders the final HTML for the bulletin, injecting theme styles.
        """
        if settings is None:
            settings = {}
        
        # --- Theme Loading Logic ---
        theme_styles = ""
        theme_filename = settings.get("theme_css")
        if theme_filename:
            theme_path = self.templates_dir / "themes" / theme_filename
            if theme_path.is_file():
                try:
                    theme_styles = theme_path.read_text(encoding='utf-8')
                except Exception as e:
                    print(f"Error reading theme file {theme_path}: {e}")
            else:
                print(f"Theme file not found: {theme_path}")

        try:
            template = self.env.get_template("main_layout.html")
            
            html_output = template.render(
                sections=sections_data,
                settings=settings,
                theme_styles=theme_styles # Pass the loaded CSS to the template
            )
            return html_output
        except Exception as e:
            print(f"Error rendering template: {e}")
            return f"<html><body><h1>Template Render Error</h1><p>{e}</p></body></html>"
