import importlib
import pkgutil
import app_core

def init_app(app):
    """
    Initialize core attributes and then discover all feature modules under app_core,
    calling their `init(app)` functions to register functionality.
    """
    try:
        from app_core.core_init import init as _core_init
        _core_init(app)
    except Exception as e:
        print(f"Error in core_init: {e}")

    # 2) then drafts, handlers, sections, exporter, preview...
    for module in ("handlers", "drafts", "sections", "exporter", "preview", "ui_setup"):
        try:
            m = importlib.import_module(f"app_core.{module}")
            if hasattr(m, "init"):
                m.init(app)
        except Exception as e:
            print(f"Error initializing module app_core.{module}: {e}")
