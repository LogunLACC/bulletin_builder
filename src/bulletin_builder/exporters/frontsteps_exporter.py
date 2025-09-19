from .postprocessors import frontsteps_pipeline


def build_frontsteps_html(state_html: str) -> str:
    """Return body-only HTML tailored for FrontSteps using the sanitizer-aware pipeline."""
    return frontsteps_pipeline(state_html)

