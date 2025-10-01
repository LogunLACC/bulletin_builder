# LACC Bulletin Builder

**A modular, drag‑and‑drop bulletin‑builder desktop app built with CustomTkinter and WeasyPrint.**

---

## Table of Contents

- [Features](#features)  
- [Requirements](#requirements)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Packaging](#packaging)
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

distributed to users on the same platform (Windows or macOS) without needing a
## Packaging & Build Instructions

### 1. Install Requirements

Open PowerShell and run:

```powershell
pip install -r requirements.txt
```

### 2. Build the Executable (Windows)

Run the build script:

```powershell
python scripts/build_exe.py
```

This will use PyInstaller and the provided spec file to create a standalone executable in the `build/bulletin_builder` directory.

### 3. Distribute the App

Copy the entire `build/bulletin_builder` folder to your target machine. Users do not need Python installed.

### 4. Configuration

Edit `config.ini` (or copy `config.example.ini` to `config.ini`) and update your OpenAI and SMTP credentials as needed.

### 5. Troubleshooting

- If you encounter missing modules, ensure all dependencies in `requirements.txt` are installed.
- For GUI issues, verify that CustomTkinter and tkhtmlview are installed and working.
- For PDF export, WeasyPrint must be installed and functional.

---

destination address to receive a preview message.
### SMTP Configuration

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

