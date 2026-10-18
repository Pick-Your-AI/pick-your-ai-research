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

    def test_note_fields_and_source_urls_are_well_formed(self):
        from urllib.parse import urlsplit
        record_fields = ('id', 'family', 'model', 'route', 'direction', 'semantics',
                         'quantity', 'value', 'unit', 'conditions', 'implication')
        source_fields = ('id', 'publisher', 'scope', 'revision', 'accessed_on',
                         'evidence_grade', 'verification_status')
        for record in self.data['records']:
            with self.subTest(record=record.get('id')):
                for field in record_fields:
                    self.assertIsInstance(record.get(field), str, field)
                    self.assertTrue(record[field].strip(), field)
                self.assertIs(type(record.get('disputed')), bool)
                self.assertIsInstance(record['source_ids'], list)
        for source in self.data['sources']:
            with self.subTest(source=source.get('id')):
                for field in source_fields:
                    self.assertIsInstance(source.get(field), str, field)
                    self.assertTrue(source[field].strip(), field)
                self.assertIsInstance(source.get('urls'), list)
                self.assertTrue(source['urls'])
                for url in source['urls']:
                    self.assertIsInstance(url, str)
                    parsed = urlsplit(url)
                    self.assertIn(parsed.scheme, ('http', 'https'))
                    self.assertTrue(parsed.hostname)
                    self.assertIsNone(parsed.username)
                    self.assertIsNone(parsed.password)
                    self.assertFalse(any(char.isspace() for char in url))

    def test_relative_note_links_resolve(self):
        from urllib.parse import unquote, urlsplit
        folder = ROOT / 'research/T1-model-selection'
        for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', self.note):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            with self.subTest(target=target):
                self.assertTrue((folder / unquote(parsed.path)).resolve().exists())
