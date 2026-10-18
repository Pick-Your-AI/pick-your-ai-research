"""Display sidecar coverage and registry binding, not owner acceptance."""
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


if __name__ == '__main__':
    unittest.main()
