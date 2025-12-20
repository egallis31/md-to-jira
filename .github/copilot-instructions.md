# Copilot Instructions for md-to-jira

## Project Overview

This repository contains Python utilities for converting between GitHub-flavored Markdown and Atlassian's JIRA/Confluence markup syntax. The project is intentionally designed to be **self-contained with no external dependencies** to remain simple and portable.

## Key Principles

1. **No External Dependencies**: This is a core design principle. Do not add any pip packages or external libraries. The code should remain pure Python with only the standard library.
2. **Python 3.6+**: The code must be compatible with Python 3.6 or later.
3. **Simplicity**: Keep the code simple and easy to understand. This is a utility tool, not a complex framework.

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

- `md_to_jira.py` - Converts Markdown to JIRA/Confluence markup
- `jira_to_md.py` - Converts JIRA/Confluence markup to Markdown
- `test_md_to_jira.py` - Unit tests for md_to_jira.py
- `test_jira_to_md.py` - Unit tests for jira_to_md.py
- `.flake8` - Flake8 linting configuration (ignores E501 line length)

## Testing

### Running Tests
```bash
# Run all tests
python3 -m unittest discover -s . -p "test_*.py" -v

# Run specific test file
python3 -m unittest test_md_to_jira.py -v
python3 -m unittest test_jira_to_md.py -v
```

### Test Framework
- Uses Python's built-in `unittest` framework
- No pytest or other external testing frameworks
- Tests should be in files prefixed with `test_`

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

Both scripts are designed as command-line tools:
- Accept a file path as the first argument
- Write output to stdout (can be redirected to a file or piped to clipboard)
- Show usage help when run without arguments

## Common Tasks

### Adding New Markdown/JIRA Syntax Support

1. **For simple inline elements**: Add regex patterns to `convert_line()` function
2. **For multiline elements**: Add regex patterns to `convert_multiline_elements()` function
3. **Handle code blocks carefully**: Use the `in_code_block` flag to avoid converting content inside code blocks
4. **Order matters**: More specific patterns should be processed before general ones
5. **Add tests**: Write unit tests for the new syntax in the appropriate test file

### Modifying Existing Conversions

1. Check if the conversion happens in `convert_line()` or `convert_multiline_elements()`
2. Update the regex pattern carefully
3. Update or add corresponding unit tests
4. Test with various edge cases

## What NOT to Do

- ❌ Do not add external dependencies (no pip packages)
- ❌ Do not use Python features newer than 3.6 (f-strings are acceptable as they were introduced in Python 3.6)
- ❌ Do not add complex build systems or package managers
- ❌ Do not make the code overly complex or add unnecessary abstractions
- ❌ Do not break the command-line interface compatibility

## What TO Do

- ✅ Keep the code self-contained and portable
- ✅ Write unit tests for new functionality
- ✅ Follow the existing code patterns
- ✅ Handle edge cases in regex patterns
- ✅ Maintain backward compatibility with existing command-line usage
- ✅ Update documentation (README.md) when adding new features
- ✅ Test code blocks carefully - they shouldn't have their content converted

## Building and Running

No build step is required. The scripts can be run directly:

```bash
# Convert Markdown to JIRA
python3 md_to_jira.py <markdown_file>

# Convert JIRA to Markdown
python3 jira_to_md.py <jira_file>
```

## Feature Roadmap

The README.md contains a feature roadmap. When implementing features from the roadmap:
1. Check the current status in README.md
2. Follow the existing patterns for similar features
3. Add comprehensive tests
4. Update the task list checkboxes (`- [ ]` to `- [x]`) in README.md for completed features
