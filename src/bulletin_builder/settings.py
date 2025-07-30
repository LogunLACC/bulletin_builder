from dataclasses import dataclass, field
from pathlib import Path
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
    template_path: str = str(Path(__file__).resolve().parent / "templates")
    theme_css: Optional[str] = None  # e.g. "club_theme.css"
    appearance_mode: str = "Dark"

    @property
    def jinja_env(self) -> Environment:
        loader = FileSystemLoader(self.template_path)
        env = Environment(
            loader=loader,
            autoescape=select_autoescape(["html", "xml"]),
            auto_reload=True,
        )
        return env
