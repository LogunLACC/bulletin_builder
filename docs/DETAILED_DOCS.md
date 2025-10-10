# Bulletin Builder - Detailed Technical Documentation

Comprehensive architecture overview and technical reference for Bulletin Builder.

## Table of Contents

- [Architecture Overview](#architecture-overview)
  - [High-Level Architecture](#high-level-architecture)
  - [Design Principles](#design-principles)
  - [Technology Stack](#technology-stack)
- [Module Structure](#module-structure)
  - [Core Modules (`app_core/`)](#core-modules-app_core)
  - [UI Modules (`ui/`)](#ui-modules-ui)
  - [Post-Processing (`postprocess/`)](#post-processing-postprocess)
- [Data Flow](#data-flow)
  - [Bulletin Creation Flow](#bulletin-creation-flow)
  - [Import Flow](#import-flow)
  - [Export Flow](#export-flow)
- [Template System](#template-system)
  - [Template Architecture](#template-architecture)
  - [Jinja2 Integration](#jinja2-integration)
  - [Email-Safe Rendering](#email-safe-rendering)
- [Configuration Management](#configuration-management)
- [Extension Points](#extension-points)
- [Performance Considerations](#performance-considerations)
- [Security Considerations](#security-considerations)

---

## Architecture Overview

### High-Level Architecture

Bulletin Builder follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                   User Interface Layer                   │
│  (CustomTkinter GUI / CLI / Programmatic API)           │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              Application Core Layer                      │
│  • Draft Management (drafts.py)                         │
│  • Import/Export (importer.py, exporter.py)             │
│  • Section Management (sections.py)                      │
│  • Preview Generation (preview.py)                       │
│  • Validation (export_validator.py)                      │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│            Post-Processing Layer                         │
│  • Email HTML Optimization (email_postprocess.py)       │
│  • CSS Inlining (premailer)                             │
│  • Image Optimization                                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              Rendering Layer                             │
│  • Jinja2 Template Engine                               │
│  • WeasyPrint PDF Generation                            │
│  • HTML Rendering                                        │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              Storage Layer                               │
│  • JSON Draft Files (user_drafts/)                      │
│  • Template Files (templates/)                          │
│  • Component Library (components/)                       │
│  • Configuration (config.ini)                           │
└─────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Separation of Concerns**: UI logic is separate from business logic
2. **Modularity**: Each module has a single, well-defined responsibility
3. **Email-First**: All exports prioritize email client compatibility
4. **User Data Preservation**: Never lose user work (autosave, drafts)
5. **Cross-Platform**: Works on Windows, macOS, and Linux
6. **Extensibility**: Easy to add new section types, templates, and features

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **GUI Framework** | CustomTkinter | Modern, themeable Tkinter wrapper |
| **Template Engine** | Jinja2 | Dynamic HTML/email generation |
| **PDF Generation** | WeasyPrint | Print-quality PDF exports |
| **HTML Processing** | premailer | CSS inlining for email |
| **CSV Parsing** | csv (stdlib) | Event data import |
| **Config Management** | configparser (stdlib) | INI file configuration |
| **Testing** | pytest | Unit and integration testing |
| **Packaging** | PyInstaller | Standalone executable creation |

---

## Module Structure

### Core Modules (`app_core/`)

#### `config.py` - Configuration Management

**Purpose:** Centralized configuration loading and validation.

**Key Functions:**
- `load_config()` - Load and parse config.ini
- `get_smtp_config()` - SMTP settings for email sending
- `get_api_keys()` - Google AI and other API keys
- `load_window_state()` / `save_window_state()` - Window geometry persistence

**Data Structures:**
```python
Config = dict[str, dict[str, Any]]  # Section → {key: value}
SMTPConfig = dict[str, str | int | bool]
WindowState = tuple[str, str]  # (geometry, state)
```

**Usage:**
```python
from bulletin_builder.app_core.config import load_config, get_smtp_config

config = load_config()
smtp = get_smtp_config(config)
```

---

#### `drafts.py` - Draft Management

**Purpose:** Save and load bulletin drafts as JSON files.

**Key Functions:**
- `save_draft(draft: dict, filepath: str) -> None` - Save draft to JSON
- `load_draft(filepath: str) -> dict` - Load draft from JSON
- `list_drafts(directory: str) -> list[str]` - List available drafts
- `validate_draft(draft: dict) -> bool` - Validate draft structure

**Draft Structure:**
```json
{
  "version": "2.0",
  "title": "Weekly Church Bulletin",
  "date": "2025-10-12",
  "theme": "light",
  "template": "default",
  "sections": [
    {
      "id": "section_1",
      "type": "text",
      "title": "Announcements",
      "content": "<p>Welcome!</p>",
      "order": 0,
      "metadata": {}
    }
  ],
  "settings": {
    "font_family": "Arial",
    "color_scheme": "blue"
  }
}
```

**Usage:**
```python
from bulletin_builder.app_core.drafts import save_draft, load_draft

# Save
draft = {'title': 'My Bulletin', 'sections': []}
save_draft(draft, 'user_drafts/my_bulletin.json')

# Load
loaded = load_draft('user_drafts/my_bulletin.json')
```

---

#### `exporter.py` - Export to HTML/PDF

**Purpose:** Convert drafts to various output formats.

**Key Functions:**
- `export_html(draft: dict, output_path: str, email_ready: bool = False) -> str`
- `export_pdf(draft: dict, output_path: str) -> bytes`
- `export_email_html(draft: dict) -> str` - Email-optimized HTML
- `copy_to_clipboard(html: str) -> None` - Copy HTML to clipboard

**Export Pipeline:**

```
Draft (JSON)
    ↓
render_template(draft, template)  # Jinja2
    ↓
Generated HTML
    ↓
inline_css(html)  # premailer (if email_ready)
    ↓
validate_email_compatibility(html)  # Check for issues
    ↓
Final HTML / PDF
```

**Usage:**
```python
from bulletin_builder.app_core.exporter import export_html, export_pdf

draft = load_draft('my_bulletin.json')

# Export HTML
html = export_html(draft, 'output.html', email_ready=True)

# Export PDF
pdf_bytes = export_pdf(draft, 'output.pdf')
```

---

#### `importer.py` - Import Events from CSV/JSON

**Purpose:** Parse external data and convert to bulletin sections.

**Key Functions:**
- `import_events_from_csv(filepath: str) -> list[dict]`
- `import_events_from_json(filepath: str) -> list[dict]`
- `parse_event_data(data: str, format: str) -> list[dict]`

**CSV Format:**
```csv
title,date,time,location,description
"Sunday Service","2025-10-12","10:00 AM","Sanctuary","Weekly worship"
"Bible Study","2025-10-14","7:00 PM","Fellowship Hall","Romans study"
```

**JSON Format:**
```json
{
  "events": [
    {
      "title": "Sunday Service",
      "date": "2025-10-12",
      "time": "10:00 AM",
      "location": "Sanctuary",
      "description": "Weekly worship"
    }
  ]
}
```

**Usage:**
```python
from bulletin_builder.app_core.importer import import_events_from_csv

events = import_events_from_csv('events.csv')
for event in events:
    section = {
        'type': 'event',
        'title': event['title'],
        'content': f"{event['date']} at {event['time']}<br>{event['location']}"
    }
    draft['sections'].append(section)
```

---

#### `sections.py` - Section Management

**Purpose:** Create, edit, reorder, and delete bulletin sections.

**Key Classes:**
- `Section` - Base section class with common properties
- `TextSection` - Rich text content
- `EventSection` - Scheduled events with date/time/location
- `ImageSection` - Images with captions
- `TableSection` - Tabular data

**Section Types:**

| Type | Use Case | Required Fields |
|------|----------|-----------------|
| `text` | Announcements, messages | `title`, `content` (HTML) |
| `event` | Calendar events | `title`, `date`, `time`, `location` |
| `image` | Photos, graphics | `image_url`, `caption`, `alt_text` |
| `table` | Structured data | `headers`, `rows` |
| `video` | Embedded videos | `video_url`, `thumbnail` |

**Usage:**
```python
from bulletin_builder.app_core.sections import create_section, reorder_sections

# Create section
section = create_section(
    type='text',
    title='Announcements',
    content='<p>Welcome!</p>'
)

# Add to draft
draft['sections'].append(section)

# Reorder
draft['sections'] = reorder_sections(draft['sections'], from_index=2, to_index=0)
```

---

#### `preview.py` - Preview Generation

**Purpose:** Generate real-time previews for desktop and mobile views.

**Key Functions:**
- `generate_preview(draft: dict, view_mode: str = 'desktop') -> str`
- `generate_mobile_preview(draft: dict) -> str`
- `generate_email_preview(draft: dict) -> str`

**View Modes:**
- `desktop` - Full-width desktop browser view
- `mobile` - Mobile-responsive view (max 600px)
- `email` - Email client preview with inlined CSS

**Usage:**
```python
from bulletin_builder.app_core.preview import generate_preview

html = generate_preview(draft, view_mode='mobile')
# Display in tkhtmlview widget or browser
```

---

#### `export_validator.py` - Email Compatibility Validation

**Purpose:** Check HTML for email client compatibility issues.

**Key Functions:**
- `validate_email_html(html: str) -> ValidationReport`
- `check_css_support(html: str) -> list[str]`
- `check_accessibility(html: str) -> list[str]`
- `check_image_urls(html: str) -> list[str]`

**Validation Rules:**
- CSS must be inlined (no `<style>` tags or external stylesheets)
- Images must have `alt` text
- No JavaScript
- Tables for layout, not CSS grid/flexbox
- All images have absolute URLs or are embedded
- No `position: fixed` or `position: absolute`
- Font sizes in `px` or `pt`, not `em` or `rem`

**ValidationReport Structure:**
```python
{
    'valid': bool,
    'errors': list[str],     # Critical issues
    'warnings': list[str],   # Best practice violations
    'info': list[str]        # Recommendations
}
```

**Usage:**
```python
from bulletin_builder.app_core.export_validator import validate_email_html

report = validate_email_html(html)
if not report['valid']:
    print("Errors:", report['errors'])
```

---

#### `logging_config.py` - Logging Setup

**Purpose:** Centralized logging configuration for the application.

**Key Functions:**
- `configure_logging(level: int = logging.INFO, console_output: bool = True, log_file: Path | None = None)`
- `get_logger(name: str) -> logging.Logger`

**Log Levels:**
- `DEBUG` - Detailed debugging information
- `INFO` - General application flow
- `WARNING` - Potential issues
- `ERROR` - Errors that need attention
- `CRITICAL` - Critical failures

**Usage:**
```python
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Processing bulletin export")
logger.error("Failed to save draft", exc_info=True)
```

---

### UI Modules (`ui/`)

#### `settings.py` - Settings Panel

**Purpose:** GUI for application configuration and bulletin metadata.

**Key Components:**
- `SettingsFrame` - Main settings container
- Title/date entry fields
- Theme selection (Light/Dark/Hybrid)
- Template gallery browser
- SMTP configuration
- API key management

**Settings Structure:**
```python
{
    'title': str,
    'date': str,
    'theme': 'light' | 'dark' | 'hybrid',
    'template': str,  # Template filename
    'confirm_on_close': bool,
    'autosave_on_close': bool,
    'font_family': str,
    'font_size': int,
    'color_scheme': str
}
```

---

#### `events.py` - Event Editor

**Purpose:** GUI for adding and editing calendar events.

**Key Components:**
- `EventEditor` - Main event editing dialog
- Date picker
- Time picker
- Location entry
- Description rich text editor

**Event Structure:**
```python
{
    'title': str,
    'date': str,  # ISO format: YYYY-MM-DD
    'time': str,  # 12-hour format with AM/PM
    'location': str,
    'description': str  # HTML content
}
```

---

#### `template_gallery.py` - Template Browser

**Purpose:** Visual browser for selecting bulletin templates.

**Key Components:**
- `TemplateGallery` - Main gallery window
- Template thumbnails
- Preview pane
- Apply button

**Template Discovery:**
```python
# Scans these directories:
templates_dirs = [
    'templates/',                    # Built-in templates
    'src/bulletin_builder/templates/',
    Path.home() / '.bulletin_builder' / 'templates'  # User templates
]
```

---

#### `tooltip.py` - UI Tooltips

**Purpose:** Contextual help tooltips for UI elements.

**Usage:**
```python
from bulletin_builder.ui.tooltip import ToolTip

button = ctk.CTkButton(parent, text="Export")
ToolTip(button, "Export bulletin to HTML or PDF")
```

---

### Post-Processing (`postprocess/`)

#### `email_postprocess.py` - Email HTML Optimization

**Purpose:** Transform generic HTML into email-client-compatible HTML.

**Key Functions:**
- `postprocess_email_html(html: str) -> str` - Main processing pipeline
- `inline_css(html: str) -> str` - Convert styles to inline attributes
- `optimize_images(html: str) -> str` - Compress and resize images
- `add_email_metadata(html: str) -> str` - Add email-specific meta tags

**Processing Pipeline:**

```
Raw HTML
    ↓
Parse with BeautifulSoup
    ↓
Inline CSS (premailer)
    ↓
Remove unsupported CSS properties
    ↓
Convert to table-based layout
    ↓
Add email-safe margin/padding
    ↓
Set image dimensions
    ↓
Add alt text to images
    ↓
Remove JavaScript
    ↓
Final Email HTML
```

**Email-Safe Transformations:**

| Original | Transformed |
|----------|-------------|
| `<div>` layout | `<table>` layout |
| `flexbox` / `grid` | Nested tables |
| `@media` queries | Inline styles |
| External CSS | Inline styles |
| `position: absolute` | Table cells |
| `rem` / `em` units | `px` units |

**Usage:**
```python
from bulletin_builder.postprocess.email_postprocess import postprocess_email_html

html = "<div style='color: red;'>Hello</div>"
email_html = postprocess_email_html(html)
# Result: <table><tr><td style="color: red;">Hello</td></tr></table>
```

---

## Data Flow

### Bulletin Creation Flow

```
User Opens App
    ↓
Initialize GUI (CustomTkinter)
    ↓
Load Configuration (config.ini)
    ↓
Restore Window State (last size/position)
    ↓
Load Last Draft (if autosave enabled)
    ↓
Render UI Components
    ↓
User Adds/Edits Sections
    ↓
Real-time Preview Updates
    ↓
Autosave to user_drafts/AutoSave/
    ↓
User Exports
    ↓
Generate HTML/PDF
    ↓
Save to User-Selected Location
```

### Import Flow

```
User Selects Import
    ↓
File Dialog (CSV or JSON)
    ↓
Read File Contents
    ↓
Parse Data (csv or json module)
    ↓
Validate Structure
    ↓
Convert to Sections
    ↓
Add to Draft
    ↓
Update UI
    ↓
Generate Preview
```

### Export Flow

```
User Clicks Export
    ↓
Validate Draft Structure
    ↓
Select Template
    ↓
Render with Jinja2
    ↓
Apply Theme (CSS)
    ↓
─┬─ HTML Export
 │      ↓
 │  Save Raw HTML
 │      ↓
 │  (Optional) Postprocess for Email
 │      ↓
 │  Inline CSS with Premailer
 │      ↓
 │  Validate Email Compatibility
 │      ↓
 │  Save Email-Ready HTML
 │
 └─ PDF Export
        ↓
    Convert HTML to PDF (WeasyPrint)
        ↓
    Save PDF File
```

---

## Template System

### Template Architecture

Templates use **Jinja2** for dynamic content generation:

**Base Template Structure:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        /* Theme-specific CSS */
        {% include 'theme_' + theme + '.css' %}
    </style>
</head>
<body>
    <header>
        <h1>{{ title }}</h1>
        <p class="date">{{ date }}</p>
    </header>
    
    <main>
        {% for section in sections %}
        <section class="section section-{{ section.type }}">
            <h2>{{ section.title }}</h2>
            <div class="content">
                {{ section.content | safe }}
            </div>
        </section>
        {% endfor %}
    </main>
    
    <footer>
        {% include 'footer.html' %}
    </footer>
</body>
</html>
```

### Jinja2 Integration

**Template Variables:**
```python
template_vars = {
    'title': str,           # Bulletin title
    'date': str,            # Bulletin date
    'theme': str,           # Theme name
    'sections': list[dict], # Section list
    'settings': dict,       # User settings
    'metadata': dict        # Additional metadata
}
```

**Template Filters:**
- `| safe` - Render HTML without escaping
- `| truncate(100)` - Truncate text to length
- `| title` - Title case
- `| upper` / `| lower` - Case conversion

**Custom Filters:**
```python
@app.template_filter('format_date')
def format_date(date_str: str) -> str:
    """Format date string for display."""
    date_obj = datetime.fromisoformat(date_str)
    return date_obj.strftime('%B %d, %Y')
```

### Email-Safe Rendering

**Email Template Rules:**
1. **Tables for layout**, not divs
2. **Inline CSS only**, no `<style>` tags
3. **Absolute image URLs** or embedded data URIs
4. **No JavaScript**
5. **No external resources** (fonts, CSS files)
6. **Alt text** on all images
7. **Simple CSS** (no flexbox, grid, transforms)

**Email Template Example:**
```html
<table cellpadding="0" cellspacing="0" border="0" width="100%">
    <tr>
        <td style="padding: 20px; font-family: Arial, sans-serif;">
            <h1 style="margin: 0; font-size: 24px; color: #333;">{{ title }}</h1>
            <p style="margin: 10px 0; font-size: 14px; color: #666;">{{ date }}</p>
        </td>
    </tr>
    {% for section in sections %}
    <tr>
        <td style="padding: 15px;">
            <h2 style="margin: 0 0 10px 0; font-size: 18px; color: #2c3e50;">
                {{ section.title }}
            </h2>
            <div style="font-size: 14px; line-height: 1.6; color: #333;">
                {{ section.content | safe }}
            </div>
        </td>
    </tr>
    {% endfor %}
</table>
```

---

## Configuration Management

### Config File Structure

`config.ini` uses INI format:

```ini
[general]
theme = light
default_template = default.html
autosave_interval = 300  # seconds

[smtp]
host = smtp.gmail.com
port = 587
username = user@example.com
password = app_specific_password
from_addr = Bulletin Builder <user@example.com>
use_tls = true

[api_keys]
google_ai_key = YOUR_API_KEY_HERE

[window]
geometry = 1200x800+100+100
state = normal

[settings]
confirm_on_close = true
autosave_on_close = true
show_tooltips = true
```

### Configuration Loading

```python
import configparser
from pathlib import Path

def load_config() -> configparser.ConfigParser:
    """Load configuration from config.ini."""
    config = configparser.ConfigParser()
    
    # Try multiple locations
    config_paths = [
        Path('config.ini'),
        Path.home() / '.bulletin_builder' / 'config.ini',
        Path('config.ini.default')
    ]
    
    for path in config_paths:
        if path.exists():
            config.read(path)
            return config
    
    return config  # Empty config
```

---

## Extension Points

### Adding New Section Types

1. **Define section class:**
```python
# app_core/sections.py
class CustomSection(Section):
    """Custom section type."""
    
    def __init__(self, title: str, custom_field: str):
        super().__init__(type='custom', title=title)
        self.custom_field = custom_field
    
    def render(self) -> str:
        """Render section to HTML."""
        return f"<div>{self.title}: {self.custom_field}</div>"
```

2. **Register section type:**
```python
SECTION_TYPES['custom'] = CustomSection
```

3. **Add UI editor:**
```python
# ui/section_editors.py
class CustomSectionEditor(ctk.CTkFrame):
    def __init__(self, parent, section):
        super().__init__(parent)
        # Add custom fields
```

### Adding New Templates

1. **Create template file:**
```html
<!-- templates/my_template.html -->
<!DOCTYPE html>
<html>
<head>
    <style>/* Your styles */</style>
</head>
<body>
    {{ content }}
</body>
</html>
```

2. **Template will be auto-discovered** in Template Gallery

### Adding New Export Formats

```python
# app_core/exporter.py
def export_custom_format(draft: dict, output_path: str) -> bytes:
    """Export to custom format."""
    # Your export logic
    return output_bytes
```

---

## Performance Considerations

### Lazy Loading

```python
# Only load sections when needed
def load_section_content(section_id: str) -> str:
    if section_id not in content_cache:
        content_cache[section_id] = _load_from_disk(section_id)
    return content_cache[section_id]
```

### Caching

```python
# Cache rendered templates
template_cache = {}

def render_template(template_name: str, context: dict) -> str:
    cache_key = f"{template_name}:{hash(frozenset(context.items()))}"
    if cache_key not in template_cache:
        template_cache[cache_key] = jinja_env.get_template(template_name).render(context)
    return template_cache[cache_key]
```

### Async Operations

```python
# Non-blocking PDF generation
import threading

def export_pdf_async(draft: dict, output_path: str, callback):
    def _export():
        pdf_bytes = export_pdf(draft, output_path)
        callback(pdf_bytes)
    
    thread = threading.Thread(target=_export)
    thread.start()
```

---

## Security Considerations

### Input Validation

```python
def validate_user_input(text: str) -> str:
    """Sanitize user input to prevent XSS."""
    from html import escape
    return escape(text)
```

### Safe File Operations

```python
from pathlib import Path

def safe_save_file(content: str, filepath: str):
    """Safely write to file with path validation."""
    path = Path(filepath).resolve()
    
    # Ensure within allowed directory
    allowed_dir = Path('user_drafts').resolve()
    if not path.is_relative_to(allowed_dir):
        raise ValueError("Invalid file path")
    
    path.write_text(content, encoding='utf-8')
```

### API Key Protection

```python
# Never log or display API keys
logger.info(f"Using API key: {api_key[:4]}...{api_key[-4:]}")

# Store in config.ini (not in code)
# Use environment variables for CI/CD
```

---

## Additional Resources

- **Developer Setup:** [DEVELOPER_SETUP.md](DEVELOPER_SETUP.md)
- **Build Instructions:** [BUILDING.md](BUILDING.md)
- **Installer Creation:** [INSTALLERS.md](INSTALLERS.md)
- **Type Hints Guide:** [TYPE_HINTS_GUIDE.md](TYPE_HINTS_GUIDE.md)
- **Roadmap:** [roadmap.json](../roadmap.json)

---

**Last Updated:** October 10, 2025  
**Version:** 2.0.0
