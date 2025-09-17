
import importlib
import pytest

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
    'bulletin_builder.ui.custom_text',
    'bulletin_builder.ui.events',
    'bulletin_builder.ui.image',
    'bulletin_builder.ui.settings',
    'bulletin_builder.ui.template_gallery',
]

@pytest.mark.parametrize("mod", MODULES)
def test_import_module(mod):
    importlib.import_module(mod)
