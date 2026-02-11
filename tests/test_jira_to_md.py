#!/usr/bin/env python3

import re
from textwrap import dedent
import unittest
from io import StringIO
from unittest.mock import patch

from md_to_jira.jira_to_md import (
    convert_line,
    convert_inline,
    convert_content,
    convert_multiline_elements,
    convert_table_row,
    is_jira_table_row,
    convert_emoji_jira_to_md,
    jira_to_markdown,
    process_code_block,
)


class TestJiraToMdConvertLine(unittest.TestCase):
    """Test convert_line for block-level elements."""

    def test_headers(self):
        self.assertEqual(convert_line('h1. Header'), '# Header')
        self.assertEqual(convert_line('h2. Header'), '## Header')
        self.assertEqual(convert_line('h3. Header'), '### Header')
        self.assertEqual(convert_line('h4. Header'), '#### Header')
        self.assertEqual(convert_line('h5. Header'), '##### Header')
        self.assertEqual(convert_line('h6. Header'), '###### Header')

    def test_blockquotes(self):
        self.assertEqual(convert_line('bq. This is a quote'), '> This is a quote')
        self.assertEqual(convert_line('bq. Quote with *bold*'), '> Quote with **bold**')

    def test_ordered_lists(self):
        self.assertEqual(convert_line('# First item'), '1. First item')
        self.assertEqual(convert_line('# Second item'), '1. Second item')

    def test_unordered_lists(self):
        self.assertEqual(convert_line('- item'), '* item')

    def test_nested_unordered_lists(self):
        self.assertEqual(convert_line('-- nested item'), '  * nested item')
        self.assertEqual(convert_line('--- deeply nested'), '    * deeply nested')

    def test_nested_ordered_lists(self):
        self.assertEqual(convert_line('## nested item'), '  1. nested item')
        self.assertEqual(convert_line('### deeply nested'), '    1. deeply nested')

    def test_horizontal_rules(self):
        self.assertEqual(convert_line('----'), '---')
        self.assertEqual(convert_line('------'), '---')

    def test_task_lists(self):
        self.assertEqual(convert_line('[x] task'), '- [x] task')
        self.assertEqual(convert_line('[ ] task'), '- [ ] task')
        self.assertEqual(convert_line('[X] task'), '- [X] task')


class TestJiraToMdConvertInline(unittest.TestCase):
    """Test convert_inline for inline formatting."""

    def test_bold(self):
        self.assertEqual(convert_inline('*bold*'), '**bold**')

    def test_italic(self):
        self.assertEqual(convert_inline('_italic_'), '*italic*')

    def test_inline_code(self):
        self.assertEqual(convert_inline('{{code}}'), '`code`')
        self.assertEqual(convert_inline('use {{git status}} here'), 'use `git status` here')

    def test_inline_code_with_braces(self):
        # Test that inline code with content containing braces works
        self.assertEqual(convert_inline('{{foo}bar}}'), '`foo}bar`')

    def test_strikethrough(self):
        self.assertEqual(convert_inline('-strikethrough-'), '~~strikethrough~~')

    def test_strikethrough_not_matching_hyphens(self):
        # Regular hyphens in text should not be converted
        self.assertEqual(convert_inline('some-text'), 'some-text')
        self.assertEqual(convert_inline('a - b'), 'a - b')

    def test_links(self):
        self.assertEqual(convert_inline('[link|http://example.com]'), '[link](http://example.com)')
        self.assertEqual(convert_inline('[text|https://example.com/path]'), '[text](https://example.com/path)')

    def test_images(self):
        self.assertEqual(convert_inline('!http://example.com/image.png!'), '![](http://example.com/image.png)')
        self.assertEqual(convert_inline('!http://example.com/image.png|alt=alt text!'), '![alt text](http://example.com/image.png)')

    def test_mixed_formatting(self):
        result = convert_inline('This has *bold* and _italic_ text')
        self.assertEqual(result, 'This has **bold** and *italic* text')

    def test_emojis(self):
        self.assertEqual(convert_inline(':)'), ':smile:')
        self.assertEqual(convert_inline(':D'), ':grinning:')
        self.assertEqual(convert_inline(';)'), ':wink:')
        self.assertEqual(convert_inline(':('), ':disappointed:')
        self.assertEqual(convert_inline('(y)'), ':thumbsup:')
        self.assertEqual(convert_inline('(n)'), ':thumbsdown:')
        self.assertEqual(convert_inline('(*)'), ':star:')
        self.assertEqual(convert_inline('(!)'), ':warning:')
        self.assertEqual(convert_inline('(?)'), ':question:')
        self.assertEqual(convert_inline('(on)'), ':bulb:')
        self.assertEqual(convert_inline('(/)'), ':white_check_mark:')
        self.assertEqual(convert_inline('(x)'), ':x:')
        self.assertEqual(convert_inline('<3'), ':heart:')
        self.assertEqual(convert_inline('(i)'), ':information_source:')

    def test_emoji_in_sentence(self):
        result = convert_inline('Great job! (y) Keep it up!')
        self.assertEqual(result, 'Great job! :thumbsup: Keep it up!')


class TestJiraToMdTables(unittest.TestCase):
    """Test table conversion."""

    def test_is_jira_table_row(self):
        self.assertTrue(is_jira_table_row('||Header 1||Header 2||'))
        self.assertTrue(is_jira_table_row('|Cell 1|Cell 2|'))
        self.assertFalse(is_jira_table_row('not a table'))

    def test_convert_table_row_header(self):
        result, is_header = convert_table_row('||Header 1||Header 2||')
        self.assertEqual(result, '| Header 1 | Header 2 |')
        self.assertTrue(is_header)

    def test_convert_table_row_regular(self):
        result, is_header = convert_table_row('|Cell 1|Cell 2|')
        self.assertEqual(result, '| Cell 1 | Cell 2 |')
        self.assertFalse(is_header)

    def test_table_in_content(self):
        jira = '''||Name||Age||
|Alice|30|
|Bob|25|'''
        expected = '''| Name | Age |
| --- | --- |
| Alice | 30 |
| Bob | 25 |'''
        self.assertEqual(convert_content(jira), expected)

    def test_table_with_formatting(self):
        jira = '''||*Bold*||_Italic_||
|{{code}}|text|'''
        expected = '''| **Bold** | *Italic* |
| --- | --- |
| `code` | text |'''
        self.assertEqual(convert_content(jira), expected)


class TestJiraToMdConvertContent(unittest.TestCase):
    """Test convert_content for full document conversion."""

    def test_code_blocks(self):
        jira = '{code:python}\nprint("Hello")\n{code}'
        expected = '```python\nprint("Hello")\n```'
        self.assertEqual(convert_content(jira), expected)

    def test_code_blocks_no_language(self):
        jira = '{code}\nsome code\n{code}'
        expected = '```\nsome code\n```'
        self.assertEqual(convert_content(jira), expected)

    def test_code_block_content_not_converted(self):
        # Code containing Jira-like syntax should not be converted
        jira = '{code:python}\nh1. This is not a header\n*not bold*\n{code}'
        expected = '```python\nh1. This is not a header\n*not bold*\n```'
        self.assertEqual(convert_content(jira), expected)

    def test_language_with_hyphen(self):
        jira = '{code:html-erb}\n<%= code %>\n{code}'
        expected = '```html-erb\n<%= code %>\n```'
        self.assertEqual(convert_content(jira), expected)

    def test_full_document(self):
        jira = dedent('''\
            h1. Test Jira Syntax Formatting

            h2. Header

            - item

            [x] task

            {code:python}
            print('Hello, World!')
            {code}''')

        expected = dedent('''\
            # Test Jira Syntax Formatting

            ## Header

            * item

            - [x] task

            ```python
            print('Hello, World!')
            ```''')

        self.assertEqual(convert_content(jira), expected)


class TestJiraToMdMultilineElements(unittest.TestCase):
    """Test convert_multiline_elements (legacy compatibility)."""

    def test_code_block(self):
        result = convert_multiline_elements('{code:python}\nprint("Hello World!")\n{code}')
        self.assertEqual(result, '```python\nprint("Hello World!")\n```')


class TestJiraToMdProcessCodeBlock(unittest.TestCase):
    """Test process_code_block helper."""

    def test_process_code_block(self):
        code_block_pattern = r'\{code(?::([\w-]+))?\}\n(.*?)\{code\}'
        code_block_string = "{code}\nprint('Hello, World!')\n{code}"
        match = re.search(code_block_pattern, code_block_string, flags=re.MULTILINE | re.DOTALL)
        self.assertEqual(process_code_block(match), "```\nprint('Hello, World!')\n```")

    def test_process_code_block_with_language(self):
        code_block_pattern = r'\{code(?::([\w-]+))?\}\n(.*?)\{code\}'
        code_block_string = "{code:python}\nprint('Hello')\n{code}"
        match = re.search(code_block_pattern, code_block_string, flags=re.MULTILINE | re.DOTALL)
        self.assertEqual(process_code_block(match), "```python\nprint('Hello')\n```")


class TestJiraToMdFileConversion(unittest.TestCase):
    """Test jira_to_markdown file reading."""

    def test_jira_to_markdown_returns_string(self):
        test_jira_content = dedent('''\
            h1. Test Jira Syntax Formatting

            h2. Header

            - item

            [x] task

            {code:python}
            print('Hello, World!')
            {code}
            ''')

        expected_output = dedent('''\
            # Test Jira Syntax Formatting

            ## Header

            * item

            - [x] task

            ```python
            print('Hello, World!')
            ```
            ''').rstrip('\n')  # Match actual output which doesn't add trailing newline

        with patch('builtins.open', return_value=StringIO(test_jira_content)):
            result = jira_to_markdown("test.jira")
            self.assertEqual(result, expected_output)


if __name__ == '__main__':
    unittest.main()
