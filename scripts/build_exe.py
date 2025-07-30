#!/usr/bin/env python3
"""Build standalone executables using PyInstaller."""
import PyInstaller.__main__

PyInstaller.__main__.run([
    'bulletin_builder.spec',
    '--clean',
])
