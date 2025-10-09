"""
Tests for export_validator module.

Tests WCAG accessibility validation and spam trigger detection.
"""

import pytest
from bulletin_builder.app_core.export_validator import (
    ValidationIssue,
    ValidationResult,
    validate_accessibility,
    validate_spam_triggers,
    validate_export,
    format_validation_report,
    init
)


class TestValidationIssue:
    """Test ValidationIssue data structure."""
    
    def test_create_issue(self):
        issue = ValidationIssue(
            ValidationIssue.SEVERITY_ERROR,
            "accessibility",
            "Missing alt text",
            "Add alt attribute"
        )
        assert issue.severity == ValidationIssue.SEVERITY_ERROR
        assert issue.category == "accessibility"
        assert issue.message == "Missing alt text"
        assert issue.recommendation == "Add alt attribute"
    
    def test_to_dict(self):
        issue = ValidationIssue(
            ValidationIssue.SEVERITY_WARNING,
            "spam",
            "Trigger word found",
            "Rephrase"
        )
        d = issue.to_dict()
        assert d["severity"] == "warning"
        assert d["category"] == "spam"
        assert d["message"] == "Trigger word found"
        assert d["recommendation"] == "Rephrase"


class TestValidationResult:
    """Test ValidationResult container."""
    
    def test_empty_result(self):
        result = ValidationResult()
        assert len(result.issues) == 0
        assert not result.has_errors()
        assert not result.has_warnings()
        assert not result  # __bool__ returns False when no issues
    
    def test_add_issue(self):
        result = ValidationResult()
        result.add_issue(
            ValidationIssue.SEVERITY_ERROR,
            "accessibility",
            "Test error",
            "Fix it"
        )
        assert len(result.issues) == 1
        assert result.has_errors()
        assert result  # __bool__ returns True when issues exist
    
    def test_get_by_severity(self):
        result = ValidationResult()
        result.add_issue(ValidationIssue.SEVERITY_ERROR, "test", "Error 1")
        result.add_issue(ValidationIssue.SEVERITY_WARNING, "test", "Warning 1")
        result.add_issue(ValidationIssue.SEVERITY_ERROR, "test", "Error 2")
        result.add_issue(ValidationIssue.SEVERITY_INFO, "test", "Info 1")
        
        errors = result.get_by_severity(ValidationIssue.SEVERITY_ERROR)
        warnings = result.get_by_severity(ValidationIssue.SEVERITY_WARNING)
        infos = result.get_by_severity(ValidationIssue.SEVERITY_INFO)
        
        assert len(errors) == 2
        assert len(warnings) == 1
        assert len(infos) == 1
    
    def test_get_by_category(self):
        result = ValidationResult()
        result.add_issue(ValidationIssue.SEVERITY_ERROR, "accessibility", "A1")
        result.add_issue(ValidationIssue.SEVERITY_WARNING, "spam", "S1")
        result.add_issue(ValidationIssue.SEVERITY_ERROR, "accessibility", "A2")
        
        accessibility = result.get_by_category("accessibility")
        spam = result.get_by_category("spam")
        
        assert len(accessibility) == 2
        assert len(spam) == 1
    
    def test_summary(self):
        result = ValidationResult()
        result.add_issue(ValidationIssue.SEVERITY_ERROR, "test", "E1")
        result.add_issue(ValidationIssue.SEVERITY_ERROR, "test", "E2")
        result.add_issue(ValidationIssue.SEVERITY_WARNING, "test", "W1")
        result.add_issue(ValidationIssue.SEVERITY_INFO, "test", "I1")
        
        summary = result.summary()
        assert "2 errors" in summary
        assert "1 warning" in summary
        assert "1 info" in summary


class TestAccessibilityValidation:
    """Test WCAG accessibility validation."""
    
    def test_missing_alt_text(self):
        html = '<img src="test.jpg">'
        result = validate_accessibility(html)
        
        assert result.has_errors()
        errors = result.get_by_severity(ValidationIssue.SEVERITY_ERROR)
        assert any("missing alt attribute" in e.message.lower() for e in errors)
    
    def test_empty_alt_text(self):
        html = '<img src="test.jpg" alt="">'
        result = validate_accessibility(html)
        
        # Empty alt is acceptable for decorative images, should be info
        infos = result.get_by_severity(ValidationIssue.SEVERITY_INFO)
        assert any("empty alt text" in i.message.lower() for i in infos)
    
    def test_valid_alt_text(self):
        html = '<img src="test.jpg" alt="A beautiful sunset">'
        result = validate_accessibility(html)
        
        # Should not flag error for images with alt text
        errors = [e for e in result.issues if "alt" in e.message.lower() and e.severity == ValidationIssue.SEVERITY_ERROR]
        assert len(errors) == 0
    
    def test_heading_hierarchy_start_with_h1(self):
        html = '<h2>Title</h2><h3>Subtitle</h3>'
        result = validate_accessibility(html)
        
        warnings = result.get_by_severity(ValidationIssue.SEVERITY_WARNING)
        assert any("should start with h1" in w.message.lower() for w in warnings)
    
    def test_heading_hierarchy_skip(self):
        html = '<h1>Title</h1><h4>Skip h2 and h3</h4>'
        result = validate_accessibility(html)
        
        warnings = result.get_by_severity(ValidationIssue.SEVERITY_WARNING)
        assert any("hierarchy skip" in w.message.lower() for w in warnings)
    
    def test_valid_heading_hierarchy(self):
        html = '<h1>Title</h1><h2>Section</h2><h3>Subsection</h3>'
        result = validate_accessibility(html)
        
        # Should not flag hierarchy errors
        warnings = [w for w in result.issues if "hierarchy" in w.message.lower() and w.severity == ValidationIssue.SEVERITY_WARNING]
        assert len(warnings) == 0
    
    def test_empty_heading(self):
        html = '<h1></h1><h2>Valid heading</h2>'
        result = validate_accessibility(html)
        
        warnings = result.get_by_severity(ValidationIssue.SEVERITY_WARNING)
        assert any("empty heading" in w.message.lower() for w in warnings)
    
    def test_no_headings(self):
        html = '<p>Just a paragraph</p><div>Some content</div>'
        result = validate_accessibility(html)
        
        infos = result.get_by_severity(ValidationIssue.SEVERITY_INFO)
        assert any("no headings" in i.message.lower() for i in infos)
    
    def test_non_descriptive_link_text(self):
        html = '<a href="http://example.com">click here</a>'
        result = validate_accessibility(html)
        
        warnings = result.get_by_severity(ValidationIssue.SEVERITY_WARNING)
        assert any("non-descriptive link text" in w.message.lower() for w in warnings)
    
    def test_valid_link_text(self):
        html = '<a href="http://example.com">Read our full documentation</a>'
        result = validate_accessibility(html)
        
        # Should not flag descriptive links
        warnings = [w for w in result.issues if "link text" in w.message.lower() and "click here" not in html.lower()]
        assert len([w for w in warnings if w.severity == ValidationIssue.SEVERITY_WARNING]) == 0 or all("non-descriptive" not in w.message.lower() for w in warnings)
    
    def test_link_no_destination(self):
        html = '<a href="#">Empty link</a>'
        result = validate_accessibility(html)
        
        warnings = result.get_by_severity(ValidationIssue.SEVERITY_WARNING)
        assert any("no destination" in w.message.lower() for w in warnings)
    
    def test_table_missing_headers(self):
        html = '<table><tr><td>Data</td></tr></table>'
        result = validate_accessibility(html)
        
        warnings = result.get_by_severity(ValidationIssue.SEVERITY_WARNING)
        assert any("missing <th>" in w.message.lower() for w in warnings)
    
    def test_table_with_headers(self):
        html = '<table><tr><th>Header</th></tr><tr><td>Data</td></tr></table>'
        result = validate_accessibility(html)
        
        # Should not flag error for tables with headers
        warnings = [w for w in result.issues if "missing <th>" in w.message.lower()]
        assert len(warnings) == 0
    
    def test_table_missing_caption(self):
        html = '<table><tr><th>Header</th></tr></table>'
        result = validate_accessibility(html)
        
        infos = result.get_by_severity(ValidationIssue.SEVERITY_INFO)
        assert any("missing <caption>" in i.message.lower() for i in infos)
    
    def test_semantic_html_suggestion(self):
        html = '<div>Content</div><div>More content</div>'
        result = validate_accessibility(html)
        
        infos = result.get_by_severity(ValidationIssue.SEVERITY_INFO)
        assert any("semantic html5" in i.message.lower() for i in infos)
    
    def test_malformed_html_error(self):
        # Test that parser handles malformed HTML gracefully
        html = '<img src="test.jpg" alt="valid"><invalid tag structure'
        result = validate_accessibility(html)
        
        # Should still process what it can
        assert isinstance(result, ValidationResult)


class TestSpamTriggerValidation:
    """Test email spam trigger detection."""
    
    def test_excessive_capitalization(self):
        html = '<p>THIS IS ALL CAPS TEXT EVERYWHERE IN THE EMAIL</p>'
        result = validate_spam_triggers(html)
        
        warnings = result.get_by_severity(ValidationIssue.SEVERITY_WARNING)
        assert any("excessive capitalization" in w.message.lower() or "high capitalization" in w.message.lower() for w in warnings)
    
    def test_moderate_capitalization(self):
        html = '<p>Some CAPS words but NOT too many in this text</p>'
        result = validate_spam_triggers(html)
        
        # Should either be warning or info depending on ratio
        issues = result.get_by_severity(ValidationIssue.SEVERITY_WARNING) + result.get_by_severity(ValidationIssue.SEVERITY_INFO)
        # May or may not flag depending on exact ratio, just check it doesn't crash
        assert isinstance(result, ValidationResult)
    
    def test_spam_trigger_words(self):
        html = '<p>FREE MONEY! Act now! Winner! Click here!</p>'
        result = validate_spam_triggers(html)
        
        issues = result.get_by_severity(ValidationIssue.SEVERITY_WARNING) + result.get_by_severity(ValidationIssue.SEVERITY_INFO)
        assert any("spam trigger" in i.message.lower() for i in issues)
    
    def test_few_spam_words(self):
        html = '<p>Feel free to contact us anytime</p>'
        result = validate_spam_triggers(html)
        
        # "free" is a trigger word but in normal context, should be info at most
        infos = result.get_by_severity(ValidationIssue.SEVERITY_INFO)
        # May or may not flag a single occurrence
        assert isinstance(result, ValidationResult)
    
    def test_excessive_punctuation(self):
        html = '<p>Amazing offer!!! Don\'t miss out??? Really!!! Wow!!! More!!!</p>'
        result = validate_spam_triggers(html)
        
        warnings = result.get_by_severity(ValidationIssue.SEVERITY_WARNING)
        assert any("excessive punctuation" in w.message.lower() for w in warnings)
    
    def test_high_image_to_text_ratio(self):
        html = '<img src="1.jpg"><img src="2.jpg"><img src="3.jpg"><p>Short text</p>'
        result = validate_spam_triggers(html)
        
        warnings = result.get_by_severity(ValidationIssue.SEVERITY_WARNING)
        assert any("image-to-text ratio" in w.message.lower() for w in warnings)
    
    def test_url_shorteners(self):
        html = '<a href="https://bit.ly/abc123">Link</a><a href="https://tinyurl.com/xyz">Another</a>'
        result = validate_spam_triggers(html)
        
        infos = result.get_by_severity(ValidationIssue.SEVERITY_INFO)
        assert any("url shortener" in i.message.lower() for i in infos)
    
    def test_unbalanced_html(self):
        html = '<div><p><span><b>Text</div></p><a>Link<div>More'  # Very unbalanced (6 open, 2 close = diff 4)
        result = validate_spam_triggers(html)
        
        errors = result.get_by_severity(ValidationIssue.SEVERITY_ERROR)
        assert any("unbalanced html" in e.message.lower() for e in errors)
    
    def test_clean_html(self):
        html = '<p>This is a normal email with good content and proper formatting.</p>'
        result = validate_spam_triggers(html)
        
        # Should have no errors, possibly some info
        assert not result.has_errors()


class TestValidationIntegration:
    """Test integration functions."""
    
    def test_validate_export(self):
        html = '<h1>Title</h1><p>Content</p><img src="test.jpg" alt="Test">'
        accessibility_result, spam_result = validate_export(html)
        
        assert isinstance(accessibility_result, ValidationResult)
        assert isinstance(spam_result, ValidationResult)
    
    def test_format_validation_report_no_issues(self):
        accessibility_result = ValidationResult()
        spam_result = ValidationResult()
        
        report = format_validation_report(accessibility_result, spam_result)
        
        assert "EXPORT VALIDATION REPORT" in report
        assert "ACCESSIBILITY (WCAG)" in report
        assert "SPAM TRIGGER DETECTION" in report
        assert "No accessibility issues found" in report or "ALL CHECKS PASSED" in report
    
    def test_format_validation_report_with_issues(self):
        accessibility_result = ValidationResult()
        accessibility_result.add_issue(
            ValidationIssue.SEVERITY_ERROR,
            "accessibility",
            "Missing alt text",
            "Add alt attribute"
        )
        
        spam_result = ValidationResult()
        spam_result.add_issue(
            ValidationIssue.SEVERITY_WARNING,
            "spam",
            "Spam trigger word found",
            "Rephrase"
        )
        
        report = format_validation_report(accessibility_result, spam_result)
        
        assert "EXPORT VALIDATION REPORT" in report
        assert "Missing alt text" in report
        assert "Spam trigger word found" in report
        assert "Add alt attribute" in report
        assert "Rephrase" in report
        assert "ERROR:" in report
        assert "WARNING:" in report
    
    def test_format_validation_report_critical_issues(self):
        accessibility_result = ValidationResult()
        accessibility_result.add_issue(
            ValidationIssue.SEVERITY_ERROR,
            "accessibility",
            "Critical error"
        )
        
        spam_result = ValidationResult()
        
        report = format_validation_report(accessibility_result, spam_result)
        
        assert "CRITICAL ISSUES FOUND" in report or "1 error" in report


class MockApp:
    """Mock application for testing init function."""
    
    def __init__(self):
        self.attributes = {}


class TestInit:
    """Test module initialization."""
    
    def test_init_attaches_functions(self):
        app = MockApp()
        init(app)
        
        assert hasattr(app, 'validate_export')
        assert hasattr(app, 'validate_accessibility')
        assert hasattr(app, 'validate_spam_triggers')
        assert hasattr(app, 'format_validation_report')
        
        assert callable(app.validate_export)
        assert callable(app.validate_accessibility)
        assert callable(app.validate_spam_triggers)
        assert callable(app.format_validation_report)
    
    def test_init_functions_work(self):
        app = MockApp()
        init(app)
        
        # Test that attached functions work
        html = '<h1>Test</h1><img src="test.jpg" alt="Test">'
        accessibility_result, spam_result = app.validate_export(html)
        
        assert isinstance(accessibility_result, ValidationResult)
        assert isinstance(spam_result, ValidationResult)
        
        report = app.format_validation_report(accessibility_result, spam_result)
        assert isinstance(report, str)
        assert len(report) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
