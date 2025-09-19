from src.exporters.postprocessors import run_pipeline

# Single public entry point for the UI

def build_frontsteps_html(state_html: str, *, minify: bool = True) -> str:
    """Return FrontSteps-ready, body-only HTML from the preview document HTML."""
    return run_pipeline(state_html, minify=minify)