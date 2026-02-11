# Markdown to JIRA and Confluence Markup Syntax Converter

Simple Python utilities for converting from Github-flavored Markdown syntax to Atlassian's custom markup syntax, and vice-versa. Useful for code maintainers and doc writers who use GitHub, JIRA, and Confluence.

## Introduction

This is a simple Python utility to convert Markdown to JIRA and Confluence
markup syntax. It is written in Python, and is designed to be used as a command line tool.

It has been purposely designed to be fully self-contained, requiring no external libraries or dependencies.

It is also designed to be easily extensible, so that it can be easily modified to support additional Markdown syntax.

## Requirements

* Requires Python 3.6 or later.
* Tested on MacOS, Linux, and Windows.

## Installation

### Using pip (recommended)

Install from PyPI using pip:

```bash
pip install md-to-jira
```

The package will install two command-line tools:
- `md2jira` - Convert Markdown to JIRA/Confluence markup
- `jira2md` - Convert JIRA/Confluence markup to Markdown

### From source

Alternatively, you can clone this repository and install from source:

```bash
git clone https://github.com/eshack94/md-to-jira.git
cd md-to-jira
pip install .
```

### Legacy method (not recommended)

You can also clone the repository and run the scripts directly without installation, though this is not recommended:

```bash
python3 md_to_jira.py <file>
python3 jira_to_md.py <file>
```

## Usage and Examples

Below are usage instructions with some simple examples. For each item, the usage syntax is first, followed by an example for illustration purposes.

### Converting from Markdown to JIRA/Confluence Markup Syntax

The `md2jira` command supports two output formats:

| Format | Flag | Description | Best For |
|--------|------|-------------|----------|
| **Markdown** | `-f markdown` | Preserves Markdown syntax | Jira Cloud, newer Confluence (native Markdown support) |
| **Atlassian** | `-f atlassian` | Converts to Jira wiki markup | Jira Server, Data Center, older Confluence |

#### Interactive Mode

When you run `md2jira` without specifying a format, it will prompt you to choose:

```bash
md2jira README.md
# Prompts: Select output format (1=Markdown, 2=Atlassian)
```

#### Specifying Output Format

```bash
# Preserve Markdown syntax (for Jira Cloud with native Markdown support)
md2jira README.md -f markdown

# Convert to Atlassian Text Formatting Notation (for Jira Server/Data Center)
md2jira README.md -f atlassian
```

#### Output to File or Clipboard

```bash
# Save to a file
md2jira README.md -f markdown > README.jira

# Copy to clipboard (macOS)
md2jira README.md -f atlassian | pbcopy

# Copy to clipboard (Linux)
md2jira README.md -f atlassian | xclip -selection clipboard

# Copy to clipboard (Windows)
md2jira README.md -f atlassian | clip
```

#### Format Conversion Reference

| Markdown | Atlassian Notation |
|----------|-------------------|
| `# Header` | `h1. Header` |
| `**bold**` | `*bold*` |
| `*italic*` | `_italic_` |
| `~~strike~~` | `-strike-` |
| `` `code` `` | `{{code}}` |
| `[text](url)` | `[text\|url]` |
| `![alt](url)` | `!url\|alt=alt!` |
| `- item` | `* item` |
| `1. item` | `# item` |
| `> quote` | `bq. quote` |
| ` ```lang ` | `{code:lang}` |
| `---` | `----` |
| `\| header \|` | `\|\|header\|\|` |

### Converting from JIRA/Confluence Markup Syntax to Markdown

```bash
# Convert a Jira/Confluence markup file to markdown and print to stdout
jira2md <jira_file>
jira2md README.jira
```

```bash
# Convert a Jira/Confluence markup file to markdown and save to a file
jira2md <jira_file> > <markdown_file>
jira2md README.jira > README.md
```

```bash
# Convert a Jira/Confluence markup file to markdown and copy to clipboard (MacOS)
jira2md <jira_file> | pbcopy
jira2md README.jira | pbcopy
```

```bash
# Convert a Jira/Confluence markup file to markdown and copy to clipboard (Linux)
jira2md <jira_file> | xclip -selection clipboard
jira2md README.jira | xclip -selection clipboard
```

```bash
# Convert a Jira/Confluence markup file to markdown and copy to clipboard (Windows)
jira2md <jira_file> | clip
jira2md README.jira | clip
```

## Features (implemented and planned)

### Current Features
- [x] Add support for headers 1-6
- [x] Add support for fenced code blocks
    - [x] Do not convert headers in fenced code blocks
    - [x] Support language tags with hyphens (e.g., `html-erb`)
- [x] Add support for indented code blocks
    - [x] Do not convert headers in indented code blocks
- [x] Add support for inline code (backticks) - should be converted to JIRA's monospace syntax
- [x] Add support for bold text
- [x] Add support for italic text
- [x] Add support for strikethrough text
- [x] Add support for unordered lists
- [x] Add support for ordered lists
- [x] Add support for nested lists (both ordered and unordered)
- [x] Add support for in-line style links (with optional title support - titles are stripped)
- [x] Add support for reference-style links (`[text][ref]` and `[text][]`)
- [x] Add support for images (with optional title support)
- [x] Add support for horizontal rules
- [x] Add support for blockquotes
- [x] Add support for tables
- [x] Add support for emojis (GitHub/Slack `:smile:` ↔ Jira `:)`, `(y)`, etc.)
- [x] Add support for task lists
  * **Note**: Added, but this is not supported by JIRA native markup and requires a JIRA plugin to work
- [x] Add `jira_to_md.py` to convert JIRA/Confluence markup to GitHub-flavored Markdown (GFM)
- [x] Add unit tests for both `md_to_jira.py` and `jira_to_md.py` (82 tests passing)
- [x] String-based API (`convert_content()`) in addition to file-based
- [x] Dual output format: Markdown-preserving (for Jira Cloud) or Atlassian notation (for Jira Server)
- [x] Interactive format selection prompt when no format flag is provided
- [x] Command-line argument parsing with `-f`/`--format` option


### Feature Roadmap
- [x] Add support for emojis (GitHub/Slack style `:smile:` ↔ Jira `:)`, `(y)`, etc.)
- [x] Add support for in-line style links with titles (titles are stripped since Jira doesn't support them)
- [x] Add support for reference style links (`[text][ref]` and `[text][]`)
- [x] Add argparse support for command line options (`-f`/`--format`)
- [x] Add interactive format selection prompt
- [x] Add dual output format support (Markdown-preserving vs Atlassian notation)
- [ ] Add support for inline HTML
- [ ] **_Other TBD_**

### Housekeeping action items
- [ ] Add GitHub Actions config to run unit tests, flake8 linting, and other checks
- [ ] Refactor and clean up code once all basic features are implemented
- [ ] Enforce branch protection rules after setting up GitHub Actions and adding unit tests
    - [ ] Require status checks to pass before merging
    - [ ] Require pull requests to be reviewed and approved before merging
    - [ ] Require branches to be up to date before merging
    - [ ] Add git tags for releases

### Why did I start this mini-project?

This project was created as a way to avoid having to use Atlassian's custom markup syntax.

I wanted to be able to write Confluence documentation and JIRA updates using Github-flavored Markdown, and then have a simple way to convert it without having to use an online converter, browser extension, or any third-party libraries or dependencies.

## Additional Resources
* [Markdown Cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
* [GitHub Flavored Markdown Spec](https://github.github.com/gfm/)
* [Atlassian Text Formatting Notation Help](https://jira.atlassian.com/secure/WikiRendererHelpAction.jspa?section=all)
* [Confluence Wiki Markup](https://confluence.atlassian.com/doc/confluence-wiki-markup-251003035.html)
