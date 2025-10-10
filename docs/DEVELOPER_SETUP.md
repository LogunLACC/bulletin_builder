# Developer Setup Guide

Complete guide for setting up a development environment for Bulletin Builder.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
  - [Python Version](#python-version)
  - [Virtual Environment](#virtual-environment)
  - [Installing Dependencies](#installing-dependencies)
- [Development Installation](#development-installation)
- [Running the Application](#running-the-application)
- [Testing](#testing)
  - [Running Tests](#running-tests)
  - [Test Coverage](#test-coverage)
  - [Writing Tests](#writing-tests)
- [Debugging](#debugging)
  - [VS Code Setup](#vs-code-setup)
  - [Logging](#logging)
  - [Common Issues](#common-issues)
- [Code Style & Quality](#code-style--quality)
- [Building & Packaging](#building--packaging)
- [Contributing](#contributing)
  - [Git Workflow](#git-workflow)
  - [Pull Request Guidelines](#pull-request-guidelines)
- [Project Structure](#project-structure)

---

## Prerequisites

### Required

- **Python 3.9 or higher** (tested with 3.13.5)
- **pip** (Python package installer)
- **git** for version control

### Recommended

- **VS Code** with Python extension
- **Windows:** PowerShell 5.1+ or PowerShell Core 7+
- **macOS/Linux:** Bash or Zsh

### Optional

- **PyInstaller** for building executables
- **Inno Setup** (Windows) for creating installers
- **pytest-cov** for test coverage reports

---

## Environment Setup

### Python Version

Check your Python version:

```bash
python --version
# Should show Python 3.9.0 or higher
```

If you need to install or upgrade Python:

- **Windows:** Download from [python.org](https://www.python.org/downloads/)
- **macOS:** Use Homebrew: `brew install python@3.13`
- **Linux:** Use your package manager: `sudo apt install python3.13` (Ubuntu/Debian)

### Virtual Environment

**Highly recommended** to avoid dependency conflicts:

```bash
# Navigate to project directory
cd bulletin_builder

# Create virtual environment
python -m venv venv

# Activate it
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows CMD:
venv\Scripts\activate.bat

# macOS/Linux:
source venv/bin/activate

# Verify activation (you should see (venv) in your prompt)
which python  # Should point to venv/bin/python or venv\Scripts\python.exe
```

**Deactivate when done:**

```bash
deactivate
```

### Installing Dependencies

With your virtual environment activated:

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Install development dependencies (testing, linting)
pip install pytest pytest-cov black flake8 mypy
```

**Verify installation:**

```bash
pip list | grep customtkinter
pip list | grep tkhtmlview
pip list | grep weasyprint
```

---

## Development Installation

Install the package in **editable mode** so changes to the code are immediately reflected:

```bash
# From project root
pip install -e .
```

This creates a link to your source code, so you can edit files and test changes without reinstalling.

**Verify installation:**

```bash
# Check the command is available
bulletin --version

# Check where it's installed
pip show bulletin-builder
```

---

## Running the Application

### GUI Mode

```bash
# Launch the GUI
bulletin --gui

# Or run as a module
python -m bulletin_builder --gui
```

### CLI Mode

```bash
# Show help
bulletin --help

# Import events
bulletin import events.csv

# Export bulletin
bulletin export output.html
```

### Running from Source (During Development)

```bash
# Run the main module directly
python src/bulletin_builder/__main__.py --gui

# Or use the package
python -m bulletin_builder --gui
```

---

## Testing

### Running Tests

The project uses **pytest** for testing:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_smoke.py

# Run specific test function
pytest tests/test_smoke.py::test_app_initialization

# Run tests matching a pattern
pytest -k "email"
```

### Test Coverage

Generate coverage reports:

```bash
# Run tests with coverage
pytest --cov=bulletin_builder --cov-report=html

# View coverage report
# Windows:
start htmlcov/index.html

# macOS:
open htmlcov/index.html

# Linux:
xdg-open htmlcov/index.html
```

**Current coverage:** 163 tests passing, 1 skipped

### Writing Tests

Example test structure:

```python
# tests/test_my_feature.py
import pytest
from bulletin_builder.app_core import exporter

def test_export_html_basic():
    """Test basic HTML export functionality."""
    draft = {
        'title': 'Test Bulletin',
        'date': '2025-10-10',
        'sections': []
    }
    
    output = exporter.export_html(draft, 'test_output.html')
    assert output is not None
    assert 'Test Bulletin' in output

def test_export_html_with_sections():
    """Test HTML export with multiple sections."""
    draft = {
        'title': 'Test',
        'date': '2025-10-10',
        'sections': [
            {'type': 'text', 'title': 'Announcements', 'content': '<p>Test</p>'}
        ]
    }
    
    output = exporter.export_html(draft, 'test_output.html')
    assert 'Announcements' in output
```

**Test fixtures:**

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_draft():
    """Provide a sample draft for testing."""
    return {
        'title': 'Test Bulletin',
        'date': '2025-10-10',
        'sections': []
    }

def test_with_fixture(sample_draft):
    """Use the fixture in your test."""
    assert sample_draft['title'] == 'Test Bulletin'
```

---

## Debugging

### VS Code Setup

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Bulletin Builder GUI",
            "type": "python",
            "request": "launch",
            "module": "bulletin_builder",
            "args": ["--gui"],
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Bulletin Builder CLI",
            "type": "python",
            "request": "launch",
            "module": "bulletin_builder",
            "args": ["export", "output.html"],
            "console": "integratedTerminal"
        },
        {
            "name": "pytest: Current File",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["${file}", "-v"],
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

**Set breakpoints:** Click in the gutter next to line numbers, then press F5 to start debugging.

### Logging

The application uses Python's `logging` module:

```python
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)

# Log messages at different levels
logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.exception("Log exception with stack trace")
```

**Configure logging:**

```python
# In your code or config
from bulletin_builder.app_core.logging_config import configure_logging
import logging

# Set log level
configure_logging(level=logging.DEBUG, console_output=True)
```

**View logs:**

```bash
# Logs are output to console when running in development
python -m bulletin_builder --gui

# Look for log messages like:
# 2025-10-10 14:30:00 [INFO] bulletin_builder.__main__: Application started
```

### Common Issues

#### Import Errors

```bash
# Error: ModuleNotFoundError: No module named 'bulletin_builder'
# Solution: Install in editable mode
pip install -e .
```

#### Tkinter Not Found

```bash
# Error: ModuleNotFoundError: No module named '_tkinter'
# Windows: Reinstall Python with tcl/tk option checked
# macOS: brew install python-tk
# Linux: sudo apt install python3-tk
```

#### WeasyPrint Build Errors

```bash
# Windows: Install GTK3 runtime or use wheels
pip install --only-binary :all: weasyprint

# macOS: Install dependencies
brew install cairo pango gdk-pixbuf libffi

# Linux: Install system libraries
sudo apt install libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0
```

#### Permission Errors During Build

```bash
# Windows: Close all instances of the app before building
taskkill /F /IM bulletin.exe /T
python scripts/build_exe.py
```

---

## Code Style & Quality

### Style Guidelines

- **PEP 8** for Python code style
- **Type hints** for function signatures
- **Docstrings** for all public functions and classes
- **4 spaces** for indentation (no tabs)
- **79-100 characters** max line length

### Code Formatting

Use **Black** for automatic formatting:

```bash
# Format all Python files
black src/ tests/

# Check what would be formatted (dry run)
black --check src/

# Format specific file
black src/bulletin_builder/__main__.py
```

### Linting

Use **flake8** for style checking:

```bash
# Lint all files
flake8 src/ tests/

# Ignore specific errors
flake8 --ignore=E501,W503 src/

# Configuration in .flake8 or setup.cfg
```

### Type Checking

Use **mypy** for static type checking:

```bash
# Check types
mypy src/bulletin_builder/

# Ignore missing imports
mypy --ignore-missing-imports src/
```

---

## Building & Packaging

### Quick Build

```bash
# Close all running instances first!
python scripts/build_exe.py
```

### Validate Build

```bash
# Run validation checks
python scripts/validate_build.py
```

### Platform-Specific Builds

```bash
# Windows
powershell -ExecutionPolicy Bypass -File scripts\force_build_windows.ps1

# macOS
python scripts/build_macos.py

# Linux
python scripts/build_linux.py
# Or with AppImage:
python scripts/build_linux.py --appimage
```

For detailed build instructions, see [docs/BUILDING.md](BUILDING.md).

---

## Contributing

### Git Workflow

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/bulletin_builder.git
   cd bulletin_builder
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/LogunLACC/bulletin_builder.git
   ```

4. **Create a feature branch:**
   ```bash
   git checkout -b feature/my-new-feature
   ```

5. **Make your changes:**
   - Write code
   - Add tests
   - Update documentation

6. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: Add amazing new feature
   
   - Detailed description of changes
   - Reference to roadmap task or issue
   - Any breaking changes noted"
   ```

7. **Keep your branch up to date:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

8. **Push to your fork:**
   ```bash
   git push origin feature/my-new-feature
   ```

9. **Create a Pull Request** on GitHub

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
feat(exporter): Add PDF export with custom margins

- Implemented WeasyPrint integration
- Added margin configuration in settings
- Updated tests for PDF export
- Roadmap: New Features & QoL - PDF export task

Closes #42
```

```bash
fix(importer): Handle malformed CSV files gracefully

- Added try-except for CSV parsing errors
- Display user-friendly error message
- Log detailed error for debugging
- Added tests for error cases

Fixes #38
```

### Pull Request Guidelines

**Before submitting:**

- [ ] Code follows PEP 8 style guidelines
- [ ] All tests pass: `pytest`
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages are clear and follow format
- [ ] PR description explains changes and references issues/roadmap

**PR Template:**

```markdown
## Description
Brief description of changes

## Related Issues
Closes #XX
Relates to roadmap task: [Task Name]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] Added new tests for changes
- [ ] Manually tested in GUI
- [ ] Tested on Windows/macOS/Linux

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] PR is linked to issue/roadmap task
```

---

## Project Structure

```
bulletin_builder/
├── src/
│   └── bulletin_builder/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # CLI entry point and GUI launcher
│       ├── cli.py               # Command-line interface
│       ├── actions_log.py       # Activity logging
│       ├── app_core/            # Core application logic
│       │   ├── config.py        # Configuration management
│       │   ├── drafts.py        # Draft save/load operations
│       │   ├── exporter.py      # HTML/PDF export
│       │   ├── importer.py      # CSV/JSON import
│       │   ├── sections.py      # Section management
│       │   ├── preview.py       # Preview generation
│       │   ├── export_validator.py  # Email compatibility checks
│       │   └── logging_config.py    # Logging setup
│       ├── ui/                  # UI components
│       │   ├── settings.py      # Settings panel
│       │   ├── events.py        # Event editor
│       │   ├── template_gallery.py  # Template browser
│       │   └── tooltip.py       # UI tooltips
│       ├── postprocess/         # Post-processing
│       │   └── email_postprocess.py  # Email HTML optimization
│       └── templates/           # Built-in templates
├── tests/                       # Test suite
│   ├── conftest.py             # pytest configuration
│   ├── test_smoke.py           # Smoke tests
│   ├── test_exporter.py        # Export tests
│   └── test_importer_parser.py # Import tests
├── scripts/                     # Build and utility scripts
│   ├── build_exe.py            # Windows build
│   ├── build_macos.py          # macOS build
│   ├── build_linux.py          # Linux build
│   ├── validate_build.py       # Build validation
│   └── force_build_windows.ps1 # Windows force build
├── packaging/                   # Packaging configuration
│   ├── bulletin_builder.spec   # PyInstaller spec
│   └── bulletin_builder.iss    # Inno Setup script
├── docs/                        # Documentation
│   ├── BUILDING.md             # Build instructions
│   ├── INSTALLERS.md           # Installer creation
│   ├── DEVELOPER_SETUP.md      # This file
│   └── TYPE_HINTS_GUIDE.md     # Type hints guide
├── templates/                   # Additional templates
├── components/                  # Saved components
├── user_drafts/                # User bulletin drafts
├── config.ini.default          # Default configuration
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project metadata
├── README.md                   # Main documentation
├── LICENSE                     # License file
└── roadmap.json               # Development roadmap
```

### Key Modules

- **`__main__.py`**: Application entry point, GUI initialization
- **`cli.py`**: Command-line interface for import/export operations
- **`app_core/`**: Core business logic (draft management, export, import)
- **`ui/`**: GUI components (settings, editors, dialogs)
- **`postprocess/`**: HTML post-processing for email compatibility
- **`templates/`**: Jinja2 templates for rendering bulletins

---

## Additional Resources

- **Architecture Overview:** See [docs/DETAILED_DOCS.md](DETAILED_DOCS.md) (coming soon)
- **Build Instructions:** See [docs/BUILDING.md](BUILDING.md)
- **Installer Creation:** See [docs/INSTALLERS.md](INSTALLERS.md)
- **Type Hints Guide:** See [docs/TYPE_HINTS_GUIDE.md](TYPE_HINTS_GUIDE.md)
- **Roadmap:** See [roadmap.json](../roadmap.json)

---

## Getting Help

- **Issues:** Report bugs or request features on [GitHub Issues](https://github.com/LogunLACC/bulletin_builder/issues)
- **Discussions:** Ask questions in [GitHub Discussions](https://github.com/LogunLACC/bulletin_builder/discussions)
- **Email:** Contact the maintainer at [support email]

---

## License

This project is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

---

**Happy developing! 🚀**
