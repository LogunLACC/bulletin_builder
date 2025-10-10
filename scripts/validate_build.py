#!/usr/bin/env python3
"""
Build Validation Script for Bulletin Builder

This script validates that the PyInstaller build is complete and functional.
It checks for:
- Executable exists and has correct structure
- All required data files are present (templates, components, config)
- Dependencies are included
- Executable can launch (basic smoke test)

Usage:
    python scripts/validate_build.py
    python scripts/validate_build.py --dist-path custom/path/to/dist

Exit codes:
    0 - All validations passed
    1 - One or more validations failed
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


class BuildValidator:
    """Validates PyInstaller build artifacts"""
    
    def __init__(self, dist_path: Path):
        self.dist_path = dist_path
        self.exe_path = dist_path / "bulletin.exe"
        self.internal_path = dist_path / "_internal"
        self.errors: list[str] = []
        self.warnings: list[str] = []
        
    def validate_all(self) -> bool:
        """Run all validation checks. Returns True if all pass."""
        print("=" * 60)
        print("Bulletin Builder - Build Validation")
        print("=" * 60)
        print(f"Validating build at: {self.dist_path}\n")
        
        checks = [
            ("Executable exists", self.check_executable_exists),
            ("Internal structure", self.check_internal_structure),
            ("Templates directory", self.check_templates),
            ("Components directory", self.check_components),
            ("Config file", self.check_config),
            ("Python dependencies", self.check_python_deps),
            ("Required DLLs", self.check_dlls),
            ("Executable launches", self.check_executable_launches),
        ]
        
        passed = 0
        failed = 0
        
        for name, check_func in checks:
            try:
                result = check_func()
                status = "✓ PASS" if result else "✗ FAIL"
                print(f"[{status}] {name}")
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"[✗ ERROR] {name}: {e}")
                self.errors.append(f"{name}: {e}")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"Results: {passed} passed, {failed} failed")
        print("=" * 60)
        
        if self.warnings:
            print("\n⚠ Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.errors:
            print("\n✗ Errors:")
            for error in self.errors:
                print(f"  - {error}")
        
        return failed == 0
    
    def check_executable_exists(self) -> bool:
        """Check if bulletin.exe exists and is executable"""
        if not self.exe_path.exists():
            self.errors.append(f"Executable not found: {self.exe_path}")
            return False
        
        if not self.exe_path.is_file():
            self.errors.append(f"Executable is not a file: {self.exe_path}")
            return False
        
        # Check file size is reasonable (should be at least 1MB)
        size_mb = self.exe_path.stat().st_size / (1024 * 1024)
        if size_mb < 1:
            self.warnings.append(f"Executable size is very small: {size_mb:.2f} MB")
        
        return True
    
    def check_internal_structure(self) -> bool:
        """Check if _internal directory exists with expected structure"""
        if not self.internal_path.exists():
            self.errors.append(f"_internal directory not found: {self.internal_path}")
            return False
        
        required_files = [
            "base_library.zip",
            "python313.dll",
        ]
        
        missing = []
        for file in required_files:
            if not (self.internal_path / file).exists():
                missing.append(file)
        
        if missing:
            self.errors.append(f"Missing required files in _internal: {', '.join(missing)}")
            return False
        
        return True
    
    def check_templates(self) -> bool:
        """Check if templates directory exists with required files"""
        templates_path = self.internal_path / "templates"
        
        if not templates_path.exists():
            # Also check bulletin_builder/templates
            templates_path = self.internal_path / "bulletin_builder" / "templates"
            if not templates_path.exists():
                self.errors.append("Templates directory not found")
                return False
        
        required_templates = [
            "base.html",
            "main_layout.html",
        ]
        
        required_themes = [
            "themes/default.css",
            "themes/holiday.css",
        ]
        
        required_partials = [
            "partials/announcements.html",
            "partials/events.html",
        ]
        
        missing = []
        for template in required_templates:
            if not (templates_path / template).exists():
                missing.append(template)
        
        for theme in required_themes:
            if not (templates_path / theme).exists():
                missing.append(theme)
        
        for partial in required_partials:
            if not (templates_path / partial).exists():
                missing.append(partial)
        
        if missing:
            self.errors.append(f"Missing template files: {', '.join(missing)}")
            return False
        
        return True
    
    def check_components(self) -> bool:
        """Check if components directory exists"""
        components_path = self.internal_path / "components"
        
        if not components_path.exists():
            self.errors.append("Components directory not found")
            return False
        
        # Check for at least one component file
        components = list(components_path.glob("*.json"))
        if not components:
            self.warnings.append("No component files found (optional)")
        
        return True
    
    def check_config(self) -> bool:
        """Check if config.ini.default exists"""
        config_path = self.internal_path / "config.ini.default"
        
        if not config_path.exists():
            self.errors.append("config.ini.default not found")
            return False
        
        return True
    
    def check_python_deps(self) -> bool:
        """Check if key Python dependencies are present"""
        required_packages = [
            "customtkinter",
            "PIL",
            "markupsafe",  # jinja2 is typically in base_library.zip
        ]
        
        missing = []
        for package in required_packages:
            if not (self.internal_path / package).exists():
                missing.append(package)
        
        if missing:
            self.errors.append(f"Missing Python packages: {', '.join(missing)}")
            return False
        
        # Optional packages - warn if missing
        optional_packages = {
            "weasyprint": "PDF export may not work",
            "lxml": "HTML parsing may be limited",
        }
        
        for package, warning in optional_packages.items():
            if not (self.internal_path / package).exists():
                self.warnings.append(f"{package} not found ({warning})")
        
        return True
    
    def check_dlls(self) -> bool:
        """Check if required DLLs are present"""
        required_dlls = [
            "python313.dll",
            "_tkinter.pyd",
            "tcl86t.dll",
            "tk86t.dll",
        ]
        
        missing = []
        for dll in required_dlls:
            if not (self.internal_path / dll).exists():
                missing.append(dll)
        
        if missing:
            self.errors.append(f"Missing required DLLs: {', '.join(missing)}")
            return False
        
        return True
    
    def check_executable_launches(self) -> bool:
        """Basic smoke test - check if executable launches without crashing"""
        print("  Testing executable launch (this may take a few seconds)...")
        
        try:
            # Launch with --version flag (quick test)
            # Note: bulletin.exe may not have --version, so we'll try --gui with quick kill
            process = subprocess.Popen(
                [str(self.exe_path), "--gui"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            # Give it 3 seconds to start
            time.sleep(3)
            
            # Check if process is still running (good sign)
            poll = process.poll()
            
            # Kill the process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            if poll is not None and poll != 0:
                # Process exited with error before we killed it
                stderr = process.stderr.read().decode('utf-8', errors='ignore')
                self.errors.append(f"Executable crashed on launch with exit code {poll}")
                if stderr:
                    self.errors.append(f"Error output: {stderr[:500]}")
                return False
            
            return True
            
        except FileNotFoundError:
            self.errors.append(f"Executable not found: {self.exe_path}")
            return False
        except Exception as e:
            self.errors.append(f"Error launching executable: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Validate Bulletin Builder PyInstaller build"
    )
    parser.add_argument(
        "--dist-path",
        type=Path,
        default=None,
        help="Path to dist/bulletin directory (default: auto-detect)"
    )
    
    args = parser.parse_args()
    
    # Determine dist path
    if args.dist_path:
        dist_path = args.dist_path
    else:
        # Auto-detect: assume we're running from project root or scripts/
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        dist_path = project_root / "dist" / "bulletin"
    
    if not dist_path.exists():
        print(f"Error: Dist directory not found: {dist_path}")
        print("\nPlease build the project first:")
        print("  python scripts/build_exe.py")
        sys.exit(1)
    
    validator = BuildValidator(dist_path)
    success = validator.validate_all()
    
    if success:
        print("\n✓ All validations passed! The build is ready for distribution.")
        sys.exit(0)
    else:
        print("\n✗ Some validations failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
