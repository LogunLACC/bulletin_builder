# Creating Installers for Bulletin Builder

This guide explains how to create professional installers for distributing Bulletin Builder to end users.

## Table of Contents

- [Windows Installer (Inno Setup)](#windows-installer-inno-setup)
- [macOS DMG Installer](#macos-dmg-installer)
- [Linux Packages](#linux-packages)
  - [Debian/Ubuntu (.deb)](#debianubuntu-deb)
  - [Fedora/RHEL (.rpm)](#fedorarhel-rpm)

---

## Windows Installer (Inno Setup)

Creates a professional Windows installer with Start Menu shortcuts, desktop icon option, and proper uninstaller.

### Prerequisites

1. **Build the executable first:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\force_build_windows.ps1
   ```

2. **Install Inno Setup:**
   - Download from: https://jrsoftware.org/isdl.php
   - Install version 6.2.0 or later
   - Add to PATH for command-line usage (optional)

3. **Optional: Create an icon file:**
   ```powershell
   # If you have a PNG, convert to ICO format
   # Use an online converter or ImageMagick:
   magick convert logo.png -define icon:auto-resize=256,128,64,48,32,16 assets/icon.ico
   ```
   
   Then uncomment the `SetupIconFile` line in `packaging/bulletin_builder.iss`

### Building the Installer

#### Using Inno Setup GUI:

1. Open Inno Setup Compiler
2. File → Open → Select `packaging\bulletin_builder.iss`
3. Build → Compile
4. The installer will be created in `dist\BulletinBuilder-2.0.0-Setup.exe`

#### Using Command Line:

```powershell
# From project root
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" packaging\bulletin_builder.iss
```

### What the Installer Includes:

- ✅ Complete application bundle from `dist\bulletin\`
- ✅ Start Menu shortcuts (Launch app, Uninstall, README)
- ✅ Optional desktop icon
- ✅ Optional Quick Launch icon (Windows 7)
- ✅ Automatic creation of `user_drafts` and `user_drafts\AutoSave` directories
- ✅ Copies `config.ini.default` to `config.ini` on first install
- ✅ Professional uninstaller with option to preserve user data
- ✅ Modern wizard UI
- ✅ License agreement display
- ✅ Requires Windows 10 (build 17763) or later

### Customizing the Installer:

Edit `packaging\bulletin_builder.iss`:

```ini
; Change application name
#define MyAppName "Your App Name"

; Change version
#define MyAppVersion "2.0.0"

; Change publisher
#define MyAppPublisher "Your Organization"

; Require admin privileges (change to 'lowest' for per-user install)
PrivilegesRequired=admin

; Default installation directory
DefaultDirName={autopf}\{#MyAppName}
```

### Testing the Installer:

1. **Clean install test:**
   ```powershell
   # Run the installer
   dist\BulletinBuilder-2.0.0-Setup.exe
   
   # Launch from Start Menu
   # Verify: Start Menu → Bulletin Builder → Bulletin Builder
   ```

2. **Upgrade test:**
   - Install version 2.0.0
   - Build version 2.0.1
   - Install 2.0.1 over 2.0.0
   - Verify settings preserved

3. **Uninstall test:**
   - Uninstall from Control Panel
   - Check if user data preservation prompt appears
   - Verify clean removal

### Distribution:

```powershell
# The installer is a single .exe file
dist\BulletinBuilder-2.0.0-Setup.exe

# Size: ~150-200 MB
# Users only need to download and run this file
# No Python or dependencies required
```

---

## macOS DMG Installer

Creates a beautiful drag-to-Applications DMG disk image.

### Prerequisites

1. **Build the macOS .app bundle first:**
   ```bash
   python scripts/build_macos.py
   ```

2. **macOS 10.13+ (High Sierra or later)**

3. **Optional: Code signing certificate**
   - Apple Developer account required ($99/year)
   - Install Developer ID certificate in Keychain

### Creating the DMG

#### Method 1: Using create-dmg (Recommended)

```bash
# Install create-dmg via Homebrew
brew install create-dmg

# Create DMG with custom background
create-dmg \
  --volname "Bulletin Builder" \
  --volicon "assets/icon.icns" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "Bulletin Builder.app" 175 120 \
  --hide-extension "Bulletin Builder.app" \
  --app-drop-link 425 120 \
  --background "assets/dmg-background.png" \
  "dist/BulletinBuilder-2.0.0.dmg" \
  "dist/"
```

#### Method 2: Using hdiutil (Built-in)

```bash
# Simple DMG without custom background
hdiutil create -volname "Bulletin Builder" \
  -srcfolder dist/ \
  -ov -format UDZO \
  dist/BulletinBuilder-2.0.0.dmg
```

### Creating Custom DMG Background:

1. **Create background image (1000x600px recommended):**
   - Include arrow from app icon to Applications folder
   - Use PNG format
   - Save as `assets/dmg-background.png`

2. **Create .icns icon from PNG:**
   ```bash
   # Create iconset
   mkdir icon.iconset
   sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
   sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
   sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
   sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
   sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
   sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
   sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
   sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
   sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
   sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
   
   # Convert to .icns
   iconutil -c icns icon.iconset
   mv icon.icns assets/
   ```

### Code Signing (Optional but Recommended):

```bash
# Sign the .app bundle
codesign --force --deep --sign "Developer ID Application: Your Name (TEAM_ID)" \
  "dist/Bulletin Builder.app"

# Verify signature
codesign --verify --verbose "dist/Bulletin Builder.app"
spctl -a -v "dist/Bulletin Builder.app"

# Sign the DMG
codesign --sign "Developer ID Application: Your Name (TEAM_ID)" \
  dist/BulletinBuilder-2.0.0.dmg

# Notarize (for macOS 10.15+)
xcrun notarytool submit dist/BulletinBuilder-2.0.0.dmg \
  --apple-id your@email.com \
  --password app-specific-password \
  --team-id TEAM_ID \
  --wait

# Staple the notarization ticket
xcrun stapler staple dist/BulletinBuilder-2.0.0.dmg
```

### What the DMG Includes:

- ✅ Bulletin Builder.app bundle
- ✅ Symbolic link to /Applications folder
- ✅ Custom background with installation instructions
- ✅ Professional appearance
- ✅ Easy drag-and-drop installation

### Testing the DMG:

```bash
# Mount and test
open dist/BulletinBuilder-2.0.0.dmg

# Drag to Applications
# Launch from Applications folder
# Verify no Gatekeeper warnings (if signed and notarized)
```

---

## Linux Packages

### Debian/Ubuntu (.deb)

Creates a Debian package for Ubuntu, Debian, and derivatives.

#### Prerequisites:

```bash
# Install build tools
sudo apt update
sudo apt install dpkg-dev debhelper

# Build the Linux executable first
python scripts/build_linux.py
```

#### Package Structure:

```
bulletin-builder_2.0.0/
├── DEBIAN/
│   ├── control          # Package metadata
│   ├── postinst         # Post-installation script
│   └── postrm           # Post-removal script
├── usr/
│   ├── bin/
│   │   └── bulletin-builder  # Symlink to executable
│   ├── share/
│   │   ├── applications/
│   │   │   └── bulletin-builder.desktop
│   │   ├── icons/
│   │   │   └── hicolor/
│   │   │       └── 256x256/
│   │   │           └── apps/
│   │   │               └── bulletin-builder.png
│   │   └── bulletin-builder/
│   │       └── [all app files]
│   └── share/doc/bulletin-builder/
│       ├── copyright
│       └── changelog.gz
```

#### Create Package Script:

```bash
#!/bin/bash
# scripts/build_deb.sh

set -e

APP_NAME="bulletin-builder"
VERSION="2.0.0"
ARCH="amd64"
PKG_DIR="${APP_NAME}_${VERSION}"

echo "Building Debian package for ${APP_NAME} ${VERSION}..."

# Clean previous build
rm -rf "$PKG_DIR" "${PKG_DIR}.deb"

# Create directory structure
mkdir -p "$PKG_DIR/DEBIAN"
mkdir -p "$PKG_DIR/usr/bin"
mkdir -p "$PKG_DIR/usr/share/applications"
mkdir -p "$PKG_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$PKG_DIR/usr/share/$APP_NAME"
mkdir -p "$PKG_DIR/usr/share/doc/$APP_NAME"

# Copy application files
cp -r dist/bulletin/* "$PKG_DIR/usr/share/$APP_NAME/"

# Create symlink in /usr/bin
ln -s "/usr/share/$APP_NAME/bulletin" "$PKG_DIR/usr/bin/$APP_NAME"

# Create control file
cat > "$PKG_DIR/DEBIAN/control" << EOF
Package: $APP_NAME
Version: $VERSION
Section: editors
Priority: optional
Architecture: $ARCH
Depends: libgtk-3-0, libpango-1.0-0, libcairo2, libgdk-pixbuf2.0-0
Maintainer: Lake Almanor Community Church <support@example.com>
Description: Bulletin Builder - Email bulletin creation tool
 Bulletin Builder is a professional email bulletin creation tool
 with a modern UI, drag-and-drop editing, and strict email
 compatibility enforcement.
EOF

# Create desktop entry
cat > "$PKG_DIR/usr/share/applications/$APP_NAME.desktop" << EOF
[Desktop Entry]
Name=Bulletin Builder
Comment=Create professional email bulletins
Exec=/usr/bin/$APP_NAME --gui
Icon=$APP_NAME
Terminal=false
Type=Application
Categories=Office;Publishing;
Keywords=email;bulletin;newsletter;
EOF

# Copy icon (if exists)
if [ -f "assets/icon.png" ]; then
    cp assets/icon.png "$PKG_DIR/usr/share/icons/hicolor/256x256/apps/$APP_NAME.png"
fi

# Create copyright file
cat > "$PKG_DIR/usr/share/doc/$APP_NAME/copyright" << EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: Bulletin Builder
Source: https://github.com/LogunLACC/bulletin_builder

Files: *
Copyright: 2025 Lake Almanor Community Church
License: MIT
 [Full license text here]
EOF

# Create changelog
cat > "$PKG_DIR/usr/share/doc/$APP_NAME/changelog" << EOF
bulletin-builder ($VERSION) stable; urgency=medium

  * Initial release

 -- Lake Almanor Community Church <support@example.com>  $(date -R)
EOF
gzip -9 "$PKG_DIR/usr/share/doc/$APP_NAME/changelog"

# Create postinst script
cat > "$PKG_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Update desktop database
if [ -x /usr/bin/update-desktop-database ]; then
    update-desktop-database -q
fi

# Update icon cache
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    gtk-update-icon-cache -q /usr/share/icons/hicolor
fi

exit 0
EOF
chmod 755 "$PKG_DIR/DEBIAN/postinst"

# Create postrm script
cat > "$PKG_DIR/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e

if [ "$1" = "remove" ] || [ "$1" = "purge" ]; then
    # Update desktop database
    if [ -x /usr/bin/update-desktop-database ]; then
        update-desktop-database -q
    fi
    
    # Update icon cache
    if [ -x /usr/bin/gtk-update-icon-cache ]; then
        gtk-update-icon-cache -q /usr/share/icons/hicolor
    fi
fi

exit 0
EOF
chmod 755 "$PKG_DIR/DEBIAN/postrm"

# Build the package
dpkg-deb --build --root-owner-group "$PKG_DIR"

echo "✅ Package created: ${PKG_DIR}.deb"
echo ""
echo "To install:"
echo "  sudo dpkg -i ${PKG_DIR}.deb"
echo "  sudo apt-get install -f  # Install dependencies if needed"
```

#### Build and Install:

```bash
# Make script executable
chmod +x scripts/build_deb.sh

# Build package
./scripts/build_deb.sh

# Install
sudo dpkg -i bulletin-builder_2.0.0.deb
sudo apt-get install -f  # Fix dependencies if needed

# Launch
bulletin-builder --gui
```

---

### Fedora/RHEL (.rpm)

Creates an RPM package for Fedora, RHEL, CentOS, and derivatives.

#### Prerequisites:

```bash
# Install build tools
sudo dnf install rpm-build rpmdevtools

# Set up RPM build environment
rpmdev-setuptree

# Build the Linux executable first
python scripts/build_linux.py
```

#### Create RPM Spec File:

```bash
# scripts/bulletin-builder.spec

Name:           bulletin-builder
Version:        2.0.0
Release:        1%{?dist}
Summary:        Professional email bulletin creation tool

License:        MIT
URL:            https://github.com/LogunLACC/bulletin_builder
Source0:        %{name}-%{version}.tar.gz

BuildArch:      x86_64
Requires:       gtk3 pango cairo gdk-pixbuf2

%description
Bulletin Builder is a professional email bulletin creation tool
with a modern UI, drag-and-drop editing, and strict email
compatibility enforcement.

%prep
%setup -q

%build
# Application is pre-built, nothing to do

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/share/%{name}
mkdir -p $RPM_BUILD_ROOT/usr/bin
mkdir -p $RPM_BUILD_ROOT/usr/share/applications
mkdir -p $RPM_BUILD_ROOT/usr/share/icons/hicolor/256x256/apps

# Copy application files
cp -r dist/bulletin/* $RPM_BUILD_ROOT/usr/share/%{name}/

# Create symlink
ln -s /usr/share/%{name}/bulletin $RPM_BUILD_ROOT/usr/bin/%{name}

# Install desktop file
cat > $RPM_BUILD_ROOT/usr/share/applications/%{name}.desktop << EOF
[Desktop Entry]
Name=Bulletin Builder
Comment=Create professional email bulletins
Exec=%{name} --gui
Icon=%{name}
Terminal=false
Type=Application
Categories=Office;Publishing;
EOF

# Install icon
install -m 644 assets/icon.png $RPM_BUILD_ROOT/usr/share/icons/hicolor/256x256/apps/%{name}.png

%files
/usr/bin/%{name}
/usr/share/%{name}/*
/usr/share/applications/%{name}.desktop
/usr/share/icons/hicolor/256x256/apps/%{name}.png

%post
/usr/bin/update-desktop-database &> /dev/null || :
/usr/bin/gtk-update-icon-cache /usr/share/icons/hicolor &> /dev/null || :

%postun
/usr/bin/update-desktop-database &> /dev/null || :
/usr/bin/gtk-update-icon-cache /usr/share/icons/hicolor &> /dev/null || :

%changelog
* $(date "+%a %b %d %Y") Lake Almanor Community Church <support@example.com> - 2.0.0-1
- Initial release
```

#### Build RPM:

```bash
# Create source tarball
tar -czf ~/rpmbuild/SOURCES/bulletin-builder-2.0.0.tar.gz \
  --transform 's,^,bulletin-builder-2.0.0/,' \
  dist/bulletin/ assets/ LICENSE README.md

# Build RPM
rpmbuild -ba scripts/bulletin-builder.spec

# RPM will be in ~/rpmbuild/RPMS/x86_64/
```

#### Install:

```bash
# Install the RPM
sudo dnf install ~/rpmbuild/RPMS/x86_64/bulletin-builder-2.0.0-1.*.x86_64.rpm

# Launch
bulletin-builder --gui
```

---

## Testing Checklist

### Windows Installer:
- [ ] Installs without errors
- [ ] Creates Start Menu shortcuts
- [ ] Desktop icon option works
- [ ] Application launches from Start Menu
- [ ] Uninstaller removes all files
- [ ] User data preservation prompt works
- [ ] Upgrade preserves settings

### macOS DMG:
- [ ] DMG mounts correctly
- [ ] Drag-to-Applications works
- [ ] Application launches from Applications folder
- [ ] No Gatekeeper warnings (if signed)
- [ ] Uninstall by dragging to Trash works

### Linux Packages:
- [ ] Package installs dependencies
- [ ] Desktop entry appears in application menu
- [ ] Icon displays correctly
- [ ] Application launches from menu
- [ ] Uninstall removes all files
- [ ] No library errors on launch

---

## Distribution

### Hosting Options:

1. **GitHub Releases** (Recommended):
   ```bash
   # Tag a release
   git tag v2.0.0
   git push origin v2.0.0
   
   # Upload installers to GitHub release
   ```

2. **Direct Download**:
   - Host on website
   - Provide checksums (SHA256)
   - Include installation instructions

3. **Package Repositories**:
   - **Linux**: Submit to distro repos (Ubuntu PPA, Fedora Copr)
   - **macOS**: Submit to Homebrew Cask
   - **Windows**: Submit to Chocolatey, Scoop, winget

### Checksums:

```bash
# Generate SHA256 checksums
sha256sum BulletinBuilder-2.0.0-Setup.exe > checksums.txt
sha256sum BulletinBuilder-2.0.0.dmg >> checksums.txt
sha256sum bulletin-builder_2.0.0_amd64.deb >> checksums.txt
sha256sum bulletin-builder-2.0.0-1.x86_64.rpm >> checksums.txt
```

---

## Notes

- **Windows**: Installer requires admin privileges for Program Files installation
- **macOS**: Unsigned apps show Gatekeeper warning (Right-click → Open to bypass)
- **Linux**: Dependencies (GTK3, Pango) are usually pre-installed on desktop distributions
- **Size**: Installers are 150-200 MB due to bundled Python runtime and dependencies
- **Updates**: Consider implementing auto-update checking in future versions

For questions or issues, see the [main BUILDING.md](BUILDING.md) documentation.
