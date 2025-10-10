# LACC Bulletin Builder

**A modular, drag‑and‑drop bulletin‑builder desktop app built with CustomTkinter and WeasyPrint.**

---

## Table of Contents

- [Features](#features)  
- [Requirements](#requirements)  
- [Installation](#installation)
  - [For Developers](#for-developers)
  - [For End Users](#for-end-users)
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

