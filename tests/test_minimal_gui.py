#!/usr/bin/env python3
"""
Minimal Bulletin Builder test to isolate the popup issue.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import customtkinter as ctk
import pytest

def test_minimal_gui():
    """Test minimal GUI without full app initialization."""
    print("Testing minimal GUI...")

    try:
        # Set appearance
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Create root window (skip if Tk not available)
        try:
            root = ctk.CTk()
        except Exception as e:
            pytest.skip(f"Tk not available: {e}")
        root.title("Minimal Bulletin Builder Test")
        root.geometry("400x200")

        # Add a simple label
        label = ctk.CTkLabel(root, text="If you see this, basic GUI works!")
        label.pack(pady=20)

        # Add a button to close
        button = ctk.CTkButton(root, text="Close", command=root.quit)
        button.pack(pady=10)

        print("âœ“ Minimal GUI created successfully")
        print("âœ“ No popups should appear")
        print("Close the window to continue...")

        # Run the GUI (this will block until window is closed)
        root.mainloop()

        print("âœ“ GUI closed successfully")
        assert True

    except Exception as e:
        print(f"âœ— Minimal GUI failed: {e}")
        import traceback
        traceback.print_exc()
        assert False

if __name__ == "__main__":
    print("Minimal Bulletin Builder GUI Test")
    print("=" * 40)

    success = test_minimal_gui()

    if success:
        print("\nâœ“ Basic GUI test passed - issue is in app initialization")
    else:
        print("\nâœ— Basic GUI test failed - issue is in GUI setup")
