#!/usr/bin/env python3
"""
macOS Build Script for Bulletin Builder

Builds a standalone .app bundle for macOS using PyInstaller.

Usage:
    python scripts/build_macos.py
    python scripts/build_macos.py --no-clean

Requirements:
    - macOS 10.13+ (High Sierra or later)
    - Python 3.9+
    - PyInstaller 6.0+
    - All project dependencies installed

Output:
    - dist/Bulletin Builder.app - macOS application bundle
    - Can be distributed as-is or packaged in a .dmg

Notes:
    - The .app bundle is self-contained and can be copied to /Applications
    - Code signing requires an Apple Developer certificate (optional)
    - To create a .dmg: hdiutil create -volname "Bulletin Builder" -srcfolder dist/ -ov -format UDZO bulletin_builder.dmg
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")


def cleanup_directories(project_root: Path, skip_clean: bool = False):
    """Clean previous build artifacts"""
    if skip_clean:
        print("Skipping cleanup (--no-clean flag)")
        return
    
    print("Cleaning previous build artifacts...")
    
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"
    
    for directory in [build_dir, dist_dir]:
        if directory.exists():
            try:
                shutil.rmtree(directory)
                print(f"  ✓ Removed {directory}")
            except PermissionError as e:
                print(f"  ⚠ Warning: Could not remove {directory}: {e}")
                print(f"  Waiting 2 seconds and retrying...")
                time.sleep(2)
                try:
                    shutil.rmtree(directory)
                    print(f"  ✓ Removed {directory} (retry successful)")
                except Exception as e2:
                    print(f"  ⚠ Warning: Still could not remove {directory}: {e2}")
                    print(f"  Continuing anyway...")


def find_spec_file(project_root: Path) -> Path:
    """Locate the canonical PyInstaller spec file"""
    spec_file = project_root / "packaging" / "bulletin_builder.spec"
    
    if not spec_file.exists():
        print(f"Error: Spec file not found: {spec_file}")
        print("Expected location: packaging/bulletin_builder.spec")
        sys.exit(1)
    
    return spec_file


def run_pyinstaller(spec_file: Path):
    """Run PyInstaller with the spec file"""
    print(f"Building from spec file: {spec_file}")
    print("This may take several minutes...\n")
    
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(spec_file),
        "--noconfirm",
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("\n✗ Build failed!")
        sys.exit(result.returncode)


def create_app_bundle(dist_dir: Path):
    """Create proper .app bundle structure for macOS"""
    # PyInstaller creates bulletin.app by default when using --windowed
    app_bundle = dist_dir / "bulletin.app"
    
    if not app_bundle.exists():
        print("\n⚠ Warning: bulletin.app not found in dist/")
        print("The spec file may need to be updated for macOS:")
        print("  - Set 'windowed=True' in the EXE section")
        print("  - Set 'bundle_identifier' in BUNDLE section")
        return
    
    # Rename to "Bulletin Builder.app" for better UX
    final_bundle = dist_dir / "Bulletin Builder.app"
    if final_bundle.exists():
        shutil.rmtree(final_bundle)
    
    shutil.move(str(app_bundle), str(final_bundle))
    print(f"\n✓ Created application bundle: {final_bundle}")
    
    # Verify bundle structure
    contents_dir = final_bundle / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"
    
    if not all([contents_dir.exists(), macos_dir.exists()]):
        print("⚠ Warning: App bundle structure may be incomplete")
        return
    
    print("\n✓ App bundle structure:")
    print(f"  - Contents/MacOS/ (executables)")
    print(f"  - Contents/Resources/ (data files)")
    if resources_dir.exists():
        print(f"  - Contents/Frameworks/ (libraries)")


def print_instructions(dist_dir: Path):
    """Print post-build instructions"""
    print_header("Build Complete!")
    
    app_bundle = dist_dir / "Bulletin Builder.app"
    
    if app_bundle.exists():
        print(f"✓ Application bundle: {app_bundle}")
        print("\nTo install:")
        print(f"  1. Open Finder and navigate to {dist_dir}")
        print("  2. Drag 'Bulletin Builder.app' to your Applications folder")
        print("\nTo run:")
        print("  1. Open 'Bulletin Builder' from Applications")
        print("  2. If you see 'unidentified developer' warning:")
        print("     - Right-click the app → Open")
        print("     - Or: System Preferences → Security → Allow")
        print("\nTo create a .dmg for distribution:")
        print('  hdiutil create -volname "Bulletin Builder" \\')
        print(f'    -srcfolder "{dist_dir}" \\')
        print('    -ov -format UDZO bulletin_builder.dmg')
    else:
        print(f"✓ Build artifacts in: {dist_dir}")
        print("\n⚠ Note: App bundle not found. Check spec file configuration.")


def main():
    # Check if running on macOS
    if sys.platform != "darwin":
        print("⚠ Warning: This script is designed for macOS (darwin).")
        print(f"Current platform: {sys.platform}")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Parse arguments
    skip_clean = "--no-clean" in sys.argv
    
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print_header("Bulletin Builder - macOS Build")
    
    # Clean previous builds
    cleanup_directories(project_root, skip_clean)
    
    # Find spec file
    spec_file = find_spec_file(project_root)
    
    # Run PyInstaller
    run_pyinstaller(spec_file)
    
    # Create proper .app bundle
    dist_dir = project_root / "dist"
    create_app_bundle(dist_dir)
    
    # Print instructions
    print_instructions(dist_dir)


if __name__ == "__main__":
    main()
