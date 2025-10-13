"""
Lazy import system for Bulletin Builder.

Defers importing heavy modules until they're actually needed, significantly
reducing startup time. Heavy modules like WeasyPrint (~390ms) and AI libraries
(~800ms) are only loaded when their features are used.

Usage:
    from bulletin_builder.app_core.lazy_imports import lazy_weasyprint, lazy_gemini
    
    # These don't import anything yet - instant!
    def export_pdf():
        weasyprint = lazy_weasyprint()  # NOW it imports (only once)
        # Use weasyprint...
    
    def generate_ai_suggestion():
        genai = lazy_gemini()  # NOW it imports (only once)
        # Use genai...
"""

import logging
from typing import Any, Callable, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


class LazyImporter:
    """Lazy import wrapper that defers module loading until first use."""
    
    def __init__(self, module_name: str, friendly_name: str):
        self.module_name = module_name
        self.friendly_name = friendly_name
        self._module: Optional[Any] = None
        self._import_attempted = False
        self._import_error: Optional[Exception] = None
    
    def get(self) -> Any:
        """Get the module, importing it if necessary."""
        if self._module is not None:
            return self._module
        
        if self._import_attempted and self._import_error:
            # Already tried and failed
            raise self._import_error
        
        # Try to import
        self._import_attempted = True
        try:
            import importlib
            import time
            
            start = time.perf_counter()
            self._module = importlib.import_module(self.module_name)
            duration = time.perf_counter() - start
            
            logger.info(f"Lazy-loaded {self.friendly_name} in {duration*1000:.2f}ms")
            return self._module
            
        except ImportError as e:
            self._import_error = ImportError(
                f"Failed to import {self.friendly_name} ({self.module_name}): {e}\n"
                f"This feature requires the module to be installed."
            )
            logger.warning(f"Lazy import failed for {self.friendly_name}: {e}")
            raise self._import_error
    
    def is_available(self) -> bool:
        """Check if module is available without importing it."""
        if self._module is not None:
            return True
        if self._import_attempted and self._import_error:
            return False
        
        # Try to find the module spec without importing
        try:
            import importlib.util
            spec = importlib.util.find_spec(self.module_name)
            return spec is not None
        except (ImportError, ValueError):
            return False


# Create lazy importers for heavy modules
_weasyprint_importer = LazyImporter("weasyprint", "WeasyPrint PDF Generator")
_gemini_importer = LazyImporter("google.generativeai", "Google Gemini AI")
_openai_importer = LazyImporter("openai", "OpenAI API")


@lru_cache(maxsize=1)
def lazy_weasyprint() -> Any:
    """
    Lazy-load WeasyPrint for PDF generation.
    
    Returns:
        weasyprint module
    
    Raises:
        ImportError: If WeasyPrint is not installed
    
    Example:
        >>> weasyprint = lazy_weasyprint()
        >>> html = weasyprint.HTML(string="<h1>Hello</h1>")
        >>> html.write_pdf("output.pdf")
    """
    return _weasyprint_importer.get()


@lru_cache(maxsize=1)
def lazy_gemini() -> Any:
    """
    Lazy-load Google Gemini AI library.
    
    Returns:
        google.generativeai module
    
    Raises:
        ImportError: If google-generativeai is not installed
    
    Example:
        >>> genai = lazy_gemini()
        >>> genai.configure(api_key="...")
        >>> model = genai.GenerativeModel("gemini-pro")
        >>> response = model.generate_content("Hello")
    """
    return _gemini_importer.get()


@lru_cache(maxsize=1)
def lazy_openai() -> Any:
    """
    Lazy-load OpenAI API library.
    
    Returns:
        openai module
    
    Raises:
        ImportError: If openai is not installed
    
    Example:
        >>> openai = lazy_openai()
        >>> client = openai.OpenAI(api_key="...")
        >>> response = client.chat.completions.create(...)
    """
    return _openai_importer.get()


def is_weasyprint_available() -> bool:
    """Check if WeasyPrint is available without importing it."""
    return _weasyprint_importer.is_available()


def is_gemini_available() -> bool:
    """Check if Google Gemini is available without importing it."""
    return _gemini_importer.is_available()


def is_openai_available() -> bool:
    """Check if OpenAI is available without importing it."""
    return _openai_importer.is_available()


class LazyModule:
    """
    Proxy object that lazily imports a module on attribute access.
    
    This allows you to import the module at the top of your file
    without actually loading it until it's used.
    
    Example:
        >>> from bulletin_builder.app_core.lazy_imports import LazyModule
        >>> weasyprint = LazyModule("weasyprint", "WeasyPrint")
        >>> # Not imported yet!
        >>> 
        >>> html = weasyprint.HTML(string="<h1>Test</h1>")
        >>> # NOW it's imported (on first attribute access)
    """
    
    def __init__(self, module_name: str, friendly_name: str):
        self._importer = LazyImporter(module_name, friendly_name)
    
    def __getattr__(self, name: str) -> Any:
        """Lazily import and return attribute."""
        module = self._importer.get()
        return getattr(module, name)
    
    def __repr__(self) -> str:
        if self._importer._module is not None:
            return f"<LazyModule '{self._importer.module_name}' (loaded)>"
        return f"<LazyModule '{self._importer.module_name}' (not loaded)>"


# Performance tracking
class ImportStats:
    """Track lazy import performance."""
    
    def __init__(self):
        self.imports = {}
    
    def record(self, name: str, duration_ms: float):
        """Record an import."""
        self.imports[name] = duration_ms
    
    def get_total_saved(self) -> float:
        """Get total startup time saved by lazy loading."""
        # Estimate: all modules would have been loaded at startup
        return sum(self.imports.values())
    
    def report(self) -> str:
        """Generate performance report."""
        if not self.imports:
            return "No lazy imports tracked yet."
        
        lines = ["Lazy Import Performance:"]
        for name, duration in sorted(self.imports.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  • {name}: {duration:.2f}ms")
        lines.append(f"\nTotal startup time saved: {self.get_total_saved():.2f}ms")
        return "\n".join(lines)


# Global stats tracker
_import_stats = ImportStats()


def get_import_stats() -> ImportStats:
    """Get the global import stats tracker."""
    return _import_stats
