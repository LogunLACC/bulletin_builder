# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
import os

block_cipher = None

hiddenimports = collect_submodules('bulletin_builder')

a = Analysis(
    ['src/bulletin_builder/cli.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/bulletin_builder/templates', 'bulletin_builder/templates'),
        ('assets', 'assets'),
        ('config.ini.default', '.'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
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
    name='bulletin',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
