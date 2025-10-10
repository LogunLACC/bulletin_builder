"""Command Line Interface for Bulletin Builder"""
import argparse
import sys
from pathlib import Path


def validate_config_command(config_path: str = "config.ini") -> int:
    """
    Validate configuration file and report issues.
    
    Args:
        config_path: Path to config.ini file
        
    Returns:
        Exit code: 0 if valid, 1 if errors found, 2 if file missing
    """
    from .app_core.settings_manager import ConfigManager
    import logging
    
    # Setup logging for validation output
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    config_file = Path(config_path)
    
    # Check if config file exists
    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_path}")
        print(f"\nExpected location: {config_file.absolute()}")
        print("\nTo create a default config file, run the application once with --gui")
        return 2
    
    print(f"📋 Validating configuration: {config_path}")
    print("=" * 60)
    
    try:
        # Load configuration
        manager = ConfigManager(config_path)
        settings = manager.load()
        
        print(f"✓ Configuration file loaded successfully")
        print(f"✓ Config version: {manager._get_config_version_from_file()}")
        print()
        
        # Validate configuration
        issues = manager.validate()
        
        if not issues:
            print("✅ Configuration is valid!")
            print("\nAll settings have been validated:")
            print(f"  • SMTP: {'✓ Configured' if settings.smtp.is_configured() else '⚠ Not configured'}")
            print(f"  • Google API: {'✓ Configured' if settings.api_keys.has_google() else '⚠ Not configured'}")
            print(f"  • OpenAI API: {'✓ Configured' if settings.api_keys.has_openai() else '⚠ Not configured'}")
            print(f"  • Events Feed: {'✓ Configured' if settings.events.has_feed_url() else '⚠ Not configured'}")
            return 0
        
        # Separate errors and warnings
        errors = [(sev, msg) for sev, msg in issues if sev == "ERROR"]
        warnings = [(sev, msg) for sev, msg in issues if sev == "WARNING"]
        
        # Display errors
        if errors:
            print(f"❌ Found {len(errors)} error(s):\n")
            for i, (sev, msg) in enumerate(errors, 1):
                print(f"  {i}. {msg}")
            print()
        
        # Display warnings
        if warnings:
            print(f"⚠️  Found {len(warnings)} warning(s):\n")
            for i, (sev, msg) in enumerate(warnings, 1):
                print(f"  {i}. {msg}")
            print()
        
        # Summary
        if errors:
            print("❌ Configuration has errors that must be fixed.")
            print(f"\nEdit {config_path} and run validation again.")
            return 1
        else:
            print("✅ Configuration is valid (warnings can be ignored).")
            return 0
            
    except Exception as e:
        print(f"❌ Failed to validate configuration: {e}")
        return 1


def main():
    """Main CLI entry point for Bulletin Builder"""
    parser = argparse.ArgumentParser(
        description="LACC Bulletin Builder - Smart desktop builder for community email bulletins",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  bulletin --gui                    # Launch the graphical editor\n"
            "  bulletin --validate-config        # Check config.ini for errors\n"
            "  bulletin --validate-config path/to/config.ini  # Validate specific config\n"
        ),
    )

    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the WYSIWYG graphical editor",
    )

    parser.add_argument(
        "--validate-config",
        nargs="?",
        const="config.ini",
        metavar="CONFIG_PATH",
        help="Validate configuration file (default: config.ini)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Bulletin Builder 0.1.0",
    )

    args = parser.parse_args()

    if args.validate_config is not None:
        exit_code = validate_config_command(args.validate_config)
        sys.exit(exit_code)
    elif args.gui:
        try:
            from .__main__ import run_gui
            run_gui()
        except ImportError as e:
            print(f"Error launching GUI: {e}")
            print("Make sure all dependencies are installed.")
            sys.exit(1)
    else:
        print("Bulletin Builder CLI")
        print("Use 'bulletin --gui' to launch the graphical editor")
        print("Use 'bulletin --validate-config' to check your configuration")
        print("Use 'bulletin --help' for more options")


if __name__ == "__main__":
    main()
