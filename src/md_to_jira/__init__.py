"""Markdown to JIRA and Confluence Markup Syntax Converter."""

try:
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version("md-to-jira")
    except PackageNotFoundError:
        __version__ = "0.0.0.dev0"  # Package not installed
except ImportError:
    # Python < 3.8
    __version__ = "0.0.0.dev0"

from .md_to_jira import (
    convert_line as md_convert_line,
    convert_inline as md_convert_inline,
    convert_multiline_elements as md_convert_multiline_elements,
    convert_content as md_convert_content,
    convert_table_row as md_convert_table_row,
    is_table_separator as md_is_table_separator,
    resolve_reference_links as md_resolve_reference_links,
    convert_emoji_md_to_jira,
    EMOJI_MD_TO_JIRA,
    markdown_to_jira,
    FORMAT_MARKDOWN,
    FORMAT_ATLASSIAN,
)
from .jira_to_md import convert_line as jira_convert_line
from .jira_to_md import convert_inline as jira_convert_inline
from .jira_to_md import convert_multiline_elements as jira_convert_multiline_elements
from .jira_to_md import convert_content as jira_convert_content
from .jira_to_md import convert_table_row as jira_convert_table_row
from .jira_to_md import is_jira_table_row
from .jira_to_md import convert_emoji_jira_to_md
from .jira_to_md import EMOJI_JIRA_TO_MD
from .jira_to_md import jira_to_markdown

# Backwards-compatible aliases for existing API names
convert_line = md_convert_line
convert_inline = md_convert_inline
convert_multiline_elements = md_convert_multiline_elements
convert_content = md_convert_content

__all__ = [
    # Output format constants
    "FORMAT_MARKDOWN",
    "FORMAT_ATLASSIAN",
    # Markdown → Jira helpers (old and new, consistent names)
    "convert_line",
    "convert_inline",
    "convert_multiline_elements",
    "convert_content",
    "md_convert_line",
    "md_convert_inline",
    "md_convert_multiline_elements",
    "md_convert_content",
    "md_convert_table_row",
    "md_is_table_separator",
    "md_resolve_reference_links",
    "convert_emoji_md_to_jira",
    "EMOJI_MD_TO_JIRA",
    "markdown_to_jira",
    # Jira → Markdown helpers
    "jira_convert_line",
    "jira_convert_inline",
    "jira_convert_multiline_elements",
    "jira_convert_content",
    "jira_convert_table_row",
    "is_jira_table_row",
    "convert_emoji_jira_to_md",
    "EMOJI_JIRA_TO_MD",
    "jira_to_markdown",
]
