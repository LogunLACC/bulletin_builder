"""
Tests for graceful degradation functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bulletin_builder.app_core.graceful_degradation import (
    FeatureAvailability,
    check_ai_google,
    check_ai_openai,
    check_network,
    check_pdf_export,
    fallback_ai_suggestion,
    fallback_network_operation,
    fallback_pdf_export,
    get_ai_provider,
    can_use_ai,
    can_use_network,
    can_export_pdf
)


class TestFeatureAvailability:
    """Test FeatureAvailability class."""
    
    @pytest.fixture
    def mock_app(self):
        """Create a mock application."""
        return Mock()
    
    @pytest.fixture
    def feature_tracker(self, mock_app):
        """Create a FeatureAvailability instance."""
        return FeatureAvailability(mock_app)
    
    def test_initialization(self, feature_tracker, mock_app):
        """Test FeatureAvailability initializes correctly."""
        assert feature_tracker.app == mock_app
        assert feature_tracker.features == {}
        assert feature_tracker.feature_messages == {}
        assert feature_tracker.fallback_handlers == {}
    
    def test_register_available_feature(self, feature_tracker):
        """Test registering an available feature."""
        def check_func():
            return True
        
        feature_tracker.register_feature(
            'test_feature',
            check_func,
            'Feature unavailable'
        )
        
        assert feature_tracker.is_available('test_feature') is True
        assert feature_tracker.get_message('test_feature') is None
    
    def test_register_unavailable_feature(self, feature_tracker):
        """Test registering an unavailable feature."""
        def check_func():
            return False
        
        feature_tracker.register_feature(
            'test_feature',
            check_func,
            'Feature unavailable'
        )
        
        assert feature_tracker.is_available('test_feature') is False
        assert feature_tracker.get_message('test_feature') == 'Feature unavailable'
    
    def test_register_feature_with_fallback(self, feature_tracker):
        """Test registering a feature with fallback handler."""
        def check_func():
            return False
        
        def fallback_func():
            return 'fallback result'
        
        feature_tracker.register_feature(
            'test_feature',
            check_func,
            'Feature unavailable',
            fallback_func
        )
        
        assert 'test_feature' in feature_tracker.fallback_handlers
        assert feature_tracker.fallback_handlers['test_feature']() == 'fallback result'
    
    def test_is_available_unknown_feature(self, feature_tracker):
        """Test checking availability of unknown feature."""
        assert feature_tracker.is_available('unknown') is False
    
    def test_use_feature_or_fallback_when_available(self, feature_tracker):
        """Test using feature when it's available."""
        def check_func():
            return True
        
        def primary_func(x):
            return x * 2
        
        feature_tracker.register_feature('test', check_func, 'N/A')
        
        result = feature_tracker.use_feature_or_fallback('test', primary_func, 5)
        assert result == 10
    
    def test_use_feature_or_fallback_when_unavailable(self, feature_tracker):
        """Test using fallback when feature is unavailable."""
        def check_func():
            return False
        
        def primary_func(x):
            return x * 2
        
        def fallback_func(x):
            return x + 10
        
        feature_tracker.register_feature('test', check_func, 'N/A', fallback_func)
        
        result = feature_tracker.use_feature_or_fallback('test', primary_func, 5)
        assert result == 15  # Fallback result
    
    def test_use_feature_fallback_on_error(self, feature_tracker):
        """Test using fallback when primary function raises error."""
        def check_func():
            return True  # Feature available
        
        def primary_func(x):
            raise ValueError("Test error")
        
        def fallback_func(x):
            return x + 10
        
        feature_tracker.register_feature('test', check_func, 'N/A', fallback_func)
        
        result = feature_tracker.use_feature_or_fallback('test', primary_func, 5)
        assert result == 15  # Fallback result
    
    def test_get_feature_status(self, feature_tracker):
        """Test getting feature status."""
        def check_available():
            return True
        
        def check_unavailable():
            return False
        
        def fallback():
            return None
        
        feature_tracker.register_feature('available', check_available, 'N/A')
        feature_tracker.register_feature('unavailable', check_unavailable, 'Not available', fallback)
        
        status = feature_tracker.get_feature_status()
        
        assert status['available']['available'] is True
        assert status['available']['has_fallback'] is False
        assert status['unavailable']['available'] is False
        assert status['unavailable']['message'] == 'Not available'
        assert status['unavailable']['has_fallback'] is True


class TestFeatureChecks:
    """Test feature check functions."""
    
    @patch('bulletin_builder.app_core.config.load_google_api_key')
    def test_check_ai_google_no_key(self, mock_load_key):
        """Test Google AI check with no API key."""
        mock_load_key.return_value = None
        assert check_ai_google() is False
    
    @patch('bulletin_builder.app_core.config.load_google_api_key')
    def test_check_ai_google_placeholder_key(self, mock_load_key):
        """Test Google AI check with placeholder API key."""
        mock_load_key.return_value = "your_google_api_key_here"
        assert check_ai_google() is False
    
    @patch('bulletin_builder.app_core.config.load_openai_key')
    def test_check_ai_openai_no_key(self, mock_load_key):
        """Test OpenAI check with no API key."""
        mock_load_key.return_value = None
        assert check_ai_openai() is False
    
    @patch('bulletin_builder.app_core.config.load_openai_key')
    def test_check_ai_openai_placeholder_key(self, mock_load_key):
        """Test OpenAI check with placeholder API key."""
        mock_load_key.return_value = "your_openai_api_key_here"
        assert check_ai_openai() is False
    
    @patch('socket.create_connection')
    def test_check_network_available(self, mock_connect):
        """Test network check when network is available."""
        mock_connect.return_value = Mock()
        assert check_network() is True
    
    @patch('socket.create_connection')
    def test_check_network_unavailable(self, mock_connect):
        """Test network check when network is unavailable."""
        import socket
        mock_connect.side_effect = socket.error("Network unreachable")
        assert check_network() is False
    
    def test_check_pdf_export_unavailable(self):
        """Test PDF export check when WeasyPrint not installed."""
        with patch.dict('sys.modules', {'weasyprint': None}):
            # WeasyPrint import will fail
            result = check_pdf_export()
            # Result depends on actual installation, but should not crash
            assert isinstance(result, bool)


class TestFallbackFunctions:
    """Test fallback functions."""
    
    def test_fallback_ai_suggestion(self):
        """Test AI fallback message."""
        result = fallback_ai_suggestion("test prompt")
        assert "unavailable" in result.lower()
        assert "api key" in result.lower()
    
    def test_fallback_network_operation(self):
        """Test network fallback."""
        result = fallback_network_operation("test operation")
        assert result['success'] is False
        assert result['error'] == 'Network unavailable'
        assert 'network' in result['message'].lower()
    
    def test_fallback_pdf_export(self):
        """Test PDF export fallback."""
        result = fallback_pdf_export("<html></html>", "output.pdf")
        assert result is False


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_get_ai_provider_google(self):
        """Test getting Google as AI provider."""
        app = Mock()
        app.feature_availability = Mock()
        app.feature_availability.is_available = lambda x: x == 'ai_google'
        
        assert get_ai_provider(app) == 'google'
    
    def test_get_ai_provider_openai(self):
        """Test getting OpenAI as AI provider."""
        app = Mock()
        app.feature_availability = Mock()
        app.feature_availability.is_available = lambda x: x == 'ai_openai'
        
        assert get_ai_provider(app) == 'openai'
    
    def test_get_ai_provider_none(self):
        """Test getting AI provider when none available."""
        app = Mock()
        app.feature_availability = Mock()
        app.feature_availability.is_available = lambda x: False
        
        assert get_ai_provider(app) is None
    
    def test_get_ai_provider_no_tracker(self):
        """Test getting AI provider when tracker not initialized."""
        app = Mock(spec=[])
        assert get_ai_provider(app) is None
    
    def test_can_use_ai_available(self):
        """Test can_use_ai when AI is available."""
        app = Mock()
        app.feature_availability = Mock()
        app.feature_availability.is_available = lambda x: x == 'ai_assistant'
        
        assert can_use_ai(app) is True
    
    def test_can_use_ai_unavailable(self):
        """Test can_use_ai when AI is unavailable."""
        app = Mock()
        app.feature_availability = Mock()
        app.feature_availability.is_available = lambda x: False
        
        assert can_use_ai(app) is False
    
    def test_can_use_network_available(self):
        """Test can_use_network when network is available."""
        app = Mock()
        app.feature_availability = Mock()
        app.feature_availability.is_available = lambda x: x == 'network'
        
        assert can_use_network(app) is True
    
    def test_can_use_network_unavailable(self):
        """Test can_use_network when network is unavailable."""
        app = Mock()
        app.feature_availability = Mock()
        app.feature_availability.is_available = lambda x: False
        
        assert can_use_network(app) is False
    
    def test_can_export_pdf_available(self):
        """Test can_export_pdf when PDF export is available."""
        app = Mock()
        app.feature_availability = Mock()
        app.feature_availability.is_available = lambda x: x == 'pdf_export'
        
        assert can_export_pdf(app) is True
    
    def test_can_export_pdf_unavailable(self):
        """Test can_export_pdf when PDF export is unavailable."""
        app = Mock()
        app.feature_availability = Mock()
        app.feature_availability.is_available = lambda x: False
        
        assert can_export_pdf(app) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
