#!/usr/bin/env python3

# Description:
#
# This script converts a JIRA/Confluence markup syntax file to a markdown file.
# It will write to stdout, so you can redirect the output to a file if desired.
#
# The original JIRA file will not be modified unless you redirect the output
# to the same file.

# Usage:
# python3 jira_to_md.py <jira_file>
# python3 jira_to_md.py <jira_file> > <markdown_file>
# python3 jira_to_md.py <jira_file> | pbcopy

import sys
import re
from typing import List, Tuple, Callable, Match, Dict

# Jira emoticon to GitHub/Slack style emoji mapping
# Note: Some Jira emoticons map to multiple GitHub emojis, we pick the most common
EMOJI_JIRA_TO_MD: Dict[str, str] = {
    # Basic emoticons - use regex patterns for these
    ':)': ':smile:',
    ':D': ':grinning:',
    ';)': ':wink:',
    ':(': ':disappointed:',
    ':P': ':stuck_out_tongue:',
    ':p': ':stuck_out_tongue:',
    '<3': ':heart:',
    '</3': ':broken_heart:',
    ':*': ':kissing_heart:',
    ':|': ':neutral_face:',
    ':/': ':confused:',
    # Jira special emoticons
    '(y)': ':thumbsup:',
    '(n)': ':thumbsdown:',
    '(i)': ':information_source:',
    '(/)': ':white_check_mark:',
    '(x)': ':x:',
    '(!)': ':warning:',
    '(?)': ':question:',
    '(+)': ':heavy_plus_sign:',
    '(-)': ':heavy_minus_sign:',
    '(on)': ':bulb:',
    '(off)': ':bulb:',
    '(*)': ':star:',
    '(flag)': ':flag:',
    '(flagoff)': ':flag:',
}


def convert_emoji_jira_to_md(text: str) -> str:
    """Convert Jira emoticons to GitHub/Slack style emojis.
    
    Uses word boundaries/context checks to avoid false positives in URLs.
    """
    # Handle parentheses-based emoticons first (these are safer)
    paren_emojis = {k: v for k, v in EMOJI_JIRA_TO_MD.items() if k.startswith('(')}
    for jira_emoji, md_emoji in paren_emojis.items():
        text = text.replace(jira_emoji, md_emoji)
    
    # Handle simple emoticons with word boundaries to avoid URL matches
    # These require careful matching to not break URLs like http://
    simple_emojis = {
        ':)': ':smile:',
        ':D': ':grinning:',
        ';)': ':wink:',
        ':(': ':disappointed:',
        ':P': ':stuck_out_tongue:',
        ':p': ':stuck_out_tongue:',
        ':*': ':kissing_heart:',
        ':|': ':neutral_face:',
    }
    
    for jira_emoji, md_emoji in simple_emojis.items():
        # Use regex with negative lookbehind for / to avoid matching ://
        pattern = r'(?<![/\w])' + re.escape(jira_emoji) + r'(?![/\w])'
        text = re.sub(pattern, md_emoji, text)
    
    # Handle :/ separately - only match if not preceded by another colon (URL) or followed by /
    text = re.sub(r'(?<![:/\w]):/(?![/\w])', ':confused:', text)
    
    # Handle heart emoticons
    text = text.replace('</3', ':broken_heart:')
    text = text.replace('<3', ':heart:')
    
    return text


def convert_inline(text: str) -> str:
    """Convert inline Jira formatting using earliest-match approach.
    
    This processes patterns by finding the earliest match position,
    which correctly handles overlapping patterns.
    """
    patterns: List[Tuple[str, Callable[[Match], str]]] = [
        # Images: !url! or !url|alt=text! -> ![alt](url)
        (r'!([^|!\s]+)(?:\|alt=([^!]+))?!', lambda m: f'![{m.group(2) or ""}]({m.group(1)})'),
        # Links: [text|url] -> [text](url)
        (r'\[([^\]|]+)\|([^\]]+)\]', lambda m: f'[{m.group(1)}]({m.group(2)})'),
        # Bold: *text* -> **text** (but not URLs or other contexts)
        (r'(?<![:\w])\*([^*\n]+)\*(?!\w)', lambda m: f'**{m.group(1)}**'),
        # Italic: _text_ -> *text*
        (r'(?<![\w])_([^_\n]+)_(?![\w])', lambda m: f'*{m.group(1)}*'),
        # Inline code: {{text}} -> `text` (use .+? for nested braces)
        (r'\{\{(.+?)\}\}', lambda m: f'`{m.group(1)}`'),
        # Strikethrough: -text- -> ~~text~~ (require word boundaries)
        (r'(?<![:\w-])-([^\s-][^-\n]*[^\s-]|[^\s-])-(?![\w-])', lambda m: f'~~{m.group(1)}~~'),
    ]
    
    result = []
    remaining = text
    
    while remaining:
        earliest_match = None
        earliest_pos = len(remaining)
        
        for pattern, formatter in patterns:
            match = re.search(pattern, remaining)
            if match and match.start() < earliest_pos:
                earliest_match = (match, formatter)
                earliest_pos = match.start()
        
        if earliest_match:
            match, formatter = earliest_match
            # Add text before the match
            result.append(remaining[:match.start()])
            # Add the formatted text
            result.append(formatter(match))
            # Continue with remaining text
            remaining = remaining[match.end():]
        else:
            # No more matches, add remaining text
            result.append(remaining)
            break
    
    # Convert emojis at the end
    return convert_emoji_jira_to_md(''.join(result))


def convert_table_row(line: str) -> Tuple[str, bool]:
    """Convert a Jira table row to markdown format.
    
    Args:
        line: The Jira table row (e.g., "||col1||col2||" or "|col1|col2|")
        
    Returns:
        Tuple of (converted_row, is_header)
    """
    stripped = line.strip()
    
    # Check if it's a header row (uses ||)
    if stripped.startswith('||'):
        # Header row - split by || and convert
        cells = [cell.strip() for cell in stripped.split('||') if cell.strip()]
        converted_cells = [convert_inline(cell) for cell in cells]
        return ('| ' + ' | '.join(converted_cells) + ' |', True)
    else:
        # Regular row - split by | and convert
        cells = [cell.strip() for cell in stripped.strip('|').split('|')]
        converted_cells = [convert_inline(cell) for cell in cells]
        return ('| ' + ' | '.join(converted_cells) + ' |', False)


def is_jira_table_row(line: str) -> bool:
    """Check if a line is a Jira table row."""
    stripped = line.strip()
    return (stripped.startswith('||') and stripped.endswith('||')) or \
           (stripped.startswith('|') and stripped.endswith('|') and not stripped.startswith('||'))


def convert_line(line: str) -> str:
    """Convert a single line of Jira markup to markdown."""
    # Convert headers
    header_match = re.match(r'^h([1-6])\.\s*(.+)$', line)
    if header_match:
        level = int(header_match.group(1))
        content = header_match.group(2)
        return f'{"#" * level} {content}'
    
    # Convert blockquotes
    blockquote_match = re.match(r'^bq\.\s+(.+)$', line)
    if blockquote_match:
        content = blockquote_match.group(1)
        return f'> {convert_inline(content)}'
    
    # Convert nested ordered lists (## or more -> indented numbered list)
    nested_ordered_match = re.match(r'^(#{2,})\s+(.+)$', line)
    if nested_ordered_match:
        hashes = nested_ordered_match.group(1)
        content = nested_ordered_match.group(2)
        # Each # beyond the first = one level of indentation (2 spaces)
        indent = '  ' * (len(hashes) - 1)
        return f'{indent}1. {convert_inline(content)}'
    
    # Convert ordered lists (# at start of line -> numbered list)
    ordered_match = re.match(r'^#\s+(.+)$', line)
    if ordered_match:
        content = ordered_match.group(1)
        return f'1. {convert_inline(content)}'
    
    # Convert nested unordered lists (-- or more -> indented bullet list)
    nested_unordered_match = re.match(r'^(-{2,})\s+(.+)$', line)
    if nested_unordered_match:
        dashes = nested_unordered_match.group(1)
        content = nested_unordered_match.group(2)
        # Each - beyond the first = one level of indentation (2 spaces)
        indent = '  ' * (len(dashes) - 1)
        return f'{indent}* {convert_inline(content)}'
    
    # Convert unordered lists (- at start of line)
    unordered_match = re.match(r'^-\s+(.+)$', line)
    if unordered_match:
        content = unordered_match.group(1)
        return f'* {convert_inline(content)}'
    
    # Convert horizontal rules
    if re.match(r'^----+$', line):
        return '---'
    
    # Convert GFM task lists
    task_match = re.match(r'^\s*\[(x|X| )\]\s*(.*)$', line)
    if task_match:
        checkbox = task_match.group(1)
        content = task_match.group(2)
        return f'- [{checkbox}] {convert_inline(content)}'
    
    # Apply inline conversions for regular lines
    return convert_inline(line)


def convert_content(content: str) -> str:
    """Convert Jira markup string to markdown using two-phase parsing.
    
    Phase 1: Extract code blocks and replace with placeholders
    Phase 2: Process remaining content line by line
    
    This approach prevents code block content from being interpreted as Jira markup.
    """
    code_blocks: List[str] = []
    
    def extract_code_block(match: Match) -> str:
        lang = match.group(1)
        code = match.group(2)
        placeholder = f"__CODE_BLOCK_{len(code_blocks)}__"
        if lang:
            code_blocks.append(f'```{lang}\n{code}```')
        else:
            code_blocks.append(f'```\n{code}```')
        return placeholder
    
    # Phase 1: Extract all code blocks with placeholders
    # Support language tags with hyphens
    content = re.sub(
        r'\{code(?::([\w-]+))?\}\n(.*?)\{code\}',
        extract_code_block,
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Phase 2: Process lines (safe - no code content to misinterpret)
    lines = []
    content_lines = content.splitlines()
    i = 0
    header_row_processed = False
    
    while i < len(content_lines):
        line = content_lines[i]
        
        # Check for code block placeholder
        if line.startswith("__CODE_BLOCK_") and line.endswith("__"):
            idx = int(line.replace("__CODE_BLOCK_", "").replace("__", ""))
            if 0 <= idx < len(code_blocks):
                lines.append(code_blocks[idx])
            header_row_processed = False
            i += 1
            continue
        
        # Check for Jira table row
        if is_jira_table_row(line):
            converted_row, is_header = convert_table_row(line)
            lines.append(converted_row)
            
            # If this was a header row, add the separator line
            if is_header and not header_row_processed:
                # Count the number of cells
                cells = [c for c in line.strip().split('||') if c.strip()]
                separator = '| ' + ' | '.join(['---'] * len(cells)) + ' |'
                lines.append(separator)
                header_row_processed = True
            
            i += 1
            continue
        else:
            # Reset header tracking when we leave a table
            header_row_processed = False
        
        lines.append(convert_line(line))
        i += 1
    
    return '\n'.join(lines)


def convert_multiline_elements(content: str) -> str:
    """Legacy function for backwards compatibility.
    
    This is now handled by convert_content() with two-phase parsing.
    """
    return convert_content(content)


def process_code_block(match: Match) -> str:
    """Legacy function for backwards compatibility."""
    lang = match.group(1)
    code = match.group(2)
    if lang:
        return f'```{lang}\n{code}```'
    else:
        return f'```\n{code}```'


def jira_to_markdown(file_path: str) -> str:
    """Convert Jira markup file to markdown.
    
    Args:
        file_path: Path to the Jira markup file
        
    Returns:
        Converted markdown as a string
    """
    with open(file_path, "r") as jira_file:
        content = jira_file.read()
    
    return convert_content(content)


def main():
    """Entry point for the jira2md CLI command."""
    if len(sys.argv) < 2:
        print("\n".join(line.strip() for line in """
        Usage:
        jira2md <jira_file>
        jira2md <jira_file> > <markdown_file>
        jira2md <jira_file> | pbcopy
        """.split("\n")))

        print("\n".join(line.strip() for line in """
        Examples:
        jira2md README.jira
        jira2md README.jira > README.md
        jira2md README.jira | pbcopy
        """.split("\n")))
        sys.exit(1)

    jira_file_path = sys.argv[1]
    result = jira_to_markdown(jira_file_path)
    print(result)


if __name__ == "__main__":
    main()
