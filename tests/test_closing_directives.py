import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('closing', Path(__file__).parents[1] / 'scripts/check_closing_directives.py')
closing = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(closing)


class ClosingDirectivesTests(unittest.TestCase):
    def test_partial_refs(self):
        self.assertEqual(closing.check_text('Refs #34, #35. Issues remain open.'), [])

    def test_closure_requires_explicit_allowlist(self):
        self.assertTrue(closing.check_text('Closes #34'))
        self.assertEqual(closing.check_text('Closes #34', ['#34']), [])

    def test_all_keywords_case_and_colon(self):
        for word in ['close', 'closes', 'closed', 'fix', 'fixes', 'fixed', 'resolve', 'resolves', 'resolved']:
            with self.subTest(word=word):
                self.assertTrue(closing.check_text(word.upper() + ': #34'))
                self.assertEqual(closing.check_text(word.upper() + ': #34', ['#34']), [])

    def test_negated_closure_is_never_allowlisted(self):
        for text in ['does not close #34', 'Never fixes #34', 'This does not resolve #34']:
            self.assertTrue(closing.check_text(text, ['#34']))

    def test_ranges_and_lists_require_separate_explicit_lines(self):
        for text in ['Closes #34–#39', 'Closes #34-39', 'Closes #34, #35']:
            self.assertTrue(closing.check_text(text, ['#34', '#35']))
        self.assertEqual(closing.check_text('Closes #34\nFixes #35', ['#34', '#35']), [])

    def test_cross_repository_and_url_targets(self):
        for target in ['owner/repo#34', 'https://github.com/owner/repo/issues/34']:
            self.assertTrue(closing.check_text('Fixes ' + target))
            self.assertEqual(closing.check_text('Fixes ' + target, [target]), [])
            self.assertTrue(closing.check_text('Fixes ' + target, ['#34']))

    def test_quotes_code_and_markdown_are_conservatively_flagged(self):
        for text in ['> Closes #34', '`Closes #34`', '**Closes** #34', '_Closes_ #34', '__Closes__ #34', 'Closes: `#34`']:
            self.assertTrue(closing.check_text(text, ['#34']))

    def test_multiline_keyword_and_target(self):
        self.assertTrue(closing.check_text('does not close\n#34', ['#34']))

    def test_report_line_numbers(self):
        self.assertEqual(closing.check_text('Refs #1\nDo not close #34'), [(2, '#34')])

    def test_ordinary_prose_without_reference(self):
        self.assertEqual(closing.check_text('Close the review loop; fixed formatting.'), [])

    def test_adjacent_negation_or_range_cannot_be_allowlisted(self):
        for text in ['does not\nclose #34', 'Closes #34\n–#39', 'Closes #34\nthrough #39']:
            self.assertTrue(closing.check_text(text, ['#34']))
        self.assertEqual(closing.check_text('Accepted evidence.\n\nCloses #34', ['#34']), [])

    def test_link_wrappers_are_flagged(self):
        for text in ['Closes [#34](https://github.com/owner/repo/issues/34)',
                     'Closes <https://github.com/owner/repo/issues/34>']:
            self.assertTrue(closing.check_text(text))

    def test_fenced_directives_are_not_standalone(self):
        self.assertTrue(closing.check_text('```\nCloses #34\n```', ['#34']))

    def test_blank_lines_do_not_end_fenced_context(self):
        for fence in ['```', '~~~', '```text', '~~~text']:
            with self.subTest(fence=fence):
                text = f'{fence}\n\nCloses #34\n\n{fence[:3]}'
                self.assertEqual(closing.check_text(text, ['#34']), [(3, '#34')])

    def test_indented_directives_are_not_plain_lines(self):
        for indentation in [' ', '   ', '    ', '\t']:
            with self.subTest(indentation=indentation):
                self.assertTrue(closing.check_text(indentation + 'Closes #34', ['#34']))

    def test_mismatched_or_short_fence_does_not_end_context(self):
        for closing_fence in ['~~~', '```', '````not-a-close']:
            with self.subTest(closing_fence=closing_fence):
                text = f'````\n\n{closing_fence}\n\nCloses #34'
                self.assertEqual(closing.check_text(text, ['#34']), [(5, '#34')])

    def test_unclosed_fence_keeps_later_paragraphs_protected(self):
        text = '```text\n\nExample.\n\nCloses #34\n\nFixes #35'
        self.assertEqual(closing.check_text(text, ['#34', '#35']), [(5, '#34'), (7, '#35')])

    def test_closed_fence_allows_later_plain_directive(self):
        text = '  ~~~text\n\nCloses #34\n\n  ~~~~\n\nFixes #35'
        self.assertEqual(closing.check_text(text, ['#34', '#35']), [(3, '#34')])
