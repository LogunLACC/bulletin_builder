# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Bulletin Builder

This is the canonical spec file for building the application.
Location: packaging/bulletin_builder.spec

Usage:
    pyinstaller packaging/bulletin_builder.spec --clean
    
Or use the build script:
    python scripts/build_exe.py
"""

from PyInstaller.utils.hooks import collect_submodules
import os
from pathlib import Path

block_cipher = None

# Collect all bulletin_builder submodules
hiddenimports = collect_submodules('bulletin_builder')

# Additional hidden imports for optional features
hiddenimports.extend([
    'customtkinter',
    'PIL',
    'PIL._tkinter_finder',
    'requests',
    'jinja2',
    'jinja2.ext',
    'weasyprint',  # Optional: for PDF export
])

# Project root directory
ROOT_DIR = Path('.').absolute()

# Data files to include
datas = [
    # Templates for bulletin rendering
    (str(ROOT_DIR / 'src' / 'bulletin_builder' / 'templates'), 'bulletin_builder/templates'),
    
    # Additional top-level templates (if any)
    (str(ROOT_DIR / 'templates'), 'templates'),
    
    # Assets (images, icons, etc.)
    (str(ROOT_DIR / 'assets'), 'assets'),
    
    # Default configuration file
    (str(ROOT_DIR / 'config.ini.default'), '.'),
    
    # Component templates (if used)
    (str(ROOT_DIR / 'components'), 'components'),
]

a = Analysis(
    [str(ROOT_DIR / 'src' / 'bulletin_builder' / '__main__.py')],
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Exclude if not used
        'scipy',       # Exclude if not used
        'numpy',       # Exclude if not used (unless required by dependencies)
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='bulletin',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for GUI app (no console window)
    icon=None,      # Add icon path here if available: 'assets/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='bulletin',
)
