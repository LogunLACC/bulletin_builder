"""
Tests for input validation functionality.
"""

import pytest
import json
import csv
from pathlib import Path
from unittest.mock import Mock
from bulletin_builder.app_core.input_validators import (
    ValidationResult,
    URLValidator,
    FilePathValidator,
    JSONValidator,
    CSVValidator,
    EmailValidator
)


class TestValidationResult:
    """Test ValidationResult class."""
    
    def test_valid_result(self):
        """Test valid validation result."""
        result = ValidationResult(is_valid=True)
        
        assert result.is_valid
        assert bool(result) is True
        assert result.error is None
        assert result.warnings == []
        assert result.suggestions == []
        assert str(result) == "Valid"
    
    def test_invalid_result(self):
        """Test invalid validation result."""
        result = ValidationResult(
            is_valid=False,
            error="Test error",
            warnings=["Warning 1"],
            suggestions=["Fix this", "Or that"]
        )
        
        assert not result.is_valid
        assert bool(result) is False
        assert result.error == "Test error"
        assert len(result.warnings) == 1
        assert len(result.suggestions) == 2
        assert "Error: Test error" in str(result)


class TestURLValidator:
    """Test URL validation."""
    
    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        result = URLValidator.validate_url("http://example.com")
        assert result.is_valid
    
    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        result = URLValidator.validate_url("https://example.com/path")
        assert result.is_valid
    
    def test_empty_url(self):
        """Test empty URL."""
        result = URLValidator.validate_url("")
        assert not result.is_valid
        assert "empty" in result.error.lower()
    
    def test_url_without_protocol(self):
        """Test URL without protocol."""
        result = URLValidator.validate_url("example.com")
        assert not result.is_valid
        assert "protocol" in result.error.lower()
    
    def test_url_with_invalid_protocol(self):
        """Test URL with invalid protocol."""
        result = URLValidator.validate_url("ftp://example.com")
        assert not result.is_valid
        assert "protocol" in result.error.lower()
    
    def test_url_without_domain(self):
        """Test URL without domain."""
        result = URLValidator.validate_url("https://")
        assert not result.is_valid
        assert "domain" in result.error.lower()
    
    def test_url_with_spaces(self):
        """Test URL with spaces."""
        result = URLValidator.validate_url("https://example.com/path with spaces")
        assert not result.is_valid
        assert "spaces" in result.error.lower()
    
    def test_http_url_with_https_requirement(self):
        """Test HTTP URL when HTTPS is required."""
        result = URLValidator.validate_url("http://example.com", require_https=True)
        assert result.is_valid  # Still valid, but with warnings
        assert len(result.warnings) > 0
        assert "insecure" in result.warnings[0].lower()
    
    def test_https_url_with_https_requirement(self):
        """Test HTTPS URL when HTTPS is required."""
        result = URLValidator.validate_url("https://example.com", require_https=True)
        assert result.is_valid
        assert len(result.warnings) == 0
    
    def test_url_with_query_parameters(self):
        """Test URL with query parameters."""
        result = URLValidator.validate_url("https://example.com/path?key=value&foo=bar")
        assert result.is_valid
    
    def test_image_url_with_extension(self):
        """Test image URL with valid extension."""
        result = URLValidator.validate_image_url("https://example.com/image.jpg")
        assert result.is_valid
    
    def test_image_url_without_extension(self):
        """Test image URL without extension."""
        result = URLValidator.validate_image_url("https://example.com/image")
        assert result.is_valid  # Valid but with warnings
        assert len(result.warnings) > 0
    
    def test_image_url_with_query_string(self):
        """Test image URL with query string (common for CDNs)."""
        result = URLValidator.validate_image_url("https://cdn.example.com/img?id=123")
        assert result.is_valid


class TestFilePathValidator:
    """Test file path validation."""
    
    def test_empty_path(self):
        """Test empty path."""
        result = FilePathValidator.validate_path("")
        assert not result.is_valid
        assert "empty" in result.error.lower()
    
    def test_path_with_invalid_characters(self):
        """Test path with invalid characters."""
        result = FilePathValidator.validate_path("path/with<invalid>chars")
        assert not result.is_valid
        assert "invalid character" in result.error.lower()
    
    def test_valid_path(self, tmp_path):
        """Test valid path."""
        result = FilePathValidator.validate_path(str(tmp_path))
        assert result.is_valid
    
    def test_nonexistent_path_when_required(self):
        """Test nonexistent path when existence is required."""
        result = FilePathValidator.validate_path(
            "/nonexistent/path/file.txt",
            must_exist=True
        )
        assert not result.is_valid
        assert "does not exist" in result.error.lower()
    
    def test_existing_file_path(self, tmp_path):
        """Test existing file path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        result = FilePathValidator.validate_path(
            str(test_file),
            must_exist=True,
            must_be_file=True
        )
        assert result.is_valid
    
    def test_directory_when_file_required(self, tmp_path):
        """Test directory when file is required."""
        result = FilePathValidator.validate_path(
            str(tmp_path),
            must_exist=True,
            must_be_file=True
        )
        assert not result.is_valid
        assert "not a file" in result.error.lower()
    
    def test_file_when_directory_required(self, tmp_path):
        """Test file when directory is required."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        result = FilePathValidator.validate_path(
            str(test_file),
            must_exist=True,
            must_be_dir=True
        )
        assert not result.is_valid
        assert "not a directory" in result.error.lower()
    
    def test_invalid_file_extension(self, tmp_path):
        """Test invalid file extension."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        result = FilePathValidator.validate_path(
            str(test_file),
            must_exist=True,
            allowed_extensions=['.json', '.csv']
        )
        assert not result.is_valid
        assert "extension" in result.error.lower()
    
    def test_valid_file_extension(self, tmp_path):
        """Test valid file extension."""
        test_file = tmp_path / "test.json"
        test_file.write_text("{}")
        
        result = FilePathValidator.validate_path(
            str(test_file),
            must_exist=True,
            allowed_extensions=['.json', '.csv']
        )
        assert result.is_valid


class TestJSONValidator:
    """Test JSON validation."""
    
    def test_valid_json_string(self):
        """Test valid JSON string."""
        json_string = '{"key": "value", "number": 123}'
        result = JSONValidator.validate_json_string(json_string)
        assert result.is_valid
    
    def test_empty_json_string(self):
        """Test empty JSON string."""
        result = JSONValidator.validate_json_string("")
        assert not result.is_valid
        assert "empty" in result.error.lower()
    
    def test_invalid_json_syntax(self):
        """Test invalid JSON syntax."""
        json_string = '{"key": "value"'  # Missing closing brace
        result = JSONValidator.validate_json_string(json_string)
        assert not result.is_valid
        assert "syntax" in result.error.lower()
    
    def test_json_with_trailing_comma(self):
        """Test JSON with trailing comma."""
        json_string = '{"key": "value",}'
        result = JSONValidator.validate_json_string(json_string)
        assert not result.is_valid
    
    def test_json_with_unquoted_keys(self):
        """Test JSON with unquoted keys."""
        json_string = '{key: "value"}'
        result = JSONValidator.validate_json_string(json_string)
        assert not result.is_valid
    
    def test_valid_json_file(self, tmp_path):
        """Test valid JSON file."""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}', encoding='utf-8')
        
        result = JSONValidator.validate_json_file(str(json_file))
        assert result.is_valid
    
    def test_invalid_json_file(self, tmp_path):
        """Test invalid JSON file."""
        json_file = tmp_path / "test.json"
        json_file.write_text('invalid json', encoding='utf-8')
        
        result = JSONValidator.validate_json_file(str(json_file))
        assert not result.is_valid
    
    def test_nonexistent_json_file(self):
        """Test nonexistent JSON file."""
        result = JSONValidator.validate_json_file("/nonexistent/file.json")
        assert not result.is_valid


class TestCSVValidator:
    """Test CSV validation."""
    
    def test_valid_csv_file(self, tmp_path):
        """Test valid CSV file."""
        csv_file = tmp_path / "test.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Age', 'City'])
            writer.writerow(['Alice', '30', 'New York'])
            writer.writerow(['Bob', '25', 'Los Angeles'])
        
        result = CSVValidator.validate_csv_file(str(csv_file))
        assert result.is_valid
    
    def test_csv_with_required_columns(self, tmp_path):
        """Test CSV with required columns."""
        csv_file = tmp_path / "test.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Age'])
            writer.writerow(['Alice', '30'])
        
        result = CSVValidator.validate_csv_file(
            str(csv_file),
            required_columns=['Name', 'Age']
        )
        assert result.is_valid
    
    def test_csv_missing_required_columns(self, tmp_path):
        """Test CSV missing required columns."""
        csv_file = tmp_path / "test.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name'])
            writer.writerow(['Alice'])
        
        result = CSVValidator.validate_csv_file(
            str(csv_file),
            required_columns=['Name', 'Age', 'City']
        )
        assert not result.is_valid
        assert "missing required columns" in result.error.lower()
    
    def test_csv_with_no_data(self, tmp_path):
        """Test CSV with no data rows."""
        csv_file = tmp_path / "test.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Age'])
        
        result = CSVValidator.validate_csv_file(str(csv_file))
        assert result.is_valid  # Valid but with warnings
        assert len(result.warnings) > 0
    
    def test_empty_csv_file(self, tmp_path):
        """Test empty CSV file."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("", encoding='utf-8')
        
        result = CSVValidator.validate_csv_file(str(csv_file))
        assert not result.is_valid
    
    def test_nonexistent_csv_file(self):
        """Test nonexistent CSV file."""
        result = CSVValidator.validate_csv_file("/nonexistent/file.csv")
        assert not result.is_valid


class TestEmailValidator:
    """Test email validation."""
    
    def test_valid_email(self):
        """Test valid email address."""
        result = EmailValidator.validate_email("user@example.com")
        assert result.is_valid
    
    def test_empty_email(self):
        """Test empty email."""
        result = EmailValidator.validate_email("")
        assert not result.is_valid
        assert "empty" in result.error.lower()
    
    def test_email_without_at(self):
        """Test email without @ symbol."""
        result = EmailValidator.validate_email("userexample.com")
        assert not result.is_valid
        assert "@" in result.suggestions[0]
    
    def test_email_with_multiple_at(self):
        """Test email with multiple @ symbols."""
        result = EmailValidator.validate_email("user@@example.com")
        assert not result.is_valid
    
    def test_email_without_domain(self):
        """Test email without domain."""
        result = EmailValidator.validate_email("user@")
        assert not result.is_valid
    
    def test_email_without_tld(self):
        """Test email without top-level domain."""
        result = EmailValidator.validate_email("user@example")
        assert not result.is_valid
        assert "period" in result.suggestions[0].lower()
    
    def test_valid_email_with_plus(self):
        """Test valid email with plus sign."""
        result = EmailValidator.validate_email("user+tag@example.com")
        assert result.is_valid
    
    def test_valid_email_with_dots(self):
        """Test valid email with dots."""
        result = EmailValidator.validate_email("first.last@example.co.uk")
        assert result.is_valid
    
    def test_disposable_email_domain(self):
        """Test disposable email domain."""
        result = EmailValidator.validate_email("test@tempmail.com")
        assert result.is_valid  # Valid but with warnings
        assert len(result.warnings) > 0
        assert "disposable" in result.warnings[0].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
