"""Display sidecar integrity; acceptance and client delivery have separate receipts."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ComponentDisplayLabels(unittest.TestCase):
    def test_proposal_matches_exact_frozen_registry(self):
        registry_bytes = (ROOT / 'contracts/v1/schemas/component-registry.json').read_bytes()
        registry = json.loads(registry_bytes)
        sidecar = json.loads((ROOT / 'research/T0-configuration/display-labels/v0.1.0.json').read_text())
        self.assertEqual(sidecar['registry_version'], registry['schema_version'])
        self.assertEqual(sidecar['registry_sha256'], hashlib.sha256(registry_bytes).hexdigest())
        self.assertEqual(set(sidecar['labels']), set(registry['kinds']))
        values = list(sidecar['labels'].values())
        self.assertTrue(all(isinstance(value, str) and value.strip() == value and value
                            for value in values))
        self.assertEqual(len(values), len(set(values)))
        self.assertEqual(sidecar['sidecar_version'], '0.1.0')
        self.assertEqual(sidecar['locale'], 'en')
        self.assertEqual(sidecar['status'], 'proposed')

    def test_accepted_release_matches_exact_frozen_registry(self):
        registry_bytes = (ROOT / 'contracts/v1/schemas/component-registry.json').read_bytes()
        registry = json.loads(registry_bytes)
        sidecar = json.loads((ROOT / 'research/T0-configuration/display-labels/v1.0.0.json').read_text())
        self.assertEqual(sidecar['registry_version'], registry['schema_version'])
        self.assertEqual(sidecar['registry_sha256'], hashlib.sha256(registry_bytes).hexdigest())
        self.assertEqual(set(sidecar['labels']), set(registry['kinds']))
        self.assertEqual(len(sidecar['labels']), 29)
        values = list(sidecar['labels'].values())
        self.assertTrue(all(isinstance(value, str) and value.strip() == value and value
                            for value in values))
        self.assertEqual(len(values), len(set(values)))
        self.assertEqual(sidecar['sidecar_version'], '1.0.0')
        self.assertEqual(sidecar['locale'], 'en')
        self.assertEqual(sidecar['status'], 'accepted')
        record_path, anchor = sidecar['decision_record'].split('#', 1)
        self.assertEqual(record_path, 'research/T0-configuration/component-schema-compatibility.md')
        self.assertEqual(anchor, 'display-label-sidecar-decision--2026-10-19')
        self.assertIn('## Display-label sidecar decision — 2026-10-19',
                      (ROOT / record_path).read_text())

    def test_accepted_release_preserves_proposed_names(self):
        folder = ROOT / 'research/T0-configuration/display-labels'
        proposal = json.loads((folder / 'v0.1.0.json').read_text())
        accepted = json.loads((folder / 'v1.0.0.json').read_text())
        self.assertEqual(accepted['labels'], proposal['labels'])
        self.assertEqual(proposal['status'], 'proposed')
        self.assertNotEqual(accepted['source_url'], proposal['source_url'])


if __name__ == '__main__':
    unittest.main()
