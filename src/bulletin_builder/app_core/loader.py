from importlib import import_module

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
    """Import a module from bulletin_builder.app_core by name.

    This thin wrapper centralizes import errors so callers can decide whether
    a missing module is fatal (required) or optional.
    """
    try:
        return import_module(f"bulletin_builder.app_core.{name}")
    except Exception:
        # Don't mask the original exception; callers will handle required vs optional
        raise


def init_app(app):
    """Initialize and attach core app modules.

    Iterates MODULES and calls their `init(app)` functions when present.
    Required modules raise a RuntimeError if initialization fails.
    """
    for name, required in MODULES:
        try:
            mod = _import_flexible(name)
            if hasattr(mod, "init"):
                mod.init(app)
        except Exception as e:
            msg = f"Error initializing module {name}: {e}"
            if required:
                raise RuntimeError(msg)
            # Non-fatal module; log and continue
            print(msg)
