#!/usr/bin/env python3
"""
Build standalone executables using PyInstaller.

This script uses the canonical spec file located at packaging/bulletin_builder.spec
and performs a clean build to ensure all dependencies and data files are properly included.

Usage:
    python scripts/build_exe.py
    
The built executable will be in the dist/bulletin/ directory.
"""
import PyInstaller.__main__
import sys
from pathlib import Path

# Ensure we're in the project root
project_root = Path(__file__).parent.parent
spec_file = project_root / 'packaging' / 'bulletin_builder.spec'

if not spec_file.exists():
    print(f"Error: Spec file not found at {spec_file}")
    sys.exit(1)

print(f"Building from spec file: {spec_file}")
print("This may take several minutes...")

PyInstaller.__main__.run([
    str(spec_file),
    '--clean',
    '--noconfirm',
])

print("\nBuild complete! Executable is in dist/bulletin/")
