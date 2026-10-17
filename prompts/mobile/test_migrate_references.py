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

    def test_previous_generator_research_misqualification(self):
        self.assertEqual(rewrite('research Pick-Your-AI/pickyour.ai#40', self.mapping),
                         'research Pick-Your-AI/pick-your-ai-research#40')

    def test_numeric_link_label_does_not_keep_obsolete_number(self):
        self.assertEqual(rewrite('[184](https://github.com/Pick-Your-AI/pickyour.ai/issues/184)', self.mapping),
                         '[Pick-Your-AI/pick-your-ai-apple#22](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/22)')


if __name__ == '__main__':
    unittest.main()
