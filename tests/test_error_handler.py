"""
Tests for the error handling system.
"""

import pytest
from pathlib import Path
from bulletin_builder.app_core.error_handler import ErrorAnalyzer
from bulletin_builder.ui.error_dialog import ErrorCategory, ErrorSeverity


class TestErrorAnalyzer:
    """Test the ErrorAnalyzer class."""
    
    def test_file_not_found_analysis(self):
        """Test analysis of FileNotFoundError."""
        error = FileNotFoundError("No such file or directory: 'test.json'")
        category, severity, suggestions = ErrorAnalyzer.analyze_exception(error)
        
        assert category == ErrorCategory.FILE_IO
        assert severity == ErrorSeverity.ERROR
        assert len(suggestions) > 0
        assert any("file path" in s.lower() for s in suggestions)
    
    def test_permission_error_analysis(self):
        """Test analysis of PermissionError."""
        error = PermissionError("Permission denied")
        category, severity, suggestions = ErrorAnalyzer.analyze_exception(error)
        
        assert category == ErrorCategory.PERMISSION
        assert severity == ErrorSeverity.ERROR
        assert len(suggestions) > 0
        assert any("permission" in s.lower() for s in suggestions)
    
    def test_json_decode_error_analysis(self):
        """Test analysis of JSON errors."""
        import json
        error = json.JSONDecodeError("Expecting value", "test", 0)
        category, severity, suggestions = ErrorAnalyzer.analyze_exception(error)
        
        assert category == ErrorCategory.IMPORT
        assert severity == ErrorSeverity.ERROR
        assert len(suggestions) > 0
        assert any("json" in s.lower() for s in suggestions)
    
    def test_network_error_analysis(self):
        """Test analysis of network errors."""
        error = ConnectionError("Connection timeout")
        category, severity, suggestions = ErrorAnalyzer.analyze_exception(error)
        
        assert category == ErrorCategory.NETWORK
        assert severity == ErrorSeverity.WARNING
        assert len(suggestions) > 0
        assert any("connection" in s.lower() or "network" in s.lower() for s in suggestions)
    
    def test_memory_error_analysis(self):
        """Test analysis of memory errors."""
        error = MemoryError("Out of memory")
        category, severity, suggestions = ErrorAnalyzer.analyze_exception(error)
        
        assert category == ErrorCategory.UNKNOWN
        assert severity == ErrorSeverity.CRITICAL
        assert len(suggestions) > 0
        assert any("memory" in s.lower() for s in suggestions)
    
    def test_generic_error_analysis(self):
        """Test analysis of generic errors."""
        error = RuntimeError("Something went wrong")
        category, severity, suggestions = ErrorAnalyzer.analyze_exception(error)
        
        assert category == ErrorCategory.UNKNOWN
        assert severity == ErrorSeverity.ERROR
        assert len(suggestions) > 0
    
    def test_format_traceback(self):
        """Test traceback formatting."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            tb = ErrorAnalyzer.format_traceback(e)
            
            assert "ValueError" in tb
            assert "Test error" in tb
            assert "Traceback" in tb or "ValueError:" in tb
    
    def test_user_friendly_message(self):
        """Test user-friendly message generation."""
        error = FileNotFoundError("[Errno 2] No such file or directory: 'test.json'")
        message = ErrorAnalyzer.get_user_friendly_message(error, "opening file")
        
        assert "opening file" in message.lower()
        assert "test.json" in message
        assert "[Errno" not in message  # Should be cleaned up
    
    def test_user_friendly_message_length_limit(self):
        """Test that long messages are truncated."""
        long_message = "x" * 300
        error = ValueError(long_message)
        message = ErrorAnalyzer.get_user_friendly_message(error)
        
        assert len(message) <= 200
        assert message.endswith("...")
    
    def test_context_specific_suggestions(self):
        """Test that context affects suggestions."""
        error = FileNotFoundError("test.json")
        
        category1, _, suggestions1 = ErrorAnalyzer.analyze_exception(error, "opening draft")
        category2, _, suggestions2 = ErrorAnalyzer.analyze_exception(error, "importing CSV")
        
        # Both should be file I/O errors
        assert category1 == ErrorCategory.FILE_IO
        assert category2 == ErrorCategory.FILE_IO
        
        # Should have suggestions
        assert len(suggestions1) > 0
        assert len(suggestions2) > 0
    
    def test_validation_error_analysis(self):
        """Test analysis of validation errors."""
        error = ValueError("Invalid email format")
        category, severity, suggestions = ErrorAnalyzer.analyze_exception(error)
        
        assert category == ErrorCategory.VALIDATION
        assert severity == ErrorSeverity.WARNING
        assert len(suggestions) > 0
    
    def test_export_error_analysis(self):
        """Test analysis of export errors."""
        error = RuntimeError("Failed to render HTML template")
        category, severity, suggestions = ErrorAnalyzer.analyze_exception(error)
        
        assert category == ErrorCategory.EXPORT
        assert severity == ErrorSeverity.ERROR
        assert len(suggestions) > 0
        assert any("template" in s.lower() or "html" in s.lower() for s in suggestions)
    
    def test_http_401_analysis(self):
        """Test analysis of 401 unauthorized errors."""
        error = RuntimeError("HTTP 401: Unauthorized access")
        category, severity, suggestions = ErrorAnalyzer.analyze_exception(error)
        
        assert category == ErrorCategory.CONFIGURATION
        assert severity == ErrorSeverity.ERROR
        assert len(suggestions) > 0
        assert any("api key" in s.lower() for s in suggestions)
    
    def test_http_404_analysis(self):
        """Test analysis of 404 not found errors."""
        error = RuntimeError("HTTP 404: Resource not found")
        category, severity, suggestions = ErrorAnalyzer.analyze_exception(error)
        
        assert category == ErrorCategory.NETWORK
        assert severity == ErrorSeverity.WARNING
        assert len(suggestions) > 0
        assert any("url" in s.lower() or "not found" in s.lower() for s in suggestions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
