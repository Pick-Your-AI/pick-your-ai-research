"""Check claim-to-source integrity, not truth of external research claims."""
import datetime
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class NontextEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = ROOT / 'research/T1-model-selection'
        cls.data = json.loads((folder / 'nontext-limit-evidence.json').read_text())
        cls.note = (folder / 'nontext-selection-limits.md').read_text()

    def test_each_claim_resolves_to_one_source_and_anchor(self):
        ids = [s['id'] for s in self.data['sources']]
        self.assertEqual(len(ids), len(set(ids)), 'Duplicate source IDs are ambiguous')
        headings = re.findall(r'^### ([A-Z]+-S\d+)\s*$', self.note, re.MULTILINE)
        self.assertCountEqual(ids, headings)
        record_ids = [r['id'] for r in self.data['records']]
        self.assertEqual(len(record_ids), len(set(record_ids)))
        for record in self.data['records']:
            with self.subTest(record=record['id']):
                self.assertTrue(record['source_ids'])
                self.assertTrue(set(record['source_ids']) <= set(ids))

    def test_dataset_checkpoint_covers_source_access_dates(self):
        checkpoint = datetime.date.fromisoformat(self.data['accessed_on'])
        dates = [datetime.date.fromisoformat(s['accessed_on']) for s in self.data['sources']]
        self.assertEqual(checkpoint, max(dates))
