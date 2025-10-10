# Automatic Draft Backup System

## Overview
The automatic draft backup system provides crash recovery and data protection for the Bulletin Builder application. It automatically saves drafts periodically and can recover work after unexpected crashes or exits.

## Features

### 1. Periodic Auto-Save
- **Interval**: 2 minutes (120,000 ms) by default
- **Location**: `./backups` directory
- **Format**: JSON files named `auto_backup_YYYYMMDD_HHMMSS.json`
- **Smart Saving**: Skips backup if no content exists

### 2. Crash Detection
- Creates a `.crash_detected` marker file on startup
- Removes marker on graceful exit
- If marker exists on next launch, crash is detected
- Automatically prompts user for recovery

### 3. Backup Rotation
- Keeps last 10 backups by default (configurable)
- Automatically removes older backups
- Uses modification time for sorting

### 4. Recovery Dialog
- Appears automatically if crash detected
- Shows timestamp of last backup
- Shows original file name if available
- User can choose to restore or skip

## Implementation Details

### Core Components

#### AutoBackupManager Class
Located in `src/bulletin_builder/app_core/auto_backup.py`

**Key Methods**:
- `start()` - Initializes crash detection and schedules first backup
- `stop()` - Cancels scheduled backups and cleanup
- `_perform_auto_save()` - Creates backup file
- `_collect_draft_data()` - Gathers current draft state
- `_rotate_backups()` - Removes old backups
- `check_for_crash()` - Detects previous crashes
- `get_available_backups()` - Lists all backups with metadata

**Backup File Structure**:
```json
{
  "timestamp": "2025-01-10T15:30:00",
  "sections": [...],
  "template_name": "main_layout.html",
  "settings": {...},
  "original_file": "user_drafts/my_draft.json"
}
```

### Integration Points

#### 1. Application Loader (`loader.py`)
```python
MODULES = [
    ...
    ("auto_backup", True),  # Required module
    ...
]
```

The auto-backup system initializes as part of the core module loading sequence:
- Loads after `drafts` module (depends on draft structure)
- Loads before UI setup (to catch any startup issues)
- Marked as `required=True` to ensure robustness

#### 2. Application Close Handler (`__main__.py`)
```python
def _finalize_close(self):
    """Save window state and destroy the window."""
    try:
        # Stop auto-backup system before closing
        if hasattr(self, 'backup_manager'):
            try:
                self.backup_manager.stop()
            except Exception as e:
                logger.debug(f"Error stopping backup manager: {e}")
        ...
    finally:
        self.destroy()
```

Ensures backup system shuts down gracefully:
- Cancels scheduled timers
- Removes crash marker
- Prevents orphaned background tasks

### Crash Recovery Flow

1. **App Starts**
   - Backup manager initializes
   - Creates crash marker file
   - Checks for existing marker (indicates previous crash)

2. **If Crash Detected**
   - Finds most recent backup file
   - Shows recovery dialog with details
   - User chooses to restore or skip

3. **If User Restores**
   - Loads backup data
   - Restores sections, settings, template
   - Clears `current_draft_path` (forces Save As)
   - Refreshes UI
   - Shows "Backup restored - please save your work" message

4. **Normal Operation**
   - Backup every 2 minutes
   - Rotates old backups
   - Updates last backup reference

5. **App Exits Gracefully**
   - Removes crash marker
   - Cancels timers
   - No recovery needed on next launch

6. **App Crashes**
   - Crash marker remains
   - Last backup available for recovery
   - Next launch detects crash and prompts

## Testing

### Test Suite (`tests/test_auto_backup.py`)
**16 comprehensive tests** covering:

#### TestAutoBackupManager (13 tests)
- Initialization and configuration
- Crash marker creation/removal
- Auto-save scheduling
- Draft data collection
- Backup file creation
- Empty content handling
- Backup rotation
- Crash detection
- Backup listing
- Timer cancellation

#### TestAutoBackupIntegration (2 tests)
- Manager initialization
- Crash recovery prompting

#### TestBackupRecovery (1 test)
- Backup restoration

**All 16 tests passing** ✓

## Usage

### For Users
The backup system runs automatically - no user action required.

**If the app crashes:**
1. Restart the app
2. Recovery dialog appears
3. Choose "Yes" to restore last backup
4. Save your work immediately

**To view available backups:**
Backups are stored in `./backups/` directory as JSON files with timestamps in the filename.

### For Developers

**Adjust backup interval:**
```python
backup_manager = AutoBackupManager(app)
backup_manager.backup_interval_ms = 300000  # 5 minutes
```

**Change max backups:**
```python
backup_manager = AutoBackupManager(app, max_backups=20)
```

**Manually trigger backup:**
```python
app.backup_manager._perform_auto_save()
```

**Get available backups:**
```python
backups = app.backup_manager.get_available_backups()
for backup in backups:
    print(f"{backup['name']}: {backup['timestamp']}")
```

## Error Handling

The backup system is designed to be resilient:

- **Logging**: Uses structured logging throughout
- **Exception Handling**: All backup operations wrapped in try/except
- **Graceful Degradation**: Backup failures don't crash the app
- **Silent Background**: Users not interrupted by backup operations

**Common scenarios handled:**
- ❌ Disk full → Logged, backup skipped
- ❌ Permission denied → Logged, error message
- ❌ Invalid JSON → Logged, recovery skipped
- ❌ Missing backup directory → Created automatically
- ❌ Corrupted backup file → Falls back to next most recent

## Future Enhancements

Potential improvements for later:
- [ ] Configurable backup interval in settings UI
- [ ] Manual backup button
- [ ] Backup browser/manager UI
- [ ] Cloud backup integration
- [ ] Differential backups (save only changes)
- [ ] Backup compression
- [ ] Encrypted backups

## Technical Notes

### Performance
- Backup operation is non-blocking (scheduled via `after()`)
- JSON serialization is fast for typical draft sizes
- Rotation cleanup is O(n log n) where n = number of backups

### Platform Compatibility
- **Windows**: Fully supported ✓
- **macOS**: Signal handlers may differ (graceful fallback)
- **Linux**: Full support with signal handlers ✓

### Dependencies
- Standard library only (no external deps for backup system)
- Uses: `json`, `atexit`, `signal`, `pathlib`, `datetime`

## Related Files
- Implementation: `src/bulletin_builder/app_core/auto_backup.py`
- Tests: `tests/test_auto_backup.py`
- Integration: `src/bulletin_builder/app_core/loader.py`
- Close handler: `src/bulletin_builder/__main__.py`

## Commits
- Implementation: `00fd046` - feat: Implement automatic draft backup system
- Documentation: `2ef2cb0` - docs: Mark Error Recovery Task 1 complete
