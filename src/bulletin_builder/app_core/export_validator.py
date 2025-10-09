"""
Export Validator Module for Bulletin Builder

Validates exported HTML for:
1. WCAG accessibility compliance (alt text, headings, contrast, semantic HTML)
2. Email spam triggers (caps lock, trigger words, suspicious patterns)

Returns structured validation results with severity levels and recommendations.
"""

import re
from typing import Dict, List, Tuple
from html.parser import HTMLParser


class ValidationIssue:
    """Represents a single validation issue."""
    
    SEVERITY_INFO = "info"
    SEVERITY_WARNING = "warning"
    SEVERITY_ERROR = "error"
    
    def __init__(self, severity: str, category: str, message: str, recommendation: str = ""):
        self.severity = severity
        self.category = category
        self.message = message
        self.recommendation = recommendation
    
    def __repr__(self):
        return f"ValidationIssue({self.severity}, {self.category}: {self.message})"
    
    def to_dict(self) -> Dict:
        return {
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "recommendation": self.recommendation
        }


class ValidationResult:
    """Container for all validation issues found."""
    
    def __init__(self):
        self.issues: List[ValidationIssue] = []
    
    def add_issue(self, severity: str, category: str, message: str, recommendation: str = ""):
        issue = ValidationIssue(severity, category, message, recommendation)
        self.issues.append(issue)
    
    def has_errors(self) -> bool:
        return any(i.severity == ValidationIssue.SEVERITY_ERROR for i in self.issues)
    
    def has_warnings(self) -> bool:
        return any(i.severity == ValidationIssue.SEVERITY_WARNING for i in self.issues)
    
    def get_by_severity(self, severity: str) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == severity]
    
    def get_by_category(self, category: str) -> List[ValidationIssue]:
        return [i for i in self.issues if i.category == category]
    
    def summary(self) -> str:
        errors = len(self.get_by_severity(ValidationIssue.SEVERITY_ERROR))
        warnings = len(self.get_by_severity(ValidationIssue.SEVERITY_WARNING))
        infos = len(self.get_by_severity(ValidationIssue.SEVERITY_INFO))
        return f"{errors} errors, {warnings} warnings, {infos} info"
    
    def __bool__(self):
        return len(self.issues) > 0


class AccessibilityHTMLParser(HTMLParser):
    """Parse HTML to extract elements for accessibility validation."""
    
    def __init__(self):
        super().__init__()
        self.images = []  # (tag, attrs)
        self.headings = []  # (level, text)
        self.links = []  # (href, text)
        self.tables = []  # (has_headers, has_caption)
        self.current_heading_level = None
        self.current_heading_text = []
        self.current_link_text = []
        self.in_link = False
        self.current_table = None
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'img':
            self.images.append((tag, attrs_dict))
        
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.current_heading_level = int(tag[1])
            self.current_heading_text = []
        
        elif tag == 'a':
            self.in_link = True
            self.current_link_text = []
            href = attrs_dict.get('href', '')
            self.links.append({'href': href, 'text': '', 'attrs': attrs_dict})
        
        elif tag == 'table':
            self.current_table = {'has_headers': False, 'has_caption': False}
        
        elif tag == 'th' and self.current_table is not None:
            self.current_table['has_headers'] = True
        
        elif tag == 'caption' and self.current_table is not None:
            self.current_table['has_caption'] = True
    
    def handle_endtag(self, tag):
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            text = ''.join(self.current_heading_text).strip()
            self.headings.append((self.current_heading_level, text))
            self.current_heading_level = None
            self.current_heading_text = []
        
        elif tag == 'a':
            self.in_link = False
            if self.links:
                self.links[-1]['text'] = ''.join(self.current_link_text).strip()
            self.current_link_text = []
        
        elif tag == 'table' and self.current_table is not None:
            self.tables.append(self.current_table)
            self.current_table = None
    
    def handle_data(self, data):
        if self.current_heading_level is not None:
            self.current_heading_text.append(data)
        if self.in_link:
            self.current_link_text.append(data)


def validate_accessibility(html: str) -> ValidationResult:
    """
    Validate HTML for WCAG accessibility compliance.
    
    Checks:
    - Alt text on images
    - Proper heading hierarchy
    - Link text clarity
    - Table accessibility (headers and captions)
    - Semantic HTML usage
    """
    result = ValidationResult()
    parser = AccessibilityHTMLParser()
    
    try:
        parser.feed(html)
    except Exception as e:
        result.add_issue(
            ValidationIssue.SEVERITY_ERROR,
            "accessibility",
            f"Failed to parse HTML: {e}",
            "Ensure HTML is well-formed"
        )
        return result
    
    # Check images for alt text
    for tag, attrs in parser.images:
        alt = attrs.get('alt', None)
        src = attrs.get('src', 'unknown')
        
        if alt is None:
            result.add_issue(
                ValidationIssue.SEVERITY_ERROR,
                "accessibility",
                f"Image missing alt attribute: {src}",
                "Add alt text to all images, even if decorative (use alt='' for decorative images)"
            )
        elif alt == '':
            result.add_issue(
                ValidationIssue.SEVERITY_INFO,
                "accessibility",
                f"Image has empty alt text (decorative): {src}",
                "Verify this image is truly decorative and doesn't convey information"
            )
    
    # Check heading hierarchy
    if parser.headings:
        prev_level = 0
        for level, text in parser.headings:
            if prev_level == 0 and level != 1:
                result.add_issue(
                    ValidationIssue.SEVERITY_WARNING,
                    "accessibility",
                    f"Document should start with h1, found h{level} first",
                    "Start with h1 for the main heading"
                )
            elif level > prev_level + 1:
                result.add_issue(
                    ValidationIssue.SEVERITY_WARNING,
                    "accessibility",
                    f"Heading hierarchy skip: h{prev_level} to h{level}",
                    "Don't skip heading levels (e.g., h2 to h4)"
                )
            
            if not text:
                result.add_issue(
                    ValidationIssue.SEVERITY_WARNING,
                    "accessibility",
                    f"Empty heading found: h{level}",
                    "All headings should contain descriptive text"
                )
            
            prev_level = level
    else:
        result.add_issue(
            ValidationIssue.SEVERITY_INFO,
            "accessibility",
            "No headings found in document",
            "Consider adding headings to structure your content"
        )
    
    # Check link text
    for link in parser.links:
        text = link['text']
        href = link['href']
        
        if not text or text.lower() in ['click here', 'here', 'link', 'read more']:
            result.add_issue(
                ValidationIssue.SEVERITY_WARNING,
                "accessibility",
                f"Non-descriptive link text: '{text}' ({href})",
                "Use descriptive link text that makes sense out of context"
            )
        
        if not href or href == '#':
            result.add_issue(
                ValidationIssue.SEVERITY_WARNING,
                "accessibility",
                f"Link with no destination: '{text}'",
                "Ensure all links have valid href attributes"
            )
    
    # Check tables
    for table in parser.tables:
        if not table['has_headers']:
            result.add_issue(
                ValidationIssue.SEVERITY_WARNING,
                "accessibility",
                "Table missing <th> header cells",
                "Use <th> elements to define table headers"
            )
        
        if not table['has_caption']:
            result.add_issue(
                ValidationIssue.SEVERITY_INFO,
                "accessibility",
                "Table missing <caption> element",
                "Add a <caption> to describe the table's purpose"
            )
    
    # Check for semantic HTML
    if '<div' in html and not any(tag in html for tag in ['<article', '<section', '<header', '<footer', '<nav', '<main']):
        result.add_issue(
            ValidationIssue.SEVERITY_INFO,
            "accessibility",
            "Consider using semantic HTML5 elements",
            "Use <article>, <section>, <header>, <footer>, <nav> instead of generic <div> where appropriate"
        )
    
    return result


# Common spam trigger words and patterns
SPAM_TRIGGER_WORDS = [
    'free', 'winner', 'congratulations', 'urgent', 'act now', 'limited time',
    'click here', 'buy now', 'order now', 'subscribe', 'apply now',
    'cash', 'prize', 'money back', '100% free', 'risk free', 'satisfaction guaranteed',
    'dear friend', 'special promotion', 'once in lifetime', 'exclusive deal'
]


def validate_spam_triggers(html: str) -> ValidationResult:
    """
    Validate HTML for common email spam triggers.
    
    Checks:
    - Excessive capitalization (ALL CAPS)
    - Spam trigger words
    - Excessive punctuation (!!!, ???)
    - Too many images vs text ratio
    - Suspicious link patterns
    - HTML balance issues
    """
    result = ValidationResult()
    
    # Extract text content (rough approximation)
    text_content = re.sub(r'<[^>]+>', '', html)
    
    # Check for excessive capitalization
    words = text_content.split()
    if words:
        caps_words = [w for w in words if w.isupper() and len(w) > 2]
        caps_ratio = len(caps_words) / len(words)
        
        if caps_ratio > 0.3:
            result.add_issue(
                ValidationIssue.SEVERITY_WARNING,
                "spam",
                f"Excessive capitalization: {int(caps_ratio * 100)}% of words are ALL CAPS",
                "Reduce use of ALL CAPS text, which triggers spam filters"
            )
        elif caps_ratio > 0.15:
            result.add_issue(
                ValidationIssue.SEVERITY_INFO,
                "spam",
                f"High capitalization: {int(caps_ratio * 100)}% of words are ALL CAPS",
                "Consider reducing ALL CAPS usage"
            )
    
    # Check for spam trigger words
    text_lower = text_content.lower()
    found_triggers = [word for word in SPAM_TRIGGER_WORDS if word in text_lower]
    
    if len(found_triggers) > 5:
        result.add_issue(
            ValidationIssue.SEVERITY_WARNING,
            "spam",
            f"Multiple spam trigger words found: {', '.join(found_triggers[:5])}...",
            "Reduce use of promotional language and spam trigger words"
        )
    elif len(found_triggers) > 2:
        result.add_issue(
            ValidationIssue.SEVERITY_INFO,
            "spam",
            f"Some spam trigger words found: {', '.join(found_triggers)}",
            "Consider rephrasing to avoid common spam trigger words"
        )
    
    # Check for excessive punctuation
    excessive_exclamation = len(re.findall(r'!{2,}', text_content))
    excessive_question = len(re.findall(r'\?{2,}', text_content))
    
    if excessive_exclamation > 2 or excessive_question > 2:
        result.add_issue(
            ValidationIssue.SEVERITY_WARNING,
            "spam",
            f"Excessive punctuation: {excessive_exclamation} instances of !!, {excessive_question} instances of ??",
            "Use single punctuation marks; excessive punctuation triggers spam filters"
        )
    
    # Check image to text ratio
    image_count = html.count('<img')
    text_length = len(text_content.strip())
    
    if image_count > 0 and text_length > 0:
        # Rough heuristic: if more than 1 image per 100 characters, might be too image-heavy
        image_ratio = image_count / (text_length / 100)
        if image_ratio > 2:
            result.add_issue(
                ValidationIssue.SEVERITY_WARNING,
                "spam",
                f"High image-to-text ratio: {image_count} images for {text_length} characters",
                "Ensure sufficient text content; image-heavy emails may be flagged as spam"
            )
    
    # Check for suspicious link patterns
    links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    suspicious_links = [link for link in links if any(pattern in link.lower() for pattern in ['bit.ly', 'tinyurl', 'goo.gl', 't.co'])]
    
    if suspicious_links:
        result.add_issue(
            ValidationIssue.SEVERITY_INFO,
            "spam",
            f"URL shorteners detected: {len(suspicious_links)} links",
            "Some email filters flag shortened URLs; consider using full URLs"
        )
    
    # Check HTML balance
    open_tags = len(re.findall(r'<(?!/)([a-z][a-z0-9]*)', html, re.IGNORECASE))
    close_tags = len(re.findall(r'</([a-z][a-z0-9]*)', html, re.IGNORECASE))
    
    if abs(open_tags - close_tags) > 3:
        result.add_issue(
            ValidationIssue.SEVERITY_ERROR,
            "spam",
            f"Unbalanced HTML tags: {open_tags} opening, {close_tags} closing",
            "Ensure all HTML tags are properly closed"
        )
    
    return result


def validate_export(html: str) -> Tuple[ValidationResult, ValidationResult]:
    """
    Run all validation checks on exported HTML.
    
    Returns:
        Tuple of (accessibility_result, spam_result)
    """
    accessibility_result = validate_accessibility(html)
    spam_result = validate_spam_triggers(html)
    
    return accessibility_result, spam_result


def format_validation_report(accessibility_result: ValidationResult, spam_result: ValidationResult) -> str:
    """
    Format validation results into a human-readable report.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("EXPORT VALIDATION REPORT")
    lines.append("=" * 60)
    lines.append("")
    
    # Accessibility section
    lines.append("ACCESSIBILITY (WCAG)")
    lines.append("-" * 60)
    if accessibility_result:
        lines.append(f"Summary: {accessibility_result.summary()}")
        lines.append("")
        
        for severity in [ValidationIssue.SEVERITY_ERROR, ValidationIssue.SEVERITY_WARNING, ValidationIssue.SEVERITY_INFO]:
            issues = accessibility_result.get_by_severity(severity)
            if issues:
                lines.append(f"{severity.upper()}:")
                for issue in issues:
                    lines.append(f"  • {issue.message}")
                    if issue.recommendation:
                        lines.append(f"    → {issue.recommendation}")
                lines.append("")
    else:
        lines.append("✓ No accessibility issues found")
        lines.append("")
    
    # Spam section
    lines.append("SPAM TRIGGER DETECTION")
    lines.append("-" * 60)
    if spam_result:
        lines.append(f"Summary: {spam_result.summary()}")
        lines.append("")
        
        for severity in [ValidationIssue.SEVERITY_ERROR, ValidationIssue.SEVERITY_WARNING, ValidationIssue.SEVERITY_INFO]:
            issues = spam_result.get_by_severity(severity)
            if issues:
                lines.append(f"{severity.upper()}:")
                for issue in issues:
                    lines.append(f"  • {issue.message}")
                    if issue.recommendation:
                        lines.append(f"    → {issue.recommendation}")
                lines.append("")
    else:
        lines.append("✓ No spam triggers detected")
        lines.append("")
    
    lines.append("=" * 60)
    
    # Overall summary
    total_errors = (accessibility_result.get_by_severity(ValidationIssue.SEVERITY_ERROR) + 
                   spam_result.get_by_severity(ValidationIssue.SEVERITY_ERROR))
    total_warnings = (accessibility_result.get_by_severity(ValidationIssue.SEVERITY_WARNING) + 
                     spam_result.get_by_severity(ValidationIssue.SEVERITY_WARNING))
    
    if total_errors:
        lines.append(f"⚠ {len(total_errors)} CRITICAL ISSUES FOUND")
    elif total_warnings:
        lines.append(f"⚠ {len(total_warnings)} warnings (export can proceed)")
    else:
        lines.append("✓ ALL CHECKS PASSED")
    
    lines.append("=" * 60)
    
    return '\n'.join(lines)


def init(app):
    """
    Initialize export validator module.
    
    Attaches validation functions to the app for use in export workflow.
    """
    app.validate_export = validate_export
    app.validate_accessibility = validate_accessibility
    app.validate_spam_triggers = validate_spam_triggers
    app.format_validation_report = format_validation_report
