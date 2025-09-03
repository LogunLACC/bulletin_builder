#!/usr/bin/env python3
"""
Step-by-step Bulletin Builder initialization test.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import customtkinter as ctk
import pytest

def test_step_by_step():
    """Test app initialization step by step."""
    print("Step-by-step Bulletin Builder initialization test")
    print("=" * 50)

    try:
        # Step 1: Basic app creation
        print("Step 1: Creating basic app...")
        try:
            app = ctk.CTk()
        except Exception as e:
            pytest.skip(f"Tk not available: {e}")
        app.title("Test Bulletin Builder")
        app.geometry("400x200")
        print("âœ“ Basic app created")

        # Step 2: Try core_init
        print("Step 2: Loading core_init...")
        from bulletin_builder.app_core.core_init import init as core_init
        core_init(app)
        print("âœ“ core_init loaded")

        # Step 3: Try handlers
        print("Step 3: Loading handlers...")
        from bulletin_builder.app_core.handlers import init as handlers_init
        handlers_init(app)
        print("âœ“ handlers loaded")

        # Step 4: Try drafts
        print("Step 4: Loading drafts...")
        from bulletin_builder.app_core.drafts import init as drafts_init
        drafts_init(app)
        print("âœ“ drafts loaded")

        # Step 5: Try sections
        print("Step 5: Loading sections...")
        from bulletin_builder.app_core.sections import init as sections_init
        sections_init(app)
        print("âœ“ sections loaded")

        print("\nâœ“ All modules loaded successfully")
        print("If popups appeared, they happened during one of these steps")

        # Close the app
        app.quit()
        assert True

    except Exception as e:
        print(f"âœ— Error during step-by-step initialization: {e}")
        import traceback
        traceback.print_exc()
        assert False

if __name__ == "__main__":
    success = test_step_by_step()

    if success:
        print("\nâœ“ Step-by-step test completed")
    else:
        print("\nâœ— Step-by-step test failed")
