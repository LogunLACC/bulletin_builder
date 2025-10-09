"""
PDF Export Module

Provides functionality to export bulletin HTML to PDF format for archiving and compliance.
Uses weasyprint for high-quality HTML-to-PDF conversion with email client styling.
"""

from pathlib import Path
from typing import Optional, Tuple
import tempfile
import os
from bulletin_builder.exceptions import PDFExportError, MissingDependencyError
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)


def export_to_pdf(html_content: str, output_path: str, client_style: str = "desktop") -> Tuple[bool, str]:
    """
    Export bulletin HTML content to PDF.
    
    Args:
        html_content: The HTML content to convert to PDF
        output_path: Path where the PDF should be saved
        client_style: Email client style to use ("desktop", "gmail", "outlook", etc.)
    
    Returns:
        Tuple of (success: bool, message: str)
    
    Raises:
        MissingDependencyError: If weasyprint is not installed
        PDFExportError: If PDF generation fails
    """
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
    except ImportError as e:
        logger.error("weasyprint library not found")
        raise MissingDependencyError(
            "PDF export requires the 'weasyprint' library. Install with: pip install weasyprint",
            dependency_name="weasyprint"
        )
    
    try:
        logger.info(f"Starting PDF export to {output_path}")
        
        # Create a temporary HTML file with proper styling
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp:
            # Add PDF-specific styling
            pdf_html = _prepare_html_for_pdf(html_content, client_style)
            tmp.write(pdf_html)
            tmp_path = tmp.name
        
        logger.debug(f"Temporary HTML file created: {tmp_path}")
        
        # Configure fonts
        font_config = FontConfiguration()
        
        # Add print-specific CSS
        print_css = CSS(string=_get_print_css(), font_config=font_config)
        
        # Convert HTML to PDF
        HTML(filename=tmp_path).write_pdf(
            output_path,
            stylesheets=[print_css],
            font_config=font_config
        )
        
        # Clean up temporary file
        try:
            os.unlink(tmp_path)
            logger.debug(f"Cleaned up temporary file: {tmp_path}")
        except Exception:
            pass
        
        logger.info(f"PDF exported successfully: {output_path}")
        return True, f"PDF exported successfully to {output_path}"
    
    except MissingDependencyError:
        # Re-raise dependency errors
        raise
    
    except PermissionError as e:
        logger.error(f"Permission denied writing PDF: {e}")
        raise PDFExportError(
            f"Permission denied: Cannot write to {Path(output_path).name}",
            output_path=output_path
        )
    
    except OSError as e:
        logger.error(f"OS error during PDF export: {e}")
        raise PDFExportError(
            f"Failed to write PDF file: {str(e)}",
            output_path=output_path
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error during PDF export: {e}")
        raise PDFExportError(
            f"PDF export failed: {str(e)}",
            output_path=output_path
        )


def _prepare_html_for_pdf(html_content: str, client_style: str) -> str:
    """
    Prepare HTML content for PDF export with proper structure and styling.
    
    Args:
        html_content: Original HTML content
        client_style: Email client style identifier
    
    Returns:
        Modified HTML ready for PDF conversion
    """
    # Wrap in proper HTML structure if needed
    if not html_content.strip().lower().startswith('<!doctype') and not html_content.strip().lower().startswith('<html'):
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bulletin Export</title>
</head>
<body>
    {html_content}
</body>
</html>"""
    
    return html_content


def _get_print_css() -> str:
    """
    Get CSS optimized for PDF printing.
    
    Returns:
        CSS string for PDF output
    """
    return """
    @page {
        size: Letter;
        margin: 0.75in;
    }
    
    body {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.5;
        color: #333;
        max-width: 7in;
        margin: 0 auto;
    }
    
    h1 {
        font-size: 18pt;
        font-weight: 600;
        margin-top: 12pt;
        margin-bottom: 8pt;
        page-break-after: avoid;
    }
    
    h2 {
        font-size: 14pt;
        font-weight: 600;
        margin-top: 10pt;
        margin-bottom: 6pt;
        page-break-after: avoid;
    }
    
    h3 {
        font-size: 12pt;
        font-weight: 600;
        margin-top: 8pt;
        margin-bottom: 4pt;
        page-break-after: avoid;
    }
    
    p {
        margin-top: 0;
        margin-bottom: 8pt;
    }
    
    img {
        max-width: 100%;
        height: auto;
        page-break-inside: avoid;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 12pt;
        page-break-inside: avoid;
    }
    
    a {
        color: #2563EB;
        text-decoration: none;
    }
    
    a[href]:after {
        content: " (" attr(href) ")";
        font-size: 9pt;
        color: #666;
    }
    
    /* Prevent orphans and widows */
    p, li {
        orphans: 3;
        widows: 3;
    }
    
    /* Better page breaks */
    h1, h2, h3, h4, h5, h6 {
        page-break-after: avoid;
    }
    
    /* Print-specific adjustments */
    @media print {
        body {
            background: white;
        }
    }
    """


def init(app):
    """
    Initialize PDF exporter module.
    
    Attaches export_to_pdf function to the app for use in export menu.
    """
    app.export_to_pdf = export_to_pdf
