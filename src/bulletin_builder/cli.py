"""
Command Line Interface for Bulletin Builder
"""
import argparse
import sys

def main():
    """Main CLI entry point for Bulletin Builder"""
    parser = argparse.ArgumentParser(
        description="LACC Bulletin Builder - Smart desktop builder for community email bulletins",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bulletin --gui          # Launch the graphical editor
  bulletin                # Show CLI help
        """
    )

    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the WYSIWYG graphical editor"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Bulletin Builder 0.1.0"
    )

    args = parser.parse_args()

    if args.gui:
        print("📰 Launching Bulletin Builder GUI...")
        try:
            from .wysiwyg_editor import launch_gui
            launch_gui()
        except ImportError as e:
            print(f"❌ Error launching GUI: {e}")
            print("Make sure all dependencies are installed.")
            sys.exit(1)
    else:
        print("📰 Bulletin Builder CLI")
        print("Use 'bulletin --gui' to launch the graphical editor")
        print("Use 'bulletin --help' for more options")


if __name__ == "__main__":
    main()
