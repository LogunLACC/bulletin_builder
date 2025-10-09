"""
Tests for best practices checklist module.
"""

import pytest


def test_best_practices_module_imports():
    """Test that the best_practices module can be imported."""
    from bulletin_builder.app_core import best_practices
    assert hasattr(best_practices, 'show_best_practices_checklist')
    assert hasattr(best_practices, 'BestPracticesDialog')
    assert hasattr(best_practices, 'init')


def test_best_practices_init_attaches_method():
    """Test that init attaches show_best_practices_checklist to app instance."""
    from bulletin_builder.app_core import best_practices
    
    class MockApp:
        pass
    
    app = MockApp()
    best_practices.init(app)
    
    assert hasattr(app, 'show_best_practices_checklist')
    assert callable(app.show_best_practices_checklist)


def test_best_practices_has_categories():
    """Test that BestPracticesDialog has defined practice categories."""
    from bulletin_builder.app_core.best_practices import BestPracticesDialog
    
    assert hasattr(BestPracticesDialog, 'PRACTICES')
    assert isinstance(BestPracticesDialog.PRACTICES, list)
    assert len(BestPracticesDialog.PRACTICES) > 0
    
    # Check structure
    for practice_group in BestPracticesDialog.PRACTICES:
        assert 'category' in practice_group
        assert 'items' in practice_group
        assert isinstance(practice_group['items'], list)
        assert len(practice_group['items']) > 0


def test_best_practices_categories_comprehensive():
    """Test that the checklist covers important categories."""
    from bulletin_builder.app_core.best_practices import BestPracticesDialog
    
    categories = [p['category'] for p in BestPracticesDialog.PRACTICES]
    
    # Should have key categories
    assert any('content' in c.lower() for c in categories)
    assert any('design' in c.lower() or 'layout' in c.lower() for c in categories)
    assert any('technical' in c.lower() for c in categories)
    assert any('send' in c.lower() or 'before' in c.lower() for c in categories)


def test_best_practices_items_not_empty():
    """Test that all practice items have text."""
    from bulletin_builder.app_core.best_practices import BestPracticesDialog
    
    for practice_group in BestPracticesDialog.PRACTICES:
        for item in practice_group['items']:
            assert isinstance(item, str)
            assert len(item) > 0
            assert len(item) < 200  # Reasonable length


def test_best_practices_covers_key_topics():
    """Test that the checklist covers important email best practices."""
    from bulletin_builder.app_core.best_practices import BestPracticesDialog
    
    # Flatten all items
    all_items = []
    for group in BestPracticesDialog.PRACTICES:
        all_items.extend(group['items'])
    
    all_text = ' '.join(all_items).lower()
    
    # Key topics to cover
    assert 'alt' in all_text or 'image' in all_text  # Image accessibility
    assert 'subject' in all_text  # Subject line
    assert 'spam' in all_text  # Spam awareness
    assert 'test' in all_text  # Testing
    assert 'link' in all_text  # Link checking
    assert 'mobile' in all_text or 'viewport' in all_text  # Mobile-friendly


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
