from dataclasses import dataclass, field
from typing import Dict, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

@dataclass
class Settings:
    bulletin_title: str = "Weekly Bulletin"
    bulletin_date: str = ""
    colors: Dict[str, str] = field(default_factory=lambda: {
        "primary": "#1F6AA5",
        "secondary": "#333333",
    })
    template_path: str = "templates"
    theme_css: Optional[str] = None  # e.g. "club_theme.css"

    @property
    def jinja_env(self) -> Environment:
        loader = FileSystemLoader(self.template_path)
        env = Environment(
            loader=loader,
            autoescape=select_autoescape(["html", "xml"]),
            auto_reload=True,
        )
        return env