"""
Input validation utilities for Bulletin Builder.

Provides comprehensive validation for all user inputs including URLs, file paths,
JSON/CSV data, and configuration values with clear error messages and suggestions.
"""

import re
import json
import csv
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any
from urllib.parse import urlparse
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)


class ValidationResult:
    """
    Result of a validation operation.
    
    Contains validation status, error messages, warnings, and suggestions.
    """
    
    def __init__(self, is_valid: bool = True, 
                 error: Optional[str] = None,
                 warnings: Optional[List[str]] = None,
                 suggestions: Optional[List[str]] = None):
        """
        Initialize validation result.
        
        Args:
            is_valid: Whether the validation passed
            error: Error message if validation failed
            warnings: List of warning messages
            suggestions: List of suggestions for fixing issues
        """
        self.is_valid = is_valid
        self.error = error
        self.warnings = warnings or []
        self.suggestions = suggestions or []
    
    def __bool__(self) -> bool:
        """Allow using ValidationResult in boolean context."""
        return self.is_valid
    
    def __str__(self) -> str:
        """String representation of validation result."""
        if self.is_valid:
            return "Valid"
        parts = [f"Error: {self.error}"]
        if self.warnings:
            parts.append(f"Warnings: {', '.join(self.warnings)}")
        if self.suggestions:
            parts.append(f"Suggestions: {', '.join(self.suggestions)}")
        return " | ".join(parts)


class URLValidator:
    """Validator for URLs (events feeds, image URLs, etc.)."""
    
    @staticmethod
    def validate_url(url: str, require_https: bool = False) -> ValidationResult:
        """
        Validate a URL for proper format and accessibility.
        
        Args:
            url: URL to validate
            require_https: Whether to require HTTPS protocol
        
        Returns:
            ValidationResult with validation status and messages
        """
        if not url or not url.strip():
            return ValidationResult(
                is_valid=False,
                error="URL cannot be empty",
                suggestions=["Enter a valid URL starting with http:// or https://"]
            )
        
        url = url.strip()
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error=f"Invalid URL format: {str(e)}",
                suggestions=[
                    "Check for typos in the URL",
                    "Ensure the URL starts with http:// or https://",
                    "Remove any special characters that may not be allowed"
                ]
            )
        
        # Check scheme
        if not parsed.scheme:
            return ValidationResult(
                is_valid=False,
                error="URL must include a protocol (http:// or https://)",
                suggestions=[f"Try: https://{url}"]
            )
        
        if parsed.scheme not in ['http', 'https']:
            return ValidationResult(
                is_valid=False,
                error=f"Invalid protocol: {parsed.scheme}. Only http:// and https:// are supported",
                suggestions=[f"Change protocol to: https://{parsed.netloc}{parsed.path}"]
            )
        
        # Check for HTTPS requirement
        warnings = []
        suggestions = []
        
        if require_https and parsed.scheme != 'https':
            warnings.append("Using HTTP instead of HTTPS may be insecure")
            suggestions.append(f"Consider using: https://{parsed.netloc}{parsed.path}")
        
        # Check netloc (domain)
        if not parsed.netloc:
            return ValidationResult(
                is_valid=False,
                error="URL must include a domain name",
                suggestions=["Example: https://example.com/path"]
            )
        
        # Check for common mistakes
        if '..' in parsed.path or '//' in parsed.path.replace('//', '', 1):
            warnings.append("URL contains unusual path patterns (.. or //)")
        
        # Check for spaces (should be encoded)
        if ' ' in url:
            return ValidationResult(
                is_valid=False,
                error="URL contains spaces",
                suggestions=[
                    "Replace spaces with %20 or hyphens",
                    f"Try: {url.replace(' ', '%20')}"
                ]
            )
        
        logger.debug(f"URL validation passed: {url}")
        return ValidationResult(is_valid=True, warnings=warnings, suggestions=suggestions)
    
    @staticmethod
    def validate_image_url(url: str) -> ValidationResult:
        """
        Validate an image URL.
        
        Args:
            url: Image URL to validate
        
        Returns:
            ValidationResult with validation status and messages
        """
        # First validate as regular URL
        result = URLValidator.validate_url(url, require_https=False)
        if not result.is_valid:
            return result
        
        # Check file extension
        parsed = urlparse(url)
        path_lower = parsed.path.lower()
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']
        has_image_extension = any(path_lower.endswith(ext) for ext in image_extensions)
        
        warnings = result.warnings.copy()
        suggestions = result.suggestions.copy()
        
        if not has_image_extension and '?' not in parsed.path:
            warnings.append("URL doesn't have a common image extension")
            suggestions.append("Verify this URL points to an image file")
        
        logger.debug(f"Image URL validation passed: {url}")
        return ValidationResult(is_valid=True, warnings=warnings, suggestions=suggestions)


class FilePathValidator:
    """Validator for file paths."""
    
    @staticmethod
    def validate_path(path: str, must_exist: bool = False, 
                     must_be_file: bool = False,
                     must_be_dir: bool = False,
                     allowed_extensions: Optional[List[str]] = None) -> ValidationResult:
        """
        Validate a file path.
        
        Args:
            path: File path to validate
            must_exist: Whether the path must exist
            must_be_file: Whether the path must be a file
            must_be_dir: Whether the path must be a directory
            allowed_extensions: List of allowed file extensions (e.g., ['.json', '.csv'])
        
        Returns:
            ValidationResult with validation status and messages
        """
        if not path or not path.strip():
            return ValidationResult(
                is_valid=False,
                error="Path cannot be empty",
                suggestions=["Enter a valid file or directory path"]
            )
        
        path = path.strip()
        
        # Check for invalid characters
        invalid_chars = ['<', '>', '|', '\0']
        for char in invalid_chars:
            if char in path:
                return ValidationResult(
                    is_valid=False,
                    error=f"Path contains invalid character: {char}",
                    suggestions=[
                        "Remove special characters from the path",
                        "Use only letters, numbers, hyphens, underscores, and forward/back slashes"
                    ]
                )
        
        # Convert to Path object
        try:
            path_obj = Path(path)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error=f"Invalid path format: {str(e)}",
                suggestions=["Check for typos in the path"]
            )
        
        warnings = []
        suggestions = []
        
        # Check existence
        if must_exist and not path_obj.exists():
            return ValidationResult(
                is_valid=False,
                error=f"Path does not exist: {path}",
                suggestions=[
                    "Check the path for typos",
                    "Verify the file or directory exists",
                    "Use the Browse button to select the file"
                ]
            )
        
        # Check if file
        if must_be_file and path_obj.exists() and not path_obj.is_file():
            return ValidationResult(
                is_valid=False,
                error=f"Path is not a file: {path}",
                suggestions=["Select a file, not a directory"]
            )
        
        # Check if directory
        if must_be_dir and path_obj.exists() and not path_obj.is_dir():
            return ValidationResult(
                is_valid=False,
                error=f"Path is not a directory: {path}",
                suggestions=["Select a directory, not a file"]
            )
        
        # Check extension
        if allowed_extensions and path_obj.suffix:
            if path_obj.suffix.lower() not in [ext.lower() for ext in allowed_extensions]:
                return ValidationResult(
                    is_valid=False,
                    error=f"Invalid file extension: {path_obj.suffix}",
                    suggestions=[
                        f"Allowed extensions: {', '.join(allowed_extensions)}",
                        "Make sure you selected the correct file type"
                    ]
                )
        
        # Check for very long paths (Windows limitation)
        if len(str(path_obj.absolute())) > 260:
            warnings.append("Path is very long (>260 characters) and may cause issues on Windows")
            suggestions.append("Consider using a shorter path or enabling long path support in Windows")
        
        logger.debug(f"Path validation passed: {path}")
        return ValidationResult(is_valid=True, warnings=warnings, suggestions=suggestions)


class JSONValidator:
    """Validator for JSON data."""
    
    @staticmethod
    def validate_json_string(json_string: str) -> ValidationResult:
        """
        Validate a JSON string.
        
        Args:
            json_string: JSON string to validate
        
        Returns:
            ValidationResult with validation status and messages
        """
        if not json_string or not json_string.strip():
            return ValidationResult(
                is_valid=False,
                error="JSON content cannot be empty",
                suggestions=["Enter valid JSON content"]
            )
        
        try:
            json.loads(json_string)
            logger.debug("JSON validation passed")
            return ValidationResult(is_valid=True)
        except json.JSONDecodeError as e:
            # Extract useful error information
            line_num = e.lineno
            col_num = e.colno
            error_msg = str(e.msg)
            
            suggestions = [
                f"Check line {line_num}, column {col_num}",
                "Common issues:",
                "  • Missing comma between items",
                "  • Missing closing bracket/brace",
                "  • Unquoted strings (use double quotes)",
                "  • Trailing commas (not allowed in JSON)"
            ]
            
            # Add specific suggestions based on error
            if "Expecting" in error_msg:
                suggestions.insert(1, f"Expected: {error_msg.split('Expecting ')[-1]}")
            
            return ValidationResult(
                is_valid=False,
                error=f"Invalid JSON syntax: {error_msg}",
                suggestions=suggestions
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error=f"JSON parsing error: {str(e)}",
                suggestions=["Verify the JSON syntax is correct"]
            )
    
    @staticmethod
    def validate_json_file(file_path: str) -> ValidationResult:
        """
        Validate a JSON file.
        
        Args:
            file_path: Path to JSON file
        
        Returns:
            ValidationResult with validation status and messages
        """
        # First validate the path
        path_result = FilePathValidator.validate_path(
            file_path, 
            must_exist=True, 
            must_be_file=True,
            allowed_extensions=['.json']
        )
        
        if not path_result.is_valid:
            return path_result
        
        # Read and validate JSON content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return JSONValidator.validate_json_string(content)
        except PermissionError:
            return ValidationResult(
                is_valid=False,
                error=f"Permission denied reading file: {file_path}",
                suggestions=[
                    "Check file permissions",
                    "Close the file if it's open in another program",
                    "Run the application as administrator"
                ]
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error=f"Error reading JSON file: {str(e)}",
                suggestions=["Verify the file is accessible and not corrupted"]
            )


class CSVValidator:
    """Validator for CSV data."""
    
    @staticmethod
    def validate_csv_file(file_path: str, 
                         required_columns: Optional[List[str]] = None) -> ValidationResult:
        """
        Validate a CSV file.
        
        Args:
            file_path: Path to CSV file
            required_columns: List of required column names
        
        Returns:
            ValidationResult with validation status and messages
        """
        # First validate the path
        path_result = FilePathValidator.validate_path(
            file_path,
            must_exist=True,
            must_be_file=True,
            allowed_extensions=['.csv']
        )
        
        if not path_result.is_valid:
            return path_result
        
        warnings = []
        suggestions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', newline='') as f:
                # Try to detect CSV dialect
                sample = f.read(4096)
                f.seek(0)
                
                try:
                    dialect = csv.Sniffer().sniff(sample)
                except csv.Error:
                    warnings.append("Could not detect CSV format, using default")
                    dialect = csv.excel
                
                # Read CSV
                reader = csv.DictReader(f, dialect=dialect)
                
                # Check for headers
                if not reader.fieldnames:
                    return ValidationResult(
                        is_valid=False,
                        error="CSV file has no headers",
                        suggestions=[
                            "Add a header row with column names",
                            "Example: Title,Date,Description"
                        ]
                    )
                
                # Check required columns
                if required_columns:
                    missing_cols = [col for col in required_columns 
                                   if col not in reader.fieldnames]
                    if missing_cols:
                        return ValidationResult(
                            is_valid=False,
                            error=f"Missing required columns: {', '.join(missing_cols)}",
                            suggestions=[
                                f"Add these columns to the CSV: {', '.join(missing_cols)}",
                                f"Found columns: {', '.join(reader.fieldnames)}"
                            ]
                        )
                
                # Read first few rows to check for data
                rows = list(reader)
                if not rows:
                    warnings.append("CSV file contains no data rows")
                    suggestions.append("Add data rows below the header row")
                elif len(rows) < 2:
                    warnings.append(f"CSV file contains only {len(rows)} data row")
                
                logger.debug(f"CSV validation passed: {file_path}")
                return ValidationResult(is_valid=True, warnings=warnings, suggestions=suggestions)
                
        except PermissionError:
            return ValidationResult(
                is_valid=False,
                error=f"Permission denied reading file: {file_path}",
                suggestions=[
                    "Check file permissions",
                    "Close the file if it's open in Excel or another program",
                    "Run the application as administrator"
                ]
            )
        except UnicodeDecodeError:
            return ValidationResult(
                is_valid=False,
                error="File encoding error - file may not be UTF-8",
                suggestions=[
                    "Save the CSV file with UTF-8 encoding",
                    "In Excel: Save As → CSV UTF-8 (Comma delimited)"
                ]
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error=f"Error reading CSV file: {str(e)}",
                suggestions=[
                    "Verify the file is a valid CSV",
                    "Check for corrupted data or special characters",
                    "Try opening the file in a text editor to check format"
                ]
            )


class EmailValidator:
    """Validator for email addresses."""
    
    @staticmethod
    def validate_email(email: str) -> ValidationResult:
        """
        Validate an email address.
        
        Args:
            email: Email address to validate
        
        Returns:
            ValidationResult with validation status and messages
        """
        if not email or not email.strip():
            return ValidationResult(
                is_valid=False,
                error="Email address cannot be empty",
                suggestions=["Enter a valid email address"]
            )
        
        email = email.strip()
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            suggestions = [
                "Email format should be: user@domain.com",
                "Check for typos or missing characters"
            ]
            
            # Provide specific suggestions based on common mistakes
            if '@' not in email:
                suggestions.insert(0, "Email must contain @ symbol")
            elif email.count('@') > 1:
                suggestions.insert(0, "Email should contain only one @ symbol")
            elif '.' not in email.split('@')[-1]:
                suggestions.insert(0, "Domain must contain a period (e.g., .com, .org)")
            
            return ValidationResult(
                is_valid=False,
                error="Invalid email format",
                suggestions=suggestions
            )
        
        warnings = []
        
        # Check for common disposable email domains
        domain = email.split('@')[1].lower()
        disposable_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
        if domain in disposable_domains:
            warnings.append(f"Using disposable email domain: {domain}")
        
        logger.debug(f"Email validation passed: {email}")
        return ValidationResult(is_valid=True, warnings=warnings)


def init(app) -> None:
    """
    Initialize input validators.
    
    Args:
        app: Main application instance
    """
    # Attach validators to app for easy access
    app.url_validator = URLValidator()
    app.file_validator = FilePathValidator()
    app.json_validator = JSONValidator()
    app.csv_validator = CSVValidator()
    app.email_validator = EmailValidator()
    
    logger.info("Input validators initialized")
