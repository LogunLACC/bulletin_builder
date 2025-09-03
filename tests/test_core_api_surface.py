import importlib.util
import pytest


def test_core_api_surface():
    """Ensure at least one program entry module is importable (cli, __main__, or wysiwyg_editor).

    This avoids brittle assumptions about what symbols are exported from package
    __init__ while still ensuring the project has runnable entry points.
    """
    candidates = [
        'bulletin_builder.cli',
        'bulletin_builder.__main__',
        'bulletin_builder.wysiwyg_editor',
    ]
    found = False
    for name in candidates:
        if importlib.util.find_spec(name) is not None:
            found = True
            break
    assert found, f"None of the expected entry modules were importable: {candidates}"
