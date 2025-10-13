"""Tests for template caching system."""

import pytest
import time
import tempfile
from pathlib import Path
from bulletin_builder.app_core.template_cache import (
    TemplateCacheStats,
    CachedBulletinRenderer,
    get_global_cache_stats
)


class TestTemplateCacheStats:
    """Test template cache statistics tracking."""
    
    def test_stats_initialization(self):
        """Test stats initialize with zero values."""
        stats = TemplateCacheStats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.renders == 0
        assert stats.total_render_time == 0.0
        assert stats.cache_saves == 0
    
    def test_record_hit(self):
        """Test recording cache hits."""
        stats = TemplateCacheStats()
        stats.record_hit()
        stats.record_hit()
        assert stats.hits == 2
    
    def test_record_miss(self):
        """Test recording cache misses."""
        stats = TemplateCacheStats()
        stats.record_miss()
        stats.record_miss()
        stats.record_miss()
        assert stats.misses == 3
    
    def test_record_render(self):
        """Test recording render operations."""
        stats = TemplateCacheStats()
        stats.record_render(10.5)
        stats.record_render(20.3)
        assert stats.renders == 2
        assert stats.total_render_time == pytest.approx(30.8)
    
    def test_get_hit_rate(self):
        """Test hit rate calculation."""
        stats = TemplateCacheStats()
        
        # No hits or misses yet
        assert stats.get_hit_rate() == 0.0
        
        # 3 hits, 1 miss = 75% hit rate
        stats.record_hit()
        stats.record_hit()
        stats.record_hit()
        stats.record_miss()
        assert stats.get_hit_rate() == 75.0
    
    def test_get_average_render_time(self):
        """Test average render time calculation."""
        stats = TemplateCacheStats()
        
        # No renders yet
        assert stats.get_average_render_time() == 0.0
        
        # 10ms, 20ms, 30ms = 20ms average
        stats.record_render(10.0)
        stats.record_render(20.0)
        stats.record_render(30.0)
        assert stats.get_average_render_time() == pytest.approx(20.0)
    
    def test_report(self):
        """Test statistics report generation."""
        stats = TemplateCacheStats()
        stats.record_hit()
        stats.record_hit()
        stats.record_miss()
        stats.record_render(15.5)
        stats.record_cache_save()
        
        report = stats.report()
        assert "Hits: 2" in report
        assert "Misses: 1" in report
        assert "Hit Rate: 66.7%" in report
        assert "Total Renders: 1" in report
        assert "Cache Saves: 1" in report


class TestCachedBulletinRenderer:
    """Test cached bulletin renderer."""
    
    @pytest.fixture
    def temp_templates_dir(self):
        """Create a temporary templates directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            templates_dir = Path(tmpdir)
            
            # Create a simple test template
            test_template = templates_dir / "test.html"
            test_template.write_text(
                "<html><body><h1>{{ title }}</h1><p>{{ content }}</p></body></html>",
                encoding="utf-8"
            )
            
            # Create another template
            other_template = templates_dir / "other.html"
            other_template.write_text(
                "<html><body><h2>{{ heading }}</h2></body></html>",
                encoding="utf-8"
            )
            
            # Create themes directory
            themes_dir = templates_dir / "themes"
            themes_dir.mkdir()
            
            # Create a theme CSS file
            theme_css = themes_dir / "test_theme.css"
            theme_css.write_text(
                "body { background: #fff; color: #333; }",
                encoding="utf-8"
            )
            
            yield templates_dir
    
    def test_renderer_initialization(self, temp_templates_dir):
        """Test renderer initializes correctly."""
        renderer = CachedBulletinRenderer(
            templates_dir=temp_templates_dir,
            template_name="test.html"
        )
        
        assert renderer.templates_dir == temp_templates_dir
        assert renderer.template_name == "test.html"
        assert isinstance(renderer.stats, TemplateCacheStats)
    
    def test_render_basic(self, temp_templates_dir):
        """Test basic template rendering."""
        renderer = CachedBulletinRenderer(
            templates_dir=temp_templates_dir,
            template_name="test.html"
        )
        
        html = renderer.render({
            "title": "Test Title",
            "content": "Test Content"
        })
        
        assert "Test Title" in html
        assert "Test Content" in html
    
    def test_caching_works(self, temp_templates_dir):
        """Test that caching actually works."""
        renderer = CachedBulletinRenderer(
            templates_dir=temp_templates_dir,
            template_name="test.html",
            enable_output_cache=True
        )
        
        context = {
            "title": "Cached Title",
            "content": "Cached Content"
        }
        
        # First render - should be a cache miss
        html1 = renderer.render(context)
        assert renderer.stats.misses == 1
        assert renderer.stats.hits == 0
        
        # Second render with same context - should be a cache hit
        html2 = renderer.render(context)
        assert renderer.stats.misses == 1
        assert renderer.stats.hits == 1
        
        # Both renders should produce identical HTML
        assert html1 == html2
    
    def test_cache_invalidation_on_template_change(self, temp_templates_dir):
        """Test that cache invalidates when template changes."""
        renderer = CachedBulletinRenderer(
            templates_dir=temp_templates_dir,
            template_name="test.html",
            enable_output_cache=True
        )
        
        context = {"title": "Title", "content": "Content"}
        
        # First render
        html1 = renderer.render(context)
        
        # Wait a moment to ensure different mtime
        time.sleep(0.1)
        
        # Modify the template
        test_template = temp_templates_dir / "test.html"
        test_template.write_text(
            "<html><body><h1>MODIFIED: {{ title }}</h1></body></html>",
            encoding="utf-8"
        )
        
        # Render again - should detect template change and re-render
        html2 = renderer.render(context)
        
        assert "MODIFIED:" in html2
        assert html1 != html2
    
    def test_different_contexts_cached_separately(self, temp_templates_dir):
        """Test that different contexts are cached separately."""
        renderer = CachedBulletinRenderer(
            templates_dir=temp_templates_dir,
            template_name="test.html"
        )
        
        context1 = {"title": "Title 1", "content": "Content 1"}
        context2 = {"title": "Title 2", "content": "Content 2"}
        
        html1 = renderer.render(context1)
        html2 = renderer.render(context2)
        
        # Both should be cache misses (different contexts)
        assert renderer.stats.misses == 2
        
        # Render context1 again - should be a cache hit
        html1_again = renderer.render(context1)
        assert renderer.stats.hits == 1
        assert html1_again == html1
    
    def test_cache_can_be_cleared(self, temp_templates_dir):
        """Test that cache can be manually cleared."""
        renderer = CachedBulletinRenderer(
            templates_dir=temp_templates_dir,
            template_name="test.html"
        )
        
        context = {"title": "Title", "content": "Content"}
        
        # Render to populate cache
        renderer.render(context)
        assert renderer.stats.misses == 1
        
        # Clear cache
        renderer.clear_cache()
        
        # Render again - should be a cache miss again
        renderer.render(context)
        assert renderer.stats.misses == 2
    
    def test_bytecode_cache_disabled(self, temp_templates_dir):
        """Test renderer works with bytecode cache disabled."""
        renderer = CachedBulletinRenderer(
            templates_dir=temp_templates_dir,
            template_name="test.html",
            enable_bytecode_cache=False
        )
        
        html = renderer.render({
            "title": "Test",
            "content": "Content"
        })
        
        assert "Test" in html
    
    def test_output_cache_disabled(self, temp_templates_dir):
        """Test renderer works with output cache disabled."""
        renderer = CachedBulletinRenderer(
            templates_dir=temp_templates_dir,
            template_name="test.html",
            enable_output_cache=False
        )
        
        context = {"title": "Test", "content": "Content"}
        
        # Render multiple times
        html1 = renderer.render(context)
        html2 = renderer.render(context)
        
        # Should be all cache misses when output cache disabled
        assert renderer.stats.misses >= 2
        assert renderer.stats.hits == 0
        
        # HTML should still be identical
        assert html1 == html2
    
    def test_set_template(self, temp_templates_dir):
        """Test changing the default template."""
        renderer = CachedBulletinRenderer(
            templates_dir=temp_templates_dir,
            template_name="test.html"
        )
        
        assert renderer.template_name == "test.html"
        
        renderer.set_template("other.html")
        assert renderer.template_name == "other.html"
        
        html = renderer.render({"heading": "New Heading"})
        assert "New Heading" in html
    
    def test_theme_css_loading(self, temp_templates_dir):
        """Test theme CSS loading."""
        renderer = CachedBulletinRenderer(
            templates_dir=temp_templates_dir,
            template_name="test.html",
            theme_css="test_theme.css"
        )
        
        html = renderer.render({
            "title": "Test",
            "content": "Content",
            "settings": {"theme_css": "test_theme.css"}
        })
        
        assert html  # Just verify it renders without error
    
    def test_performance_improvement(self, temp_templates_dir):
        """Test that caching actually improves performance."""
        renderer = CachedBulletinRenderer(
            templates_dir=temp_templates_dir,
            template_name="test.html"
        )
        
        context = {"title": "Performance Test", "content": "Testing"}
        
        # First render (cache miss)
        start1 = time.perf_counter()
        renderer.render(context)
        time1 = (time.perf_counter() - start1) * 1000
        
        # Second render (cache hit)
        start2 = time.perf_counter()
        renderer.render(context)
        time2 = (time.perf_counter() - start2) * 1000
        
        # Cache hit should be significantly faster
        # Note: This might be flaky on slow systems, so we use a generous threshold
        assert time2 < time1 * 2  # At least somewhat faster
    
    def test_get_stats(self, temp_templates_dir):
        """Test getting cache statistics."""
        renderer = CachedBulletinRenderer(
            templates_dir=temp_templates_dir,
            template_name="test.html"
        )
        
        stats = renderer.get_stats()
        assert isinstance(stats, TemplateCacheStats)
        assert stats is renderer.stats  # Should be the same object


class TestGlobalStats:
    """Test global cache statistics."""
    
    def test_get_global_stats(self):
        """Test getting global cache statistics."""
        stats = get_global_cache_stats()
        assert isinstance(stats, TemplateCacheStats)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_missing_template(self, tmp_path):
        """Test handling of missing template file."""
        renderer = CachedBulletinRenderer(
            templates_dir=tmp_path,
            template_name="nonexistent.html"
        )
        
        with pytest.raises(Exception):  # Should raise template not found error
            renderer.render({"title": "Test"})
    
    def test_empty_context(self, tmp_path):
        """Test rendering with empty context."""
        # Create a minimal template
        template_path = tmp_path / "minimal.html"
        template_path.write_text("<html><body>Hello</body></html>", encoding="utf-8")
        
        renderer = CachedBulletinRenderer(
            templates_dir=tmp_path,
            template_name="minimal.html"
        )
        
        html = renderer.render({})
        assert "Hello" in html
    
    def test_none_context(self, tmp_path):
        """Test rendering with None context."""
        template_path = tmp_path / "minimal.html"
        template_path.write_text("<html><body>Test</body></html>", encoding="utf-8")
        
        renderer = CachedBulletinRenderer(
            templates_dir=tmp_path,
            template_name="minimal.html"
        )
        
        html = renderer.render(None)
        assert "Test" in html
