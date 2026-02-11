# Copilot Instructions for md-to-jira

## Project Overview

This repository contains Python utilities for converting between GitHub-flavored Markdown and Atlassian's JIRA/Confluence markup syntax. The project is intentionally designed to be **self-contained with no external dependencies** (other than build tools) to remain simple and portable.

The package is published to PyPI as `md-to-jira` and can be installed via pip. It provides both command-line tools and a Python API for programmatic use.

## Key Principles

1. **No External Runtime Dependencies**: The core conversion code should remain pure Python with only the standard library. Build/packaging tools (hatchling, pip) are acceptable as development dependencies.
2. **Python 3.6+**: The code must be compatible with Python 3.6 or later.
3. **Simplicity**: Keep the code simple and easy to understand. This is a utility tool, not a complex framework.
4. **Backwards Compatibility**: Maintain compatibility with existing CLI usage and API exports.

## Code Style and Conventions

### Python Style
- Follow PEP 8 conventions with the exception of line length (E501 is ignored in `.flake8`)
- Use descriptive variable names
- Add docstrings to functions when the purpose isn't immediately obvious
- Use type hints sparingly (not required for Python 3.6 compatibility)

### Regular Expressions
- The project heavily uses regex for pattern matching and text conversion
- Be careful with regex order - more specific patterns should come before general ones
- Test regex patterns thoroughly, especially for edge cases

### Comments
- Add comments only when necessary to explain complex logic
- Keep comments concise and meaningful
- Avoid obvious comments that just restate the code

## File Structure

### Source Code
- `src/md_to_jira/` - Main package directory
  - `__init__.py` - Package exports and API
  - `md_to_jira.py` - Converts Markdown to JIRA/Confluence markup
  - `jira_to_md.py` - Converts JIRA/Confluence markup to Markdown

### Legacy Scripts (Backwards Compatibility)
- `md_to_jira.py` - Legacy script in root (still functional)
- `jira_to_md.py` - Legacy script in root (still functional)

### Tests
- `tests/` - Test package directory
  - `__init__.py` - Test package marker
  - `conftest.py` - Pytest fixtures
  - `test_md_to_jira.py` - Unit tests for md_to_jira module
  - `test_jira_to_md.py` - Unit tests for jira_to_md module

### Configuration
- `pyproject.toml` - Package configuration using hatchling build system
- `.flake8` - Flake8 linting configuration (ignores E501 line length)
- `.gitignore` - Ignores build artifacts, __pycache__, dist/, etc.

### CI/CD
- `.github/workflows/publish-to-pypi.yml` - Automated PyPI publishing on releases

## Testing

### Running Tests
```bash
# Recommended: Install with dev dependencies and run pytest
pip install -e ".[dev]"
pytest

# Run with coverage
pytest --cov

# Run specific test class
pytest tests/test_md_to_jira.py::TestMdToJiraAtlassianFormat -v
```

### Test Framework
- Uses `pytest` for testing (installed via `pip install -e ".[dev]"`)
- Also compatible with Python's built-in `unittest` framework
- Tests are located in `tests/` directory
- Test imports should work with both the package structure and legacy scripts
- Configuration in `pyproject.toml` under `[tool.pytest.ini_options]`

### Writing Tests
- Follow the existing test patterns in `test_md_to_jira.py` and `test_jira_to_md.py`
- Use `unittest.TestCase` as the base class
- Use descriptive test method names starting with `test_`
- Test both line-by-line conversion and multiline elements
- Use `textwrap.dedent()` for multiline test strings

## Linting

The project uses flake8 for linting (though it may not be installed in all environments):
```bash
# If flake8 is available
python3 -m flake8 .
```

Configuration is in `.flake8`:
- Line length (E501) is ignored to allow for longer lines when needed

## Command Line Interface

The package provides two command-line tools after installation via pip:

### md2jira - Markdown to JIRA/Confluence

```bash
md2jira <file>              # Interactive mode - prompts for format selection
md2jira <file> -f markdown  # Preserve Markdown syntax (Jira Cloud)
md2jira <file> -f atlassian # Convert to Atlassian notation (Jira Server)
md2jira --help              # Show help with all options
```

**Output Formats:**
- `markdown` - Preserves Markdown syntax for Jira Cloud/Confluence with native Markdown support
- `atlassian` - Converts to Atlassian Text Formatting Notation for Jira Server/Data Center

### jira2md - JIRA/Confluence to Markdown

```bash
jira2md <file>  # Convert to Markdown
```

Both tools:
- Write output to stdout (can be redirected to a file or piped to clipboard)
- Show usage help when run with `--help` or without arguments

## Package API

The package exports functions for programmatic use:

```python
from md_to_jira import (
    # Output format constants
    FORMAT_MARKDOWN,   # 'markdown' - preserve Markdown syntax
    FORMAT_ATLASSIAN,  # 'atlassian' - convert to Jira wiki markup
    
    # Markdown → JIRA functions
    md_convert_line,
    md_convert_inline,
    md_convert_content,
    md_convert_multiline_elements,
    markdown_to_jira,
    
    # JIRA → Markdown functions
    jira_convert_line,
    jira_convert_inline,
    jira_convert_content,
    jira_convert_multiline_elements,
    jira_to_markdown,
    
    # Backwards-compatible aliases
    convert_line,  # alias for md_convert_line
    convert_inline,  # alias for md_convert_inline
    convert_content,  # alias for md_convert_content
    convert_multiline_elements,  # alias for md_convert_multiline_elements
)

# Using with format parameter
from md_to_jira import markdown_to_jira, convert_content, FORMAT_ATLASSIAN

# File-based conversion
result = markdown_to_jira("README.md", output_format=FORMAT_ATLASSIAN)

# String-based conversion
result = convert_content("# Hello **world**", output_format=FORMAT_ATLASSIAN)
# Returns: "h1. Hello *world*"
```

## Common Tasks

### Adding New Markdown/JIRA Syntax Support

1. **Edit the source files** in `src/md_to_jira/` directory (not the root legacy scripts)
2. **For simple inline elements**: Add regex patterns to `convert_line()` function
3. **For multiline elements**: Add regex patterns to `convert_multiline_elements()` function
4. **Handle code blocks carefully**: Use the `in_code_block` flag to avoid converting content inside code blocks
5. **Order matters**: More specific patterns should be processed before general ones
6. **Add tests**: Write unit tests for the new syntax in the appropriate test file
7. **Update version**: Increment version in both `pyproject.toml` and `src/md_to_jira/__init__.py`

### Modifying Existing Conversions

1. **Edit source files** in `src/md_to_jira/` (not root scripts)
2. Check if the conversion happens in `convert_line()` or `convert_multiline_elements()`
3. Update the regex pattern carefully
4. Update or add corresponding unit tests
5. Test with various edge cases
6. Root scripts will be synced if needed for backwards compatibility

## What NOT to Do

- ❌ Do not install packages to system Python - always use the `.venv` virtual environment
- ❌ Do not add external runtime dependencies (no pip packages beyond build tools)
- ❌ Do not use Python features newer than 3.6 (f-strings are acceptable as they were introduced in Python 3.6)
- ❌ Do not break the command-line interface compatibility
- ❌ Do not break the package API exports
- ❌ Do not make changes only to root legacy scripts - always update `src/md_to_jira/` first

## What TO Do

- ✅ **Always use the `.venv` virtual environment** - Create with `python3 -m venv .venv` and activate before any development work
- ✅ Keep the core conversion code self-contained and portable
- ✅ Write unit tests for new functionality
- ✅ Follow the existing code patterns
- ✅ Handle edge cases in regex patterns
- ✅ Maintain backward compatibility with existing CLI and API usage
- ✅ Update documentation (README.md) when adding new features
- ✅ Test code blocks carefully - they shouldn't have their content converted
- ✅ Edit source files in `src/md_to_jira/` for all code changes
- ✅ Update package exports in `__init__.py` when adding new functions
- ✅ Keep version numbers in sync between `pyproject.toml` and `__init__.py`

## Virtual Environment

**IMPORTANT**: Always use a virtual environment (`.venv`) for development. This isolates dependencies and prevents conflicts with system Python packages.

### Setting Up the Virtual Environment

```bash
# Create the virtual environment (if it doesn't exist)
python3 -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# Verify you're in the virtual environment (should show .venv path)
which python3  # macOS/Linux
where python   # Windows
```

### Installing for Development

```bash
# Always activate the virtual environment first!
source .venv/bin/activate  # macOS/Linux

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# This installs:
# - The md-to-jira package in editable mode
# - pytest and pytest-cov for testing
```

## Building and Running

### For Development (from source)

```bash
# Clone the repository
git clone https://github.com/eshack94/md-to-jira.git
cd md-to-jira

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov
```

### Building the Package

```bash
# Ensure virtual environment is active
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install build tools
pip install build

# Build distribution packages
python -m build

# This creates dist/ directory with wheel and source distributions
```

### Using the Package

```bash
# For development (in virtual environment)
source .venv/bin/activate
pip install -e ".[dev]"

# Or install from PyPI (in any environment)
pip install md-to-jira

# Use command-line tools
md2jira <markdown_file>                # Interactive format selection
md2jira <markdown_file> -f markdown    # Preserve Markdown (Jira Cloud)
md2jira <markdown_file> -f atlassian   # Atlassian notation (Jira Server)
jira2md <jira_file>                    # Convert JIRA to Markdown
```

## Packaging and Releases

### Package Configuration
- **Build system**: `hatchling` (specified in `pyproject.toml`)
- **Package name**: `md-to-jira` (published to PyPI)
- **Version**: Maintained in both `pyproject.toml` and `src/md_to_jira/__init__.py`
- **Entry points**: `md2jira` and `jira2md` command-line scripts

### Release Process
1. Update version in `pyproject.toml` and `src/md_to_jira/__init__.py`
2. Update CHANGELOG or release notes if applicable
3. Create a GitHub release with a tag (e.g., `v1.0.0`)
4. GitHub Actions workflow automatically builds and publishes to PyPI

### Distribution Files
- `.gitignore` excludes build artifacts: `dist/`, `build/`, `*.egg-info/`, `__pycache__/`
- Source distribution (sdist) includes: `src/`, `test_*.py`, `README.md`, `LICENSE`
- Wheel distribution packages the `md_to_jira` package from `src/`

## Feature Roadmap

The README.md contains a feature roadmap. When implementing features from the roadmap:
1. Check the current status in README.md
2. Follow the existing patterns for similar features
3. Add comprehensive tests
4. Update the task list checkboxes (`- [ ]` to `- [x]`) in README.md for completed features
