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
