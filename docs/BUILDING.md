# Building Bulletin Builder

This guide explains how to build standalone executables of Bulletin Builder using PyInstaller.

## Quick Start

```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# IMPORTANT: Close the Bulletin Builder application if it's running
# (to avoid Windows permission errors)

# Build the executable
python scripts/build_exe.py
```

The built application will be in `dist/bulletin/`.

## Prerequisites

- Python 3.9+ with pip
- PyInstaller 6.0+
- All project dependencies installed (`pip install -e .`)
- **Windows users:** Close any running instances of Bulletin Builder before building

## Build Process

### 1. Canonical Spec File

The project uses a single, canonical PyInstaller spec file:

**Location:** `packaging/bulletin_builder.spec`

This spec file:
- Collects all Python modules and dependencies
- Includes all necessary data files (templates, assets, config)
- Configures the executable settings
- Is the **only** spec file that should be used or modified

### 2. What Gets Included

The build process automatically includes:

**Python Modules:**
- All `bulletin_builder` submodules
- `customtkinter` - GUI framework
- `PIL` - Image processing
- `requests` - HTTP requests
- `jinja2` - Template rendering
- `weasyprint` - PDF export (optional)

**Data Files:**
- `src/bulletin_builder/templates/` → Template files for rendering
- `templates/` → Additional top-level templates
- `assets/` → Images, icons, and other assets
- `config.ini.default` → Default configuration
- `components/` → Component templates

### 3. Build Script

**File:** `scripts/build_exe.py`

The build script:
1. Manually cleans build/dist directories (with retry logic for Windows)
2. Locates the canonical spec file
3. Runs PyInstaller with `--noconfirm` flag
4. Reports build progress and completion

**Options:**
- Default: Cleans previous builds before building
- `--no-clean`: Skip the cleanup step

```bash
python scripts/build_exe.py          # Normal build with cleanup
python scripts/build_exe.py --no-clean  # Build without cleanup
```

### 4. Manual Build

If you need to build manually:

```bash
# From project root
pyinstaller packaging/bulletin_builder.spec --clean --noconfirm
```

## Build Configuration

### Modifying the Spec File

Only edit `packaging/bulletin_builder.spec`. Key sections:

**Hidden Imports** - Add any modules not automatically detected:
```python
hiddenimports.extend([
    'your_module_here',
])
```

**Data Files** - Add additional data files:
```python
datas = [
    ('source/path', 'destination/in/bundle'),
]
```

**Excludes** - Exclude large unused packages:
```python
excludes=[
    'matplotlib',
    'scipy',
]
```

**Console Mode** - Toggle console window:
```python
exe = EXE(
    ...
    console=False,  # False = GUI only, True = show console
)
```

**Icon** - Set application icon:
```python
exe = EXE(
    ...
    icon='assets/icon.ico',  # Path to .ico file
)
```

## Build Output

After building, you'll find:

```
dist/
└── bulletin/
    ├── bulletin.exe          # Main executable (Windows)
    ├── bulletin_builder/     # Python package
    │   └── templates/        # Included templates
    ├── templates/            # Additional templates
    ├── assets/               # Images and assets
    ├── components/           # Component templates
    ├── config.ini.default    # Default config
    └── _internal/            # PyInstaller internals and dependencies
```

## Distribution

To distribute the application:

### Option 1: Zip the Directory

```bash
# Windows PowerShell
Compress-Archive -Path dist/bulletin -DestinationPath bulletin_builder_v1.0.zip
```

### Option 2: Installer (Future)

Consider using:
- **Windows:** Inno Setup, NSIS, or WiX
- **macOS:** Create .app bundle and .dmg
- **Linux:** AppImage, snap, or flatpak

## Testing the Build

After building, test the executable:

```bash
# Navigate to build directory
cd dist/bulletin

# Run the executable
./bulletin.exe --gui        # Windows
./bulletin --gui            # Linux/macOS

# Test CLI mode
./bulletin.exe --version
```

## Troubleshooting

### Windows Permission Errors (PermissionError [WinError 5])

**Problem:** Build fails with "PermissionError: [WinError 5] Access is denied" when trying to remove build or dist directories.

**Common Cause:** The Bulletin Builder application is still running in the background, holding locks on files in the dist folder (especially `dist\bulletin\_internal\aiohttp\_websocket` and other DLL files).

**Solutions:**

1. **Close the Application First (Recommended):**
   ```bash
   # Make sure no bulletin.exe or python processes are running
   # On Windows PowerShell:
   taskkill /F /IM bulletin.exe /T
   
   # Or close via Task Manager:
   # Ctrl+Shift+Esc → Find "bulletin.exe" or "Bulletin Builder" → End Task
   
   # Then build:
   python scripts/build_exe.py
   ```

2. **Use the --no-clean Flag:**
   ```bash
   # Skip cleanup and build anyway
   python scripts/build_exe.py --no-clean
   ```

3. **Use Build Directory Output:**
   If the build succeeds but fails copying to dist, the executable is still created successfully in `build/bulletin_builder/bulletin.exe`. You can use this directly:
   ```bash
   # Run from build directory
   build\bulletin_builder\bulletin.exe --gui
   ```

4. **Manual Cleanup:**
   ```powershell
   # Force remove directories (requires admin privileges)
   Remove-Item -Path "build" -Recurse -Force
   Remove-Item -Path "dist" -Recurse -Force
   
   # Then build
   python scripts/build_exe.py --no-clean
   ```

**Technical Details:**
- PyInstaller completes all build stages successfully (Analysis → PYZ → PKG → EXE)
- The EXE is created in `build/bulletin_builder/bulletin.exe`
- Only the final COLLECT stage (copying to dist) fails when files are locked
- The build script includes retry logic with 2-second delays for transient locks
- If retry fails, you'll see warnings but the build continues

### Missing Modules

**Problem:** ImportError when running the executable

**Solution:** Add the missing module to `hiddenimports` in the spec file:

```python
hiddenimports.extend([
    'missing_module_name',
])
```

### Missing Data Files

**Problem:** FileNotFoundError for templates or assets

**Solution:** Add the files to `datas` in the spec file:

```python
datas = [
    ('path/to/file', 'destination/in/bundle'),
]
```

### Large Build Size

**Problem:** Executable is too large

**Solutions:**
1. Add unused packages to `excludes`
2. Use UPX compression (already enabled)
3. Remove unused dependencies from requirements.txt

```python
excludes=[
    'matplotlib',  # If not used
    'scipy',       # If not used
    'numpy',       # If not used
]
```

### Build Fails

**Problem:** PyInstaller fails during build

**Solutions:**
1. **First:** Close any running instances of the application (see Windows Permission Errors above)
2. Ensure all dependencies are installed: `pip install -r requirements.txt`
3. Update PyInstaller: `pip install --upgrade pyinstaller`
4. Check the build log in `build/bulletin/` directory
5. Try with `--no-clean` flag to skip problematic cleanup

### Console Window Appears

**Problem:** Console window shows behind GUI (Windows)

**Solution:** Set `console=False` in spec file:

```python
exe = EXE(
    ...
    console=False,
)
```

## Platform-Specific Notes

### Windows

- Build creates `.exe` executable
- No console window if `console=False`
- Can add icon with `.ico` file
- Antivirus may flag the executable (false positive)

### macOS

- Build creates Unix executable
- May need to sign and notarize for distribution
- Create `.app` bundle for better integration

### Linux

- Build creates ELF executable
- May need to mark as executable: `chmod +x bulletin`
- Consider creating AppImage for better portability

## Clean Build

To ensure a fresh build:

```bash
# Remove old builds
rm -rf build dist

# Clean PyInstaller cache
rm -rf __pycache__ .pytest_cache

# Rebuild
python scripts/build_exe.py
```

## Continuous Integration

For CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Build executable
  run: |
    pip install pyinstaller
    python scripts/build_exe.py
    
- name: Upload artifact
  uses: actions/upload-artifact@v3
  with:
    name: bulletin-builder-windows
    path: dist/bulletin/
```

## Version Management

Update version in builds:

1. Update version in `src/bulletin_builder/__init__.py`
2. Rebuild
3. Rename output: `bulletin_v1.2.3.zip`

## Security Considerations

- Don't include sensitive data in the build
- `config.ini` is NOT included (only `config.ini.default`)
- Users must configure their own API keys
- Consider code signing for distribution

## Further Reading

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyInstaller Spec Files](https://pyinstaller.org/en/stable/spec-files.html)
- [Distributing Python Applications](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/)
