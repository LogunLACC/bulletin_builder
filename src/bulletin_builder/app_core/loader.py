from importlib import import_module

<<<<<<< HEAD
MODULES = [
    ("core_init", True),      # builds frames, status/progress, basic hooks
    ("handlers", False),
    ("drafts", False),
    ("sections", False),
    ("suggestions", False),   # Ensure full menubar (File + Tools) is wired even if ui_setup's fallback kicks in
    ("menu", False),
    ("importer", False),      # CSV/Sheet/Feed importers
    ("exporter", False),      # HTML/TXT export, ICS, email
    ("preview", True),        # defines show_placeholder + update_preview
    ("ui_setup", True),       # builds UI; attaches _build_menus and calls it
]

def _import_flexible(name):
    # Always use bulletin_builder.app_core.<name> for core modules
    try:
        return import_module(f"bulletin_builder.app_core.{name}")
    except Exception as e:
        raise e

def init_app(app):
    for name, required in MODULES:
        try:
            mod = _import_flexible(name)
            if hasattr(mod, "init"):
                mod.init(app)
        except Exception as e:
            msg = f"Error initializing module {name}: {e}"
            if required:
                raise RuntimeError(msg)
            print(msg)
=======

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
>>>>>>> origin/harden/email-sanitize-and-ci
