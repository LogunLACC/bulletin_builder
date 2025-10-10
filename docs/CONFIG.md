# Configuration Reference

Complete reference for all configuration options in `config.ini`.

## Table of Contents

- [Overview](#overview)
- [Configuration File Locations](#configuration-file-locations)
- [Section Reference](#section-reference)
  - [API / google / openai](#api--google--openai)
  - [smtp](#smtp)
  - [events](#events)
  - [window](#window)
- [Configuration Examples](#configuration-examples)
- [Environment Variables](#environment-variables)
- [Validation and Troubleshooting](#validation-and-troubleshooting)

---

## Overview

Bulletin Builder uses an INI-format configuration file (`config.ini`) to store settings, API keys, SMTP credentials, and application preferences. The configuration is loaded at startup and can be modified through the Settings UI or by editing the file directly.

**File Format:** Standard INI format with `[sections]` and `key = value` pairs.

**Default Location:** Project root directory (`./config.ini`)

**Fallback:** If `config.ini` doesn't exist, copy `config.ini.default` to `config.ini` and customize.

---

## Configuration File Locations

Bulletin Builder searches for `config.ini` in the following locations (in order):

1. **Current working directory:** `./config.ini`
2. **Application directory:** Same directory as the executable
3. **User home directory:** `~/.bulletin_builder/config.ini` (future enhancement)

**Note:** Currently, only the first location is used. Create `config.ini` in the project root or executable directory.

---

## Section Reference

### `[API]` / `[google]` / `[openai]`

Configuration for external API services.

#### `[API]`

Legacy section for backward compatibility. Prefer using `[google]` or `[openai]` sections.

**Format:**
```ini
[API]
google_api_key = "YOUR_GOOGLE_API_KEY_HERE"
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `google_api_key` | string | `"REPLACE_ME_GOOGLE_API_KEY"` | Google AI/Cloud API key (deprecated, use `[google]` section instead) |

---

#### `[google]`

Google AI and Google Cloud API configuration.

**Format:**
```ini
[google]
api_key = "YOUR_GOOGLE_API_KEY_HERE"
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `api_key` | string | `"REPLACE_ME_GOOGLE_API_KEY"` | Google AI API key for AI-powered features (optional) |

**How to Obtain:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste into `config.ini`

**Usage:**
- Used for AI-powered content suggestions (if implemented)
- Optional: Application works without this key

---

#### `[openai]`

OpenAI API configuration for AI features.

**Format:**
```ini
[openai]
api_key = "YOUR_OPENAI_API_KEY_HERE"
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `api_key` | string | `"REPLACE_ME_OPENAI_API_KEY"` | OpenAI API key for ChatGPT/GPT-4 integration (optional) |

**How to Obtain:**
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Copy and paste into `config.ini`

**Usage:**
- Used for AI content generation features (if implemented)
- Optional: Application works without this key

**Security Warning:** Never commit API keys to version control. Add `config.ini` to `.gitignore`.

---

### `[smtp]`

SMTP configuration for sending test emails.

**Format:**
```ini
[smtp]
host = "smtp.gmail.com"
port = 587
username = "your.email@gmail.com"
password = "your_app_password"
from_addr = "Church Bulletin <your.email@gmail.com>"
use_tls = true
```

| Key | Type | Default | Description | Required |
|-----|------|---------|-------------|----------|
| `host` | string | `"smtp.example.com"` | SMTP server hostname | ✅ Yes |
| `port` | integer | `587` | SMTP server port (usually 587 for TLS, 465 for SSL) | ✅ Yes |
| `username` | string | `"your_username"` | SMTP authentication username (usually your email address) | ✅ Yes |
| `password` | string | `"your_password"` | SMTP authentication password or app-specific password | ✅ Yes |
| `from_addr` | string | `"Bulletin Builder <user@example.com>"` | From address with display name in format: `"Name <email>"` | ✅ Yes |
| `use_tls` | boolean | `true` | Use TLS encryption (recommended for port 587) | ❌ No |

**Common SMTP Providers:**

#### Gmail

```ini
[smtp]
host = smtp.gmail.com
port = 587
username = your.email@gmail.com
password = your_16_char_app_password
from_addr = "Your Name <your.email@gmail.com>"
use_tls = true
```

**Gmail Setup:**
1. Enable 2-Step Verification in Google Account settings
2. Go to Security → App passwords
3. Generate an app password for "Bulletin Builder"
4. Use the 16-character password in `config.ini`

**Gmail Resources:**
- [App passwords guide](https://support.google.com/accounts/answer/185833)
- [SMTP settings](https://support.google.com/mail/answer/7126229)

---

#### Outlook / Microsoft 365

```ini
[smtp]
host = smtp-mail.outlook.com
port = 587
username = your.email@outlook.com
password = your_account_password
from_addr = "Your Name <your.email@outlook.com>"
use_tls = true
```

**Outlook Setup:**
1. Use your Microsoft account password
2. Enable 2FA for better security
3. May need to allow "less secure apps" (not recommended) or use app password

**Outlook Resources:**
- [SMTP settings](https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-8361e398-8af4-4e97-b147-6c6c4ac95353)

---

#### Yahoo Mail

```ini
[smtp]
host = smtp.mail.yahoo.com
port = 587
username = your.email@yahoo.com
password = your_app_password
from_addr = "Your Name <your.email@yahoo.com>"
use_tls = true
```

**Yahoo Setup:**
1. Generate an app password in Account Security settings
2. Use app password instead of account password

**Yahoo Resources:**
- [App passwords guide](https://help.yahoo.com/kb/generate-manage-third-party-passwords-sln15241.html)

---

#### Office 365 / Exchange

```ini
[smtp]
host = smtp.office365.com
port = 587
username = your.email@yourcompany.com
password = your_password
from_addr = "Your Name <your.email@yourcompany.com>"
use_tls = true
```

---

#### Custom SMTP Server

```ini
[smtp]
host = mail.yourserver.com
port = 587
username = username
password = password
from_addr = "Display Name <email@yourserver.com>"
use_tls = true
```

Contact your email provider or IT administrator for:
- SMTP hostname
- Port number (587 for TLS, 465 for SSL, 25 for unencrypted)
- Authentication requirements
- TLS/SSL requirements

---

**Testing SMTP Configuration:**

After configuring SMTP settings:

1. Launch Bulletin Builder
2. **File → Send Test Email**
3. Enter your email address
4. Click "Send"
5. Check your inbox for the test email

If the test fails:
- Verify all settings are correct
- Check username/password
- Ensure firewall allows outbound SMTP connections
- For Gmail/Yahoo, ensure app password is used
- Check spam/junk folder

---

### `[events]`

Event feed configuration for importing events from remote sources.

**Format:**
```ini
[events]
feed_url = "https://raw.githubusercontent.com/LogunLACC/bulletin_builder/refs/heads/main/events.json"
auto_import = false
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `feed_url` | string | `""` | URL to JSON event feed (HTTP/HTTPS) |
| `auto_import` | boolean | `false` | Automatically import events from feed on app startup |

**Event Feed Format:**

The `feed_url` should point to a JSON file with the following structure:

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

**Usage:**

- **Manual Import:** Settings → Import Events → Import from URL
- **Auto Import:** Set `auto_import = true` to fetch events on every app launch
- **Local Files:** Can also import from local JSON/CSV files via GUI

**Security Note:** Only use trusted URLs. The feed is fetched over HTTPS when possible.

---

### `[window]`

Window state and behavior preferences.

**Format:**
```ini
[window]
geometry = 1200x800+100+100
state = zoomed
confirm_on_close = true
autosave_on_close = true
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `geometry` | string | `""` | Window size and position in format: `WIDTHxHEIGHT+X+Y` |
| `state` | string | `""` | Window state: `normal`, `zoomed` (maximized), `iconic` (minimized), or empty |
| `confirm_on_close` | boolean | `true` | Show confirmation dialog when closing the application |
| `autosave_on_close` | boolean | `true` | Automatically save draft when closing the application |

#### `geometry`

Standard Tk geometry string specifying window size and position.

**Format:** `WIDTHxHEIGHT+X_OFFSET+Y_OFFSET`

**Examples:**
- `1200x800+100+50` - 1200px wide, 800px tall, at position (100, 50)
- `1024x768+0+0` - 1024x768 at top-left corner
- `""` (empty) - Use default size and position

**Automatic Saving:** Window geometry is automatically saved when you close the application (if window state persistence is enabled).

---

#### `state`

Window display state.

**Valid Values:**
- `normal` - Regular windowed mode
- `zoomed` - Maximized/full-screen mode
- `iconic` - Minimized to taskbar (not recommended as default)
- `""` (empty) - Use default state (normal)

**Example:**
```ini
state = zoomed  # Start maximized
```

**Automatic Saving:** Window state is saved automatically on close.

---

#### `confirm_on_close`

Control whether the application shows a confirmation dialog when closing with unsaved changes.

**Type:** Boolean (`true` or `false`)

**Default:** `true`

**Behavior:**
- `true` - Show "Do you want to save before closing?" dialog
- `false` - Close immediately without confirmation (respects `autosave_on_close` setting)

**Example:**
```ini
confirm_on_close = true
```

**Recommended:** Keep `true` to prevent accidental data loss.

---

#### `autosave_on_close`

Automatically save the current draft when closing the application.

**Type:** Boolean (`true` or `false`)

**Default:** `true`

**Behavior:**
- `true` - Save draft to `user_drafts/AutoSave/` folder before closing
- `false` - Do not auto-save (you'll lose unsaved changes unless you save manually)

**Example:**
```ini
autosave_on_close = true
```

**AutoSave Location:** `user_drafts/AutoSave/autosave_YYYY-MM-DD_HH-MM-SS.json`

**Recommended:** Keep `true` as a safety net.

---

## Configuration Examples

### Minimal Configuration

For local use without email or API features:

```ini
[window]
geometry = 1024x768+0+0
state = normal
confirm_on_close = true
autosave_on_close = true
```

---

### Gmail with Auto-Import

For church bulletins with Gmail and event feed:

```ini
[google]
api_key = "YOUR_GOOGLE_API_KEY_HERE"

[smtp]
host = smtp.gmail.com
port = 587
username = church.bulletin@gmail.com
password = abcd efgh ijkl mnop
from_addr = "First Church Bulletin <church.bulletin@gmail.com>"
use_tls = true

[events]
feed_url = "https://yourchurch.org/events.json"
auto_import = true

[window]
geometry = 1400x900+100+50
state = zoomed
confirm_on_close = true
autosave_on_close = true
```

---

### Microsoft 365 with OpenAI

For organizations using Office 365 and AI features:

```ini
[openai]
api_key = "sk-proj-XXXXXXXXXXXXXXXXXXXX"

[smtp]
host = smtp.office365.com
port = 587
username = bulletin@yourcompany.com
password = YourPassword123
from_addr = "Company Newsletter <bulletin@yourcompany.com>"
use_tls = true

[events]
feed_url = ""
auto_import = false

[window]
geometry = 1600x1000+200+100
state = normal
confirm_on_close = true
autosave_on_close = true
```

---

### Production Configuration Template

Complete template with all sections:

```ini
# Google AI API Key (optional)
[google]
api_key = "REPLACE_WITH_YOUR_GOOGLE_API_KEY"

# OpenAI API Key (optional)
[openai]
api_key = "REPLACE_WITH_YOUR_OPENAI_API_KEY"

# SMTP Configuration for Email Sending
[smtp]
host = "smtp.gmail.com"
port = 587
username = "your.email@gmail.com"
password = "your_app_password"
from_addr = "Bulletin Builder <your.email@gmail.com>"
use_tls = true

# Event Feed Configuration
[events]
feed_url = "https://example.com/events.json"
auto_import = false

# Window State and Preferences
[window]
geometry = 1200x800+100+100
state = normal
confirm_on_close = true
autosave_on_close = true
```

---

## Environment Variables

**Future Enhancement:** Environment variable support is planned for CI/CD and container deployments.

Proposed environment variables (not yet implemented):

```bash
# API Keys
export BULLETIN_GOOGLE_API_KEY="your_key_here"
export BULLETIN_OPENAI_API_KEY="your_key_here"

# SMTP Configuration
export BULLETIN_SMTP_HOST="smtp.gmail.com"
export BULLETIN_SMTP_PORT="587"
export BULLETIN_SMTP_USERNAME="user@example.com"
export BULLETIN_SMTP_PASSWORD="password"
export BULLETIN_SMTP_FROM="Bulletin <user@example.com>"
export BULLETIN_SMTP_USE_TLS="true"

# Events
export BULLETIN_EVENTS_FEED_URL="https://example.com/events.json"
export BULLETIN_EVENTS_AUTO_IMPORT="false"
```

**Priority:** Environment variables would override `config.ini` values.

---

## Validation and Troubleshooting

### Configuration Validation

Bulletin Builder performs basic validation on startup:

1. **File Existence:** Checks if `config.ini` exists
2. **Section Validation:** Warns if required sections are missing
3. **Type Validation:** Validates boolean and integer values
4. **SMTP Validation:** Can test SMTP connection via GUI

**Validation Errors:**

If configuration is invalid, the application:
- Logs warnings to console and log file
- Uses default values for invalid settings
- Shows error dialog for critical issues (e.g., invalid SMTP config when sending email)

---

### Common Issues

#### Issue: Application doesn't load config.ini

**Symptoms:**
- Settings are always default
- Changes don't persist

**Solutions:**
1. Verify `config.ini` exists in the correct location
2. Check file permissions (must be readable/writable)
3. Ensure file is valid INI format (no syntax errors)
4. Check application logs for errors

---

#### Issue: SMTP authentication fails

**Symptoms:**
- "SMTP authentication failed" error when sending test email
- "Connection refused" or timeout errors

**Solutions:**
1. Verify username/password are correct
2. For Gmail/Yahoo: Use app-specific password, not account password
3. Check `use_tls` setting (should be `true` for port 587)
4. Ensure firewall allows outbound connections on port 587/465
5. Test SMTP settings manually:
   ```bash
   telnet smtp.gmail.com 587
   ```
6. Check if 2FA is enabled (requires app password)

---

#### Issue: API keys not working

**Symptoms:**
- "Invalid API key" errors
- AI features not working

**Solutions:**
1. Verify API key is correct (no extra quotes or spaces)
2. Remove surrounding quotes in config.ini:
   ```ini
   # Wrong
   api_key = "YOUR_KEY_HERE"
   
   # Correct
   api_key = YOUR_KEY_HERE
   ```
3. Check API key hasn't expired or been revoked
4. Verify API key has correct permissions/scopes
5. Test API key with provider's test endpoint

---

#### Issue: Window state not persisting

**Symptoms:**
- Window size/position resets every launch
- Settings don't save

**Solutions:**
1. Check `config.ini` is writable
2. Verify no file permission errors in logs
3. Ensure `[window]` section exists
4. Check if running from read-only location (e.g., CD-ROM)

---

#### Issue: Events auto-import not working

**Symptoms:**
- Events don't load on startup despite `auto_import = true`
- Empty event list

**Solutions:**
1. Verify `feed_url` is correct and accessible
2. Check internet connection
3. Test URL in web browser
4. Verify JSON format is valid
5. Check application logs for fetch errors
6. Try manual import: Settings → Import Events → Import from URL

---

### Manual Configuration Reset

To reset configuration to defaults:

1. **Backup current config:**
   ```bash
   cp config.ini config.ini.backup
   ```

2. **Restore default config:**
   ```bash
   cp config.ini.default config.ini
   ```

3. **Edit and customize:**
   Open `config.ini` in text editor and update values

---

### Configuration Best Practices

✅ **Do:**
- Keep `config.ini` in version control with placeholder values
- Use `config.ini.default` as a template
- Document custom settings in comments
- Use app-specific passwords for email services
- Enable 2FA on email accounts
- Test SMTP configuration before production use
- Back up working configuration

❌ **Don't:**
- Commit real API keys or passwords to version control
- Share `config.ini` with credentials publicly
- Use plain account passwords (use app passwords)
- Disable `confirm_on_close` unless you have reliable auto-save
- Store sensitive credentials in plain text (consider using environment variables when supported)

---

### Getting Help

If you encounter configuration issues:

1. **Check logs:**
   - Console output (if running from terminal)
   - `logs/bulletin_builder.log` (if logging is enabled)

2. **Validate config syntax:**
   - Use an INI validator or Python's `configparser`:
     ```python
     import configparser
     config = configparser.ConfigParser()
     config.read('config.ini')
     print(config.sections())
     ```

3. **Test individual components:**
   - SMTP: Use GUI "Test Connection" button
   - Events: Try manual import first
   - Window state: Delete `[window]` section and restart

4. **Consult documentation:**
   - [USER_MANUAL.md](USER_MANUAL.md) - End-user guide
   - [DEVELOPER_SETUP.md](DEVELOPER_SETUP.md) - Development environment setup
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Troubleshooting guide

5. **Report issues:**
   - GitHub Issues: https://github.com/LogunLACC/bulletin_builder/issues
   - Include config.ini (with credentials removed)
   - Include error messages and logs

---

## Related Documentation

- **[USER_MANUAL.md](USER_MANUAL.md)** - Complete user guide with settings UI walkthrough
- **[DEVELOPER_SETUP.md](DEVELOPER_SETUP.md)** - Development environment configuration
- **[DETAILED_DOCS.md](DETAILED_DOCS.md)** - Technical architecture and configuration management
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

---

**Last Updated:** October 2025  
**Version:** 1.0.0
