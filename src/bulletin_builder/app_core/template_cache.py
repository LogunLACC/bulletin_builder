"""
Template Caching System for Bulletin Builder.

Provides enhanced template caching with:
- Bytecode compilation caching
- Template content caching
- File modification detection
- Cache statistics and monitoring
"""

from pathlib import Path
from typing import Dict, Any, Optional
import time
import hashlib
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.bccache import FileSystemBytecodeCache
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)


class TemplateCacheStats:
    """Track template caching statistics."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.renders = 0
        self.total_render_time = 0.0
        self.cache_saves = 0
        
    def record_hit(self):
        """Record a cache hit."""
        self.hits += 1
    
    def record_miss(self):
        """Record a cache miss."""
        self.misses += 1
    
    def record_render(self, duration_ms: float):
        """Record a render operation."""
        self.renders += 1
        self.total_render_time += duration_ms
    
    def record_cache_save(self):
        """Record a cache save operation."""
        self.cache_saves += 1
    
    def get_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
    
    def get_average_render_time(self) -> float:
        """Calculate average render time."""
        return (self.total_render_time / self.renders) if self.renders > 0 else 0.0
    
    def report(self) -> str:
        """Generate a human-readable statistics report."""
        hit_rate = self.get_hit_rate()
        avg_time = self.get_average_render_time()
        
        return f"""Template Cache Statistics:
  Hits: {self.hits}
  Misses: {self.misses}
  Hit Rate: {hit_rate:.1f}%
  Total Renders: {self.renders}
  Average Render Time: {avg_time:.2f}ms
  Cache Saves: {self.cache_saves}
  Total Time Saved: ~{(self.hits * 5.0):.2f}ms (estimated)
"""


class CachedBulletinRenderer:
    """
    Enhanced BulletinRenderer with aggressive template caching.
    
    Features:
    - Bytecode compilation caching (Jinja2 built-in)
    - Rendered output caching with content hashing
    - File modification time tracking
    - Cache statistics tracking
    """
    
    def __init__(
        self,
        templates_dir: Path | str,
        template_name: str = "main_layout.html",
        theme_css: Optional[str] = None,
        enable_bytecode_cache: bool = True,
        enable_output_cache: bool = True
    ):
        """
        Initialize the cached renderer.
        
        Args:
            templates_dir: Directory containing templates
            template_name: Default template name
            theme_css: Optional theme CSS filename
            enable_bytecode_cache: Enable Jinja2 bytecode caching
            enable_output_cache: Enable rendered output caching
        """
        self.templates_dir = Path(templates_dir)
        self.template_name = template_name
        self.theme_css = theme_css
        self.enable_output_cache = enable_output_cache
        
        # Statistics tracking
        self.stats = TemplateCacheStats()
        
        # Output cache: hash(template_name + context) -> (html, mtime)
        self._output_cache: Dict[str, tuple[str, float]] = {}
        
        # Template modification times
        self._template_mtimes: Dict[str, float] = {}
        
        # Setup Jinja2 environment with bytecode caching
        if enable_bytecode_cache:
            # Create cache directory
            cache_dir = Path(".template_cache")
            cache_dir.mkdir(exist_ok=True)
            
            bytecode_cache = FileSystemBytecodeCache(
                directory=str(cache_dir),
                pattern='__jinja2_%s.cache'
            )
            logger.info(f"Bytecode cache enabled: {cache_dir}")
        else:
            bytecode_cache = None
        
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            bytecode_cache=bytecode_cache,
            auto_reload=True,  # Check for template changes
            cache_size=400     # Keep 400 compiled templates in memory
        )
        
        logger.info(f"Template cache initialized: {self.templates_dir}")
    
    def _get_template_mtime(self, template_name: str) -> float:
        """Get the modification time of a template file."""
        template_path = self.templates_dir / template_name
        try:
            return template_path.stat().st_mtime
        except Exception:
            return 0.0
    
    def _is_template_modified(self, template_name: str) -> bool:
        """Check if a template has been modified since last cache."""
        current_mtime = self._get_template_mtime(template_name)
        cached_mtime = self._template_mtimes.get(template_name, 0.0)
        
        if current_mtime > cached_mtime:
            self._template_mtimes[template_name] = current_mtime
            return True
        return False
    
    def _get_cache_key(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Generate a cache key from template name and context.
        
        Uses SHA256 hash of template name + sorted context keys/values.
        """
        # Create a stable string representation of the context
        context_str = str(sorted(context.items()))
        combined = f"{template_name}:{context_str}"
        
        # Hash it to create a shorter key
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _load_theme_css(self, settings: Dict[str, Any]) -> str:
        """Load theme CSS from file."""
        css_name = (settings or {}).get("theme_css") or self.theme_css
        if not css_name:
            return ""
        
        css_path = self.templates_dir / "themes" / css_name
        try:
            return css_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.debug(f"Could not load theme CSS {css_name}: {e}")
            return ""
    
    def set_template(self, name: str) -> None:
        """Change the default template."""
        self.template_name = name
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._output_cache.clear()
        self._template_mtimes.clear()
        logger.info("Template cache cleared")
    
    def get_stats(self) -> TemplateCacheStats:
        """Get cache statistics."""
        return self.stats
    
    def render(self, ctx: Optional[Dict[str, Any]] = None) -> str:
        """
        Render a template with caching.
        
        Args:
            ctx: Template context dictionary
        
        Returns:
            Rendered HTML string
        """
        start_time = time.perf_counter()
        
        ctx = dict(ctx or {})
        template_name = ctx.pop("template", self.template_name)
        
        # Normalize + enrich context
        settings = ctx.get("settings") or {}
        ctx["settings"] = settings
        ctx["theme_styles"] = self._load_theme_css(settings)
        ctx["sections"] = list(ctx.get("sections") or [])
        
        # Check output cache if enabled
        if self.enable_output_cache:
            cache_key = self._get_cache_key(template_name, ctx)
            
            # Check if template was modified
            if not self._is_template_modified(template_name):
                # Try to get from cache
                if cache_key in self._output_cache:
                    cached_html, cached_mtime = self._output_cache[cache_key]
                    current_mtime = self._get_template_mtime(template_name)
                    
                    # Cache is valid if template hasn't changed
                    if cached_mtime >= current_mtime:
                        self.stats.record_hit()
                        duration_ms = (time.perf_counter() - start_time) * 1000
                        self.stats.record_render(duration_ms)
                        logger.debug(f"Cache HIT for {template_name} (key: {cache_key[:8]}...)")
                        return cached_html
        
        # Cache miss - render the template
        self.stats.record_miss()
        
        try:
            template = self.env.get_template(template_name)
            html_output = template.render(**ctx)
            
            # Store in output cache
            if self.enable_output_cache:
                cache_key = self._get_cache_key(template_name, ctx)
                current_mtime = self._get_template_mtime(template_name)
                self._output_cache[cache_key] = (html_output, current_mtime)
                self.stats.record_cache_save()
                logger.debug(f"Cache MISS for {template_name} - cached (key: {cache_key[:8]}...)")
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.stats.record_render(duration_ms)
            
            return html_output
            
        except Exception as e:
            logger.error(f"Error rendering template '{template_name}': {e}")
            raise


# Global statistics instance
_global_stats = TemplateCacheStats()


def get_global_cache_stats() -> TemplateCacheStats:
    """Get global cache statistics."""
    return _global_stats
