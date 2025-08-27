#!/usr/bin/env python3
"""
Quick test script to verify Bulletin Builder functionality
"""
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def test_imports():
    """Test that all core modules can be imported"""
    try:
        from bulletin_builder.app_core.sanitize import sanitize_email_html
        from bulletin_builder.app_core.config import load_api_key, load_events_feed_url
        from bulletin_builder.bulletin_renderer import BulletinRenderer
        print('✓ Core modules imported successfully')
        return True
    except Exception as e:
        print(f'✗ Import error: {e}')
        return False

def test_sanitize():
    """Test the sanitize functionality"""
    try:
        from bulletin_builder.app_core.sanitize import sanitize_email_html

        test_html = '<a href="#" style="color:red;">Test</a>'
        sanitized = sanitize_email_html(test_html)
        print(f'✓ Sanitize test passed: {sanitized}')

        # Test CSS merging
        from bulletin_builder.app_core.sanitize import _prepend_rule
        result = _prepend_rule('color:red; font-size:14px', 'margin:0; padding:0')
        print(f'✓ CSS merging test: {result}')

        return True
    except Exception as e:
        print(f'✗ Sanitize error: {e}')
        return False

def test_config():
    """Test configuration loading"""
    try:
        from bulletin_builder.app_core.config import load_api_key, load_events_feed_url
        api_key = load_api_key()
        events_url = load_events_feed_url()
        print('✓ Configuration loaded successfully')
        return True
    except Exception as e:
        print(f'✗ Config error: {e}')
        return False

def main():
    """Run all tests"""
    print("Running Bulletin Builder tests...")
    print("=" * 40)

    tests = [
        ("Import Test", test_imports),
        ("Sanitize Test", test_sanitize),
        ("Config Test", test_config)
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"\n{name}:")
        if test_func():
            passed += 1

    print("\n" + "=" * 40)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Bulletin Builder is working correctly.")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())</content>
<parameter name="filePath">c:\Users\LogunJohnston\OneDrive - Lake Almanor\Documents\MyPy\GitHub\lacc-dev\Bulletin Builder\test_run.py
