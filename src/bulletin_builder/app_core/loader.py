import importlib
import pkgutil


def init_app(app):
    """
    Initialize core attributes and then discover all feature modules under app_core,
    calling their `init(app)` functions to register functionality.
    """
    base_pkg = __name__  # e.g., 'bulletin_builder.app_core'

    try:
        from .core_init import init as _core_init
        _core_init(app)
    except Exception as e:
        print(f"Error in core_init: {e}")

    # 2) then drafts, handlers, sections, components, exporter, preview, importer...
    for module in ("handlers", "drafts", "sections", "component_library", "exporter", "preview", "importer", "ui_setup"):
        try:
            m = importlib.import_module(f"{base_pkg}.{module}")
            if hasattr(m, "init"):
                m.init(app)
        except Exception as e:
            print(f"Error initializing module app_core.{module}: {e}")
