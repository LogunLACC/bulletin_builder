import importlib
import pkgutil


def init_app(app):
    """
    Initialize core attributes and then discover all feature modules under app_core,
    calling their `init(app)` functions to register functionality.
    """
    base_pkg = "bulletin_builder.app_core"  # Fixed base package name

    # Initialize feature modules (core_init is called separately from main app)
    for module in (
        "handlers",
        "drafts",
        "sections",
        "component_library",
        "exporter",
        "preview",
        "suggestions",
        "importer",
        "ui_setup",
    ):
        try:
            m = importlib.import_module(f"{base_pkg}.{module}")
            if hasattr(m, "init"):
                m.init(app)
        except Exception as e:
            print(f"Error initializing module app_core.{module}: {e}")
