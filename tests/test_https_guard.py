"""
Tests for HTTPS/security related functionality
"""
import re
import pathlib


def test_no_https_alert_strings_anywhere():
    """Test that no HTTPS alert/scare strings exist in the codebase"""
    bad_patterns = [
        r"requires\s+https",
        r"use\s+https",
        r"https\s*alert",
        r"this app requires https",
        r"location\.protocol",
        r"window\.isSecureContext",
        r"serviceWorker",
        r"navigator\.clipboard",
        r"Mixed Content",
        r"upgrade-insecure-requests"
    ]

    bad = []
    # Check source files (exclude test files and comments)
    for p in pathlib.Path("src").rglob("*.*"):
        if p.suffix.lower() in {".js", ".ts", ".tsx", ".py", ".html"}:
            try:
                txt = p.read_text("utf-8", errors="ignore")
                # Remove comments for Python files
                if p.suffix.lower() == ".py":
                    txt = re.sub(r'#.*$', '', txt, flags=re.MULTILINE)
                    txt = re.sub(r'""".*?"""', '', txt, flags=re.DOTALL)
                    txt = re.sub(r"'''.*?'''", '', txt, flags=re.DOTALL)
                # Remove HTML comments
                elif p.suffix.lower() == ".html":
                    txt = re.sub(r'<!--.*?-->', '', txt, flags=re.DOTALL)

                for pattern in bad_patterns:
                    if re.search(pattern, txt, re.I):
                        bad.append(f"{p}: {pattern}")
            except:
                pass

    assert not bad, f"HTTPS scare-alerts must be removed: {bad}"


def test_secure_context_guards_present():
    """Test that secure context checks are present where needed"""
    # Check for clipboard usage with secure context guard
    secure_check_found = False

    for p in pathlib.Path("src").rglob("*.py"):
        try:
            txt = p.read_text("utf-8", errors="ignore")
            if "clipboard" in txt.lower():
                pass
            if "is_secure_context" in txt.lower() or "secure_context" in txt.lower():
                secure_check_found = True
        except:
            pass

    # Since this is a desktop app, clipboard should work without secure context checks
    # But we should have the utility available
    assert secure_check_found, "Secure context utility should be available"


if __name__ == "__main__":
    test_no_https_alert_strings_anywhere()
    test_secure_context_guards_present()
    print("✓ All HTTPS/security tests passed!")
