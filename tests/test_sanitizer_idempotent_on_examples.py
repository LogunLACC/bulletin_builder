"""Test sanitizer idempotence on gold fixture examples."""

import os
from bulletin_builder.app_core.sanitize import sanitize_email_html


def test_sanitize_idempotent_on_fixture_1():
    """Test that sanitizer is idempotent on fixture 1."""
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'correct', '1.html')
    with open(fixture_path, 'r', encoding='utf-8') as f:
        original_html = f.read()

    # Apply sanitization
    sanitized = sanitize_email_html(original_html)

    # Apply sanitization again - should be identical (idempotent)
    sanitized_again = sanitize_email_html(sanitized)

    # The sanitizer should produce consistent output
    assert sanitized == sanitized_again, "Sanitizer is not idempotent on fixture 1"


def test_sanitize_idempotent_on_fixture_2():
    """Test that sanitizer is idempotent on fixture 2."""
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'correct', '2.html')
    with open(fixture_path, 'r', encoding='utf-8') as f:
        original_html = f.read()

    # Apply sanitization
    sanitized = sanitize_email_html(original_html)

    # Apply sanitization again - should be identical (idempotent)
    sanitized_again = sanitize_email_html(sanitized)

    # The sanitizer should produce consistent output
    assert sanitized == sanitized_again, "Sanitizer is not idempotent on fixture 2"


def test_sanitize_idempotent_on_fixture_3():
    """Test that sanitizer is idempotent on fixture 3."""
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'correct', '3.html')
    with open(fixture_path, 'r', encoding='utf-8') as f:
        original_html = f.read()

    # Apply sanitization
    sanitized = sanitize_email_html(original_html)

    # Apply sanitization again - should be identical (idempotent)
    sanitized_again = sanitize_email_html(sanitized)

    # The sanitizer should produce consistent output
    assert sanitized == sanitized_again, "Sanitizer is not idempotent on fixture 3"


def test_sanitize_preserves_fixture_content():
    """Test that sanitizer preserves the core content of fixtures."""
    for fixture_num in [1, 2, 3]:
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'correct', f'{fixture_num}.html')
        with open(fixture_path, 'r', encoding='utf-8') as f:
            original_html = f.read()

        # Apply sanitization
        sanitized = sanitize_email_html(original_html)

        # Check that core structural elements are preserved
        # (This is a basic check - in practice you'd want more specific assertions)
        assert len(sanitized) > 0, f"Sanitized fixture {fixture_num} should not be empty"
        assert '<table' in sanitized, f"Fixture {fixture_num} should contain tables"
        assert '<td' in sanitized, f"Fixture {fixture_num} should contain table cells"
