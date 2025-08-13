# test_imports.py
"""
Test script to verify all core modules in bulletin_builder load without import errors.
"""
import sys
import importlib

MODULES = [
    'bulletin_builder',
    'bulletin_builder.app_core.core_init',
    'bulletin_builder.app_core.drafts',
    'bulletin_builder.app_core.exporter',
    'bulletin_builder.app_core.handlers',
    'bulletin_builder.app_core.image_utils',
    'bulletin_builder.app_core.importer',
    'bulletin_builder.app_core.loader',
    'bulletin_builder.app_core.menu',
    'bulletin_builder.app_core.preview',
    'bulletin_builder.app_core.sections',
    'bulletin_builder.app_core.suggestions',
    'bulletin_builder.app_core.ui_setup',
    'bulletin_builder.bulletin_renderer',
    'bulletin_builder.event_feed',
    'bulletin_builder.image_utils',
    'bulletin_builder.settings',
    'bulletin_builder.ui.announcements',
    'bulletin_builder.ui.base_section',
    'bulletin_builder.ui.calendar_event_dialog',
    'bulletin_builder.ui.component_library',
    'bulletin_builder.ui.custom_text',
    'bulletin_builder.ui.email_dialog',
    'bulletin_builder.ui.events',
    'bulletin_builder.ui.image',
    'bulletin_builder.ui.settings',
    'bulletin_builder.ui.template_gallery',
]

failures = []
for mod in MODULES:
    try:
        importlib.import_module(mod)
        print(f"[OK] {mod}")
    except Exception as e:
        print(f"[FAIL] {mod}: {e}")
        failures.append((mod, str(e)))

if failures:
    print("\nSome modules failed to import:")
    for mod, err in failures:
        print(f" - {mod}: {err}")
    sys.exit(1)
else:
    print("\nAll modules imported successfully.")
    sys.exit(0)
