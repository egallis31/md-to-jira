#!/usr/bin/env python3

# Author: Elijah Shackelford (eshack94)

# Description:
#
# This script converts a markdown file to Jira/Confluence markup syntax.
# It will write to stdout, so you can redirect the output to a file if desired.
#
# The original markdown file will not be modified unless you redirect the output
# to the same file.

# Usage:
# python3 md_to_jira.py <markdown_file>
# python3 md_to_jira.py <markdown_file> > <jira_file>
# python3 md_to_jira.py <markdown_file> | pbcopy

import sys
import re
import argparse
from typing import List, Tuple, Callable, Match, Dict, Optional

# Output format constants
FORMAT_MARKDOWN = 'markdown'
FORMAT_ATLASSIAN = 'atlassian'

# GitHub/Slack style emoji to Jira emoticon mapping
# Jira uses emoticons like :) :( :D etc. and some named ones
EMOJI_MD_TO_JIRA: Dict[str, str] = {
    # Faces
    ':smile:': ':)',
    ':smiley:': ':D',
    ':grinning:': ':D',
    ':laughing:': ':D',
    ':grin:': ':D',
    ':joy:': ':D',
    ':wink:': ';)',
    ':blush:': ':)',
    ':slightly_smiling_face:': ':)',
    ':upside_down_face:': ':)',
    ':relaxed:': ':)',
    ':heart_eyes:': '<3',
    ':kissing_heart:': ':*',
    ':kissing:': ':*',
    ':stuck_out_tongue:': ':P',
    ':stuck_out_tongue_winking_eye:': ':P',
    ':stuck_out_tongue_closed_eyes:': ':P',
    ':disappointed:': ':(',
    ':sad:': ':(',
    ':worried:': ':(',
    ':frowning:': ':(',
    ':cry:': ':(',
    ':sob:': ':(',
    ':angry:': ':(',
    ':rage:': ':(',
    ':confused:': ':/',
    ':neutral_face:': ':|',
    ':expressionless:': ':|',
    ':no_mouth:': ':|',
    ':thinking:': '(?)',
    ':thumbsup:': '(y)',
    ':thumbs_up:': '(y)',
    ':+1:': '(y)',
    ':thumbsdown:': '(n)',
    ':thumbs_down:': '(n)',
    ':-1:': '(n)',
    ':ok_hand:': '(y)',
    ':clap:': '(y)',
    ':star:': '(*)',
    ':star2:': '(*)',
    ':heart:': '<3',
    ':broken_heart:': '</3',
    ':fire:': '(/)',
    ':warning:': '(!)',
    ':exclamation:': '(!)',
    ':question:': '(?)',
    ':bulb:': '(on)',
    ':idea:': '(on)',
    ':light_bulb:': '(on)',
    ':check:': '(/)',
    ':white_check_mark:': '(/)',
    ':heavy_check_mark:': '(/)',
    ':x:': '(x)',
    ':cross_mark:': '(x)',
    ':heavy_multiplication_x:': '(x)',
    ':information_source:': '(i)',
    ':info:': '(i)',
    ':flag:': '(flag)',
    ':tada:': '(*)',
    ':party_popper:': '(*)',
}


def convert_emoji_md_to_jira(text: str) -> str:
    """Convert GitHub/Slack style emojis to Jira emoticons."""
    for md_emoji, jira_emoji in EMOJI_MD_TO_JIRA.items():
        text = text.replace(md_emoji, jira_emoji)
    return text


def convert_inline(text: str, output_format: str = FORMAT_MARKDOWN) -> str:
    """Convert inline markdown formatting using earliest-match approach.
    
    This processes patterns by finding the earliest match position,
    which correctly handles overlapping patterns like bold vs italic.
    
    Args:
        text: The text to convert
        output_format: Either FORMAT_MARKDOWN (preserve markdown) or FORMAT_ATLASSIAN (Jira wiki markup)
    """
    def format_link_md(m: Match) -> str:
        """Keep links in markdown format, just strip title if present."""
        text = m.group(1)
        url = m.group(2)
        # Strip title if present: url "title" or url 'title'
        url = re.sub(r'\s+["\'][^"\']*["\']$', '', url.strip())
        return f'[{text}]({url})'
    
    def format_link_atlassian(m: Match) -> str:
        """Convert links to Atlassian format [text|url]."""
        text = m.group(1)
        url = m.group(2)
        # Strip title if present
        url = re.sub(r'\s+["\'][^"\']*["\']$', '', url.strip())
        return f'[{text}|{url}]'
    
    def format_image_md(m: Match) -> str:
        """Keep images in markdown format, strip title if present."""
        alt = m.group(1)
        url = m.group(2)
        # Strip title if present
        url = re.sub(r'\s+["\'][^"\']*["\']$', '', url.strip())
        return f'![{alt}]({url})'
    
    def format_image_atlassian(m: Match) -> str:
        """Convert images to Atlassian format !url!."""
        alt = m.group(1)
        url = m.group(2)
        # Strip title if present
        url = re.sub(r'\s+["\'][^"\']*["\']$', '', url.strip())
        # Atlassian format: !url! or !url|alt=text!
        if alt:
            return f'!{url}|alt={alt}!'
        return f'!{url}!'
    
    if output_format == FORMAT_ATLASSIAN:
        patterns: List[Tuple[str, Callable[[Match], str]]] = [
            # Images - convert to Atlassian !url! format
            (r'!\[([^\]]*)\]\(([^)]+)\)', format_image_atlassian),
            # Links - convert to Atlassian [text|url] format
            (r'\[([^\]]+)\]\(([^)]+)\)', format_link_atlassian),
            # Bold **text** or __text__ -> *text*
            (r'\*\*(.+?)\*\*', lambda m: f'*{m.group(1)}*'),
            (r'__(.+?)__', lambda m: f'*{m.group(1)}*'),
            # Italic *text* or _text_ -> _text_ (but avoid matching bold)
            (r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', lambda m: f'_{m.group(1)}_'),
            # Strikethrough ~~text~~ -> -text-
            (r'~~(.+?)~~', lambda m: f'-{m.group(1)}-'),
            # Inline code `code` -> {{code}}
            (r'`([^`]+)`', lambda m: f'{{{{{m.group(1)}}}}}'),
        ]
    else:
        # Markdown-preserving mode
        patterns = [
            # Images - keep in markdown format, strip titles
            (r'!\[([^\]]*)\]\(([^)]+)\)', format_image_md),
            # Links - keep in markdown format, strip titles
            (r'\[([^\]]+)\]\(([^)]+)\)', format_link_md),
            # Normalize __bold__ to **bold** for consistency
            (r'__(.+?)__', lambda m: f'**{m.group(1)}**'),
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
    return convert_emoji_md_to_jira(''.join(result))


def convert_table_row(line: str, is_header: bool = False, output_format: str = FORMAT_MARKDOWN) -> str:
    """Convert a markdown table row.
    
    Args:
        line: The markdown table row (e.g., "| col1 | col2 |")
        is_header: Whether this is a header row (used for Atlassian format)
        output_format: Either FORMAT_MARKDOWN or FORMAT_ATLASSIAN
        
    Returns:
        Converted table row
    """
    # Remove leading/trailing pipes and split by |
    cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
    
    if output_format == FORMAT_ATLASSIAN:
        # Atlassian format: ||header1||header2|| or |cell1|cell2|
        converted_cells = [convert_inline(cell, output_format) for cell in cells]
        if is_header:
            return '||' + '||'.join(converted_cells) + '||'
        else:
            return '|' + '|'.join(converted_cells) + '|'
    else:
        # Keep markdown table format
        converted_cells = [convert_inline(cell, output_format) for cell in cells]
        return '| ' + ' | '.join(converted_cells) + ' |'


def is_table_separator(line: str) -> bool:
    """Check if line is a markdown table separator (e.g., |---|---|)."""
    stripped = line.strip()
    if not stripped.startswith('|') or not stripped.endswith('|'):
        return False
    # Check if all cells are just dashes/colons (alignment markers)
    cells = stripped.strip('|').split('|')
    for cell in cells:
        cell = cell.strip()
        if not re.match(r'^:?-+:?$', cell):
            return False
    return True


def convert_line(line: str, output_format: str = FORMAT_MARKDOWN) -> str:
    """Convert a single line of markdown to Jira markup.
    
    Args:
        line: The line to convert
        output_format: Either FORMAT_MARKDOWN or FORMAT_ATLASSIAN
    """
    # Headers
    header_match = re.match(r'^(#{1,6})\s*(.+)$', line)
    if header_match:
        level = len(header_match.group(1))
        content = header_match.group(2)
        if output_format == FORMAT_ATLASSIAN:
            return f'h{level}. {convert_inline(content, output_format)}'
        return line  # Keep markdown format
    
    # Blockquotes
    blockquote_match = re.match(r'^>\s+(.+)$', line)
    if blockquote_match:
        content = blockquote_match.group(1)
        if output_format == FORMAT_ATLASSIAN:
            return f'bq. {convert_inline(content, output_format)}'
        return f'> {convert_inline(content, output_format)}'
    
    # Nested ordered lists
    nested_ordered_match = re.match(r'^(\s+)(\d+)\.\s+(.+)$', line)
    if nested_ordered_match:
        indent = nested_ordered_match.group(1)
        num = nested_ordered_match.group(2)
        content = nested_ordered_match.group(3)
        if output_format == FORMAT_ATLASSIAN:
            # Calculate nesting level (2 spaces = 1 level typically)
            level = max(1, len(indent) // 2)
            return f'{"#" * (level + 1)} {convert_inline(content, output_format)}'
        return f'{indent}{num}. {convert_inline(content, output_format)}'
    
    # Ordered lists
    ordered_match = re.match(r'^(\d+)\.\s+(.+)$', line)
    if ordered_match:
        num = ordered_match.group(1)
        content = ordered_match.group(2)
        if output_format == FORMAT_ATLASSIAN:
            return f'# {convert_inline(content, output_format)}'
        return f'{num}. {convert_inline(content, output_format)}'
    
    # GFM task lists
    task_match = re.match(r'^(\s*)[\-\*]\s*\[(x|X| )\]\s*(.*)$', line)
    if task_match:
        indent = task_match.group(1)
        checkbox = task_match.group(2)
        content = task_match.group(3)
        if output_format == FORMAT_ATLASSIAN:
            # Atlassian doesn't have native task lists, use emoji
            status = '(/)' if checkbox.lower() == 'x' else '(x)'
            level = max(1, len(indent) // 2)
            return f'{"*" * (level + 1)} {status} {convert_inline(content, output_format)}'
        return f'{indent}- [{checkbox}] {convert_inline(content, output_format)}'
    
    # Nested unordered lists
    nested_unordered_match = re.match(r'^(\s+)[\*\-]\s+(.+)$', line)
    if nested_unordered_match:
        indent = nested_unordered_match.group(1)
        content = nested_unordered_match.group(2)
        if output_format == FORMAT_ATLASSIAN:
            level = max(1, len(indent) // 2)
            return f'{"*" * (level + 1)} {convert_inline(content, output_format)}'
        return f'{indent}- {convert_inline(content, output_format)}'
    
    # Unordered lists
    unordered_match = re.match(r'^[\*\-]\s+(.+)$', line)
    if unordered_match:
        content = unordered_match.group(1)
        if output_format == FORMAT_ATLASSIAN:
            return f'* {convert_inline(content, output_format)}'
        return f'- {convert_inline(content, output_format)}'
    
    # Horizontal rules
    if re.match(r'^---+$', line) or re.match(r'^\*\*\*+$', line) or re.match(r'^___+$', line):
        if output_format == FORMAT_ATLASSIAN:
            return '----'
        return '---'
    
    # Apply inline conversions for regular lines
    return convert_inline(line, output_format)


def resolve_reference_links(content: str) -> str:
    """Resolve reference-style links to inline links.
    
    Converts [text][ref] and [text][] to [text](url) format.
    Also handles image references ![alt][ref].
    """
    # Find all reference definitions [ref]: url "optional title"
    references: Dict[str, str] = {}
    ref_pattern = re.compile(r'^\[([^\]]+)\]:\s*(\S+)(?:\s+["\'].*?["\'])?\s*$', re.MULTILINE)
    
    for match in ref_pattern.finditer(content):
        ref_id = match.group(1).lower()
        url = match.group(2)
        references[ref_id] = url
    
    # Remove reference definitions from content
    content = ref_pattern.sub('', content)
    
    # Replace image references ![alt][ref]
    def replace_img_ref(m: Match) -> str:
        alt = m.group(1)
        ref_id = m.group(2).lower() if m.group(2) else alt.lower()
        url = references.get(ref_id, '')
        if url:
            return f'![{alt}]({url})'
        return m.group(0)  # Keep original if ref not found
    
    content = re.sub(r'!\[([^\]]*)\]\[([^\]]*)\]', replace_img_ref, content)
    
    # Replace link references [text][ref] and shorthand [text][]
    def replace_link_ref(m: Match) -> str:
        text = m.group(1)
        ref_id = m.group(2).lower() if m.group(2) else text.lower()
        url = references.get(ref_id, '')
        if url:
            return f'[{text}]({url})'
        return m.group(0)  # Keep original if ref not found
    
    content = re.sub(r'\[([^\]]+)\]\[([^\]]*)\]', replace_link_ref, content)
    
    # Clean up empty lines left by removed reference definitions
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content


def convert_content(content: str, output_format: str = FORMAT_MARKDOWN) -> str:
    """Convert markdown string to Jira markup using two-phase parsing.
    
    Phase 0: Resolve reference-style links
    Phase 1: Extract code blocks and replace with placeholders
    Phase 2: Process remaining content line by line
    
    This approach prevents code block content from being interpreted as markdown.
    
    Args:
        content: The markdown content to convert
        output_format: Either FORMAT_MARKDOWN (preserve markdown) or FORMAT_ATLASSIAN (Jira wiki markup)
    """
    # Phase 0: Resolve reference-style links to inline format
    content = resolve_reference_links(content)
    
    code_blocks: List[str] = []
    
    def extract_fenced_code_block(match: Match) -> str:
        """Extract fenced code blocks."""
        lang = match.group(1) or ''
        code = match.group(2)
        placeholder = f"<<<CODE_BLOCK_{len(code_blocks)}>>>"
        
        if output_format == FORMAT_ATLASSIAN:
            # Atlassian {code} format
            if lang:
                code_blocks.append(f'{{code:{lang}}}\n{code}\n{{code}}')
            else:
                code_blocks.append(f'{{code}}\n{code}\n{{code}}')
        else:
            # Keep as markdown fenced code block
            code_blocks.append(f'```{lang}\n{code}\n```')
        return placeholder
    
    def extract_indented_code_block(match: Match) -> str:
        """Convert indented code blocks."""
        code = match.group(1)
        # Remove the leading 4 spaces or tab from each line
        code = re.sub(r'^ {4}|\t', '', code, flags=re.MULTILINE)
        placeholder = f"<<<CODE_BLOCK_{len(code_blocks)}>>>"
        
        if output_format == FORMAT_ATLASSIAN:
            code_blocks.append(f'{{code}}\n{code}{{code}}')
        else:
            # Convert to fenced code block (no language)
            code_blocks.append(f'```\n{code}```')
        return placeholder
    
    # Phase 1: Extract all code blocks with placeholders
    # Fenced code blocks (support language tags with hyphens like 'html-erb')
    # Allow optional leading whitespace before closing ``` for indented code blocks in list items
    content = re.sub(
        r'```([\w-]+)?\n(.*?)\n[ \t]*```',
        extract_fenced_code_block,
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Indented code blocks (4 spaces)
    content = re.sub(
        r'((?:^ {4}.*\n?)+)',
        extract_indented_code_block,
        content,
        flags=re.MULTILINE
    )
    
    # Phase 2: Process lines (safe - no code content to misinterpret)
    lines = []
    content_lines = content.splitlines()
    i = 0
    
    while i < len(content_lines):
        line = content_lines[i]
        
        # Check for code block placeholder (may be indented in list items)
        stripped = line.strip()
        if stripped.startswith("<<<CODE_BLOCK_") and stripped.endswith(">>>"):
            idx = int(stripped.replace("<<<CODE_BLOCK_", "").replace(">>>", ""))
            if 0 <= idx < len(code_blocks):
                # Preserve original indentation
                indent = line[:len(line) - len(line.lstrip())]
                # Indent each line of the code block
                code_block = code_blocks[idx]
                if indent:
                    code_lines = code_block.split('\n')
                    code_block = '\n'.join(indent + l if l else l for l in code_lines)
                lines.append(code_block)
            i += 1
            continue
        
        # Check for markdown table (starts with |)
        if line.strip().startswith('|') and line.strip().endswith('|'):
            # Look ahead for separator row to determine if this is a header
            if i + 1 < len(content_lines) and is_table_separator(content_lines[i + 1]):
                # This is a header row
                lines.append(convert_table_row(line, is_header=True, output_format=output_format))
                if output_format == FORMAT_MARKDOWN:
                    lines.append(content_lines[i + 1])  # Keep separator row for markdown
                i += 2
                
                # Process remaining table rows
                while i < len(content_lines):
                    next_line = content_lines[i]
                    if next_line.strip().startswith('|') and next_line.strip().endswith('|'):
                        if not is_table_separator(next_line):
                            lines.append(convert_table_row(next_line, is_header=False, output_format=output_format))
                        elif output_format == FORMAT_MARKDOWN:
                            lines.append(next_line)  # Keep separators in markdown
                        i += 1
                    else:
                        break
                continue
            else:
                # Regular table row (no header)
                lines.append(convert_table_row(line, is_header=False, output_format=output_format))
                i += 1
                continue
        
        lines.append(convert_line(line, output_format))
        i += 1
    
    return '\n'.join(lines)


def convert_multiline_elements(content: str, output_format: str = FORMAT_MARKDOWN) -> str:
    """Legacy function for backwards compatibility.
    
    This is now handled by convert_content() with two-phase parsing.
    """
    return convert_content(content, output_format)


def markdown_to_jira(file_path: str, output_format: str = FORMAT_MARKDOWN) -> str:
    """Convert markdown file to Jira markup.
    
    Args:
        file_path: Path to the markdown file
        output_format: Either FORMAT_MARKDOWN (preserve markdown) or FORMAT_ATLASSIAN (Jira wiki markup)
        
    Returns:
        Converted Jira markup as a string
    """
    with open(file_path, "r") as md_file:
        content = md_file.read()
    
    return convert_content(content, output_format)


def prompt_for_format() -> str:
    """Interactive prompt to select output format."""
    print("\n" + "=" * 60)
    print("Markdown to Jira Converter - Output Format Selection")
    print("=" * 60)
    print()
    print("Select the output format for conversion:")
    print()
    print("  [1] Markdown (paste-friendly)")
    print("      - Preserves Markdown syntax")
    print("      - Works with Jira's native Markdown rendering")
    print("      - Best for: Jira Cloud, newer Confluence versions")
    print()
    print("  [2] Atlassian Text Formatting Notation")
    print("      - Converts to Jira wiki markup syntax")
    print("      - Uses {code}, *bold*, _italic_, etc.")
    print("      - Best for: Jira Server, older Confluence, Data Center")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1 or 2): ").strip()
            if choice == '1':
                return FORMAT_MARKDOWN
            elif choice == '2':
                return FORMAT_ATLASSIAN
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            sys.exit(0)


def main():
    """Entry point for the md2jira CLI command."""
    parser = argparse.ArgumentParser(
        description='Convert Markdown to Jira/Confluence markup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  md2jira README.md                    # Convert with interactive format prompt
  md2jira README.md -f markdown        # Preserve Markdown (Jira Cloud)
  md2jira README.md -f atlassian       # Convert to Jira wiki markup
  md2jira README.md > README.jira      # Save output to file
  md2jira README.md | pbcopy           # Copy to clipboard (macOS)
        """
    )
    parser.add_argument(
        'file',
        nargs='?',
        help='Markdown file to convert'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['markdown', 'atlassian'],
        default=None,
        help='Output format: "markdown" (preserve Markdown for Jira Cloud) or "atlassian" (Jira wiki markup)'
    )
    
    args = parser.parse_args()
    
    # Show help if no file provided
    if not args.file:
        parser.print_help()
        sys.exit(1)
    
    # Determine output format
    if args.format:
        output_format = FORMAT_MARKDOWN if args.format == 'markdown' else FORMAT_ATLASSIAN
    elif sys.stdin.isatty():
        # Interactive mode - prompt user
        output_format = prompt_for_format()
        print()  # Blank line before output
    else:
        # Non-interactive (piped), default to markdown
        output_format = FORMAT_MARKDOWN
    
    result = markdown_to_jira(args.file, output_format)
    print(result)


if __name__ == "__main__":
    main()
