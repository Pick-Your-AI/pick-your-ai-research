"""Synthetic regression cases for the proposed #28 encryption capability rule.

The rule remains research awaiting #40 review. These tests use the frozen
evaluator and schema-valid fictional fixtures; they do not certify encryption.
"""
import importlib.util
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'contracts/v1'
SPEC = importlib.util.spec_from_file_location('memory_rule_evaluator', CONTRACT / 'reference/evaluate.py')
EVALUATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVALUATOR)
SCHEMAS = {p.name: json.loads(p.read_text()) for p in (CONTRACT / 'schemas').glob('*.schema.json')}
REGISTRY = Registry().with_resources((s['$id'], Resource.from_contents(s)) for s in SCHEMAS.values())


class MemoryEncryptionProposal(unittest.TestCase):
    def setUp(self):
        self.build = json.loads((CONTRACT / 'examples/build.json').read_text())
        self.catalog = json.loads((CONTRACT / 'examples/catalog.json').read_text())
        self.rules = json.loads((CONTRACT / 'examples/ruleset.json').read_text())
        lines = (ROOT / 'research/T4-agents-integrations/agent-memory.md').read_text(encoding='utf-8').splitlines()
        candidates = [json.loads(line) for line in lines if line.startswith('{"id":"rule.t4.memory.sensitive.encryption"')]
        self.assertEqual(len(candidates), 1, 'Test the unique rule actually proposed in the note')
        self.rules['rules'] = candidates
        self.memory = next(x for x in self.catalog['items'] if x['kind'] == 'memory_store')
        self.selection = next(x for x in self.build['selections'] if x['kind'] == 'memory_store')
        self.build['objectives']['data_classification'] = 'restricted'

    def finding(self):
        for name, payload in [('build.schema.json', self.build), ('catalog-snapshot.schema.json', self.catalog), ('ruleset.schema.json', self.rules)]:
            Draft202012Validator(SCHEMAS[name], registry=REGISTRY, format_checker=FormatChecker()).validate(payload)
        return EVALUATOR.Evaluator(self.build, self.catalog, self.rules).evaluate()['findings'][0]

    def test_unused_key_cannot_override_false_or_unknown_capability(self):
        for capability, expected in [(False, 'fail'), (None, 'unknown')]:
            for key in [None, 'secret://unused/key']:
                with self.subTest(capability=capability, key=key):
                    if capability is None:
                        self.memory['spec'].pop('encryption_at_rest', None)
                    else:
                        self.memory['spec']['encryption_at_rest'] = capability
                    if key is None:
                        self.selection['settings'].pop('encryption_key_ref', None)
                    else:
                        self.selection['settings']['encryption_key_ref'] = key
                    finding = self.finding()
                    self.assertEqual(finding['outcome'], expected)
                    self.assertTrue(finding['remediation'])
                    self.assertEqual(self.rules['rules'][0]['on_unknown'], 'review')

    def test_documented_default_capability_can_pass_without_customer_key(self):
        self.memory['spec']['encryption_at_rest'] = True
        self.selection['settings'].pop('encryption_key_ref', None)
        for classification in ['restricted', 'confidential']:
            with self.subTest(classification=classification):
                self.build['objectives']['data_classification'] = classification
                self.assertEqual(self.finding()['outcome'], 'pass')

    def test_unencrypted_confidential_store_also_fails(self):
        self.memory['spec']['encryption_at_rest'] = False
        self.build['objectives']['data_classification'] = 'confidential'
        self.assertEqual(self.finding()['outcome'], 'fail')

    def test_out_of_scope_and_disabled_memory_skip(self):
        self.memory['spec']['encryption_at_rest'] = False
        self.build['objectives']['data_classification'] = 'internal'
        self.assertEqual(self.finding()['outcome'], 'skipped')
        self.build['objectives']['data_classification'] = 'restricted'
        self.memory['spec']['memory_type'] = 'session'
        self.assertEqual(self.finding()['outcome'], 'skipped')
        self.memory['spec']['memory_type'] = 'long_term'
        self.selection['enabled'] = False
        self.assertEqual(self.finding()['outcome'], 'skipped')


if __name__ == '__main__':
    unittest.main()
