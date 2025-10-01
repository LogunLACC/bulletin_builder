# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None

a = Analysis([
    'src/bulletin_builder/__main__.py'
],
    pathex=[str(Path(".").resolve())],
    binaries=[],
    datas=[
        ('src/bulletin_builder/templates/partials', 'bulletin_builder/templates/partials'),
        ('src/bulletin_builder/templates/themes', 'bulletin_builder/templates/themes'),
        ('assets', 'assets'),
        ('user_drafts', 'user_drafts'),
        ('config.ini', '.'),
    ],
    hiddenimports=[
        'bulletin_builder.app_core.core_init',
        'bulletin_builder.app_core.handlers',
        'bulletin_builder.app_core.drafts',
        'bulletin_builder.app_core.sections',
        'bulletin_builder.app_core.suggestions',
        'bulletin_builder.app_core.menu',
        'bulletin_builder.app_core.importer',
        'bulletin_builder.app_core.exporter',
        'bulletin_builder.app_core.preview',
        'bulletin_builder.app_core.ui_setup',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='bulletin_builder',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='bulletin_builder'
)
