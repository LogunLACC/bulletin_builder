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
- [Testing](#testing)  
- [Contributing](#contributing)  
- [License](#license)  

---

## Features

- Add / remove / reorder sections  
- Preview in‑app (HTML via `tkhtmlview`) or open browser  
- Export to PDF via WeasyPrint  
- Copy email‑ready HTML to clipboard  
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

## Packaging

Run the build script to create a standalone executable (requires PyInstaller):

```bash
python scripts/build_exe.py
```

The resulting `bulletin_builder` directory contains an executable that can be
distributed to users on the same platform (Windows or macOS) without needing a
Python installation.

