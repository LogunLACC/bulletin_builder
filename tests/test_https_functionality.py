#!/usr/bin/env python3
"""
Test script for HTTPS/security functionality
"""
import sys

# Add src to path
sys.path.insert(0, 'src')

def test_functionality():
    """Test that all HTTPS/security functionality works"""
    try:
        # Import new modules
        from bulletin_builder.app_core.url_upgrade import upgrade_http_to_https, is_secure_context
        print('âœ“ All modules imported successfully')

        # Test URL upgrade functionality
        test_html = '<img src="http://lakealmanorcountryclub.com/test.jpg">'
        upgraded = upgrade_http_to_https(test_html)
        print(f'âœ“ URL upgrade works: {upgraded}')

        # Test secure context
        secure = is_secure_context()
        print(f'âœ“ Secure context check: {secure}')

        # Test that upgraded URL is HTTPS
        if 'https://lakealmanorcountryclub.com/test.jpg' in upgraded:
            print('âœ“ HTTP to HTTPS upgrade working correctly')
        else:
            print('âœ— HTTP to HTTPS upgrade failed')
            assert False

        print('âœ“ All HTTPS/security functionality working correctly!')
        assert True

    except Exception as e:
        print(f'âœ— Error: {e}')
        import traceback
        traceback.print_exc()
        assert False

if __name__ == "__main__":
    success = test_functionality()
    sys.exit(0 if success else 1)
