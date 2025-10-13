"""Tests for lazy import system."""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from bulletin_builder.app_core.lazy_imports import (
    LazyImporter,
    lazy_weasyprint,
    lazy_gemini,
    lazy_openai,
    is_weasyprint_available,
    is_gemini_available,
    is_openai_available,
    LazyModule,
    ImportStats,
    get_import_stats
)


class TestLazyImporter:
    """Test LazyImporter class."""
    
    def test_lazy_importer_initialization(self):
        """Test LazyImporter initializes correctly."""
        importer = LazyImporter("json", "JSON")
        assert importer.module_name == "json"
        assert importer.friendly_name == "JSON"
        assert importer._module is None
        assert not importer._import_attempted
    
    def test_lazy_importer_get_success(self):
        """Test successful lazy import."""
        importer = LazyImporter("json", "JSON")
        
        # Module not loaded yet
        assert importer._module is None
        
        # Get module
        module = importer.get()
        assert module is not None
        assert importer._module is module
        assert importer._import_attempted
        
        # Second call returns same module
        module2 = importer.get()
        assert module2 is module
    
    def test_lazy_importer_get_failure(self):
        """Test lazy import failure."""
        importer = LazyImporter("nonexistent_module_12345", "Fake Module")
        
        # First call should raise ImportError
        with pytest.raises(ImportError) as exc_info:
            importer.get()
        
        assert "Fake Module" in str(exc_info.value)
        assert importer._import_attempted
        assert importer._import_error is not None
        
        # Second call should also raise (cached error)
        with pytest.raises(ImportError):
            importer.get()
    
    def test_lazy_importer_is_available(self):
        """Test is_available method."""
        # Available module
        importer1 = LazyImporter("json", "JSON")
        assert importer1.is_available()
        
        # Unavailable module
        importer2 = LazyImporter("nonexistent_module_12345", "Fake")
        assert not importer2.is_available()
    
    def test_lazy_importer_is_available_after_import(self):
        """Test is_available after successful import."""
        importer = LazyImporter("json", "JSON")
        
        # Import the module
        module = importer.get()
        assert module is not None
        
        # Should still be available
        assert importer.is_available()
    
    def test_lazy_importer_is_available_after_failure(self):
        """Test is_available after failed import."""
        importer = LazyImporter("nonexistent_module_12345", "Fake")
        
        # Try to import (will fail)
        with pytest.raises(ImportError):
            importer.get()
        
        # Should not be available
        assert not importer.is_available()


class TestLazyFunctions:
    """Test lazy import functions."""
    
    @pytest.mark.skipif(
        not is_weasyprint_available(),
        reason="WeasyPrint not installed"
    )
    def test_lazy_weasyprint(self):
        """Test lazy_weasyprint function."""
        # Clear cache
        lazy_weasyprint.cache_clear()
        
        # Get module
        weasyprint = lazy_weasyprint()
        assert weasyprint is not None
        assert hasattr(weasyprint, 'HTML')
        
        # Second call returns same module (cached)
        weasyprint2 = lazy_weasyprint()
        assert weasyprint2 is weasyprint
    
    @pytest.mark.skipif(
        not is_gemini_available(),
        reason="Google Gemini not installed"
    )
    def test_lazy_gemini(self):
        """Test lazy_gemini function."""
        # Clear cache
        lazy_gemini.cache_clear()
        
        # Get module
        genai = lazy_gemini()
        assert genai is not None
        assert hasattr(genai, 'configure') or hasattr(genai, 'GenerativeModel')
    
    @pytest.mark.skipif(
        not is_openai_available(),
        reason="OpenAI not installed"
    )
    def test_lazy_openai(self):
        """Test lazy_openai function."""
        # Clear cache
        lazy_openai.cache_clear()
        
        # Get module
        openai = lazy_openai()
        assert openai is not None
        assert hasattr(openai, 'OpenAI') or hasattr(openai, 'ChatCompletion')
    
    def test_is_weasyprint_available(self):
        """Test is_weasyprint_available function."""
        result = is_weasyprint_available()
        assert isinstance(result, bool)
    
    def test_is_gemini_available(self):
        """Test is_gemini_available function."""
        result = is_gemini_available()
        assert isinstance(result, bool)
    
    def test_is_openai_available(self):
        """Test is_openai_available function."""
        result = is_openai_available()
        assert isinstance(result, bool)


class TestLazyModule:
    """Test LazyModule proxy class."""
    
    def test_lazy_module_initialization(self):
        """Test LazyModule initializes correctly."""
        lazy_mod = LazyModule("json", "JSON")
        assert lazy_mod._importer.module_name == "json"
        assert lazy_mod._importer.friendly_name == "JSON"
    
    def test_lazy_module_attribute_access(self):
        """Test LazyModule attribute access triggers import."""
        lazy_json = LazyModule("json", "JSON")
        
        # Module not imported yet
        assert lazy_json._importer._module is None
        
        # Access attribute - triggers import
        dumps = lazy_json.dumps
        assert callable(dumps)
        
        # Module now imported
        assert lazy_json._importer._module is not None
    
    def test_lazy_module_method_call(self):
        """Test calling methods on LazyModule."""
        lazy_json = LazyModule("json", "JSON")
        
        # Call method
        result = lazy_json.dumps({"test": "data"})
        assert isinstance(result, str)
        assert "test" in result
    
    def test_lazy_module_repr(self):
        """Test LazyModule __repr__."""
        lazy_mod = LazyModule("json", "JSON")
        
        # Before import
        repr_str = repr(lazy_mod)
        assert "not loaded" in repr_str
        
        # Trigger import
        _ = lazy_mod.dumps
        
        # After import
        repr_str = repr(lazy_mod)
        assert "loaded" in repr_str
    
    def test_lazy_module_import_error(self):
        """Test LazyModule with non-existent module."""
        lazy_mod = LazyModule("nonexistent_module_12345", "Fake")
        
        # Accessing attribute should raise ImportError
        with pytest.raises(ImportError) as exc_info:
            _ = lazy_mod.some_attribute
        
        assert "Fake" in str(exc_info.value)


class TestImportStats:
    """Test ImportStats class."""
    
    def test_import_stats_initialization(self):
        """Test ImportStats initializes correctly."""
        stats = ImportStats()
        assert stats.imports == {}
    
    def test_import_stats_record(self):
        """Test recording imports."""
        stats = ImportStats()
        
        stats.record("module1", 100.5)
        stats.record("module2", 50.3)
        
        assert stats.imports["module1"] == 100.5
        assert stats.imports["module2"] == 50.3
    
    def test_import_stats_get_total_saved(self):
        """Test calculating total time saved."""
        stats = ImportStats()
        
        stats.record("module1", 100.0)
        stats.record("module2", 50.0)
        stats.record("module3", 25.5)
        
        total = stats.get_total_saved()
        assert total == 175.5
    
    def test_import_stats_get_total_saved_empty(self):
        """Test total saved with no imports."""
        stats = ImportStats()
        assert stats.get_total_saved() == 0.0
    
    def test_import_stats_report(self):
        """Test generating report."""
        stats = ImportStats()
        
        # Empty report
        report = stats.report()
        assert "No lazy imports" in report
        
        # With data
        stats.record("weasyprint", 390.5)
        stats.record("gemini", 794.2)
        stats.record("openai", 21.0)
        
        report = stats.report()
        assert "weasyprint" in report
        assert "gemini" in report
        assert "openai" in report
        assert "390.5" in report or "390.50" in report
        assert "Total startup time saved" in report
        assert "1205.7" in report or "1205.70" in report
    
    def test_get_import_stats(self):
        """Test get_import_stats global function."""
        stats = get_import_stats()
        assert isinstance(stats, ImportStats)
        
        # Should return same instance
        stats2 = get_import_stats()
        assert stats2 is stats


class TestPerformanceImpact:
    """Test actual performance impact of lazy loading."""
    
    def test_lazy_loading_defers_import(self):
        """Test that lazy loading defers import."""
        import time
        
        # Create lazy importer
        lazy_mod = LazyImporter("pathlib", "PathLib")
        
        # Should be instant (no import yet)
        start = time.perf_counter()
        importer_created = lazy_mod
        creation_time = time.perf_counter() - start
        
        assert creation_time < 0.001  # Should be < 1ms
        assert lazy_mod._module is None
        
        # Now trigger import
        start = time.perf_counter()
        module = lazy_mod.get()
        import_time = time.perf_counter() - start
        
        assert module is not None
        assert import_time > 0  # Some time should have passed
    
    def test_lazy_module_defers_import(self):
        """Test that LazyModule defers import until attribute access."""
        import time
        
        # Create LazyModule
        start = time.perf_counter()
        lazy_json = LazyModule("json", "JSON")
        creation_time = time.perf_counter() - start
        
        assert creation_time < 0.001  # Should be < 1ms
        assert lazy_json._importer._module is None
        
        # Trigger import
        start = time.perf_counter()
        _ = lazy_json.dumps
        access_time = time.perf_counter() - start
        
        assert lazy_json._importer._module is not None
        assert access_time > 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_lazy_importer_repeated_failures(self):
        """Test that repeated import attempts fail consistently."""
        importer = LazyImporter("fake_module_xyz", "Fake")
        
        # First attempt
        with pytest.raises(ImportError):
            importer.get()
        
        # Second attempt (should use cached error)
        with pytest.raises(ImportError):
            importer.get()
        
        # Third attempt
        with pytest.raises(ImportError):
            importer.get()
    
    def test_lazy_module_with_special_attributes(self):
        """Test LazyModule with __dunder__ attributes."""
        lazy_mod = LazyModule("json", "JSON")
        
        # __repr__ should work without importing
        repr_str = repr(lazy_mod)
        assert isinstance(repr_str, str)
        assert lazy_mod._importer._module is None  # Still not imported
    
    def test_is_available_with_import_error(self):
        """Test is_available handles import errors gracefully."""
        importer = LazyImporter("invalid.module.name", "Invalid")
        
        # Should return False, not raise
        available = importer.is_available()
        assert available is False
