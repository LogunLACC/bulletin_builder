#!/usr/bin/env python3
"""
Debug script to identify the source of repeated popups in Bulletin Builder.
"""

import sys
import os
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test basic imports without GUI."""
    print("Testing basic imports...")
    try:
        print("✓ bulletin_builder imported")
    except Exception as e:
        print(f"✗ bulletin_builder import failed: {e}")
        traceback.print_exc()
        return False

    try:
        print("✓ config module imported")
    except Exception as e:
        print(f"✗ config import failed: {e}")
        traceback.print_exc()
        return False

    try:
        print("✓ config functions imported")
    except Exception as e:
        print(f"✗ config functions import failed: {e}")
        traceback.print_exc()
        return False

    return True

def test_config_loading():
    """Test configuration loading."""
    print("\nTesting configuration loading...")
    try:
        from bulletin_builder.app_core.config import load_api_key, load_openai_key, load_events_feed_url

        google_key = load_api_key()
        openai_key = load_openai_key()
        events_url = load_events_feed_url()

        print(f"✓ Google API key loaded: {'Yes' if google_key else 'No'}")
        print(f"✓ OpenAI API key loaded: {'Yes' if openai_key else 'No'}")
        print(f"✓ Events URL loaded: {'Yes' if events_url else 'No'}")

        if events_url:
            print(f"  Events URL: {events_url}")

    except Exception as e:
        print(f"✗ Config loading failed: {e}")
        traceback.print_exc()
        return False

    return True

def test_template_loading():
    """Test template loading."""
    print("\nTesting template loading...")
    try:
        from pathlib import Path
        template_dir = Path(__file__).parent / "templates"
        main_layout = template_dir / "main_layout.html"

        if main_layout.exists():
            print("✓ main_layout.html exists")
        else:
            print("✗ main_layout.html not found")
            return False

    except Exception as e:
        print(f"✗ Template loading test failed: {e}")
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    print("Bulletin Builder Debug Script")
    print("=" * 40)

    success = True
    success &= test_imports()
    success &= test_config_loading()
    success &= test_template_loading()

    if success:
        print("\n✓ All basic tests passed")
    else:
        print("\n✗ Some tests failed")
