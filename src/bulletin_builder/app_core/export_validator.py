"""
Export Validator Module for Bulletin Builder

Validates exported HTML for:
1. WCAG accessibility compliance (alt text, headings, contrast, semantic HTML)
2. Email spam triggers (caps lock, trigger words, suspicious patterns)

Returns structured validation results with severity levels and recommendations.
"""

import re
from typing import Any, Dict, List, Tuple
from html.parser import HTMLParser


class ValidationIssue:
    """Represents a single validation issue."""
    
    SEVERITY_INFO = "info"
    SEVERITY_WARNING = "warning"
    SEVERITY_ERROR = "error"
    
    def __init__(self, severity: str, category: str, message: str, recommendation: str = "") -> None:
        """
        Initialize a validation issue.
        
        Args:
            severity: One of SEVERITY_INFO, SEVERITY_WARNING, or SEVERITY_ERROR
            category: Category of issue (e.g., 'accessibility', 'spam', 'email_css')
            message: Description of the issue
            recommendation: Suggested fix or improvement
        """
        self.severity = severity
        self.category = category
        self.message = message
        self.recommendation = recommendation
    
    def __repr__(self) -> str:
        return f"ValidationIssue({self.severity}, {self.category}: {self.message})"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert issue to dictionary format."""
        return {
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "recommendation": self.recommendation
        }


class ValidationResult:
    """Container for all validation issues found."""
    
    def __init__(self) -> None:
        """Initialize empty validation result."""
        self.issues: List[ValidationIssue] = []
    
    def add_issue(self, severity: str, category: str, message: str, recommendation: str = "") -> None:
        """
        Add a validation issue to the result.
        
        Args:
            severity: One of SEVERITY_INFO, SEVERITY_WARNING, or SEVERITY_ERROR
            category: Category of issue (e.g., 'accessibility', 'spam', 'email_css')
            message: Description of the issue
            recommendation: Suggested fix or improvement
        """
        issue = ValidationIssue(severity, category, message, recommendation)
        self.issues.append(issue)
    
    def has_errors(self) -> bool:
        """Check if result contains any errors."""
        return any(i.severity == ValidationIssue.SEVERITY_ERROR for i in self.issues)
    
    def has_warnings(self) -> bool:
        """Check if result contains any warnings."""
        return any(i.severity == ValidationIssue.SEVERITY_WARNING for i in self.issues)
    
    def get_by_severity(self, severity: str) -> List[ValidationIssue]:
        """Get all issues matching the specified severity."""
        return [i for i in self.issues if i.severity == severity]
    
    def get_by_category(self, category: str) -> List[ValidationIssue]:
        """Get all issues matching the specified category."""
        return [i for i in self.issues if i.category == category]
    
    def summary(self) -> str:
        """Generate a summary string of issue counts."""
        errors = len(self.get_by_severity(ValidationIssue.SEVERITY_ERROR))
        warnings = len(self.get_by_severity(ValidationIssue.SEVERITY_WARNING))
        infos = len(self.get_by_severity(ValidationIssue.SEVERITY_INFO))
        return f"{errors} errors, {warnings} warnings, {infos} info"
    
    def __bool__(self) -> bool:
        """Return True if there are any issues."""
        return len(self.issues) > 0


class AccessibilityHTMLParser(HTMLParser):
    """Parse HTML to extract elements for accessibility validation."""
    
    def __init__(self) -> None:
        """Initialize the HTML parser with tracking structures."""
        super().__init__()
        self.images: List[Tuple[str, Dict[str, str]]] = []  # (tag, attrs)
        self.headings: List[Tuple[int, str]] = []  # (level, text)
        self.links: List[Dict[str, Any]] = []  # (href, text)
        self.tables: List[Dict[str, bool]] = []  # (has_headers, has_caption)
        self.current_heading_level: int | None = None
        self.current_heading_text: List[str] = []
        self.current_link_text: List[str] = []
        self.in_link: bool = False
        self.current_table: Dict[str, bool] | None = None
    
    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str | None]]) -> None:
        """Handle opening HTML tags and extract relevant attributes."""
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
    
    def handle_endtag(self, tag: str) -> None:
        """Handle closing HTML tags and finalize element data."""
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
    
    def handle_data(self, data: str) -> None:
        """Handle text content within HTML elements."""
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
    
    Args:
        html: HTML content to validate
        
    Returns:
        ValidationResult containing any accessibility issues found
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
    
    Args:
        html: HTML content to validate
        
    Returns:
        ValidationResult containing any spam trigger issues found
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


def validate_html_css_email_safety(html: str) -> ValidationResult:
    """
    Validate HTML/CSS for email client compatibility.
    
    Checks:
    - Presence of <style> tags (should use inline styles)
    - Use of position/float CSS (poor email support)
    - External CSS links (not allowed in emails)
    - JavaScript usage (blocked in emails)
    - Unsupported CSS properties
    - Missing inline styles on key elements
    - Use of web fonts that may not render
    - Video/audio tags (limited support)
    
    Args:
        html: HTML content to validate
        
    Returns:
        ValidationResult containing any email compatibility issues found
    """
    result = ValidationResult()
    
    # Check for <style> tags - email clients often strip these
    style_tags = re.findall(r'<style[^>]*>.*?</style>', html, re.IGNORECASE | re.DOTALL)
    if style_tags:
        result.add_issue(
            ValidationIssue.SEVERITY_WARNING,
            "email_css",
            f"Found {len(style_tags)} <style> tag(s) in HTML",
            "Email clients often strip <style> tags. Use inline styles instead (style=\"...\") for better compatibility"
        )
    
    # Check for external CSS links
    css_links = re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*>', html, re.IGNORECASE)
    if css_links:
        result.add_issue(
            ValidationIssue.SEVERITY_ERROR,
            "email_css",
            f"Found {len(css_links)} external CSS link(s)",
            "External CSS is blocked by email clients. All styles must be inline"
        )
    
    # Check for JavaScript - completely blocked in emails
    script_tags = re.findall(r'<script[^>]*>.*?</script>', html, re.IGNORECASE | re.DOTALL)
    onclick_handlers = re.findall(r'\son\w+\s*=', html, re.IGNORECASE)
    
    if script_tags:
        result.add_issue(
            ValidationIssue.SEVERITY_ERROR,
            "email_js",
            f"Found {len(script_tags)} <script> tag(s)",
            "JavaScript is completely blocked in email clients. Remove all scripts"
        )
    
    if onclick_handlers:
        result.add_issue(
            ValidationIssue.SEVERITY_ERROR,
            "email_js",
            f"Found {len(onclick_handlers)} inline event handler(s) (onclick, onload, etc.)",
            "Event handlers don't work in emails. Use <a> tags with mailto: or http: links instead"
        )
    
    # Check for CSS position property - poor email support
    position_css = re.findall(r'position\s*:\s*(absolute|fixed|sticky)', html, re.IGNORECASE)
    if position_css:
        result.add_issue(
            ValidationIssue.SEVERITY_WARNING,
            "email_css",
            f"Found CSS position property: {', '.join(set(position_css))}",
            "CSS positioning (absolute/fixed/sticky) has poor support in email clients. Use table-based layouts instead"
        )
    
    # Check for float property - inconsistent email support
    float_css = re.findall(r'float\s*:\s*(left|right)', html, re.IGNORECASE)
    if float_css:
        result.add_issue(
            ValidationIssue.SEVERITY_WARNING,
            "email_css",
            f"Found CSS float property used {len(float_css)} time(s)",
            "CSS float has inconsistent support in email clients. Use table columns for side-by-side layouts"
        )
    
    # Check for flexbox/grid - not supported in most email clients
    modern_css = re.findall(r'display\s*:\s*(flex|grid|inline-flex|inline-grid)', html, re.IGNORECASE)
    if modern_css:
        result.add_issue(
            ValidationIssue.SEVERITY_ERROR,
            "email_css",
            f"Found modern CSS layout: {', '.join(set(modern_css))}",
            "Flexbox and Grid are not supported in email clients. Use table-based layouts for structure"
        )
    
    # Check for web fonts - limited support
    font_face = re.findall(r'@font-face', html, re.IGNORECASE)
    if font_face:
        result.add_issue(
            ValidationIssue.SEVERITY_INFO,
            "email_css",
            "Found @font-face declaration",
            "Web fonts have limited support in email clients. Provide fallback to web-safe fonts (Arial, Georgia, etc.)"
        )
    
    # Check for video/audio tags - very limited support
    video_tags = re.findall(r'<video[^>]*>', html, re.IGNORECASE)
    audio_tags = re.findall(r'<audio[^>]*>', html, re.IGNORECASE)
    
    if video_tags:
        result.add_issue(
            ValidationIssue.SEVERITY_WARNING,
            "email_media",
            f"Found {len(video_tags)} <video> tag(s)",
            "Video tags are not supported in most email clients. Use a linked image thumbnail instead"
        )
    
    if audio_tags:
        result.add_issue(
            ValidationIssue.SEVERITY_WARNING,
            "email_media",
            f"Found {len(audio_tags)} <audio> tag(s)",
            "Audio tags are not supported in email clients. Provide a link to audio content instead"
        )
    
    # Check for background images - Outlook doesn't support
    bg_image_css = re.findall(r'background-image\s*:', html, re.IGNORECASE)
    if bg_image_css:
        result.add_issue(
            ValidationIssue.SEVERITY_INFO,
            "email_css",
            f"Found {len(bg_image_css)} background-image declaration(s)",
            "Background images don't work in Outlook. Use bgcolor for solid colors or VML for Outlook compatibility"
        )
    
    # Check for forms - limited support
    form_tags = re.findall(r'<form[^>]*>', html, re.IGNORECASE)
    if form_tags:
        result.add_issue(
            ValidationIssue.SEVERITY_WARNING,
            "email_html",
            f"Found {len(form_tags)} <form> tag(s)",
            "Forms have limited support in email clients. Link to a web-based form instead"
        )
    
    # Check for iframes - blocked in emails
    iframe_tags = re.findall(r'<iframe[^>]*>', html, re.IGNORECASE)
    if iframe_tags:
        result.add_issue(
            ValidationIssue.SEVERITY_ERROR,
            "email_html",
            f"Found {len(iframe_tags)} <iframe> tag(s)",
            "Iframes are blocked in email clients for security. Link to external content instead"
        )
    
    # Check if using tables for layout (good for email)
    table_count = html.count('<table')
    has_divs = '<div' in html
    
    if has_divs and table_count < 2:
        result.add_issue(
            ValidationIssue.SEVERITY_INFO,
            "email_layout",
            "Using <div>-based layout with few tables",
            "Email clients work best with table-based layouts. Consider using nested tables for complex structures"
        )
    
    # Check for CSS3 properties that may not work
    css3_properties = [
        (r'border-radius\s*:', 'border-radius', 'rounded corners'),
        (r'box-shadow\s*:', 'box-shadow', 'shadows'),
        (r'text-shadow\s*:', 'text-shadow', 'text shadows'),
        (r'transform\s*:', 'transform', 'transforms'),
        (r'transition\s*:', 'transition', 'transitions'),
        (r'animation\s*:', 'animation', 'animations'),
    ]
    
    for pattern, prop, description in css3_properties:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            result.add_issue(
                ValidationIssue.SEVERITY_INFO,
                "email_css",
                f"Using CSS3 property '{prop}' ({len(matches)} occurrence(s))",
                f"CSS3 {description} have limited support in email clients (work in iOS/Apple Mail, not in Outlook/Gmail)"
            )
    
    return result


def validate_export(html: str) -> Tuple[ValidationResult, ValidationResult, ValidationResult]:
    """
    Run all validation checks on exported HTML.
    
    Args:
        html: HTML content to validate
    
    Returns:
        Tuple of (accessibility_result, spam_result, email_css_result)
    """
    accessibility_result = validate_accessibility(html)
    spam_result = validate_spam_triggers(html)
    email_css_result = validate_html_css_email_safety(html)
    
    return accessibility_result, spam_result, email_css_result


def format_validation_report(accessibility_result: ValidationResult, spam_result: ValidationResult, email_css_result: ValidationResult, max_issues_per_type: int = 5) -> str:
    """
    Format validation results into a human-readable report.
    
    Args:
        accessibility_result: Accessibility validation results
        spam_result: Spam trigger validation results
        email_css_result: Email compatibility validation results
        max_issues_per_type: Maximum number of issues to show per severity type (default: 5)
        
    Returns:
        Formatted string report with all validation results
    """
    lines = []
    lines.append("=" * 60)
    lines.append("EXPORT VALIDATION REPORT")
    lines.append("=" * 60)
    lines.append("")
    
    # Accessibility section
    lines.append("ACCESSIBILITY (WCAG)")
    lines.append("-" * 60)
    if accessibility_result.issues:
        lines.append(f"Summary: {accessibility_result.summary()}")
        lines.append("")
        
        for severity in [ValidationIssue.SEVERITY_ERROR, ValidationIssue.SEVERITY_WARNING, ValidationIssue.SEVERITY_INFO]:
            issues = accessibility_result.get_by_severity(severity)
            if issues:
                lines.append(f"{severity.upper()} ({len(issues)} total):")
                # Show only first max_issues_per_type issues
                for issue in issues[:max_issues_per_type]:
                    lines.append(f"  • {issue.message}")
                    if issue.recommendation:
                        lines.append(f"    → {issue.recommendation}")
                if len(issues) > max_issues_per_type:
                    lines.append(f"  ... and {len(issues) - max_issues_per_type} more {severity} issues")
                lines.append("")
    else:
        lines.append("✓ No accessibility issues found")
        lines.append("")
    
    # Spam section
    lines.append("SPAM TRIGGER DETECTION")
    lines.append("-" * 60)
    if spam_result.issues:
        lines.append(f"Summary: {spam_result.summary()}")
        lines.append("")
        
        for severity in [ValidationIssue.SEVERITY_ERROR, ValidationIssue.SEVERITY_WARNING, ValidationIssue.SEVERITY_INFO]:
            issues = spam_result.get_by_severity(severity)
            if issues:
                lines.append(f"{severity.upper()} ({len(issues)} total):")
                # Show only first max_issues_per_type issues
                for issue in issues[:max_issues_per_type]:
                    lines.append(f"  • {issue.message}")
                    if issue.recommendation:
                        lines.append(f"    → {issue.recommendation}")
                if len(issues) > max_issues_per_type:
                    lines.append(f"  ... and {len(issues) - max_issues_per_type} more {severity} issues")
                lines.append("")
    else:
        lines.append("✓ No spam triggers detected")
        lines.append("")
    
    # Email compatibility section
    lines.append("EMAIL COMPATIBILITY (HTML/CSS)")
    lines.append("-" * 60)
    if email_css_result.issues:
        lines.append(f"Summary: {email_css_result.summary()}")
        lines.append("")
        
        for severity in [ValidationIssue.SEVERITY_ERROR, ValidationIssue.SEVERITY_WARNING, ValidationIssue.SEVERITY_INFO]:
            issues = email_css_result.get_by_severity(severity)
            if issues:
                lines.append(f"{severity.upper()} ({len(issues)} total):")
                # Show only first max_issues_per_type issues
                for issue in issues[:max_issues_per_type]:
                    lines.append(f"  • {issue.message}")
                    if issue.recommendation:
                        lines.append(f"    → {issue.recommendation}")
                if len(issues) > max_issues_per_type:
                    lines.append(f"  ... and {len(issues) - max_issues_per_type} more {severity} issues")
                lines.append("")
    else:
        lines.append("✓ No email compatibility issues found")
        lines.append("")
    
    lines.append("=" * 60)
    
    # Overall summary
    total_errors = (accessibility_result.get_by_severity(ValidationIssue.SEVERITY_ERROR) + 
                   spam_result.get_by_severity(ValidationIssue.SEVERITY_ERROR) +
                   email_css_result.get_by_severity(ValidationIssue.SEVERITY_ERROR))
    total_warnings = (accessibility_result.get_by_severity(ValidationIssue.SEVERITY_WARNING) + 
                     spam_result.get_by_severity(ValidationIssue.SEVERITY_WARNING) +
                     email_css_result.get_by_severity(ValidationIssue.SEVERITY_WARNING))
    
    if total_errors:
        lines.append(f"⚠ {len(total_errors)} CRITICAL ISSUES FOUND")
    elif total_warnings:
        lines.append(f"⚠ {len(total_warnings)} warnings (export can proceed)")
    else:
        lines.append("✓ ALL CHECKS PASSED")
    
    lines.append("=" * 60)
    
    return '\n'.join(lines)


def init(app: Any) -> None:
    """
    Initialize export validator module.
    
    Attaches validation functions to the app for use in export workflow.
    
    Args:
        app: Application instance to attach validator functions to
    """
    app.validate_export = validate_export
    app.validate_accessibility = validate_accessibility
    app.validate_spam_triggers = validate_spam_triggers
    app.validate_html_css_email_safety = validate_html_css_email_safety
    app.format_validation_report = format_validation_report
