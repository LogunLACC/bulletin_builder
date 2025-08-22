from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

class BulletinRenderer:
    """
    Jinja-based renderer:
      • exposes `self.env` for includes/extends
      • accepts `template_name` (default: main_layout.html)
      • supports `set_template(name)` and `render(ctx)`; ctx["template"] can override
      • injects theme CSS into {{ theme_styles }} if templates/themes/<css> exists
    """
    def __init__(self, templates_dir: Path | str, template_name: str = "main_layout.html", theme_css: str | None = None):
        self.templates_dir = Path(templates_dir)
        self.template_name = template_name
        self.theme_css = theme_css
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def set_template(self, name: str) -> None:
        self.template_name = name

    def _load_theme_css(self, settings: Dict[str, Any]) -> str:
        css_name = (settings or {}).get("theme_css") or self.theme_css
        if not css_name:
            return ""
        css_path = self.templates_dir / "themes" / css_name
        try:
            return css_path.read_text(encoding="utf-8")
        except Exception:
            return ""

    def render(self, ctx: Optional[Dict[str, Any]] = None) -> str:
        ctx = dict(ctx or {})
        template_name = ctx.pop("template", self.template_name)
        # normalize + enrich context
        settings = ctx.get("settings") or {}
        ctx["settings"] = settings
        ctx["theme_styles"] = self._load_theme_css(settings)
        ctx["sections"] = list(ctx.get("sections") or [])
        return self.env.get_template(template_name).render(**ctx)
