#!/usr/bin/env python3
"""
Linux Build Script for Bulletin Builder

Builds a standalone Linux executable using PyInstaller.
Optionally creates an AppImage for universal Linux distribution.

Usage:
    python scripts/build_linux.py
    python scripts/build_linux.py --no-clean
    python scripts/build_linux.py --appimage  # Create AppImage (requires appimagetool)

Requirements:
    - Linux (tested on Ubuntu 20.04+)
    - Python 3.9+
    - PyInstaller 6.0+
    - All project dependencies installed
    - For AppImage: appimagetool (https://github.com/AppImage/AppImageKit/releases)

Output:
    - dist/bulletin/ - Standalone Linux executable directory
    - dist/Bulletin_Builder-x86_64.AppImage (with --appimage flag)

Notes:
    - The executable requires glibc 2.27+ (Ubuntu 18.04+, Debian 10+, Fedora 28+)
    - AppImage is portable and works on most modern Linux distributions
    - May require installing system dependencies: libgtk-3-0, libpango-1.0-0
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


def create_appimage(project_root: Path, dist_dir: Path) -> bool:
    """Create an AppImage from the built executable"""
    print("\nCreating AppImage...")
    
    # Check if appimagetool is available
    appimagetool = shutil.which("appimagetool")
    if not appimagetool:
        print("⚠ appimagetool not found!")
        print("\nTo create AppImages, install appimagetool:")
        print("  wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage")
        print("  chmod +x appimagetool-x86_64.AppImage")
        print("  sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool")
        return False
    
    # Create AppDir structure
    appdir = dist_dir / "Bulletin_Builder.AppDir"
    if appdir.exists():
        shutil.rmtree(appdir)
    
    appdir.mkdir()
    
    # Copy executable and dependencies
    bulletin_dir = dist_dir / "bulletin"
    if not bulletin_dir.exists():
        print(f"✗ Error: bulletin directory not found: {bulletin_dir}")
        return False
    
    usr_bin = appdir / "usr" / "bin"
    usr_bin.mkdir(parents=True)
    
    # Copy all files from bulletin/ to usr/bin/
    shutil.copytree(bulletin_dir, usr_bin / "bulletin")
    
    # Create AppRun script
    apprun = appdir / "AppRun"
    apprun.write_text("""#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin/:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib/:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/bulletin/bulletin" "$@"
""")
    apprun.chmod(0o755)
    
    # Create .desktop file
    desktop_file = appdir / "bulletin_builder.desktop"
    desktop_file.write_text("""[Desktop Entry]
Name=Bulletin Builder
Exec=bulletin
Icon=bulletin_builder
Type=Application
Categories=Office;Publishing;
Comment=Create and publish bulletins with ease
Terminal=false
""")
    
    # Create or copy icon (placeholder for now)
    icon_file = appdir / "bulletin_builder.png"
    # TODO: Copy actual icon from assets/
    assets_icon = project_root / "assets" / "icon.png"
    if assets_icon.exists():
        shutil.copy(assets_icon, icon_file)
    else:
        # Create a minimal placeholder icon
        print("  ⚠ No icon found, creating placeholder")
        icon_file.write_bytes(b"")  # Placeholder
    
    # Run appimagetool
    appimage_name = "Bulletin_Builder-x86_64.AppImage"
    appimage_path = dist_dir / appimage_name
    
    if appimage_path.exists():
        appimage_path.unlink()
    
    print(f"  Running appimagetool...")
    result = subprocess.run(
        [appimagetool, str(appdir), str(appimage_path)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"✗ appimagetool failed: {result.stderr}")
        return False
    
    if appimage_path.exists():
        appimage_path.chmod(0o755)
        print(f"✓ Created AppImage: {appimage_path}")
        return True
    else:
        print("✗ AppImage creation failed (file not created)")
        return False


def print_instructions(dist_dir: Path, has_appimage: bool):
    """Print post-build instructions"""
    print_header("Build Complete!")
    
    bulletin_dir = dist_dir / "bulletin"
    
    print(f"✓ Executable directory: {bulletin_dir}")
    print("\nTo run:")
    print(f"  cd {bulletin_dir}")
    print("  ./bulletin --gui")
    
    if has_appimage:
        appimage = dist_dir / "Bulletin_Builder-x86_64.AppImage"
        print(f"\n✓ AppImage: {appimage}")
        print("\nTo run AppImage:")
        print(f"  chmod +x {appimage.name}")
        print(f"  ./{appimage.name}")
        print("\nTo distribute:")
        print(f"  - Share {appimage.name} - it works on most Linux distributions")
        print("  - Users can run it directly or integrate with their system")
    
    print("\nSystem Requirements:")
    print("  - glibc 2.27+ (Ubuntu 18.04+, Debian 10+, Fedora 28+)")
    print("  - GTK3, Pango (usually pre-installed)")
    print("\nIf missing dependencies:")
    print("  sudo apt install libgtk-3-0 libpango-1.0-0  # Ubuntu/Debian")
    print("  sudo dnf install gtk3 pango                  # Fedora")


def main():
    # Check if running on Linux
    if sys.platform != "linux":
        print("⚠ Warning: This script is designed for Linux.")
        print(f"Current platform: {sys.platform}")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Parse arguments
    skip_clean = "--no-clean" in sys.argv
    create_appimage_flag = "--appimage" in sys.argv
    
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print_header("Bulletin Builder - Linux Build")
    
    # Clean previous builds
    cleanup_directories(project_root, skip_clean)
    
    # Find spec file
    spec_file = find_spec_file(project_root)
    
    # Run PyInstaller
    run_pyinstaller(spec_file)
    
    # Create AppImage if requested
    dist_dir = project_root / "dist"
    has_appimage = False
    if create_appimage_flag:
        has_appimage = create_appimage(project_root, dist_dir)
    
    # Print instructions
    print_instructions(dist_dir, has_appimage)


if __name__ == "__main__":
    main()
