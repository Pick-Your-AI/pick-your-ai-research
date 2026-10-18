"""Regression checks for cross-repository reference corruption during transfer."""
import unittest
from migrate_references import rewrite


class ReferenceMigrationTests(unittest.TestCase):
    def setUp(self):
        self.mapping = [
            {'old_number': 40, 'repository': 'Pick-Your-AI/pick-your-ai-android',
             'new_number': 7, 'new_url': 'https://github.com/Pick-Your-AI/pick-your-ai-android/issues/7'},
            {'old_number': 184, 'repository': 'Pick-Your-AI/pick-your-ai-apple',
             'new_number': 22, 'new_url': 'https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/22'},
        ]

    def test_link_target_controls_research_label(self):
        source = '[research #40](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40)'
        result = rewrite(source, self.mapping, True)
        self.assertIn('research Pick-Your-AI/pick-your-ai-research#40', result)
        self.assertNotIn('android', result)

    def test_unlinked_research_chain_and_platform_reference(self):
        result = rewrite('research #41/#60; #184; Project #5', self.mapping, True)
        self.assertEqual(result, 'research Pick-Your-AI/pick-your-ai-research#41/Pick-Your-AI/pick-your-ai-research#60; Pick-Your-AI/pick-your-ai-apple#22; Project #5')

    def test_canonical_website_and_existing_namespaces_survive(self):
        source = 'Pick-Your-AI/pickyour.ai#15; Pick-Your-AI/pick-your-ai-research#40; Pick-Your-AI/pick-your-ai-apple#40'
        self.assertEqual(rewrite(source, self.mapping, True), source)

    def test_url_and_label_migrate_together(self):
        source = '[#184](https://github.com/Pick-Your-AI/pickyour.ai/issues/184)'
        result = rewrite(source, self.mapping, True)
        self.assertEqual(result, '[Pick-Your-AI/pick-your-ai-apple#22](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/22)')
        self.assertEqual(rewrite(result, self.mapping, True), result)

    def test_comment_anchor_keeps_destination_identity(self):
        source = '[#184](https://github.com/Pick-Your-AI/pickyour.ai/issues/184#issuecomment-123)'
        expected = '[Pick-Your-AI/pick-your-ai-apple#22](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/22#issuecomment-123)'
        self.assertEqual(rewrite(source, self.mapping, True), expected)
        self.assertEqual(rewrite(expected, self.mapping, True), expected)

    def test_previous_generator_research_misqualification(self):
        self.assertEqual(rewrite('research Pick-Your-AI/pickyour.ai#40', self.mapping),
                         'research Pick-Your-AI/pick-your-ai-research#40')

    def test_numeric_link_label_does_not_keep_obsolete_number(self):
        self.assertEqual(rewrite('[184](https://github.com/Pick-Your-AI/pickyour.ai/issues/184)', self.mapping),
                         '[Pick-Your-AI/pick-your-ai-apple#22](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/22)')

    def test_bare_slash_chain_migrates_every_old_identity(self):
        source = '#184/#40'
        expected = 'Pick-Your-AI/pick-your-ai-apple#22/Pick-Your-AI/pick-your-ai-android#7'
        self.assertEqual(rewrite(source, self.mapping, True), expected)
        self.assertEqual(rewrite(expected, self.mapping, True), expected)

    def test_raw_url_fragments_are_not_issue_references(self):
        source = ('https://example.org/#184 '
                  'https://example.org/#184/#40 '
                  'https://example.org/path#184; #184/#40')
        expected = ('https://example.org/#184 '
                    'https://example.org/#184/#40 '
                    'https://example.org/path#184; '
                    'Pick-Your-AI/pick-your-ai-apple#22/'
                    'Pick-Your-AI/pick-your-ai-android#7')
        self.assertEqual(rewrite(source, self.mapping, True), expected)
        self.assertEqual(rewrite(expected, self.mapping, True), expected)

    def test_namespaced_chain_preserves_repository(self):
        source = 'Pick-Your-AI/pick-your-ai-research#40/#184'
        expected = 'Pick-Your-AI/pick-your-ai-research#40/Pick-Your-AI/pick-your-ai-research#184'
        self.assertEqual(rewrite(source, self.mapping, True), expected)

    def test_research_range_and_pr_prefix_are_not_mobile_issues(self):
        source = 'Merged research #40-#184; open research\nPRs #40-#184'
        expected = ('Merged research Pick-Your-AI/pick-your-ai-research#40-'
                    'Pick-Your-AI/pick-your-ai-research#184; open research\n'
                    'PRs Pick-Your-AI/pick-your-ai-research#40-'
                    'Pick-Your-AI/pick-your-ai-research#184')
        self.assertEqual(rewrite(source, self.mapping, True), expected)
        self.assertEqual(rewrite(expected, self.mapping, True), expected)

    def test_research_pr_list_keeps_all_research_identities(self):
        source = 'research PRs #40-#184, #40 and #184'
        expected = ('research PRs Pick-Your-AI/pick-your-ai-research#40-'
                    'Pick-Your-AI/pick-your-ai-research#184, '
                    'Pick-Your-AI/pick-your-ai-research#40 and '
                    'Pick-Your-AI/pick-your-ai-research#184')
        self.assertEqual(rewrite(source, self.mapping, True), expected)

    def test_spaced_slash_does_not_extend_research_namespace(self):
        source = 'research #40 / #184 lifecycle'
        expected = ('research Pick-Your-AI/pick-your-ai-research#40 / '
                    'Pick-Your-AI/pick-your-ai-apple#22 lifecycle')
        self.assertEqual(rewrite(source, self.mapping, True), expected)

    def test_tracking_references_keep_review_and_service_meaning(self):
        from pathlib import Path
        tracking = (Path(__file__).resolve().parents[2] /
                    'docs/APPLE_DELIVERY_TRACKING.md').read_text()
        self.assertIn('pick-your-ai-apple#44/Pick-Your-AI/pick-your-ai-apple#50', tracking)
        self.assertIn('pick-your-ai-android#78 lifecycle', tracking)
        self.assertIn('pick-your-ai-android#79 capacity/quality', tracking)
        self.assertIn('Merged research Pick-Your-AI/pick-your-ai-research#100-'
                      'Pick-Your-AI/pick-your-ai-research#105', tracking)
        self.assertIn('PRs Pick-Your-AI/pick-your-ai-research#69-'
                      'Pick-Your-AI/pick-your-ai-research#73', tracking)
        self.assertNotRegex(tracking, r'Pick-Your-AI/[\w.-]+#\d+[/,-]#\d+')


if __name__ == '__main__':
    unittest.main()
