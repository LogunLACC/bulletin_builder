# LACC Bulletin Builder

**A modular, drag‑and‑drop bulletin‑builder desktop app built with CustomTkinter and WeasyPrint.**

---

## Table of Contents

- [Features](#features)  
- [Requirements](#requirements)  
- [Installation](#installation)
  - [For Developers](#for-developers)
  - [For End Users](#for-end-users)
- [Quick Start Guide](#quick-start-guide)
  - [Creating Your First Bulletin](#creating-your-first-bulletin)
  - [Importing Events](#importing-events)
  - [Working with Templates](#working-with-templates)
  - [Exporting](#exporting)
- [Usage](#usage)  
- [Packaging](#packaging--build-instructions)
  - [Quick Build](#quick-build)
  - [Validate the Build](#validate-the-build)
  - [Platform-Specific Notes](#platform-specific-notes)
- [Configuration](#configuration)
- [Auto‑Update](#auto‑update)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Testing](#testing)
- [Contributing](#contributing)  
- [License](#license)  

---

## Features

- Add / remove / reorder sections  
- Preview in‑app (HTML via `tkhtmlview`) or open browser  
- Export to PDF via WeasyPrint
- Export HTML + plain text versions for email
- Copy email‑ready HTML to clipboard
- Send preview emails via configurable SMTP server
- Pluggable “sections” architecture for custom text, events, images, announcements
- Themeable: pick CSS file, colors, title/date, Google AI key integration

---

## Requirements

- Python 3.9+  
- Dependencies in `requirements.txt` (see below)  

```text
customtkinter
tkhtmlview
weasyprint
premailer
bulletin_renderer
google-generativeai
pytest               # for tests
pyinstaller          # for packaging
pyupdater            # for auto‑update (optional)

```

---

## Installation

### For Developers

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LogunLACC/bulletin_builder.git
   cd bulletin_builder
   ```

2. **Install in development mode:**
   ```bash
   pip install -e .
   ```

3. **Configure the application:**
   ```bash
   # Copy the default config
   cp config.ini.default config.ini
   
   # Edit config.ini with your settings
   # (API keys, SMTP credentials, etc.)
   ```

4. **Run the application:**
   ```bash
   bulletin --gui
   ```

### For End Users

Download the latest standalone executable from the [Releases](https://github.com/LogunLACC/bulletin_builder/releases) page:

- **Windows:** `bulletin_builder_windows.zip` - Extract and run `bulletin.exe`
- **macOS:** `bulletin_builder_macos.dmg` - Mount and drag to Applications
- **Linux:** `bulletin_builder_linux.AppImage` - Make executable and run

No Python installation required!

---

## Quick Start Guide

### Creating Your First Bulletin

**Using the GUI:**

1. Launch the application:
   ```bash
   bulletin --gui
   ```

2. **Configure basic settings:**
   - Click the **Settings** tab
   - Enter your bulletin title (e.g., "Weekly Church Bulletin")
   - Set the bulletin date
   - Choose a theme (Light, Dark, or Hybrid)

3. **Add your first section:**
   - In the left sidebar, click **"+ Add Section"**
   - Choose a section type:
     - **Text Section** - For announcements, messages, devotionals
     - **Event Section** - For scheduled events with dates/times
     - **Image Section** - For photos, graphics, flyers
     - **Table Section** - For structured data
   
4. **Edit section content:**
   - Select the section from the sidebar
   - Use the WYSIWYG editor to add and format content
   - Drag elements to reorder them
   - Use the toolbar for headings, lists, images, and formatting

5. **Preview your work:**
   - Click **Preview** to see how it will look
   - Toggle between Desktop and Mobile views
   - Check the email preview for compatibility

6. **Save your draft:**
   ```bash
   # Press Ctrl+S or click File → Save Draft
   ```
   Your draft is saved as JSON in `user_drafts/`

### Importing Events

**From CSV:**

```python
# Prepare your events.csv file:
# title,date,time,location,description
# "Sunday Service","2025-10-12","10:00 AM","Main Sanctuary","Weekly worship service"
# "Bible Study","2025-10-14","7:00 PM","Fellowship Hall","Studying Romans"
```

```bash
# In the GUI:
# 1. Click "Import" → "Import Events from CSV"
# 2. Select your events.csv file
# 3. Events are automatically parsed and added to your bulletin
```

**From JSON:**

```json
{
  "events": [
    {
      "title": "Sunday Service",
      "date": "2025-10-12",
      "time": "10:00 AM",
      "location": "Main Sanctuary",
      "description": "Weekly worship service"
    },
    {
      "title": "Bible Study",
      "date": "2025-10-14",
      "time": "7:00 PM",
      "location": "Fellowship Hall",
      "description": "Studying Romans"
    }
  ]
}
```

```bash
# In the GUI:
# File → Import → Import Events from JSON
# Select your events.json file
```

**Using the CLI:**

```bash
# Import events from CSV
bulletin import events.csv

# Import events from JSON
bulletin import events.json --format json
```

### Working with Templates

**Using Built-in Templates:**

```bash
# Browse available templates in the GUI:
# Settings → Template Gallery
# Select a template to apply it to your bulletin
```

**Creating Custom Templates:**

```python
# templates/my_custom_template.html
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Your custom CSS */
        body { font-family: Georgia, serif; }
        .section { margin: 20px 0; }
        h1 { color: #2c3e50; }
    </style>
</head>
<body>
    <!-- Jinja2 template variables -->
    <h1>{{ title }}</h1>
    <p class="date">{{ date }}</p>
    
    {% for section in sections %}
    <div class="section">
        <h2>{{ section.title }}</h2>
        {{ section.content | safe }}
    </div>
    {% endfor %}
</body>
</html>
```

```bash
# Apply your custom template:
# 1. Place template in templates/ directory
# 2. Settings → Custom Template → Select your file
# 3. Your bulletin now uses your custom styling!
```

**Saving Content as Components:**

```bash
# Reuse common sections across bulletins:
# 1. Create a section (e.g., "Weekly Announcements")
# 2. Right-click the section → "Save as Component"
# 3. Give it a name (e.g., "Standard Announcements")
# 4. Load it in future bulletins: "Insert Component" → Select your saved component
```

### Exporting

**Export to HTML:**

```bash
# Using the GUI:
# File → Export → Export to HTML
# Saves both raw HTML and email-ready HTML with inlined CSS
```

```bash
# Using the CLI:
# Export raw HTML
bulletin export output.html

# Export email-ready HTML (inlined CSS, optimized)
bulletin export output.html --email-ready
```

**Export to PDF:**

```bash
# Using the GUI:
# File → Export → Export to PDF
# Creates a print-ready PDF using WeasyPrint
```

```bash
# Using the CLI:
bulletin export output.pdf
```

**Copy to Clipboard for Email:**

```bash
# Using the GUI:
# 1. File → Export → Copy Email HTML to Clipboard
# 2. Paste directly into your email client (Gmail, Outlook, etc.)
# 3. All styles are inlined and email-compatible!
```

**Send Test Email:**

```bash
# Configure SMTP in config.ini first:
[smtp]
host = smtp.gmail.com
port = 587
username = your.email@gmail.com
password = your_app_password
from_addr = "Church Bulletin <your.email@gmail.com>"
use_tls = true
```

```bash
# Using the GUI:
# File → Send Test Email
# Enter recipient address and send
```

```bash
# Using the CLI:
bulletin send-email recipient@example.com --subject "Test Bulletin"
```

**Programmatic Usage:**

```python
from bulletin_builder.app_core.exporter import export_html, export_pdf
from bulletin_builder.app_core.importer import import_events_from_csv

# Load draft
with open('user_drafts/my_bulletin.json', 'r') as f:
    draft = json.load(f)

# Export to HTML
export_html(draft, 'output.html', email_ready=True)

# Export to PDF
export_pdf(draft, 'output.pdf')

# Import and process events
events = import_events_from_csv('events.csv')
for event in events:
    draft['sections'].append({
        'type': 'event',
        'title': event['title'],
        'content': f"{event['date']} at {event['time']}<br>{event['location']}"
    })
```

---

## Usage

---

## Packaging & Build Instructions

### Quick Build

```bash
# IMPORTANT: Close any running instances of Bulletin Builder first!

# Install PyInstaller if needed
pip install pyinstaller

# Build the executable
python scripts/build_exe.py
```

The built application will be in `dist/bulletin/`.

**Windows Users:** If you encounter permission errors, make sure to close the application before building. See [troubleshooting](docs/BUILDING.md#troubleshooting) for details.

### Validate the Build

After building, verify the executable is complete:

```bash
python scripts/validate_build.py
```

This runs 8 checks including templates, dependencies, DLLs, and a launch test.

### Detailed Build Instructions

See [docs/BUILDING.md](docs/BUILDING.md) for comprehensive build documentation including:
- Prerequisites and platform requirements
- Build configuration and spec file details
- Data file management (templates, assets, config)
- Windows permission error troubleshooting
- Platform-specific notes for Windows/macOS/Linux
- Distribution options (zip, installer, AppImage)

### Platform-Specific Notes

**Windows:**
- Build tested on Windows 11 with Python 3.13.5
- Creates `bulletin.exe` with all dependencies bundled
- Known issue: Must close app before building to avoid permission errors
- Build size: ~150-200 MB (includes Python runtime, tkinter, and all dependencies)

**macOS & Linux:**
- Build scripts coming soon
- Will use same PyInstaller spec file
- Expected to work with Python 3.9+ on both platforms

---

## Configuration

Edit `config.ini` (or copy `config.ini.default` to `config.ini`) and update your API keys and SMTP credentials as needed.

---

To use the **Send Test Email** feature, update `config.ini` with your SMTP credentials:

```ini
[smtp]
host = "smtp.example.com"
port = 587
username = "your_username"
password = "your_password"
from_addr = "Bulletin Builder <user@example.com>"
use_tls = true
```

After configuring, click **Send Test Email...** in the app and enter the destination address to receive a preview message.

## Keyboard Shortcuts

Common actions can be triggered from the keyboard:

| Shortcut | Action |
| -------- | ------ |
| `Ctrl+N` | New draft |
| `Ctrl+O` | Open draft |
| `Ctrl+S` | Save draft |
| `Ctrl+Shift+S` | Save draft as... |
| `Ctrl+Z` | Undo (WYSIWYG editor) |
| `Ctrl+Y` | Redo (WYSIWYG editor) |
| `Ctrl+E` | Export HTML (WYSIWYG editor) |

