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

    def run_validator(self, data, optimized, raw_json=None):
        for name, value in data.items():
            text = raw_json[name] if raw_json and name in raw_json else json.dumps(value)
            (self.base / name).write_text(text, encoding='utf-8')
        return subprocess.run([sys.executable, *(['-O'] if optimized else []), str(self.script)],
                              capture_output=True, text=True, timeout=5)

    def test_valid_unknown_claim_passes_in_both_modes(self):
        # Unknown cells intentionally need neither asserted capability nor evidence.
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self.run_validator(self.data, optimized)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('Market integrity OK: 1 entities, 1 cells, 1 issues', result.stdout)

    def supported_claim(self):
        data = deepcopy(self.data)
        data['features.json']['cells'][0].update(
            status='Documented', evidence_ids=['synthetic-source'],
            basis='Synthetic claim for validator regression only',
            verification_method='Synthetic documentary check',
            evidence_grade='Vendor claim',
            evidence_url='https://example.com/synthetic-claim',
            access_date='2026-10-18', confidence='Synthetic limited confidence',
            limitations='Not real product evidence', audit_scope='synthetic-test-only')
        return data

    def test_complete_supported_claims_pass_in_both_modes(self):
        for status in ('Documented', 'Exercised', 'Unsupported'):
            data = self.supported_claim()
            data['features.json']['status_semantics'][status] = 'Synthetic test grade'
            data['features.json']['cells'][0]['status'] = status
            for optimized in (False, True):
                with self.subTest(status=status, optimized=optimized):
                    result = self.run_validator(data, optimized)
                    self.assertEqual(result.returncode, 0, result.stderr)

    def test_supported_claim_metadata_cannot_be_missing_blank_or_nontext(self):
        for field in ('basis', 'verification_method', 'evidence_grade', 'evidence_url',
                      'access_date', 'confidence', 'limitations', 'audit_scope'):
            for value in (None, '', '   ', [], 1):
                data = self.supported_claim()
                if value is None:
                    del data['features.json']['cells'][0][field]
                else:
                    data['features.json']['cells'][0][field] = value
                for optimized in (False, True):
                    with self.subTest(field=field, value=value, optimized=optimized):
                        result = self.run_validator(data, optimized)
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        self.assertIn('MarketValidationError', result.stderr)
                        self.assertIn(field, result.stderr)
                        self.assertNotIn('Market integrity OK', result.stdout)

    def test_supported_claim_requires_a_credential_free_http_url(self):
        for url in ('file:///synthetic', '/synthetic', 'https:///synthetic',
                    'https://user:password@example.com/synthetic',
                    'https://@example.com/synthetic', 'https://[invalid',
                    'https://example.com/synthetic claim'):
            data = self.supported_claim()
            data['features.json']['cells'][0]['evidence_url'] = url
            for optimized in (False, True):
                with self.subTest(url=url, optimized=optimized):
                    result = self.run_validator(data, optimized)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('MarketValidationError', result.stderr)
                    self.assertIn('evidence_url', result.stderr)
                    self.assertNotIn('Market integrity OK', result.stdout)

    def test_supported_claim_requires_an_actual_iso_access_date(self):
        for access_date in ('2026-02-30', '20261018', '2026-10-18T00:00:00Z', 'yesterday'):
            data = self.supported_claim()
            data['features.json']['cells'][0]['access_date'] = access_date
            for optimized in (False, True):
                with self.subTest(access_date=access_date, optimized=optimized):
                    result = self.run_validator(data, optimized)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('MarketValidationError', result.stderr)
                    self.assertIn('access_date', result.stderr)
                    self.assertNotIn('Market integrity OK', result.stdout)

    def test_duplicate_json_keys_fail_before_market_data_is_interpreted(self):
        original = json.dumps(self.data['features.json'])
        cases = (
            original.replace('"definitions":', '"definitions": {}, "definitions":', 1),
            original.replace('"status": "Unknown"',
                             '"status": "Documented", "status": "Unknown"', 1),
            original.replace('"status": "Unknown"',
                             r'"\u0073tatus": "Documented", "status": "Unknown"', 1),
        )
        for raw in cases:
            for optimized in (False, True):
                with self.subTest(raw=raw, optimized=optimized):
                    result = self.run_validator(self.data, optimized, {'features.json': raw})
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('duplicate JSON object key', result.stderr)
                    self.assertNotIn('Market integrity OK', result.stdout)

    def test_nonfinite_json_numbers_fail_even_in_unconsumed_metadata(self):
        original = json.dumps(self.data['features.json'])
        for literal in ('NaN', 'Infinity', '-Infinity', '1e400', '-1e400'):
            raw = original[:-1] + ', "synthetic_numeric_metadata": ' + literal + '}'
            for optimized in (False, True):
                with self.subTest(literal=literal, optimized=optimized):
                    result = self.run_validator(self.data, optimized, {'features.json': raw})
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('finite', result.stderr)
                    self.assertNotIn('Market integrity OK', result.stdout)

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
