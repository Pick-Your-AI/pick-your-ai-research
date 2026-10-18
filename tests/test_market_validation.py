"""Exercise the market validator CLI using synthetic, isolated invalid inputs."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MarketValidation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'scripts').mkdir()
        self.base = self.root / 'research/market'
        self.base.mkdir(parents=True)
        self.script = self.root / 'scripts/validate_market_research.py'
        shutil.copyfile(ROOT / 'scripts/validate_market_research.py', self.script)
        (self.base / 'note.md').write_text('Synthetic test-only deliverable.\n')
        self.data = {
            'competitors.json': [{'id': 'synthetic-product', 'source_ids': ['synthetic-source'],
                                  'last_verification': '2026-10-18', 'limitations': 'Synthetic fixture'}],
            'sources.json': [{'id': 'synthetic-source', 'url': 'https://example.com/synthetic',
                              'access_date': '2026-10-18', 'access_status': 'synthetic'}],
            'features.json': {'definitions': {'feature': {}},
                              'capability_tests': {'feature': {'scenario': 'Synthetic input',
                                  'pass_observable': 'Synthetic output',
                                  'failure_policy': 'Unperformed is Unknown',
                                  'required_conditions': ['synthetic condition']}}, 'status_semantics': {'Unknown': {}, 'Documented': {}},
                              'cells': [{'product_id': 'synthetic-product', 'feature': 'feature',
                                         'status': 'Unknown', 'evidence_ids': []}]},
            'research-backlog.json': [{'number': 1, 'question': 'Synthetic?', 'owner': 'fixture',
                                      'workstream': 'fixture', 'priority': 'fixture', 'readiness': 'fixture',
                                      'status': 'In Progress', 'deliverable': 'note.md', 'steps': ['fixture'],
                                      'priority_rationale': 'fixture', 'next_action': 'fixture',
                                      'scores': [1, 1, 1, 1, 1, 1], 'score': 1.0}],
        }

    def run_validator(self, data, optimized):
        for name, value in data.items():
            (self.base / name).write_text(json.dumps(value), encoding='utf-8')
        return subprocess.run([sys.executable, *(['-O'] if optimized else []), str(self.script)],
                              capture_output=True, text=True, timeout=5)

    def test_valid_unknown_claim_passes_in_both_modes(self):
        # Unknown cells intentionally need neither asserted capability nor evidence.
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self.run_validator(self.data, optimized)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('Market integrity OK: 1 entities, 1 cells, 1 issues', result.stdout)

    def test_capability_test_integrity_in_both_modes(self):
        mutations = [
            ('missing tests', None),
            ('missing feature', {}),
            ('extra feature', {'extra': deepcopy(self.data['features.json']['capability_tests']['feature'])}),
            ('non-object test', {'feature': []}),
        ]
        baseline = self.data['features.json']['capability_tests']
        for field in ('scenario', 'pass_observable', 'failure_policy', 'required_conditions'):
            for value in (None, '', '   ', [], [None]):
                tests = deepcopy(baseline)
                tests['feature'][field] = value
                mutations.append((f'{field}={value!r}', tests))
        for name, tests in mutations:
            data = deepcopy(self.data)
            if tests is None:
                del data['features.json']['capability_tests']
            else:
                data['features.json']['capability_tests'] = tests
            for optimized in (False, True):
                with self.subTest(case=name, optimized=optimized):
                    result = self.run_validator(data, optimized)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('MarketValidationError', result.stderr)
                    self.assertNotIn('Market integrity OK', result.stdout)

    def test_invalid_inputs_fail_in_both_modes(self):
        cases = []
        data = deepcopy(self.data)
        data['competitors.json'].append(deepcopy(data['competitors.json'][0]))
        cases.append(('duplicate competitor', data, 'duplicate competitor IDs'))
        data = deepcopy(self.data)
        data['sources.json'][0]['url'] = 'https://fixture:fixture@example.com/synthetic'
        cases.append(('credential URL', data, 'credentials in source URL'))
        data = deepcopy(self.data)
        data['features.json']['cells'] = []
        cases.append(('incomplete matrix', data, 'incomplete matrix'))
        data = deepcopy(self.data)
        data['features.json']['cells'][0].update(status='Documented', basis='synthetic', verification_method='synthetic')
        cases.append(('unsupported documented claim', data, 'market integrity check failed'))
        data = deepcopy(self.data)
        data['competitors.json'][0]['source_ids'] = ['missing-source']
        cases.append(('dangling source', data, 'market integrity check failed'))
        data = deepcopy(self.data)
        data['research-backlog.json'][0]['score'] = 5.0
        cases.append(('wrong priority arithmetic', data, 'incorrect priority arithmetic'))
        data = deepcopy(self.data)
        data['research-backlog.json'][0]['status'] = 'Done'
        cases.append(('unrecorded acceptance', data, 'Done requires recorded acceptance evidence'))
        data = deepcopy(self.data)
        data['research-backlog.json'][0]['parent_number'] = 1
        cases.append(('parent cycle', data, 'cyclic parent links'))
        for name, data, message in cases:
            for optimized in (False, True):
                with self.subTest(case=name, optimized=optimized):
                    result = self.run_validator(data, optimized)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('MarketValidationError', result.stderr)
                    self.assertIn(message, result.stderr)
                    self.assertNotIn('Market integrity OK', result.stdout)
