# Troubleshooting Guide

Comprehensive troubleshooting guide for common issues in Bulletin Builder.

## Table of Contents

- [Installation Issues](#installation-issues)
  - [Application Won't Launch](#application-wont-launch)
  - [Missing DLL Errors (Windows)](#missing-dll-errors-windows)
  - [Gatekeeper Blocking (macOS)](#gatekeeper-blocking-macos)
  - [Permission Denied (Linux)](#permission-denied-linux)
- [Import/Export Issues](#importexport-issues)
  - [CSV Import Failures](#csv-import-failures)
  - [JSON Import Failures](#json-import-failures)
  - [PDF Export Fails](#pdf-export-fails)
  - [HTML Export Issues](#html-export-issues)
- [File Operations](#file-operations)
  - [Can't Save Drafts](#cant-save-drafts)
  - [Auto-Save Not Working](#auto-save-not-working)
  - [Drafts Disappear](#drafts-disappear)
- [Email and SMTP Issues](#email-and-smtp-issues)
  - [SMTP Authentication Failed](#smtp-authentication-failed)
  - [Connection Refused/Timeout](#connection-refusedtimeout)
  - [Email Looks Broken in Client](#email-looks-broken-in-client)
- [Image and Media Issues](#image-and-media-issues)
  - [Images Not Displaying](#images-not-displaying)
  - [Video Embeds Not Working](#video-embeds-not-working)
  - [Large Images Cause Slowdown](#large-images-cause-slowdown)
- [Performance Issues](#performance-issues)
  - [Application Slow or Unresponsive](#application-slow-or-unresponsive)
  - [High Memory Usage](#high-memory-usage)
  - [Preview Takes Too Long](#preview-takes-too-long)
- [Build and Development Issues](#build-and-development-issues)
  - [Permission Errors During Build](#permission-errors-during-build)
  - [Module Import Errors](#module-import-errors)
  - [WeasyPrint Installation Problems](#weasyprint-installation-problems)
- [Configuration Issues](#configuration-issues)
  - [Settings Don't Persist](#settings-dont-persist)
  - [API Keys Not Working](#api-keys-not-working)
  - [Window State Not Saved](#window-state-not-saved)
- [Platform-Specific Issues](#platform-specific-issues)
  - [Windows](#windows)
  - [macOS](#macos)
  - [Linux](#linux)
- [Getting Additional Help](#getting-additional-help)

---

## Installation Issues

### Application Won't Launch

**Symptoms:**
- Double-clicking executable does nothing
- Application crashes immediately on startup
- Error message appears briefly then disappears

**Solutions:**

#### Windows:
1. **Run as Administrator:**
   ```
   Right-click bulletin.exe → "Run as administrator"
   ```

2. **Check Windows Defender/Antivirus:**
   - Add `bulletin.exe` to antivirus exceptions
   - Windows Defender may block unsigned executables

3. **Install Visual C++ Redistributables:**
   ```powershell
   # Download from Microsoft:
   # https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist
   ```

4. **Check Event Viewer for errors:**
   ```
   Windows Logs → Application → Look for "bulletin" errors
   ```

#### macOS:
1. **Bypass Gatekeeper** (see [Gatekeeper Blocking](#gatekeeper-blocking-macos))

2. **Check Console for errors:**
   ```bash
   # Open Console.app
   # Filter by "BulletinBuilder" or "bulletin"
   ```

3. **Reset quarantine attributes:**
   ```bash
   xattr -cr /Applications/BulletinBuilder.app
   ```

#### Linux:
1. **Make executable:**
   ```bash
   chmod +x BulletinBuilder.AppImage
   ```

2. **Install FUSE** (for AppImage):
   ```bash
   # Ubuntu/Debian
   sudo apt install libfuse2
   
   # Fedora
   sudo dnf install fuse-libs
   ```

3. **Run from terminal to see errors:**
   ```bash
   ./BulletinBuilder.AppImage
   ```

---

### Missing DLL Errors (Windows)

**Symptoms:**
- "python313.dll not found"
- "Failed to load Python DLL"
- "VCRUNTIME140.dll is missing"

**Cause:** Running executable from wrong location or missing system libraries.

**Solutions:**

1. **Use the correct executable location:**
   ```
   ✅ CORRECT: dist\bulletin\bulletin.exe
   ❌ WRONG:   build\bulletin_builder\bulletin.exe
   ```
   
   The `build/` folder contains intermediate artifacts without proper DLL bundling.

2. **Install Visual C++ Redistributables:**
   - Download from [Microsoft](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)
   - Install both x64 and x86 versions
   - Restart computer after installation

3. **Check _internal folder:**
   - Verify `dist\bulletin\_internal\` exists and contains `python313.dll`
   - If missing, rebuild from clean state:
     ```powershell
     .\scripts\force_build_windows.ps1
     ```

4. **Run dependency checker:**
   ```powershell
   # Download Dependency Walker: https://www.dependencywalker.com/
   # Analyze bulletin.exe to find missing DLLs
   ```

---

### Gatekeeper Blocking (macOS)

**Symptoms:**
- "BulletinBuilder.app is damaged and can't be opened"
- "BulletinBuilder.app is from an unidentified developer"
- Application won't open after download

**Solutions:**

1. **First-time bypass:**
   ```
   Right-click BulletinBuilder.app → Click "Open"
   → Click "Open" in security dialog
   ```

2. **Remove quarantine attribute:**
   ```bash
   xattr -cr /Applications/BulletinBuilder.app
   ```

3. **Allow in System Preferences:**
   ```
   System Preferences → Security & Privacy → General
   → Click "Open Anyway" next to blocked app message
   ```

4. **For repeated issues:**
   ```bash
   # Disable Gatekeeper (not recommended for security)
   sudo spctl --master-disable
   
   # Re-enable later
   sudo spctl --master-enable
   ```

---

### Permission Denied (Linux)

**Symptoms:**
- "Permission denied" when trying to run AppImage
- Application won't execute

**Solutions:**

1. **Make executable:**
   ```bash
   chmod +x BulletinBuilder.AppImage
   ```

2. **Run with explicit interpreter:**
   ```bash
   bash ./BulletinBuilder.AppImage
   ```

3. **Check file permissions:**
   ```bash
   ls -la BulletinBuilder.AppImage
   # Should show: -rwxr-xr-x (executable)
   ```

4. **Move out of restricted directory:**
   ```bash
   # Don't run from /tmp or root-owned directories
   mv BulletinBuilder.AppImage ~/Applications/
   ```

---

## Import/Export Issues

### CSV Import Failures

**Symptoms:**
- "Failed to parse CSV file"
- Events not imported correctly
- Missing data in imported events

**Solutions:**

1. **Verify CSV format:**
   ```csv
   Title,Date,Time,Location,Description
   "Sunday Service","2025-10-12","10:00 AM","Main Sanctuary","Weekly worship"
   "Bible Study","2025-10-15","7:00 PM","Fellowship Hall","Midweek study"
   ```

2. **Check encoding:**
   - Save CSV as UTF-8 (not UTF-8 with BOM)
   - Avoid special characters or escape them with quotes

3. **Required columns:**
   - Must have: `Title`, `Date`
   - Optional: `Time`, `Location`, `Description`
   - Column names are case-insensitive

4. **Date format:**
   - Use ISO format: `YYYY-MM-DD` (e.g., `2025-10-12`)
   - Or: `MM/DD/YYYY` (e.g., `10/12/2025`)
   - Consistent format throughout file

5. **Common issues:**
   ```csv
   # ❌ WRONG: Missing quotes around comma-containing text
   Event Name, Date, Location, Description
   Coffee, Donuts, and Fellowship, 2025-10-12, Hall, Join us
   
   # ✅ CORRECT: Quoted text with commas
   Title,Date,Location,Description
   "Coffee, Donuts, and Fellowship","2025-10-12","Fellowship Hall","Join us"
   ```

6. **Test with minimal CSV:**
   ```csv
   Title,Date
   "Test Event","2025-10-12"
   ```
   If this works, gradually add more columns to find problematic data.

---

### JSON Import Failures

**Symptoms:**
- "Invalid JSON format"
- "Failed to parse JSON file"
- Unexpected import results

**Solutions:**

1. **Validate JSON syntax:**
   - Use online validator: [jsonlint.com](https://jsonlint.com/)
   - Check for:
     * Missing commas
     * Trailing commas (not allowed in JSON)
     * Unquoted keys
     * Single quotes instead of double quotes

2. **Expected JSON format:**
   ```json
   [
     {
       "title": "Sunday Service",
       "date": "2025-10-12",
       "time": "10:00 AM",
       "location": "Main Sanctuary",
       "description": "Weekly worship service"
     },
     {
       "title": "Bible Study",
       "date": "2025-10-15",
       "time": "7:00 PM",
       "location": "Fellowship Hall",
       "description": "Midweek Bible study"
     }
   ]
   ```

3. **Common JSON errors:**
   ```json
   // ❌ WRONG: Trailing comma
   [
     {"title": "Event 1", "date": "2025-10-12"},
     {"title": "Event 2", "date": "2025-10-13"},  ← Remove this comma
   ]
   
   // ❌ WRONG: Single quotes
   [
     {'title': 'Event', 'date': '2025-10-12'}  ← Use double quotes
   ]
   
   // ❌ WRONG: Unquoted keys
   [
     {title: "Event", date: "2025-10-12"}  ← Quote the keys
   ]
   
   // ✅ CORRECT
   [
     {"title": "Event 1", "date": "2025-10-12"},
     {"title": "Event 2", "date": "2025-10-13"}
   ]
   ```

4. **Encoding issues:**
   ```bash
   # Save JSON as UTF-8 without BOM
   # Use a proper text editor (VS Code, Notepad++, not Notepad)
   ```

---

### PDF Export Fails

**Symptoms:**
- "PDF export failed"
- "WeasyPrint error"
- Blank or incomplete PDF

**Solutions:**

1. **Verify WeasyPrint installation:**
   ```bash
   pip install --upgrade weasyprint
   ```

2. **Install system dependencies:**

   **Windows:**
   ```powershell
   # Install GTK3 runtime
   # Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
   ```

   **macOS:**
   ```bash
   brew install python3 cairo pango gdk-pixbuf libffi
   ```

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0
   ```

   **Fedora:**
   ```bash
   sudo dnf install python3-cffi python3-brotli pango
   ```

3. **Simplify bulletin:**
   - Remove complex CSS (animations, transforms)
   - Use standard fonts
   - Optimize images (< 100KB each)

4. **Check console output:**
   ```bash
   # Run from terminal to see WeasyPrint errors:
   bulletin --gui  # (or double-click executable)
   ```

5. **Test with minimal content:**
   - Create bulletin with only text sections
   - If this works, add sections one by one to find problematic content

6. **Font issues:**
   ```css
   /* Use system fonts instead of custom fonts */
   body {
     font-family: Arial, sans-serif;  /* Avoid: @font-face imports */
   }
   ```

---

### HTML Export Issues

**Symptoms:**
- Broken layout in exported HTML
- Missing styles
- Images not showing

**Solutions:**

1. **Use email-ready export for portable HTML:**
   ```
   File → Export → Export for Email (inlined CSS)
   ```

2. **Check image URLs:**
   - Use absolute URLs: `https://example.com/image.jpg`
   - Not relative paths: `../images/photo.jpg`

3. **Validate HTML:**
   - Use [validator.w3.org](https://validator.w3.org/)
   - Fix validation errors

4. **Test in different browsers:**
   - Chrome/Edge (Chromium)
   - Firefox
   - Safari

5. **Check file encoding:**
   - Save as UTF-8
   - Include `<meta charset="UTF-8">` in HTML

---

## File Operations

### Can't Save Drafts

**Symptoms:**
- "Failed to save draft"
- Permission denied errors
- File not created

**Solutions:**

1. **Check disk space:**
   ```bash
   # Windows
   wmic logicaldisk get size,freespace,caption
   
   # macOS/Linux
   df -h
   ```

2. **Verify write permissions:**
   ```bash
   # Check user_drafts folder permissions
   ls -la user_drafts/
   
   # Fix permissions if needed
   chmod 755 user_drafts/
   ```

3. **Try different location:**
   ```
   File → Save Draft As → Choose different drive/folder
   ```

4. **Disable OneDrive sync:**
   - OneDrive may lock files during sync
   - Pause sync temporarily
   - Or save outside OneDrive folder

5. **Close other programs:**
   - Antivirus may lock files
   - File sync services (Dropbox, Google Drive)
   - Other instances of Bulletin Builder

6. **Check filename:**
   - Avoid special characters: `< > : " / \ | ? *`
   - Keep filename under 255 characters

---

### Auto-Save Not Working

**Symptoms:**
- Auto-save folder empty
- No auto-save notifications
- Drafts lost after crash

**Solutions:**

1. **Enable auto-save in settings:**
   ```ini
   [window]
   autosave_on_close = true
   ```

2. **Check auto-save folder exists:**
   ```bash
   # Should exist:
   user_drafts/AutoSave/
   
   # Create if missing:
   mkdir -p user_drafts/AutoSave/
   ```

3. **Verify permissions:**
   ```bash
   # Make sure app can write to AutoSave folder
   chmod 755 user_drafts/AutoSave/
   ```

4. **Check auto-save interval:**
   - Settings → General → Auto-save interval
   - Default: 5 minutes
   - Set to shorter interval for more frequent saves

5. **Test manually:**
   - Make changes to bulletin
   - Wait for auto-save interval
   - Check `user_drafts/AutoSave/` for new file

---

### Drafts Disappear

**Symptoms:**
- Saved drafts not visible in Open dialog
- Draft file exists but won't load
- Recent drafts missing

**Solutions:**

1. **Check file location:**
   ```bash
   # Default location:
   user_drafts/
   
   # Auto-save location:
   user_drafts/AutoSave/
   ```

2. **Search for JSON files:**
   ```bash
   # Windows
   dir /s *.json
   
   # macOS/Linux
   find . -name "*.json" -type f
   ```

3. **Verify JSON validity:**
   ```bash
   # Test with Python:
   python -m json.tool your_draft.json
   
   # Or use online validator: jsonlint.com
   ```

4. **Check recent files:**
   ```
   File → Open Recent → Check list
   ```

5. **Restore from backup:**
   - Check `user_drafts/AutoSave/` for recent auto-saves
   - Sort by date to find latest version

---

## Email and SMTP Issues

### SMTP Authentication Failed

**Symptoms:**
- "SMTP authentication failed"
- "Username and password not accepted"
- 535 authentication error

**Solutions:**

1. **Verify credentials:**
   - Check username (usually full email address)
   - Check password (use app-specific password, not account password)

2. **Generate app-specific password:**

   **Gmail:**
   ```
   Google Account → Security → 2-Step Verification → App passwords
   → Generate password for "Bulletin Builder"
   → Use 16-character password in config.ini
   ```

   **Yahoo:**
   ```
   Yahoo Account Security → Generate app password
   → Use generated password
   ```

   **Outlook:**
   ```
   Microsoft Account → Security → App passwords
   → Create new app password
   ```

3. **Check SMTP settings:**
   ```ini
   [smtp]
   host = smtp.gmail.com        # Correct hostname
   port = 587                   # TLS port (or 465 for SSL)
   username = user@gmail.com    # Full email address
   password = app_password      # App-specific password
   use_tls = true              # Must be true for port 587
   ```

4. **Enable 2FA:**
   - Most providers require 2FA for app passwords
   - Enable in account security settings

5. **Test SMTP manually:**
   ```bash
   # Install swaks (SMTP test tool)
   # Ubuntu/Debian
   sudo apt install swaks
   
   # Test connection
   swaks --to recipient@example.com \
         --from user@gmail.com \
         --server smtp.gmail.com:587 \
         --auth LOGIN \
         --auth-user user@gmail.com \
         --auth-password "app_password"
   ```

---

### Connection Refused/Timeout

**Symptoms:**
- "Connection refused" error
- "Connection timed out"
- "Unable to connect to SMTP server"

**Solutions:**

1. **Check firewall:**
   ```powershell
   # Windows: Allow outbound connections on port 587
   New-NetFirewallRule -DisplayName "SMTP" -Direction Outbound -LocalPort 587 -Protocol TCP -Action Allow
   ```

2. **Verify port:**
   - **Port 587:** TLS (STARTTLS) - Most common
   - **Port 465:** SSL - Gmail supports this
   - **Port 25:** Unencrypted - Usually blocked

3. **Test connectivity:**
   ```bash
   # Test port 587
   telnet smtp.gmail.com 587
   
   # Or use PowerShell (Windows)
   Test-NetConnection -ComputerName smtp.gmail.com -Port 587
   ```

4. **Check antivirus/security software:**
   - Disable temporarily to test
   - Add exception for Bulletin Builder
   - Allow outbound SMTP connections

5. **Try different port:**
   ```ini
   [smtp]
   port = 465    # Try SSL instead of TLS
   use_tls = false  # For SSL on port 465
   ```

6. **Check network restrictions:**
   - Corporate networks may block SMTP
   - Public Wi-Fi may restrict ports
   - Try from different network

---

### Email Looks Broken in Client

**Symptoms:**
- Layout broken in email client
- Styles not applied
- Images missing

**Solutions:**

1. **Use Email Preview:**
   ```
   Tools → Preview → Email Preview
   ```
   Test in different email client simulations.

2. **Export for email:**
   ```
   File → Export → Copy Email HTML to Clipboard
   ```
   This inlines all CSS for email compatibility.

3. **Validate email HTML:**
   ```
   Tools → Validate Email HTML
   ```
   Fix any warnings or errors.

4. **Follow email best practices:**
   - Width < 600px
   - Use tables for layout
   - Inline CSS (done automatically)
   - Absolute image URLs
   - Avoid: flexbox, grid, animations, custom fonts

5. **Test in actual email clients:**
   - Send test email to yourself
   - Check on desktop and mobile
   - Test in: Gmail, Outlook, Apple Mail

6. **Check image URLs:**
   ```html
   <!-- ❌ WRONG: Relative URL -->
   <img src="../images/photo.jpg">
   
   <!-- ✅ CORRECT: Absolute URL -->
   <img src="https://yoursite.com/images/photo.jpg">
   ```

---

## Image and Media Issues

### Images Not Displaying

**Symptoms:**
- Broken image icons
- Blank spaces where images should be
- Images work locally but not in email

**Solutions:**

1. **Use absolute URLs:**
   ```
   ✅ CORRECT: https://example.com/image.jpg
   ❌ WRONG:   file:///C:/path/to/image.jpg
   ❌ WRONG:   ../images/photo.jpg
   ```

2. **Host images online:**
   - Upload to image hosting service
   - Use church website server
   - Or embed as data URI (small images only)

3. **Check image format:**
   - Supported: JPG, PNG, GIF, WebP
   - Not supported in email: SVG, AVIF
   - Convert if needed

4. **Verify image accessible:**
   ```bash
   # Test URL in browser or with curl:
   curl -I https://example.com/image.jpg
   ```

5. **Add alt text:**
   ```html
   <img src="https://example.com/photo.jpg" alt="Church photo">
   ```
   Alt text shows if image fails to load.

6. **Check image size:**
   - Large images may not load in email
   - Recommended: < 100KB each
   - Optimize before importing

---

### Video Embeds Not Working

**Symptoms:**
- Video player not showing
- Embedded video doesn't play
- Video works in preview but not email

**Cause:** Most email clients don't support embedded video.

**Solutions:**

1. **Use video thumbnail + link:**
   ```html
   <a href="https://youtube.com/watch?v=VIDEO_ID">
     <img src="https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg" 
          alt="Watch video">
   </a>
   ```

2. **Add YouTube/Vimeo sections:**
   - Use built-in Video section type
   - Automatically creates thumbnail + link

3. **Link to video page:**
   ```
   Instead of embedding, add link:
   "Watch the video at: https://youtube.com/..."
   ```

4. **For web HTML only:**
   - Video embeds work in web browsers
   - Just not in email clients
   - Export separate HTML for web vs. email

---

### Large Images Cause Slowdown

**Symptoms:**
- Application slow when editing
- Preview takes long to load
- High memory usage

**Solutions:**

1. **Optimize images before importing:**
   ```bash
   # Resize to max 1200px wide
   # Compress to < 100KB
   
   # Use tools:
   # - TinyPNG.com (online)
   # - ImageOptim (macOS)
   # - RIOT (Windows)
   # - ImageMagick (command line):
   convert input.jpg -resize 1200x -quality 85 output.jpg
   ```

2. **Limit number of images:**
   - Recommended: < 10 images per bulletin
   - Use image galleries/collages for multiple photos

3. **Use appropriate formats:**
   - Photos: JPG (smaller file size)
   - Graphics: PNG (transparency, sharp lines)
   - Avoid: BMP, TIFF (large files)

4. **Enable lazy loading (future feature):**
   - Images load as needed
   - Reduces initial load time

---

## Performance Issues

### Application Slow or Unresponsive

**Symptoms:**
- Lag when typing
- Preview takes long to update
- UI freezes temporarily

**Solutions:**

1. **Reduce bulletin complexity:**
   - Limit sections to < 30
   - Simplify CSS (avoid complex selectors)
   - Reduce number of images

2. **Close unused drafts:**
   - File → Close Draft
   - Free up memory

3. **Restart application:**
   - Close and reopen to clear memory

4. **Check system resources:**
   ```bash
   # Windows
   Task Manager → Performance
   
   # macOS
   Activity Monitor → CPU / Memory
   
   # Linux
   htop or top
   ```

5. **Update to latest version:**
   - Newer versions have performance improvements

6. **Disable auto-save temporarily:**
   - Settings → Auto-save interval → Off
   - For large bulletins

---

### High Memory Usage

**Symptoms:**
- Application uses > 500MB RAM
- System becomes slow
- Out of memory errors

**Solutions:**

1. **Optimize images** (see [Large Images Cause Slowdown](#large-images-cause-slowdown))

2. **Close drafts when done:**
   - Don't keep multiple drafts open

3. **Restart periodically:**
   - Long sessions accumulate memory

4. **Increase system RAM:**
   - Minimum 4GB recommended
   - 8GB+ for large bulletins

5. **Check for memory leaks:**
   - Report to developers if memory grows continuously

---

### Preview Takes Too Long

**Symptoms:**
- Preview generation slow
- Preview doesn't update
- Preview window freezes

**Solutions:**

1. **Use Desktop preview instead of Email:**
   - Email preview is slower (CSS inlining)
   - Desktop preview is faster

2. **Disable live preview:**
   - Settings → Disable auto-preview
   - Manually refresh when needed

3. **Simplify styles:**
   - Reduce CSS complexity
   - Use built-in themes

4. **Optimize images:**
   - Smaller images = faster preview

---

## Build and Development Issues

### Permission Errors During Build

**Symptoms:**
- `PermissionError: [WinError 5] Access is denied`
- Can't delete build/ or dist/ folders
- Build fails with file in use errors

**Cause:** Application or Windows Explorer has files open.

**Solutions:**

1. **Close running instances:**
   ```powershell
   # Kill any running bulletin processes
   taskkill /F /IM bulletin.exe /T
   ```

2. **Close Windows Explorer windows:**
   - Close any explorer windows viewing build/dist folders

3. **Use force build script:**
   ```powershell
   .\scripts\force_build_windows.ps1
   ```
   Handles cleanup automatically.

4. **Disable OneDrive sync:**
   - OneDrive may lock files
   - Pause sync or move project outside OneDrive

5. **Run PowerShell as Administrator:**
   ```powershell
   # Right-click PowerShell → "Run as administrator"
   ```

6. **Manual cleanup:**
   ```powershell
   # Stop OneDrive
   taskkill /F /IM OneDrive.exe
   
   # Delete folders
   Remove-Item -Recurse -Force build, dist
   
   # Restart OneDrive
   Start-Process "$env:LOCALAPPDATA\Microsoft\OneDrive\OneDrive.exe"
   ```

---

### Module Import Errors

**Symptoms:**
- `ModuleNotFoundError: No module named 'bulletin_builder'`
- `ImportError: cannot import name 'X'`
- Module not found when running from source

**Solutions:**

1. **Install in editable mode:**
   ```bash
   pip install -e .
   ```

2. **Verify virtual environment:**
   ```bash
   # Check active environment
   which python  # macOS/Linux
   where python  # Windows
   
   # Should point to venv/bin/python or venv\Scripts\python.exe
   ```

3. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

4. **Check Python path:**
   ```python
   import sys
   print(sys.path)
   ```
   Project root should be in path.

5. **Add to PyInstaller hiddenimports:**
   ```python
   # In bulletin_builder.spec
   hiddenimports=[
       'missing_module_name',
       # ... other imports
   ]
   ```

---

### WeasyPrint Installation Problems

**Symptoms:**
- `ImportError: cannot import name 'weasyprint'`
- WeasyPrint build errors
- Missing system dependencies

**Solutions:**

1. **Install system dependencies first:**

   **Windows:**
   ```powershell
   # Download GTK3 runtime installer:
   # https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
   # Run installer
   ```

   **macOS:**
   ```bash
   brew install cairo pango gdk-pixbuf libffi
   ```

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
   ```

   **Fedora:**
   ```bash
   sudo dnf install python3-devel cairo pango gdk-pixbuf2
   ```

2. **Install WeasyPrint:**
   ```bash
   pip install --upgrade weasyprint
   ```

3. **Test installation:**
   ```python
   python -c "import weasyprint; print(weasyprint.__version__)"
   ```

4. **Use wheels (Windows):**
   ```bash
   pip install --upgrade --find-links=https://pypi.org/simple/ weasyprint
   ```

---

## Configuration Issues

### Settings Don't Persist

**Symptoms:**
- Settings reset after closing app
- Changes not saved to config.ini
- Window size/position forgotten

**Solutions:**

1. **Check config.ini permissions:**
   ```bash
   # Make sure file is writable
   ls -la config.ini
   
   # Fix permissions if needed
   chmod 644 config.ini
   ```

2. **Verify config.ini location:**
   ```bash
   # Should be in project root or executable directory
   # Not in read-only location
   ```

3. **Check disk space:**
   - Need space to write config file

4. **Run from writable location:**
   - Don't run from CD-ROM or network drive
   - Move to local drive (C:\, ~/Applications/)

5. **Manually edit config.ini:**
   ```ini
   # Open in text editor and verify changes save
   [window]
   geometry = 1200x800+100+100
   state = normal
   ```

---

### API Keys Not Working

**Symptoms:**
- "Invalid API key" errors
- AI features not working
- 401 Unauthorized errors

**Solutions:**

1. **Verify API key format:**
   ```ini
   # Remove extra quotes or spaces
   [google]
   api_key = YOUR_API_KEY_HERE
   
   # NOT:
   api_key = "YOUR_API_KEY_HERE"  # Remove quotes
   api_key =  YOUR_API_KEY_HERE   # Remove extra spaces
   ```

2. **Check API key validity:**
   - Test key with provider's API
   - Verify not expired or revoked
   - Check quota limits

3. **Verify API enabled:**
   - Google Cloud: Enable required APIs
   - OpenAI: Check account status

4. **Test with curl:**
   ```bash
   # Google AI
   curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_API_KEY"
   
   # OpenAI
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_API_KEY"
   ```

5. **Check permissions:**
   - API key must have correct scopes
   - Verify not restricted to specific IPs

---

### Window State Not Saved

**Symptoms:**
- Window size resets every launch
- Position not remembered
- Always opens maximized/normal

**Solutions:**

1. **Enable window state saving:**
   ```ini
   [window]
   geometry = 1200x800+100+100
   state = normal
   ```

2. **Check config.ini writable:**
   - See [Settings Don't Persist](#settings-dont-persist)

3. **Manually set window state:**
   ```ini
   [window]
   geometry = WIDTHxHEIGHT+X+Y
   state = normal  # or: zoomed, iconic
   ```

4. **Reset window state:**
   ```ini
   # Delete [window] section to reset to defaults
   # Then restart application
   ```

---

## Platform-Specific Issues

### Windows

#### Issue: "Windows protected your PC" dialog

**Solution:**
1. Click "More info"
2. Click "Run anyway"
3. Or: Add to Windows Defender exceptions

#### Issue: High DPI scaling issues

**Solution:**
1. Right-click bulletin.exe → Properties → Compatibility
2. Check "Override high DPI scaling behavior"
3. Select "System (Enhanced)"

#### Issue: OneDrive sync conflicts

**Solution:**
1. Pause OneDrive sync during editing
2. Or move project outside OneDrive folder
3. Or exclude `user_drafts/` from sync

#### Issue: Long path names

**Solution:**
```powershell
# Enable long paths in Windows 10/11
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
  -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

---

### macOS

#### Issue: "Cannot verify developer" / Code signing

**Solution:**
```bash
xattr -cr /Applications/BulletinBuilder.app
# Or: Right-click → Open (first time only)
```

#### Issue: Dark mode issues

**Solution:**
1. System Preferences → General → Appearance
2. Or use Light/Hybrid theme in app

#### Issue: Retina display scaling

**Solution:**
- Application handles this automatically
- If issues: System Preferences → Displays → Scaled

#### Issue: Permissions for file access

**Solution:**
1. System Preferences → Security & Privacy → Files and Folders
2. Grant BulletinBuilder access to Documents, Desktop, etc.

---

### Linux

#### Issue: AppImage won't run

**Solution:**
```bash
# Install FUSE
sudo apt install libfuse2  # Ubuntu/Debian
sudo dnf install fuse-libs  # Fedora

# Or extract and run directly
./BulletinBuilder.AppImage --appimage-extract
./squashfs-root/AppRun
```

#### Issue: Missing GTK3 themes

**Solution:**
```bash
# Install GTK3
sudo apt install libgtk-3-0  # Ubuntu/Debian
sudo dnf install gtk3        # Fedora
```

#### Issue: Font rendering issues

**Solution:**
```bash
# Install font packages
sudo apt install fonts-liberation fonts-dejavu  # Ubuntu/Debian
sudo dnf install liberation-fonts dejavu-fonts  # Fedora
```

#### Issue: Wayland vs X11

**Solution:**
```bash
# Force X11 if Wayland causes issues
export GDK_BACKEND=x11
./BulletinBuilder.AppImage
```

---

## Getting Additional Help

### Collect Debug Information

Before reporting issues, collect:

1. **Application version:**
   ```
   Help → About → Copy version info
   ```

2. **Error messages:**
   - Screenshot error dialogs
   - Copy full error text

3. **Console output:**
   ```bash
   # Run from terminal to see errors:
   # Windows
   dist\bulletin\bulletin.exe
   
   # macOS
   /Applications/BulletinBuilder.app/Contents/MacOS/bulletin
   
   # Linux
   ./BulletinBuilder.AppImage
   ```

4. **Log files:**
   ```
   logs/bulletin_builder.log  # If logging enabled
   ```

5. **Configuration:**
   ```bash
   # Share config.ini (REMOVE PASSWORDS/API KEYS first!)
   ```

6. **System information:**
   - OS version
   - Python version: `python --version`
   - Dependencies: `pip list`

---

### Report Issues

**GitHub Issues:** https://github.com/LogunLACC/bulletin_builder/issues

**Include in report:**
- Clear description of problem
- Steps to reproduce
- Expected vs. actual behavior
- Debug information (see above)
- Screenshots if applicable

**Template:**
```markdown
## Problem Description
[Describe what's wrong]

## Steps to Reproduce
1. Step one
2. Step two
3. ...

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## System Information
- OS: [Windows 11 / macOS 14 / Ubuntu 22.04]
- App Version: [1.0.0]
- Python Version: [3.11.0]

## Error Messages
```
[Paste error messages here]
```

## Additional Context
[Any other relevant information]
```

---

### Community Support

- **GitHub Discussions:** https://github.com/LogunLACC/bulletin_builder/discussions
- **Documentation:** [docs/](https://github.com/LogunLACC/bulletin_builder/tree/main/docs)
- **Stack Overflow:** Tag `bulletin-builder`

---

### Professional Support

For organizations needing dedicated support:

- Custom deployment assistance
- Training for staff
- Feature development
- SLA-based support

Contact: [Your contact information]

---

## Related Documentation

- **[USER_MANUAL.md](USER_MANUAL.md)** - Complete user guide
- **[CONFIG.md](CONFIG.md)** - Configuration reference
- **[DEVELOPER_SETUP.md](DEVELOPER_SETUP.md)** - Development environment setup
- **[BUILDING.md](BUILDING.md)** - Build and packaging guide
- **[DETAILED_DOCS.md](DETAILED_DOCS.md)** - Technical architecture

---

**Last Updated:** October 2025  
**Version:** 1.0.0
