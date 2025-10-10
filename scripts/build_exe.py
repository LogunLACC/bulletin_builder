#!/usr/bin/env python3
"""
Build standalone executables using PyInstaller.

This script uses the canonical spec file located at packaging/bulletin_builder.spec
and performs a clean build to ensure all dependencies and data files are properly included.

Usage:
    python scripts/build_exe.py [--no-clean]
    
The built executable will be in the dist/bulletin/ directory.
"""
import PyInstaller.__main__
import sys
import shutil
import time
from pathlib import Path

# Ensure we're in the project root
project_root = Path(__file__).parent.parent
spec_file = project_root / 'packaging' / 'bulletin_builder.spec'

if not spec_file.exists():
    print(f"Error: Spec file not found at {spec_file}")
    sys.exit(1)

# Check for --no-clean flag
use_clean = '--no-clean' not in sys.argv

if use_clean:
    # Manually clean build directories to avoid permission errors
    build_dir = project_root / 'build'
    dist_dir = project_root / 'dist'
    
    print("Cleaning previous build artifacts...")
    for directory in [build_dir, dist_dir]:
        if directory.exists():
            try:
                shutil.rmtree(directory)
                print(f"  Removed {directory}")
            except PermissionError as e:
                print(f"  Warning: Could not remove {directory}: {e}")
                print(f"  Waiting 2 seconds and retrying...")
                time.sleep(2)
                try:
                    shutil.rmtree(directory)
                    print(f"  Successfully removed {directory} on retry")
                except Exception as retry_error:
                    print(f"  Warning: Still could not remove {directory}: {retry_error}")
                    print(f"  Continuing anyway...")

print(f"\nBuilding from spec file: {spec_file}")
print("This may take several minutes...")

# Build without --clean since we manually cleaned above
PyInstaller.__main__.run([
    str(spec_file),
    '--noconfirm',
])

print("\n" + "="*60)
print("Build complete! Executable is in dist/bulletin/")
print("="*60)
