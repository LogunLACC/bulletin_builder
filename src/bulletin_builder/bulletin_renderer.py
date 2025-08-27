<<<<<<< HEAD

=======
>>>>>>> origin/harden/email-sanitize-and-ci
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown import markdown

from typing import Optional, List, Dict, Any
from collections import OrderedDict
<<<<<<< HEAD
from datetime import datetime, date


class BulletinRenderer:
    def __init__(self, templates_dir: Path | str | None = None, theme: str = "default.css", template_name: str | None = None):
        # Resolve template directory (allow None and auto-detect)
        def _auto_templates_dir() -> Path:
            here = Path(__file__).resolve()
            candidates = [
                Path.cwd() / "templates",
                here.parent / "templates",
                here.parent.parent / "templates",
                here.parents[2] / "templates" if len(here.parents) >= 3 else here.parent / "templates",
            ]
            for c in candidates:
                if (c / "index.html").exists():
                    return c
            return candidates[0]

        self.templates_dir = Path(templates_dir) if templates_dir else _auto_templates_dir()
        self.theme = theme
        # default template used by preview/export unless overridden at render()
        self.template_name = template_name or "main_layout.html"
        # Optional legacy cache kept for compatibility
        self._template_cache = getattr(self, "_template_cache", {})
        # Jinja environment used by preview/export
=======


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

>>>>>>> origin/harden/email-sanitize-and-ci
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            enable_async=False,
        )
        # Filters
        def _md(value):
            """
            Accept strings OR dicts like {"text": "..."} and return HTML.
            This prevents errors like: AttributeError: 'dict' object has no attribute 'strip'
            """
            try:
                if isinstance(value, dict):
                    value = value.get("text", "")
                elif value is None:
                    value = ""
                else:
                    value = str(value)
                return markdown(value, output_format="html")
            except Exception as e:
                # Fail soft: return a safe string instead of crashing the preview
                print(f"[WARN] markdown filter failed: {e!r}")
                return str(value or "")
        self.env.filters["markdown"] = _md
        self.env.filters["group_events"] = self._group_events
        self.env.filters["group_events_by_tag"] = self._group_events_by_tag


    def _get_template(self, name: str):
        # Prefer Jinja environment
        return self.env.get_template(name)

    def render(self, context: dict) -> str:
        # Provide safe defaults so templates don't explode if callers omit fields
        ctx = dict(context)
        ctx.setdefault("settings", {})     # templates use settings.*
        ctx.setdefault("theme", self.theme)
        ctx.setdefault("sections", [])
        ctx.setdefault("bulletin", {"title": "", "date": ""})
        template_name = ctx.pop("template", self.template_name)
        try:
            return self._get_template(template_name).render(**ctx)
        except Exception as e:
            # Bubble a readable error up to the UI while keeping logs actionable
            print(f"[ERROR] Render failed in template '{template_name}': {e!r}")
            raise

        # Register event grouping filters
        self.env.filters["group_events"] = self._group_events
        self.env.filters["group_events_by_tag"] = self._group_events_by_tag

    # --- Event Grouping Logic -------------------------------------------------
    def _parse_date(self, value: str, default_year: int) -> date | None:
        """Try to parse a variety of human friendly date strings."""
        if not value:
            return None
        clean = value.split("-")[0].strip()
        patterns = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%m/%d/%y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%A, %B %d, %Y",
            "%A, %B %d",
            "%B %d",
            "%b %d",
        ]
        for fmt in patterns:
            try:
                dt = datetime.strptime(clean, fmt)
                if "%Y" not in fmt:
                    dt = dt.replace(year=default_year)
                return dt.date()
            except ValueError:
                continue
        return None

    def _group_events(self, events: List[Dict[str, str]], bulletin_date: str = "") -> List[Dict[str, object]]:
        """Return events sorted and grouped by week relative to bulletin_date."""
        base = self._parse_date(bulletin_date, datetime.today().year) or date.today()
        parsed = []
        for ev in events:
            ev_date = self._parse_date(ev.get("date", ""), base.year)
            parsed.append((ev_date, ev))

        parsed.sort(key=lambda t: t[0] or date.max)

        groups: OrderedDict[str, Dict[str, object]] = OrderedDict()
        for ev_date, ev in parsed:
            if ev_date is None:
                header = "Other"
            else:
                week_diff = (ev_date.isocalendar()[1] - base.isocalendar()[1]) + (
                    ev_date.year - base.year
                ) * 52
                if week_diff < 0:
                    header = "Past"
                elif week_diff == 0:
                    header = "This Week"
                elif week_diff == 1:
                    header = "Next Week"
                else:
                    header = ev_date.strftime("%B %d, %Y")
            grp = groups.setdefault(header, {"header": header, "events": []})
            grp["events"].append(ev)

        return list(groups.values())

    def _group_events_by_tag(self, events: List[Dict[str, str]]) -> List[Dict[str, object]]:
        """Group events by their first tag."""
        groups: OrderedDict[str, Dict[str, object]] = OrderedDict()
        for ev in events:
            tags = ev.get("tags") or []
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]
            tag = tags[0] if tags else "Other"
            grp = groups.setdefault(tag.capitalize(), {"header": tag.capitalize(), "events": []})
            grp["events"].append(ev)
        return list(groups.values())

    def set_template(self, name: str):
        """Change the layout template used for rendering."""
        self.template_name = name
<<<<<<< HEAD
=======

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
                # Filter out fields that don't belong in Settings class
                valid_fields = {
                    'bulletin_title', 'bulletin_date', 'colors', 'template_path',
                    'theme_css', 'appearance_mode'
                }
                filtered_settings = {k: v for k, v in settings.items() if k in valid_fields}
                settings = Settings(**filtered_settings)
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
>>>>>>> origin/harden/email-sanitize-and-ci
