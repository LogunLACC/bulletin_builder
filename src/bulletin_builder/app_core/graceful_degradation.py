"""
Graceful Degradation System for Bulletin Builder.

Provides feature detection and fallback mechanisms for optional features
like AI assistants, network operations, and analytics, ensuring the app
continues to function even when these features are unavailable.
"""

import os
from typing import Dict, Optional, Callable, Any
from pathlib import Path
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)


class FeatureAvailability:
    """
    Tracks availability of optional features and provides fallback mechanisms.
    
    Features are checked at startup and during runtime, with clear messaging
    when features are unavailable.
    """
    
    def __init__(self, app):
        """
        Initialize feature availability tracking.
        
        Args:
            app: Main application instance
        """
        self.app = app
        self.features: Dict[str, bool] = {}
        self.feature_messages: Dict[str, str] = {}
        self.fallback_handlers: Dict[str, Callable] = {}
        
        logger.info("FeatureAvailability initialized")
    
    def register_feature(self, feature_name: str, 
                        check_func: Callable[[], bool],
                        unavailable_message: str,
                        fallback: Optional[Callable] = None) -> None:
        """
        Register a feature with availability checking.
        
        Args:
            feature_name: Name of the feature (e.g., 'ai_assistant', 'network')
            check_func: Function that returns True if feature is available
            unavailable_message: Message to show when feature is unavailable
            fallback: Optional fallback function to use when feature unavailable
        """
        try:
            is_available = check_func()
            self.features[feature_name] = is_available
            
            if not is_available:
                self.feature_messages[feature_name] = unavailable_message
                logger.warning(f"Feature '{feature_name}' unavailable: {unavailable_message}")
            else:
                logger.info(f"Feature '{feature_name}' available")
            
            if fallback:
                self.fallback_handlers[feature_name] = fallback
                
        except Exception as e:
            logger.error(f"Error checking feature '{feature_name}': {e}")
            self.features[feature_name] = False
            self.feature_messages[feature_name] = f"Error checking feature: {str(e)}"
    
    def is_available(self, feature_name: str) -> bool:
        """
        Check if a feature is available.
        
        Args:
            feature_name: Name of the feature to check
        
        Returns:
            True if feature is available, False otherwise
        """
        return self.features.get(feature_name, False)
    
    def get_message(self, feature_name: str) -> Optional[str]:
        """
        Get the unavailability message for a feature.
        
        Args:
            feature_name: Name of the feature
        
        Returns:
            Unavailability message or None if feature is available
        """
        return self.feature_messages.get(feature_name)
    
    def use_feature_or_fallback(self, feature_name: str, 
                                primary_func: Callable,
                                *args, **kwargs) -> Any:
        """
        Use a feature if available, otherwise use fallback.
        
        Args:
            feature_name: Name of the feature
            primary_func: Function to call if feature is available
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
        
        Returns:
            Result from primary function or fallback
        """
        if self.is_available(feature_name):
            try:
                return primary_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error using feature '{feature_name}': {e}")
                # Fall through to fallback
        
        # Use fallback if available
        if feature_name in self.fallback_handlers:
            logger.info(f"Using fallback for '{feature_name}'")
            try:
                return self.fallback_handlers[feature_name](*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in fallback for '{feature_name}': {e}")
                return None
        
        logger.warning(f"No fallback available for '{feature_name}'")
        return None
    
    def get_feature_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all features.
        
        Returns:
            Dictionary with feature status information
        """
        status = {}
        for feature_name, available in self.features.items():
            status[feature_name] = {
                'available': available,
                'message': self.get_message(feature_name),
                'has_fallback': feature_name in self.fallback_handlers
            }
        return status


def check_ai_google() -> bool:
    """Check if Google AI (Gemini) is available."""
    try:
        # Check for API key
        from bulletin_builder.app_core.config import load_google_api_key
        api_key = load_google_api_key()
        
        if not api_key or api_key == "your_google_api_key_here":
            return False
        
        # Check if library is available (use non-importing check)
        from bulletin_builder.app_core.lazy_imports import is_gemini_available
        return is_gemini_available()
            
    except Exception as e:
        logger.debug(f"Google AI check failed: {e}")
        return False


def check_ai_openai() -> bool:
    """Check if OpenAI is available."""
    try:
        # Check for API key
        from bulletin_builder.app_core.config import load_openai_key
        api_key = load_openai_key()
        
        if not api_key or api_key == "your_openai_api_key_here":
            return False
        
        # Check if library is available (use non-importing check)
        from bulletin_builder.app_core.lazy_imports import is_openai_available
        return is_openai_available()
            
    except Exception as e:
        logger.debug(f"OpenAI check failed: {e}")
        return False


def check_network() -> bool:
    """Check if network connectivity is available."""
    try:
        import socket
        
        # Try to connect to a reliable host (Google DNS)
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except (socket.error, socket.timeout):
        return False
    except Exception as e:
        logger.debug(f"Network check failed: {e}")
        return False


def check_pdf_export() -> bool:
    """Check if PDF export (WeasyPrint) is available."""
    try:
        from bulletin_builder.app_core.lazy_imports import is_weasyprint_available
        return is_weasyprint_available()
    except Exception as e:
        logger.debug(f"PDF export check failed: {e}")
        return False


def fallback_ai_suggestion(prompt: str) -> str:
    """
    Fallback for AI suggestions when AI is unavailable.
    
    Args:
        prompt: The prompt (ignored in fallback)
    
    Returns:
        Helpful message about AI unavailability
    """
    return ("AI assistant is currently unavailable. "
            "Please configure your API key in Settings → AI Assistant, "
            "or write your content manually.")


def fallback_network_operation(operation: str) -> Dict[str, Any]:
    """
    Fallback for network operations when network is unavailable.
    
    Args:
        operation: Description of the operation
    
    Returns:
        Dictionary with error information
    """
    return {
        'success': False,
        'error': 'Network unavailable',
        'message': 'Cannot connect to the internet. Please check your network connection.',
        'cached': False
    }


def fallback_pdf_export(html_content: str, output_path: str) -> bool:
    """
    Fallback for PDF export when WeasyPrint is unavailable.
    
    Args:
        html_content: HTML content to export
        output_path: Path where PDF would be saved
    
    Returns:
        False (export failed)
    """
    logger.warning("PDF export unavailable - WeasyPrint not installed")
    return False


def init(app) -> None:
    """
    Initialize graceful degradation system.
    
    Args:
        app: Main application instance
    """
    try:
        # Create feature availability tracker
        feature_tracker = FeatureAvailability(app)
        app.feature_availability = feature_tracker
        
        # Register AI features
        feature_tracker.register_feature(
            'ai_google',
            check_ai_google,
            "Google AI (Gemini) is unavailable. Configure your API key in Settings to enable AI features.",
            fallback_ai_suggestion
        )
        
        feature_tracker.register_feature(
            'ai_openai',
            check_ai_openai,
            "OpenAI is unavailable. Configure your API key in Settings to enable AI features.",
            fallback_ai_suggestion
        )
        
        # Check if at least one AI provider is available
        has_ai = feature_tracker.is_available('ai_google') or feature_tracker.is_available('ai_openai')
        feature_tracker.features['ai_assistant'] = has_ai
        
        if not has_ai:
            feature_tracker.feature_messages['ai_assistant'] = (
                "AI assistant is unavailable. Configure an API key (Google or OpenAI) in Settings to enable AI features."
            )
            logger.info("AI assistant unavailable - no API keys configured")
        else:
            logger.info("AI assistant available")
        
        # Register network feature
        feature_tracker.register_feature(
            'network',
            check_network,
            "Network connection unavailable. Some features (events feed, online images) may not work.",
            fallback_network_operation
        )
        
        # Register PDF export feature
        feature_tracker.register_feature(
            'pdf_export',
            check_pdf_export,
            "PDF export unavailable. Install WeasyPrint to enable PDF export: pip install weasyprint",
            fallback_pdf_export
        )
        
        # Log feature status
        status = feature_tracker.get_feature_status()
        available_features = [name for name, info in status.items() if info['available']]
        unavailable_features = [name for name, info in status.items() if not info['available']]
        
        logger.info(f"Available features: {', '.join(available_features) if available_features else 'none'}")
        if unavailable_features:
            logger.info(f"Unavailable features: {', '.join(unavailable_features)}")
        
        # Show status message if any features are unavailable
        if unavailable_features and hasattr(app, 'show_status_message'):
            count = len(unavailable_features)
            app.show_status_message(
                f"{count} optional feature{'s' if count > 1 else ''} unavailable. Check Settings for details.",
                duration_ms=5000
            )
        
        logger.info("Graceful degradation system initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize graceful degradation system: {e}")
        # Continue anyway - graceful degradation is optional


def get_ai_provider(app) -> Optional[str]:
    """
    Get the name of an available AI provider.
    
    Args:
        app: Application instance
    
    Returns:
        'google' or 'openai' if available, None otherwise
    """
    if not hasattr(app, 'feature_availability'):
        return None
    
    if app.feature_availability.is_available('ai_google'):
        return 'google'
    elif app.feature_availability.is_available('ai_openai'):
        return 'openai'
    
    return None


def can_use_ai(app) -> bool:
    """
    Check if AI features can be used.
    
    Args:
        app: Application instance
    
    Returns:
        True if at least one AI provider is available
    """
    return hasattr(app, 'feature_availability') and app.feature_availability.is_available('ai_assistant')


def can_use_network(app) -> bool:
    """
    Check if network features can be used.
    
    Args:
        app: Application instance
    
    Returns:
        True if network is available
    """
    return hasattr(app, 'feature_availability') and app.feature_availability.is_available('network')


def can_export_pdf(app) -> bool:
    """
    Check if PDF export is available.
    
    Args:
        app: Application instance
    
    Returns:
        True if PDF export is available
    """
    return hasattr(app, 'feature_availability') and app.feature_availability.is_available('pdf_export')
