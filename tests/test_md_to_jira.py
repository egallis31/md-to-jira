#!/usr/bin/env python3

import re
from textwrap import dedent
import unittest
from io import StringIO
from unittest.mock import patch

from md_to_jira.md_to_jira import (
    convert_line,
    convert_inline,
    convert_content,
    convert_multiline_elements,
    convert_table_row,
    is_table_separator,
    resolve_reference_links,
    convert_emoji_md_to_jira,
    markdown_to_jira,
)


class TestMdToJiraConvertLine(unittest.TestCase):
    """Test convert_line for block-level elements."""

    def test_headers(self):
        # Headers stay in markdown format (Jira accepts markdown-style headers)
        self.assertEqual(convert_line('# Header'), '# Header')
        self.assertEqual(convert_line('## Header'), '## Header')
        self.assertEqual(convert_line('### Header'), '### Header')
        self.assertEqual(convert_line('#### Header'), '#### Header')
        self.assertEqual(convert_line('##### Header'), '##### Header')
        self.assertEqual(convert_line('###### Header'), '###### Header')

    def test_blockquotes(self):
        # Blockquotes stay in markdown format
        self.assertEqual(convert_line('> This is a quote'), '> This is a quote')
        self.assertEqual(convert_line('> Quote with **bold**'), '> Quote with **bold**')

    def test_ordered_lists(self):
        # Ordered lists stay in markdown format
        self.assertEqual(convert_line('1. First item'), '1. First item')
        self.assertEqual(convert_line('2. Second item'), '2. Second item')
        self.assertEqual(convert_line('10. Tenth item'), '10. Tenth item')

    def test_unordered_lists(self):
        self.assertEqual(convert_line('* item'), '- item')
        self.assertEqual(convert_line('- item'), '- item')

    def test_nested_unordered_lists(self):
        # Nested lists stay in markdown format
        self.assertEqual(convert_line('  * nested item'), '  - nested item')
        self.assertEqual(convert_line('    * deeply nested'), '    - deeply nested')

    def test_nested_ordered_lists(self):
        # Nested ordered lists stay in markdown format
        self.assertEqual(convert_line('  1. nested item'), '  1. nested item')
        self.assertEqual(convert_line('    1. deeply nested'), '    1. deeply nested')

    def test_horizontal_rules(self):
        # Horizontal rules stay in markdown format
        self.assertEqual(convert_line('---'), '---')
        self.assertEqual(convert_line('----'), '---')
        self.assertEqual(convert_line('***'), '---')
        self.assertEqual(convert_line('___'), '---')

    def test_task_lists(self):
        # Task lists stay in markdown format
        self.assertEqual(convert_line('- [x] task'), '- [x] task')
        self.assertEqual(convert_line('- [ ] task'), '- [ ] task')
        self.assertEqual(convert_line('- [X] task'), '- [X] task')


class TestMdToJiraConvertInline(unittest.TestCase):
    """Test convert_inline for inline formatting."""

    def test_bold(self):
        # Bold stays in markdown format, __bold__ normalized to **bold**
        self.assertEqual(convert_inline('**bold**'), '**bold**')
        self.assertEqual(convert_inline('__bold__'), '**bold**')

    def test_italic(self):
        # Italic stays in markdown format
        self.assertEqual(convert_inline('*italic*'), '*italic*')
        self.assertEqual(convert_inline('_italic_'), '_italic_')

    def test_inline_code(self):
        # Inline code stays in markdown format
        self.assertEqual(convert_inline('`code`'), '`code`')
        self.assertEqual(convert_inline('use `git status` here'), 'use `git status` here')

    def test_strikethrough(self):
        # Strikethrough stays in markdown format
        self.assertEqual(convert_inline('~~strikethrough~~'), '~~strikethrough~~')

    def test_links(self):
        # Links stay in markdown format
        self.assertEqual(convert_inline('[link](http://example.com)'), '[link](http://example.com)')
        self.assertEqual(convert_inline('[text](https://example.com/path)'), '[text](https://example.com/path)')

    def test_links_with_titles(self):
        # Link titles should be stripped
        self.assertEqual(convert_inline('[link](http://example.com "title")'), '[link](http://example.com)')
        self.assertEqual(convert_inline("[link](http://example.com 'title')"), '[link](http://example.com)')

    def test_images(self):
        # Images stay in markdown format
        self.assertEqual(convert_inline('![alt text](http://example.com/image.png)'), '![alt text](http://example.com/image.png)')
        self.assertEqual(convert_inline('![](http://example.com/image.png)'), '![](http://example.com/image.png)')

    def test_images_with_titles(self):
        # Image titles should be stripped
        self.assertEqual(convert_inline('![alt](http://example.com/img.png "title")'), '![alt](http://example.com/img.png)')

    def test_emojis(self):
        self.assertEqual(convert_inline(':smile:'), ':)')
        self.assertEqual(convert_inline(':thumbsup:'), '(y)')
        self.assertEqual(convert_inline(':thumbsdown:'), '(n)')
        self.assertEqual(convert_inline(':star:'), '(*)')
        self.assertEqual(convert_inline(':warning:'), '(!)')
        self.assertEqual(convert_inline(':question:'), '(?)')
        self.assertEqual(convert_inline(':bulb:'), '(on)')
        self.assertEqual(convert_inline(':white_check_mark:'), '(/)')
        self.assertEqual(convert_inline(':x:'), '(x)')
        self.assertEqual(convert_inline(':heart:'), '<3')

    def test_emoji_in_sentence(self):
        result = convert_inline('Great job! :thumbsup: Keep it up!')
        self.assertEqual(result, 'Great job! (y) Keep it up!')

    def test_mixed_formatting(self):
        # Markdown formatting stays as-is
        result = convert_inline('This has **bold** and *italic* text')
        self.assertEqual(result, 'This has **bold** and *italic* text')

    def test_bold_italic_no_collision(self):
        # Bold and italic stay in markdown format
        result = convert_inline('**bold** and *italic*')
        self.assertEqual(result, '**bold** and *italic*')


class TestMdToJiraReferenceLinks(unittest.TestCase):
    """Test reference-style link resolution."""

    def test_basic_reference_link(self):
        md = '''Check out [this link][example]

[example]: https://example.com'''
        result = resolve_reference_links(md)
        self.assertIn('[this link](https://example.com)', result)
        self.assertNotIn('[example]:', result)

    def test_shorthand_reference_link(self):
        md = '''Visit [Example][]

[Example]: https://example.com'''
        result = resolve_reference_links(md)
        self.assertIn('[Example](https://example.com)', result)

    def test_image_reference(self):
        md = '''![logo][img]

[img]: https://example.com/logo.png'''
        result = resolve_reference_links(md)
        self.assertIn('![logo](https://example.com/logo.png)', result)

    def test_reference_with_title(self):
        md = '''Check out [link][ref]

[ref]: https://example.com "Title"'''
        result = resolve_reference_links(md)
        self.assertIn('[link](https://example.com)', result)

    def test_case_insensitive_reference(self):
        md = '''[LINK][REF]

[ref]: https://example.com'''
        result = resolve_reference_links(md)
        self.assertIn('[LINK](https://example.com)', result)

    def test_reference_links_in_full_conversion(self):
        md = '''See the [docs][doc-link] for more info.

[doc-link]: https://docs.example.com'''
        result = convert_content(md)
        self.assertIn('[docs](https://docs.example.com)', result)
        self.assertNotIn('[doc-link]:', result)


class TestMdToJiraTables(unittest.TestCase):
    """Test table conversion."""

    def test_is_table_separator(self):
        self.assertTrue(is_table_separator('|---|---|'))
        self.assertTrue(is_table_separator('| --- | --- |'))
        self.assertTrue(is_table_separator('|:---|---:|'))
        self.assertFalse(is_table_separator('| text | text |'))
        self.assertFalse(is_table_separator('not a table'))

    def test_convert_table_row_header(self):
        # Tables stay in markdown format
        result = convert_table_row('| Header 1 | Header 2 |', is_header=True)
        self.assertEqual(result, '| Header 1 | Header 2 |')

    def test_convert_table_row_regular(self):
        result = convert_table_row('| Cell 1 | Cell 2 |', is_header=False)
        self.assertEqual(result, '| Cell 1 | Cell 2 |')

    def test_table_in_content(self):
        # Tables stay in markdown format with separator preserved
        md = '''| Name | Age |
|---|---|
| Alice | 30 |
| Bob | 25 |'''
        expected = '''| Name | Age |
|---|---|
| Alice | 30 |
| Bob | 25 |'''
        self.assertEqual(convert_content(md), expected)

    def test_table_with_formatting(self):
        # Tables stay in markdown format, inline formatting stays as markdown
        md = '''| **Bold** | *Italic* |
|---|---|
| `code` | text |'''
        expected = '''| **Bold** | *Italic* |
|---|---|
| `code` | text |'''
        self.assertEqual(convert_content(md), expected)


class TestMdToJiraConvertContent(unittest.TestCase):
    """Test convert_content for full document conversion."""

    def test_fenced_code_blocks(self):
        # Code blocks stay in markdown format
        md = '```python\nprint("Hello")\n```'
        expected = '```python\nprint("Hello")\n```'
        self.assertEqual(convert_content(md), expected)

    def test_fenced_code_blocks_no_language(self):
        md = '```\nsome code\n```'
        expected = '```\nsome code\n```'
        self.assertEqual(convert_content(md), expected)

    def test_code_block_content_not_converted(self):
        # Code containing markdown-like syntax should not be converted
        md = '```python\n# This is a comment, not a header\n**not bold**\n```'
        expected = '```python\n# This is a comment, not a header\n**not bold**\n```'
        self.assertEqual(convert_content(md), expected)

    def test_language_with_hyphen(self):
        md = '```html-erb\n<%= code %>\n```'
        expected = '```html-erb\n<%= code %>\n```'
        self.assertEqual(convert_content(md), expected)

    def test_full_document(self):
        md = dedent('''\
            # Test Markdown Syntax Formatting

            ## Header

            * item

            - [x] task

            ```python
            print('Hello, World!')
            ```''')

        expected = dedent('''\
            # Test Markdown Syntax Formatting

            ## Header

            - item

            - [x] task

            ```python
            print('Hello, World!')
            ```''')

        self.assertEqual(convert_content(md), expected)


class TestMdToJiraMultilineElements(unittest.TestCase):
    """Test convert_multiline_elements (legacy compatibility)."""

    def test_code_block(self):
        # Code blocks stay in markdown format
        result = convert_multiline_elements('```python\nprint("Hello World!")\n```')
        self.assertEqual(result, '```python\nprint("Hello World!")\n```')


class TestMdToJiraFileConversion(unittest.TestCase):
    """Test markdown_to_jira file reading."""

    def test_markdown_to_jira_returns_string(self):
        test_md_content = dedent('''\
            # Test Markdown Syntax Formatting

            ## Header

            * item

            - [x] task

            ```python
            print('Hello, World!')
            ```
            ''')

        expected_output = dedent('''\
            # Test Markdown Syntax Formatting

            ## Header

            - item

            - [x] task

            ```python
            print('Hello, World!')
            ```
            ''').rstrip('\n')  # Match actual output which doesn't add trailing newline

        with patch('builtins.open', return_value=StringIO(test_md_content)):
            result = markdown_to_jira("test.md")
            self.assertEqual(result, expected_output)


class TestMdToJiraAtlassianFormat(unittest.TestCase):
    """Test Atlassian Text Formatting Notation output."""

    def test_headers_atlassian(self):
        from md_to_jira.md_to_jira import FORMAT_ATLASSIAN
        self.assertEqual(convert_line('# Header', FORMAT_ATLASSIAN), 'h1. Header')
        self.assertEqual(convert_line('## Header', FORMAT_ATLASSIAN), 'h2. Header')
        self.assertEqual(convert_line('### Header', FORMAT_ATLASSIAN), 'h3. Header')

    def test_bold_atlassian(self):
        from md_to_jira.md_to_jira import FORMAT_ATLASSIAN
        self.assertEqual(convert_inline('**bold**', FORMAT_ATLASSIAN), '*bold*')
        self.assertEqual(convert_inline('__bold__', FORMAT_ATLASSIAN), '*bold*')

    def test_strikethrough_atlassian(self):
        from md_to_jira.md_to_jira import FORMAT_ATLASSIAN
        self.assertEqual(convert_inline('~~deleted~~', FORMAT_ATLASSIAN), '-deleted-')

    def test_inline_code_atlassian(self):
        from md_to_jira.md_to_jira import FORMAT_ATLASSIAN
        self.assertEqual(convert_inline('`code`', FORMAT_ATLASSIAN), '{{code}}')

    def test_links_atlassian(self):
        from md_to_jira.md_to_jira import FORMAT_ATLASSIAN
        self.assertEqual(
            convert_inline('[text](http://example.com)', FORMAT_ATLASSIAN),
            '[text|http://example.com]'
        )

    def test_images_atlassian(self):
        from md_to_jira.md_to_jira import FORMAT_ATLASSIAN
        self.assertEqual(
            convert_inline('![alt](http://example.com/img.png)', FORMAT_ATLASSIAN),
            '!http://example.com/img.png|alt=alt!'
        )

    def test_lists_atlassian(self):
        from md_to_jira.md_to_jira import FORMAT_ATLASSIAN
        self.assertEqual(convert_line('- item', FORMAT_ATLASSIAN), '* item')
        self.assertEqual(convert_line('1. item', FORMAT_ATLASSIAN), '# item')

    def test_blockquote_atlassian(self):
        from md_to_jira.md_to_jira import FORMAT_ATLASSIAN
        self.assertEqual(convert_line('> quote', FORMAT_ATLASSIAN), 'bq. quote')

    def test_horizontal_rule_atlassian(self):
        from md_to_jira.md_to_jira import FORMAT_ATLASSIAN
        self.assertEqual(convert_line('---', FORMAT_ATLASSIAN), '----')

    def test_code_block_atlassian(self):
        from md_to_jira.md_to_jira import FORMAT_ATLASSIAN
        result = convert_content('```python\nprint("hi")\n```', FORMAT_ATLASSIAN)
        self.assertIn('{code:python}', result)
        self.assertIn('{code}', result)

    def test_table_atlassian(self):
        from md_to_jira.md_to_jira import FORMAT_ATLASSIAN
        self.assertEqual(
            convert_table_row('| Header 1 | Header 2 |', is_header=True, output_format=FORMAT_ATLASSIAN),
            '||Header 1||Header 2||'
        )
        self.assertEqual(
            convert_table_row('| Cell 1 | Cell 2 |', is_header=False, output_format=FORMAT_ATLASSIAN),
            '|Cell 1|Cell 2|'
        )


if __name__ == '__main__':
    unittest.main()
