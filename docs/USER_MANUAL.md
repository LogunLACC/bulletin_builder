# Bulletin Builder - User Manual

Complete guide for creating professional email bulletins with Bulletin Builder.

## Table of Contents

- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [First Launch](#first-launch)
  - [Understanding the Interface](#understanding-the-interface)
- [Creating Your First Bulletin](#creating-your-first-bulletin)
  - [Setting Up Basic Information](#setting-up-basic-information)
  - [Choosing a Theme](#choosing-a-theme)
  - [Selecting a Template](#selecting-a-template)
- [Working with Sections](#working-with-sections)
  - [Adding Sections](#adding-sections)
  - [Editing Section Content](#editing-section-content)
  - [Reordering Sections](#reordering-sections)
  - [Deleting Sections](#deleting-sections)
- [Importing Events](#importing-events)
  - [Importing from CSV](#importing-from-csv)
  - [Importing from JSON](#importing-from-json)
  - [Manual Event Entry](#manual-event-entry)
- [Using the WYSIWYG Editor](#using-the-wysiwyg-editor)
  - [Text Formatting](#text-formatting)
  - [Adding Images](#adding-images)
  - [Creating Lists](#creating-lists)
  - [Adding Links](#adding-links)
  - [Tables](#tables)
- [Preview Modes](#preview-modes)
  - [Desktop Preview](#desktop-preview)
  - [Mobile Preview](#mobile-preview)
  - [Email Preview](#email-preview)
- [Saving and Loading Drafts](#saving-and-loading-drafts)
  - [Saving Your Work](#saving-your-work)
  - [Loading Existing Drafts](#loading-existing-drafts)
  - [Auto-Save Feature](#auto-save-feature)
- [Exporting Bulletins](#exporting-bulletins)
  - [Export to HTML](#export-to-html)
  - [Export to PDF](#export-to-pdf)
  - [Export for Email](#export-for-email)
  - [Sending Test Emails](#sending-test-emails)
- [Settings and Configuration](#settings-and-configuration)
  - [General Settings](#general-settings)
  - [SMTP Configuration](#smtp-configuration)
  - [API Keys](#api-keys)
- [Tips and Best Practices](#tips-and-best-practices)
- [Troubleshooting](#troubleshooting)
- [Keyboard Shortcuts](#keyboard-shortcuts)

---

## Getting Started

### Installation

#### Windows

1. Download `BulletinBuilder-Setup.exe` from the [Releases page](https://github.com/LogunLACC/bulletin_builder/releases)
2. Run the installer
3. Follow the installation wizard
4. Launch from Start Menu → "Bulletin Builder"

#### macOS

1. Download `BulletinBuilder.dmg` from the [Releases page](https://github.com/LogunLACC/bulletin_builder/releases)
2. Open the DMG file
3. Drag "Bulletin Builder.app" to your Applications folder
4. Launch from Applications

**Note:** On first launch, you may see a Gatekeeper warning. Right-click the app and select "Open" to bypass.

#### Linux

1. Download `BulletinBuilder.AppImage` from the [Releases page](https://github.com/LogunLACC/bulletin_builder/releases)
2. Make it executable:
   ```bash
   chmod +x BulletinBuilder.AppImage
   ```
3. Run it:
   ```bash
   ./BulletinBuilder.AppImage
   ```

### First Launch

When you first launch Bulletin Builder:

1. **Configuration Setup:** If `config.ini` doesn't exist, it will be created from `config.ini.default`
2. **Welcome Screen:** You'll see the main interface with an empty bulletin
3. **Tutorial Tooltips:** Hover over buttons and fields to see helpful tooltips

### Understanding the Interface

The Bulletin Builder interface has three main areas:

```
┌─────────────────────────────────────────────────────────────┐
│  Menu Bar: File | Edit | View | Help                        │
├─────────────┬───────────────────────────────┬───────────────┤
│             │                               │               │
│  Left       │     Center Editor             │  Right Panel  │
│  Sidebar    │     (WYSIWYG)                 │  (Settings,   │
│             │                               │   Preview)    │
│  • Sections │                               │               │
│  • Add      │                               │               │
│  • Remove   │                               │               │
│  • Reorder  │                               │               │
│             │                               │               │
├─────────────┴───────────────────────────────┴───────────────┤
│  Status Bar: Ready | Autosave: ON | Last saved: 2 mins ago  │
└─────────────────────────────────────────────────────────────┘
```

**Key Components:**

- **Menu Bar:** Access all features (File, Edit, View, Help)
- **Left Sidebar:** Section list with add/remove/reorder controls
- **Center Editor:** WYSIWYG editor for section content
- **Right Panel:** Settings, preview, and properties
- **Status Bar:** Application status and autosave indicator

---

## Creating Your First Bulletin

### Setting Up Basic Information

1. **Click the "Settings" tab** in the right panel
2. **Enter bulletin title:**
   - Example: "Weekly Church Bulletin"
   - This appears as the main heading in your bulletin
3. **Set the bulletin date:**
   - Click the date field
   - Select date from calendar picker
   - Format: October 12, 2025
4. **Add optional subtitle** (if template supports it)

### Choosing a Theme

Bulletin Builder offers three themes:

1. **Light Theme** - Clean, bright design with dark text on white background
2. **Dark Theme** - Modern design with light text on dark background
3. **Hybrid Theme** - Balanced design with customizable accent colors

**To change theme:**
1. Settings tab → Theme dropdown
2. Select your preferred theme
3. Preview updates automatically

### Selecting a Template

Templates control the overall layout and styling:

1. **Settings tab → "Template Gallery" button**
2. **Browse available templates:**
   - Default - Clean, professional layout
   - Modern - Contemporary design with bold headers
   - Traditional - Classic church bulletin style
   - Minimalist - Simple, clean design
3. **Click on a template to preview**
4. **Click "Apply" to use the template**

**Custom Templates:**
- Place your own templates in the `templates/` folder
- They'll appear in the gallery automatically
- Use Jinja2 syntax for dynamic content

---

## Working with Sections

Sections are the building blocks of your bulletin. Each section has a type, title, and content.

### Adding Sections

1. **Click "+ Add Section"** in the left sidebar
2. **Choose section type:**
   - **Text Section** - For announcements, messages, devotionals
   - **Event Section** - For scheduled events with date/time/location
   - **Image Section** - For photos, graphics, flyers
   - **Table Section** - For structured data (schedules, rosters)
   - **Video Section** - For embedded video links (YouTube, Vimeo)
3. **Section appears in the sidebar** and is ready to edit

**Section Types Explained:**

| Type | Use Case | Example |
|------|----------|---------|
| Text | General content | "Pastor's Message", "Announcements" |
| Event | Calendar items | "Sunday Service - 10am", "Bible Study" |
| Image | Visual content | Photos, flyers, graphics |
| Table | Structured data | Volunteer schedule, attendance records |
| Video | Embedded videos | Sermon recordings, testimonials |

### Editing Section Content

1. **Click on a section** in the left sidebar to select it
2. **The center editor displays** the section content
3. **Edit the section title** at the top of the editor
4. **Use the WYSIWYG toolbar** to format content (see [Using the WYSIWYG Editor](#using-the-wysiwyg-editor))
5. **Changes auto-save** every few seconds (watch status bar)

**Quick Tips:**
- Use Ctrl+Z to undo changes
- Use Ctrl+Y to redo changes
- Right-click for context menu with more options

### Reordering Sections

Change the order sections appear in your bulletin:

**Method 1: Drag and Drop**
1. Click and hold a section in the sidebar
2. Drag to desired position
3. Release to drop

**Method 2: Arrow Buttons**
1. Select a section
2. Click ↑ (Move Up) or ↓ (Move Down) buttons
3. Section moves one position

**Method 3: Context Menu**
1. Right-click a section
2. Select "Move to Top" or "Move to Bottom"

### Deleting Sections

1. **Select the section** in the left sidebar
2. **Click the "Delete" button** (trash icon) or press Delete key
3. **Confirm deletion** in the dialog that appears

**Note:** Deleted sections cannot be recovered unless you have a saved draft backup.

---

## Importing Events

Import events from external sources to quickly populate your bulletin.

### Importing from CSV

**CSV Format:**
```csv
title,date,time,location,description
"Sunday Service","2025-10-12","10:00 AM","Main Sanctuary","Weekly worship service with communion"
"Bible Study","2025-10-14","7:00 PM","Fellowship Hall","Studying the book of Romans"
"Youth Group","2025-10-15","6:00 PM","Youth Room","Pizza and games night"
```

**Steps:**
1. **Prepare your CSV file** with the columns above
2. **File → Import → Import Events from CSV**
3. **Select your CSV file** in the file dialog
4. **Events are automatically added** as Event sections
5. **Review and edit** events as needed

**Tips:**
- Use quotes around text with commas
- Date format: YYYY-MM-DD
- Time format: 12-hour with AM/PM

### Importing from JSON

**JSON Format:**
```json
{
  "events": [
    {
      "title": "Sunday Service",
      "date": "2025-10-12",
      "time": "10:00 AM",
      "location": "Main Sanctuary",
      "description": "Weekly worship service with communion"
    },
    {
      "title": "Bible Study",
      "date": "2025-10-14",
      "time": "7:00 PM",
      "location": "Fellowship Hall",
      "description": "Studying the book of Romans"
    }
  ]
}
```

**Steps:**
1. **Create JSON file** with format above
2. **File → Import → Import Events from JSON**
3. **Select your JSON file**
4. **Events appear as sections**

### Manual Event Entry

For individual events:

1. **Add an Event Section** (see [Adding Sections](#adding-sections))
2. **Fill in event details:**
   - Title: Event name
   - Date: Click calendar picker
   - Time: Enter time (e.g., "10:00 AM")
   - Location: Where the event takes place
   - Description: Additional details
3. **Save** (auto-saved)

---

## Using the WYSIWYG Editor

The What-You-See-Is-What-You-Get editor lets you format content visually.

### Text Formatting

**Toolbar Buttons:**

| Button | Function | Keyboard Shortcut |
|--------|----------|-------------------|
| **B** | Bold | Ctrl+B |
| *I* | Italic | Ctrl+I |
| <u>U</u> | Underline | Ctrl+U |
| H1 | Heading 1 | Ctrl+Alt+1 |
| H2 | Heading 2 | Ctrl+Alt+2 |
| H3 | Heading 3 | Ctrl+Alt+3 |
| Font | Font family dropdown | - |
| Size | Font size dropdown | - |
| Color | Text color picker | - |

**Using Headings:**
- **H1 (Heading 1)** - Major section titles
- **H2 (Heading 2)** - Subsection titles
- **H3 (Heading 3)** - Minor headings
- **Paragraph** - Body text

### Adding Images

1. **Click the "Image" button** in the toolbar (📷 icon)
2. **Choose image source:**
   - **Upload File** - Select from your computer
   - **URL** - Enter image web address
3. **Set image properties:**
   - Width: Pixels or percentage (e.g., "600px" or "100%")
   - Alt Text: Description for accessibility (required for email)
   - Caption: Optional caption displayed below image
4. **Click "Insert"**

**Image Best Practices:**
- Use images ≤ 600px wide for email compatibility
- Always add alt text for accessibility
- Use JPG for photos, PNG for graphics with transparency
- Compress images before uploading (< 100KB recommended)

### Creating Lists

**Bullet List:**
1. Click "Bullet List" button (• icon)
2. Type list items, press Enter for new item
3. Press Enter twice to exit list

**Numbered List:**
1. Click "Numbered List" button (1. icon)
2. Type list items, press Enter for new item
3. Press Enter twice to exit list

**Nested Lists:**
1. Create a list
2. Press Tab to indent (create sub-list)
3. Press Shift+Tab to outdent

**Example:**
```
• Announcements
  • Church potluck this Saturday
  • VBS registration open
• Prayer Requests
  • John's surgery
  • Mission trip team
```

### Adding Links

1. **Select text** to make into a link
2. **Click "Link" button** (🔗 icon)
3. **Enter URL** (e.g., "https://example.com")
4. **Choose link behavior:**
   - Open in new tab (recommended for external links)
   - Open in same tab
5. **Click "Insert"**

**Link Tips:**
- Use descriptive link text (not "click here")
- Always use https:// for security
- Test links before exporting

### Tables

1. **Click "Table" button** in toolbar
2. **Select table size** (rows × columns)
3. **Click to insert table**
4. **Fill in cells** by clicking and typing
5. **Right-click for table options:**
   - Add row above/below
   - Add column left/right
   - Delete row/column
   - Merge cells
   - Table properties (borders, spacing)

**Table Example:**

| Time | Event | Location |
|------|-------|----------|
| 9:30 AM | Sunday School | Classrooms |
| 10:30 AM | Worship Service | Sanctuary |
| 6:00 PM | Evening Service | Sanctuary |

---

## Preview Modes

### Desktop Preview

View how your bulletin looks on desktop browsers:

1. **Click "Preview" tab** in right panel
2. **Select "Desktop" view**
3. **Scroll to review content**
4. **Click "Refresh"** to update after edits

**Desktop preview shows:**
- Full-width layout
- All images and formatting
- Desktop-optimized fonts and spacing

### Mobile Preview

See how your bulletin appears on phones and tablets:

1. **Click "Preview" tab**
2. **Select "Mobile" view**
3. **Preview shows max 600px width**

**Mobile preview features:**
- Responsive layout
- Optimized for small screens
- Stacked sections
- Touch-friendly buttons

**Note:** Always check mobile preview! Many people read emails on phones.

### Email Preview

See email client compatibility:

1. **Click "Preview" tab**
2. **Select "Email" view**
3. **Preview shows email-optimized HTML:**
   - Inlined CSS
   - Email-safe fonts
   - Simplified layout
   - Compatibility warnings (if any)

**Email preview checks:**
- ✅ CSS properly inlined
- ✅ No unsupported properties
- ✅ Images have alt text
- ✅ Links are absolute URLs
- ⚠️ Warnings for potential issues

---

## Saving and Loading Drafts

### Saving Your Work

**Manual Save:**
1. **File → Save Draft** (or press Ctrl+S)
2. **Choose location** (defaults to `user_drafts/`)
3. **Enter filename** (e.g., "2025-10-12_bulletin.json")
4. **Click "Save"**

**Save As:**
1. **File → Save Draft As** (or press Ctrl+Shift+S)
2. **Enter new filename**
3. **Choose location**
4. **Click "Save"**

**Draft File Format:**
- JSON format (human-readable)
- Contains all bulletin data: sections, settings, metadata
- Can be edited in text editor if needed

### Loading Existing Drafts

1. **File → Open Draft** (or press Ctrl+O)
2. **Navigate to draft location** (`user_drafts/` by default)
3. **Select JSON file**
4. **Click "Open"**
5. **Bulletin loads** with all sections and settings

**Recent Drafts:**
- File → Recent → Select from list
- Quick access to last 10 drafts

### Auto-Save Feature

Bulletin Builder automatically saves your work:

**Auto-Save Settings:**
- **Interval:** Every 5 minutes (configurable in Settings)
- **Location:** `user_drafts/AutoSave/`
- **Filename:** Includes timestamp (e.g., `MyBulletin_2025-10-12_14-30-00.json`)

**Status Indicator:**
- **Status bar** shows last auto-save time
- **Green icon** = Successfully saved
- **Yellow icon** = Save in progress
- **Red icon** = Save failed

**Auto-Save on Close:**
- Enabled by default
- Saves draft before closing app
- **Settings → Auto-save on close** to toggle

---

## Exporting Bulletins

### Export to HTML

Create a web-ready HTML file:

1. **File → Export → Export to HTML**
2. **Choose export type:**
   - **Standard HTML** - For web viewing
   - **Email-Ready HTML** - Optimized for email clients
3. **Select output location**
4. **Enter filename** (e.g., "bulletin.html")
5. **Click "Save"**

**What's Included:**
- Complete HTML document
- All styling (CSS)
- Embedded images (optional)
- Responsive layout

**Use Cases:**
- Post on church website
- Share via link
- Archive bulletins

### Export to PDF

Create a print-ready PDF:

1. **File → Export → Export to PDF**
2. **Select output location**
3. **Enter filename** (e.g., "bulletin.pdf")
4. **Click "Save"**
5. **PDF generation** takes a few seconds

**PDF Features:**
- Print-optimized layout
- High-quality fonts
- Embedded images
- Paginated for printing

**Use Cases:**
- Print physical copies
- Distribute via email attachment
- Archive for records

### Export for Email

Prepare HTML optimized for email clients:

1. **File → Export → Copy Email HTML to Clipboard**
2. **HTML is copied** (ready to paste)
3. **Open your email client** (Gmail, Outlook, etc.)
4. **Create new email**
5. **Paste** (Ctrl+V)
6. **Send email!**

**Email Export Features:**
- All CSS inlined
- Email-safe styling
- Table-based layout
- Absolute image URLs
- Tested with major email clients

**Supported Email Clients:**
- ✅ Gmail (web, mobile)
- ✅ Outlook (Windows, Mac, web)
- ✅ Apple Mail
- ✅ Thunderbird
- ✅ Yahoo Mail
- ✅ Most mobile email apps

### Sending Test Emails

Send a test email to yourself:

1. **Configure SMTP** first (see [SMTP Configuration](#smtp-configuration))
2. **File → Send Test Email**
3. **Enter recipient email address**
4. **Click "Send"**
5. **Check your inbox!**

**Test Email Tips:**
- Always send a test before mass distribution
- Check on both desktop and mobile
- Forward to different email clients to test compatibility
- Ask volunteers to review before sending to congregation

---

## Settings and Configuration

### General Settings

**Settings Tab → General:**

- **Bulletin Title:** Main heading (e.g., "Weekly Bulletin")
- **Bulletin Date:** Date for this bulletin
- **Theme:** Light, Dark, or Hybrid
- **Font Family:** Default font for text
- **Font Size:** Base font size (12pt, 14pt, etc.)
- **Color Scheme:** Primary color for headers and accents

**Application Settings:**
- **Confirm on Close:** Show confirmation dialog when closing
- **Auto-save on Close:** Save draft before closing
- **Auto-save Interval:** How often to auto-save (minutes)
- **Show Tooltips:** Display helpful tooltips on hover

### SMTP Configuration

To send test emails, configure SMTP:

1. **Settings → SMTP Configuration**
2. **Enter details:**
   - **Host:** SMTP server (e.g., `smtp.gmail.com`)
   - **Port:** Usually 587 (TLS) or 465 (SSL)
   - **Username:** Your email address
   - **Password:** Email password or app-specific password
   - **From Address:** Display name and email (e.g., "Church Bulletin <bulletin@church.org>")
   - **Use TLS:** Check for encrypted connection
3. **Click "Test Connection"** to verify
4. **Save settings**

**Common SMTP Servers:**

| Provider | Host | Port | Notes |
|----------|------|------|-------|
| Gmail | smtp.gmail.com | 587 | Requires app password |
| Outlook | smtp-mail.outlook.com | 587 | Use Microsoft account |
| Yahoo | smtp.mail.yahoo.com | 587 | Requires app password |
| Custom | ask@provider.com | varies | Contact your email provider |

**Gmail App Password:**
1. Google Account → Security → 2-Step Verification → App passwords
2. Create app password for "Bulletin Builder"
3. Use generated password in SMTP settings

### API Keys

For AI features (optional):

1. **Settings → API Keys**
2. **Google AI Key:**
   - Get key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Paste into field
   - Used for AI-assisted content suggestions
3. **Save settings**

---

## Tips and Best Practices

### Writing Effective Bulletins

✅ **DO:**
- Keep titles short and descriptive
- Use bullet points for easy scanning
- Include essential info: who, what, when, where
- Add contact info for event organizers
- Proofread before exporting
- Use high-quality images

❌ **DON'T:**
- Use tiny fonts (minimum 12pt for body text)
- Overuse bold/italic/underline
- Use too many fonts (2-3 max)
- Include broken links
- Forget to add image alt text
- Use all caps for entire paragraphs

### Email Compatibility

For maximum email compatibility:

1. **Keep width under 600px**
2. **Use web-safe fonts:**
   - Arial, Helvetica, Times New Roman, Georgia
   - System fonts work best
3. **Avoid advanced CSS:**
   - No flexbox or grid
   - No transforms or animations
   - Use tables for layout
4. **Test images:**
   - Use absolute URLs (https://)
   - Add alt text
   - Test that images load
5. **Use inline styles:**
   - Bulletin Builder does this automatically
   - Don't use external CSS files

### Performance Tips

- **Optimize images** before importing (< 100KB each)
- **Limit sections** to 20-30 for best performance
- **Close unused drafts** to free memory
- **Regularly export and archive** old bulletins
- **Clear auto-save folder** periodically

### Accessibility

Make bulletins accessible to all:

- **Use semantic headings** (H1, H2, H3 in order)
- **Add alt text** to all images
- **Use sufficient color contrast** (test with tools)
- **Make links descriptive** ("Registration Form" not "Click Here")
- **Use clear, readable fonts** (14pt minimum)
- **Test with screen readers** if possible

---

## Troubleshooting

### Common Issues

**Issue: App won't launch**
- **Windows:** Right-click → "Run as Administrator"
- **macOS:** Right-click → "Open" (bypass Gatekeeper)
- **Linux:** Make sure file is executable: `chmod +x BulletinBuilder.AppImage`

**Issue: Can't save drafts**
- Check file permissions on `user_drafts/` folder
- Make sure disk isn't full
- Try "Save As" with different location

**Issue: Images not displaying**
- Use absolute URLs (https:// not relative paths)
- Check image file exists and is accessible
- Try re-importing image
- Verify image format (JPG, PNG, GIF supported)

**Issue: Email looks broken**
- Use "Email Preview" to check compatibility
- Run "Validate Email HTML" (Tools menu)
- Review warnings and fix issues
- Test in actual email client

**Issue: PDF export fails**
- Make sure WeasyPrint dependencies are installed
- Check console for error messages
- Try simplifying bulletin (remove complex CSS)
- Update to latest version

**Issue: SMTP error when sending test email**
- Verify SMTP settings are correct
- Check username/password
- Use app-specific password for Gmail
- Test connection in Settings
- Check firewall/antivirus settings

### Getting Help

- **Documentation:** [docs/](https://github.com/LogunLACC/bulletin_builder/tree/main/docs)
- **GitHub Issues:** [Report bugs or request features](https://github.com/LogunLACC/bulletin_builder/issues)
- **Discussions:** [Ask questions](https://github.com/LogunLACC/bulletin_builder/discussions)

---

## Keyboard Shortcuts

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| **File Operations** |
| New Draft | Ctrl+N | Cmd+N |
| Open Draft | Ctrl+O | Cmd+O |
| Save Draft | Ctrl+S | Cmd+S |
| Save Draft As | Ctrl+Shift+S | Cmd+Shift+S |
| **Editing** |
| Undo | Ctrl+Z | Cmd+Z |
| Redo | Ctrl+Y | Cmd+Y |
| Cut | Ctrl+X | Cmd+X |
| Copy | Ctrl+C | Cmd+C |
| Paste | Ctrl+V | Cmd+V |
| Select All | Ctrl+A | Cmd+A |
| **Formatting** |
| Bold | Ctrl+B | Cmd+B |
| Italic | Ctrl+I | Cmd+I |
| Underline | Ctrl+U | Cmd+U |
| Heading 1 | Ctrl+Alt+1 | Cmd+Opt+1 |
| Heading 2 | Ctrl+Alt+2 | Cmd+Opt+2 |
| Heading 3 | Ctrl+Alt+3 | Cmd+Opt+3 |
| **View** |
| Toggle Preview | F5 | F5 |
| Zoom In | Ctrl++ | Cmd++ |
| Zoom Out | Ctrl+- | Cmd+- |
| Reset Zoom | Ctrl+0 | Cmd+0 |
| **Application** |
| Settings | Ctrl+, | Cmd+, |
| Help | F1 | F1 |
| Quit | Ctrl+Q | Cmd+Q |

---

## Appendix: File Locations

### Windows

- **Config:** `C:\Users\[YourName]\AppData\Roaming\bulletin_builder\config.ini`
- **Drafts:** `C:\Users\[YourName]\Documents\bulletin_builder\user_drafts\`
- **Auto-Save:** `user_drafts\AutoSave\`
- **Templates:** `%PROGRAMFILES%\Bulletin Builder\templates\`

### macOS

- **Config:** `~/Library/Application Support/bulletin_builder/config.ini`
- **Drafts:** `~/Documents/bulletin_builder/user_drafts/`
- **Auto-Save:** `user_drafts/AutoSave/`
- **Templates:** `/Applications/Bulletin Builder.app/Contents/Resources/templates/`

### Linux

- **Config:** `~/.config/bulletin_builder/config.ini`
- **Drafts:** `~/Documents/bulletin_builder/user_drafts/`
- **Auto-Save:** `user_drafts/AutoSave/`
- **Templates:** `~/.local/share/bulletin_builder/templates/`

---

**Need more help?** Visit our [GitHub repository](https://github.com/LogunLACC/bulletin_builder) or contact support.

**Version:** 2.0.0  
**Last Updated:** October 10, 2025
