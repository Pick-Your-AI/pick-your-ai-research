"""Exercise the market validator CLI using synthetic, isolated invalid inputs."""
from copy import deepcopy
import importlib.util
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
            'integrations.json': [{
                'product_id': 'synthetic-product', 'investigation_rank': 1,
                'access': 'Synthetic documented access', 'rights': 'Synthetic unknown rights',
                'maintenance': 'Synthetic estimate', 'next_action': 'Review synthetic scope',
                'source_ids': ['synthetic-source'], 'review_owner': 'fixture',
                'consumer_issue': 41, 'status': 'Not approved for integration',
                'access_date': '2026-10-16', 'last_checked': '2026-10-16',
                'terms_urls': ['https://example.com/synthetic-terms'],
                'update_cadence': 'Unknown; no service guarantee',
                'rights_evidence_grade': 'Synthetic fixture',
                'reuse_permitted': {use: {'value': 'unknown',
                    'conditions': 'No source-use approval in synthetic input',
                    'basis': 'Synthetic unresolved material scope'}
                    for use in ('automated_retrieval', 'internal_research', 'display', 'redistribution')},
                'research_assessment': {
                    'assessment_date': '2026-10-18', 'scope': 'Synthetic analyst assessment',
                    'ranking_rationale': 'Synthetic research priority, not product approval',
                    'maintenance_evidence_class': 'Estimate',
                    'maintenance_basis': 'Synthetic assumptions, not measured effort',
                    'code_material_scope': 'Synthetic code licence not established',
                    'data_material_scope': 'Synthetic data licence separately unknown',
                    'unresolved_decisions': 'Synthetic receiver reviews exact use',
                },
            }],
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

    def assert_invalid_deliverable(self, value, error_text):
        data = deepcopy(self.data)
        data['research-backlog.json'][0]['deliverable'] = value
        for optimized in (False, True):
            with self.subTest(value=value, optimized=optimized):
                result = self.run_validator(data, optimized)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn('MarketValidationError', result.stderr)
                self.assertIn('backlog #1: deliverable', result.stderr)
                self.assertIn(error_text, result.stderr)
                self.assertNotIn('Market integrity OK', result.stdout)

    def test_deliverable_requires_nonempty_path_text(self):
        for value in (None, True, 1, 1.25, [], {}, '', ' \t\n'):
            self.assert_invalid_deliverable(value, 'nonempty relative file path')

    def test_deliverable_rejects_directories_and_absolute_or_escaping_files(self):
        (self.base / 'nested').mkdir()
        outside = self.root / 'outside-note.md'
        outside.write_text('Synthetic file outside the market directory.\n')
        for value in ('.', 'nested'):
            self.assert_invalid_deliverable(value, 'requires an existing file')
        for value in (str(self.base / 'note.md'), str(outside)):
            self.assert_invalid_deliverable(value, 'requires a relative file path')
        self.assert_invalid_deliverable('../../outside-note.md',
                                        'must remain within research/market')

    def test_deliverable_rejects_external_and_unresolvable_symlinks(self):
        outside = self.root / 'outside-note.md'
        outside.write_text('Synthetic external symlink target.\n')
        self.create_test_symlink(self.base / 'outside-link.md', outside)
        self.assert_invalid_deliverable('outside-link.md',
                                        'must remain within research/market')
        (self.base / 'broken-link.md').symlink_to('missing.md')
        (self.base / 'loop-link.md').symlink_to('loop-link.md')
        for value in ('broken-link.md', 'loop-link.md'):
            self.assert_invalid_deliverable(value, 'resolvable path')

    def test_deliverable_rejects_missing_and_invalid_paths(self):
        for value in ('missing.md', 'missing/../note.md', 'null\x00byte.md'):
            self.assert_invalid_deliverable(value, 'resolvable path')

    def create_test_symlink(self, path, target):
        try:
            path.symlink_to(target)
        except NotImplementedError:
            self.skipTest('symbolic links are unavailable on this platform')
        except OSError as error:
            if sys.platform == 'win32' and error.winerror in (5, 50, 1314):
                self.skipTest('this Windows environment cannot create symbolic links')
            raise

    def test_deliverable_accepts_existing_local_paths_without_rewriting_input(self):
        (self.base / 'nested').mkdir()
        (self.base / 'nested' / 'scoped note.md').write_text('Synthetic nested note.\n')
        for value in ('note.md', 'nested/scoped note.md',
                      'nested/../note.md'):
            self.assert_valid_deliverable(value)

    def test_deliverable_accepts_internal_symlink_without_rewriting_input(self):
        self.create_test_symlink(self.base / 'local-link.md', 'note.md')
        self.assert_valid_deliverable('local-link.md')

    def assert_valid_deliverable(self, value):
        data = deepcopy(self.data)
        data['research-backlog.json'][0]['deliverable'] = value
        for optimized in (False, True):
            with self.subTest(value=value, optimized=optimized):
                result = self.run_validator(data, optimized)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('Market integrity OK', result.stdout)
                self.assertEqual((self.base / 'research-backlog.json').read_text(),
                                 json.dumps(data['research-backlog.json']))

    def assert_invalid_integration(self, records, error_text):
        data = deepcopy(self.data)
        data['integrations.json'] = records
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self.run_validator(data, optimized)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn('MarketValidationError', result.stderr)
                self.assertIn(error_text, result.stderr)
                self.assertNotIn('Market integrity OK', result.stdout)

    def test_integration_shortlist_requires_known_distinct_products_and_ranks(self):
        baseline = self.data['integrations.json']
        for records in (None, {}, [], [None]):
            with self.subTest(records=records):
                self.assert_invalid_integration(records, 'integrations')
        for product in (None, '', 'unknown-product'):
            records = deepcopy(baseline)
            records[0]['product_id'] = product
            self.assert_invalid_integration(records, 'product_id')
        self.assert_invalid_integration(baseline + deepcopy(baseline), 'duplicate product_id')
        for rank in (None, True, 0, -1, 1.0, '1', 2):
            records = deepcopy(baseline)
            records[0]['investigation_rank'] = rank
            with self.subTest(rank=rank):
                self.assert_invalid_integration(records, 'investigation_rank')

    def test_two_integrations_need_distinct_contiguous_ranks(self):
        for rank, valid in ((1, False), (2, True), (3, False)):
            data = deepcopy(self.data)
            product = deepcopy(data['competitors.json'][0])
            product['id'] = 'second-synthetic-product'
            data['competitors.json'].append(product)
            cell = deepcopy(data['features.json']['cells'][0])
            cell['product_id'] = product['id']
            data['features.json']['cells'].append(cell)
            record = deepcopy(data['integrations.json'][0])
            record.update(product_id=product['id'], investigation_rank=rank)
            data['integrations.json'].append(record)
            for optimized in (False, True):
                with self.subTest(rank=rank, optimized=optimized):
                    result = self.run_validator(data, optimized)
                    if valid:
                        self.assertEqual(result.returncode, 0, result.stderr)
                    else:
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        self.assertIn('investigation_rank', result.stderr)

    def test_integration_references_and_terms_are_checked(self):
        for field, values in (
            ('source_ids', (None, [], [None], ['missing'], ['synthetic-source'] * 2)),
            ('terms_urls', (None, [], [None], ['file:///synthetic'],
                            ['https://user:password@example.com/terms'],
                            ['https://example.com/terms'] * 2)),
            ('consumer_issue', (None, True, 0, 1.0, '41')),
        ):
            for value in values:
                with self.subTest(field=field, value=value):
                    records = deepcopy(self.data['integrations.json'])
                    records[0][field] = value
                    self.assert_invalid_integration(records, field)

    def test_integration_metadata_and_independent_dates_are_required(self):
        for field in ('access', 'rights', 'maintenance', 'next_action', 'review_owner',
                      'update_cadence', 'rights_evidence_grade'):
            for value in (None, '', '   ', []):
                records = deepcopy(self.data['integrations.json'])
                records[0][field] = value
                with self.subTest(field=field, value=value):
                    self.assert_invalid_integration(records, field)
        for field in ('access_date', 'last_checked'):
            for value in (None, '2026-02-30', '20261018', '2026-10-18T00:00:00Z'):
                records = deepcopy(self.data['integrations.json'])
                records[0][field] = value
                with self.subTest(field=field, value=value):
                    self.assert_invalid_integration(records, field)

    def test_integration_use_matrix_cannot_gain_unsupported_approval(self):
        for status in (None, '', 'Approved for integration', True):
            records = deepcopy(self.data['integrations.json'])
            records[0]['status'] = status
            self.assert_invalid_integration(records, 'status')
        for matrix in (None, [], {}, {'display': {'value': 'yes'}}):
            records = deepcopy(self.data['integrations.json'])
            records[0]['reuse_permitted'] = matrix
            self.assert_invalid_integration(records, 'reuse_permitted')
        for use in self.data['integrations.json'][0]['reuse_permitted']:
            for mutation in (None, {'value': 'approved'}, {'value': True},
                             {'value': 'yes', 'conditions': '', 'basis': 'Synthetic'},
                             {'value': 'no', 'conditions': 'Synthetic', 'basis': ''}):
                records = deepcopy(self.data['integrations.json'])
                records[0]['reuse_permitted'][use] = mutation
                with self.subTest(use=use, mutation=mutation):
                    self.assert_invalid_integration(records, f'reuse_permitted.{use}')

    def test_conditional_use_and_unknown_rights_do_not_approve_integration(self):
        for value in ('yes', 'no', 'unclear', 'unknown'):
            data = deepcopy(self.data)
            for decision in data['integrations.json'][0]['reuse_permitted'].values():
                decision['value'] = value
            for optimized in (False, True):
                with self.subTest(value=value, optimized=optimized):
                    result = self.run_validator(data, optimized)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(data['integrations.json'][0]['status'],
                                     'Not approved for integration')

    def test_product_exclusion_remains_distinct_from_conditional_source_permission(self):
        data = deepcopy(self.data)
        data['integrations.json'][0]['reuse_permitted']['display']['value'] = 'yes'
        exclusion = {'disposition': 'exclude_from_current_product_scope',
                     'status': 'Synthetic proposal', 'basis': 'Synthetic source/use distinction',
                     'reconsideration': 'Synthetic scoped review',
                     'automated_product_retrieval': False, 'commercial_display': False,
                     'redistribution': False}
        data['integrations.json'][0]['project_use_decision'] = exclusion
        for optimized in (False, True):
            result = self.run_validator(data, optimized)
            self.assertEqual(result.returncode, 0, result.stderr)
        for field in ('automated_product_retrieval', 'commercial_display', 'redistribution'):
            for value in (None, True, 0, 'false'):
                records = deepcopy(data['integrations.json'])
                records[0]['project_use_decision'][field] = value
                with self.subTest(field=field, value=value):
                    self.assert_invalid_integration(records, field)
        for mutation in (None, [], {'disposition': 'approve_for_product_scope'},
                         {**exclusion, 'basis': ''}):
            records = deepcopy(data['integrations.json'])
            records[0]['project_use_decision'] = mutation
            self.assert_invalid_integration(records, 'project_use_decision')

    def test_integration_assessment_separates_materials_and_estimated_maintenance(self):
        for field in self.data['integrations.json'][0]['research_assessment']:
            for value in (None, '', []):
                records = deepcopy(self.data['integrations.json'])
                records[0]['research_assessment'][field] = value
                with self.subTest(field=field, value=value):
                    self.assert_invalid_integration(records, field)
        for value in ('20260230', '2026-02-30', '2026-10-18T00:00:00Z'):
            records = deepcopy(self.data['integrations.json'])
            records[0]['research_assessment']['assessment_date'] = value
            self.assert_invalid_integration(records, 'assessment_date')
        records = deepcopy(self.data['integrations.json'])
        records[0]['research_assessment']['maintenance_evidence_class'] = 'Measured'
        self.assert_invalid_integration(records, 'maintenance_evidence_class')

    def test_integration_json_duplicates_and_nonfinite_values_are_rejected(self):
        original = json.dumps(self.data['integrations.json'])
        cases = ((original.replace('"investigation_rank": 1',
                    '"investigation_rank": 2, "investigation_rank": 1'), 'duplicate JSON object key'),
                 (original.replace('"value": "unknown"',
                    r'"\u0076alue": "yes", "value": "unknown"', 1), 'duplicate JSON object key'),
                 (original.replace('"investigation_rank": 1',
                    '"investigation_rank": NaN'), 'non-finite'))
        for raw, error in cases:
            for optimized in (False, True):
                with self.subTest(error=error, optimized=optimized):
                    result = self.run_validator(self.data, optimized, {'integrations.json': raw})
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn(error, result.stderr)
                    self.assertNotIn('Market integrity OK', result.stdout)

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
                    'https://example.com/synthetic claim',
                    'https://example.com:bad/synthetic',
                    'https://example.com:-1/synthetic',
                    'https://example.com:65536/synthetic',
                    'https://[2001:db8::1]:bad/synthetic'):
            data = self.supported_claim()
            data['features.json']['cells'][0]['evidence_url'] = url
            for optimized in (False, True):
                with self.subTest(url=url, optimized=optimized):
                    result = self.run_validator(data, optimized)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('MarketValidationError', result.stderr)
                    self.assertIn('evidence_url', result.stderr)
                    self.assertNotIn('Market integrity OK', result.stdout)

    def test_supported_claim_accepts_valid_explicit_ports(self):
        for url in ('http://example.com:80/synthetic',
                    'https://example.com:443/synthetic',
                    'https://example.com:8443/synthetic',
                    'https://[2001:db8::1]:443/synthetic'):
            data = self.supported_claim()
            data['features.json']['cells'][0]['evidence_url'] = url
            for optimized in (False, True):
                with self.subTest(url=url, optimized=optimized):
                    result = self.run_validator(data, optimized)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('Market integrity OK', result.stdout)

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

    def data_with_url(self, url, boundary):
        data = self.supported_claim()
        if boundary == 'source URL':
            data['sources.json'][0]['url'] = url
        else:
            data['features.json']['cells'][0]['evidence_url'] = url
        return data

    def assert_invalid_source_metadata(self, field, value, *, missing=False):
        data = deepcopy(self.data)
        if missing:
            del data['sources.json'][0][field]
        else:
            data['sources.json'][0][field] = value
        for optimized in (False, True):
            with self.subTest(field=field, value=value, missing=missing, optimized=optimized):
                result = self.run_validator(data, optimized)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn('MarketValidationError', result.stderr)
                self.assertIn('sources[0]', result.stderr)
                self.assertIn(field, result.stderr)
                self.assertNotIn('Market integrity OK', result.stdout)

    def test_source_access_metadata_requires_nonempty_text(self):
        for field in ('access_date', 'access_status'):
            self.assert_invalid_source_metadata(field, None, missing=True)
            for value in (None, '', ' \t\u2003', True, False, 0, 1, 1.5,
                          [], ['synthetic'], {}, {'synthetic': 'record'}):
                self.assert_invalid_source_metadata(field, value)

    def test_source_access_date_requires_canonical_calendar_date(self):
        for value in ('2026-02-30', '2023-02-29', '1900-02-29', '0000-01-01',
                      '20261018', '2026-W42-7', '2026-10-18T00:00:00Z',
                      '2026-1-8', 'yesterday', '\uff12\uff10\uff12\uff16-\uff11\uff10-\uff11\uff18',
                      '2026-10-18\n', '2026-10-18\x00'):
            self.assert_invalid_source_metadata('access_date', value)

    def test_source_metadata_preserves_valid_dates_statuses_and_original_bytes(self):
        # Complete synthetic rechecks preserve both shapes through their own gate.
        recheck_metadata = {
            'access_date': '2026-10-18', 'access_status': 'Synthetic blocked access',
            'version': 'Unknown; synthetic fixture', 'region': 'Unknown',
            'confidence': 'Unverified synthetic record',
            'limitations': 'No source or product assertion is verified',
            'rights': 'Unknown; no source-use permission established',
        }
        claim_metadata = {
            'publisher': 'Synthetic publisher', 'evidence_class': 'Synthetic fixture',
            'url': 'https://example.com/synthetic-recheck',
        }
        rechecks = [
            {**recheck_metadata, **claim_metadata,
             'claim': 'Synthetic retained singular claim'},
            {**recheck_metadata, 'method': 'Synthetic offline fixture',
             'reviewed_urls': [{'url': claim_metadata['url'],
                                'publisher': claim_metadata['publisher'],
                                'access_status': recheck_metadata['access_status']}],
             'claims': [{**claim_metadata, 'claim': 'Synthetic retained array claim'}]},
        ]
        for access_date, status in (('0001-01-01', 'unverified-access-blocked'),
                                    ('1900-02-28', 'partial / manually retained'),
                                    ('2000-02-29', ' retrieved \u2003'),
                                    ('2024-02-29', '\u672a\u78ba\u8a8d')):
            data = deepcopy(self.data)
            data['sources.json'][0].update(
                access_date=access_date, access_status=status,
                rechecks=deepcopy(rechecks))
            for optimized in (False, True):
                with self.subTest(access_date=access_date, status=status, optimized=optimized):
                    result = self.run_validator(data, optimized)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('Market integrity OK', result.stdout)
                    for name, document in data.items():
                        self.assertEqual((self.base / name).read_bytes(),
                                         json.dumps(document).encode('utf-8'))

    def test_source_url_requires_text_and_credential_free_http_shape(self):
        for url in (None, '', '   ', [], 1, 'file:///synthetic', '/synthetic',
                    'https:///synthetic', 'https://user:password@example.com/synthetic',
                    'https://@example.com/synthetic', 'https://[invalid',
                    'https://example.com/synthetic claim'):
            for optimized in (False, True):
                with self.subTest(url=url, optimized=optimized):
                    result = self.run_validator(self.data_with_url(url, 'source URL'), optimized)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('MarketValidationError', result.stderr)
                    self.assertIn('source URL', result.stderr)
                    self.assertNotIn('Market integrity OK', result.stdout)

    def test_claim_and_source_urls_validate_port_shape_in_both_modes(self):
        for authority, valid in (('example.com', True), ('example.com:443', True),
                                 ('example.com:0', True), ('example.com:65535', True),
                                 ('[::1]:8443', True), ('example.com:not-a-port', False),
                                 ('example.com:65536', False), ('example.com:-1', False)):
            for boundary in ('source URL', 'evidence_url'):
                data = self.data_with_url(f'https://{authority}/synthetic', boundary)
                for optimized in (False, True):
                    with self.subTest(authority=authority, valid=valid, boundary=boundary,
                                      optimized=optimized):
                        result = self.run_validator(data, optimized)
                        if valid:
                            self.assertEqual(result.returncode, 0, result.stderr)
                        else:
                            self.assertNotEqual(result.returncode, 0, result.stdout)
                            self.assertIn('MarketValidationError', result.stderr)
                            self.assertIn(boundary, result.stderr)
                            self.assertNotIn('Market integrity OK', result.stdout)

    def test_claim_and_source_urls_reject_raw_controls_in_both_modes(self):
        for control in ('\x00', '\x1b', '\x7f'):
            for url in (f'{control}https://example.com/synthetic',
                        f'https://exa{control}mple.com/synthetic',
                        f'https://example.com/synthetic{control}'):
                for boundary in ('source URL', 'evidence_url'):
                    data = self.data_with_url(url, boundary)
                    for optimized in (False, True):
                        with self.subTest(url=url, boundary=boundary, optimized=optimized):
                            result = self.run_validator(data, optimized)
                            self.assertNotEqual(result.returncode, 0, result.stdout)
                            self.assertIn('MarketValidationError', result.stderr)
                            self.assertIn(boundary, result.stderr)
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

    def assert_invalid_backlog(self, records, error_text):
        data = deepcopy(self.data)
        data['research-backlog.json'] = records
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self.run_validator(data, optimized)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn('MarketValidationError', result.stderr)
                self.assertIn(error_text, result.stderr)
                self.assertNotIn('Market integrity OK', result.stdout)

    def test_backlog_issue_numbers_are_positive_json_integers(self):
        baseline = self.data['research-backlog.json']
        for value in (True, False, 0, -1, 1.0, 1.5, '1', '', None):
            with self.subTest(number=value):
                records = deepcopy(baseline)
                records[0]['number'] = value
                self.assert_invalid_backlog(records, 'number must be a positive JSON integer')
        records = deepcopy(baseline)
        del records[0]['number']
        self.assert_invalid_backlog(records, 'number must be a positive JSON integer')

    def test_backlog_parent_numbers_cannot_alias_or_disappear(self):
        baseline = self.data['research-backlog.json']
        for value in (True, False, 0, -1, 1.0, 1.5, '1', ''):
            with self.subTest(parent_number=value):
                records = deepcopy(baseline)
                child = deepcopy(records[0])
                child.update(number=2, parent_number=value)
                records.append(child)
                self.assert_invalid_backlog(records, 'parent_number must be a positive JSON integer')

    def test_backlog_scores_require_six_ordinal_integers_or_null(self):
        baseline = self.data['research-backlog.json']
        for scores, total in ((None, 1), ([], 1), ('111111', 1),
                              ([1] * 5, 1), ([1] * 7, 1),
                              ([True] * 6, 1), ([False] * 6, 0),
                              ([1.0] * 6, 1), ([1.5] * 6, 1.5),
                              ([0] * 6, 0), ([6] * 6, 6), (['1'] * 6, 1)):
            with self.subTest(scores=scores):
                records = deepcopy(baseline)
                records[0].update(scores=scores, score=total)
                self.assert_invalid_backlog(records, 'six ordinal JSON integers from 1 to 5 or null')

    def test_backlog_total_requires_a_number_or_exact_unknown(self):
        baseline = self.data['research-backlog.json']
        for total in (True, False, '1', None):
            with self.subTest(total=total):
                records = deepcopy(baseline)
                records[0]['score'] = total
                self.assert_invalid_backlog(records, 'incorrect priority arithmetic')
        for total in (True, 0, 1):
            records = deepcopy(baseline)
            records[0].update(scores=[None, 1, 2, 3, 4, 5], score=total)
            self.assert_invalid_backlog(records, 'incorrect priority arithmetic')

    def test_backlog_integer_graph_and_known_unknown_scores_still_pass(self):
        for scores, total in (([1, 1, 1, 1, 1, 1], 1),
                              ([5, 5, 5, 5, 5, 5], 5.0),
                              ([1, 2, 3, 4, 5, 1], 2.45),
                              ([None, 1, 2, 3, 4, 5], None),
                              ([None] * 6, None)):
            data = deepcopy(self.data)
            root = data['research-backlog.json'][0]
            root.update(scores=scores, score=total, parent_number=None)
            child = deepcopy(root)
            child.update(number=2, parent_number=1)
            data['research-backlog.json'].append(child)
            for optimized in (False, True):
                with self.subTest(scores=scores, total=total, optimized=optimized):
                    result = self.run_validator(data, optimized)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('Market integrity OK: 1 entities, 1 cells, 2 issues', result.stdout)

    def test_raw_priority_totals_cannot_round_to_the_expected_result(self):
        cases = (
            ([1] * 6, '1.0000000000000000000001'),
            ([1] * 6, '0.9999999999999999999999'),
            ([1] * 6, '10000000000000000000001e-22'),
            ([5] * 6, '4.999999999999999999999999'),
            ([5] * 6, '5.000000000000000000000001'),
            ([1, 2, 3, 4, 5, 1], '2.4500000000000000000001'),
            ([1, 2, 3, 4, 5, 1], '2.4499999999999999999999'),
        )
        for scores, token in cases:
            data = deepcopy(self.data)
            data['research-backlog.json'][0].update(scores=scores, score='RAW_TOTAL')
            raw = json.dumps(data['research-backlog.json']).replace('"RAW_TOTAL"', token)
            for optimized in (False, True):
                with self.subTest(token=token, optimized=optimized):
                    result = self.run_validator(data, optimized,
                                                raw_json={'research-backlog.json': raw})
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('incorrect priority arithmetic', result.stderr)
                    self.assertIn('MarketValidationError', result.stderr)
                    self.assertNotIn('Market integrity OK', result.stdout)
                    self.assertEqual((self.base / 'research-backlog.json').read_text(), raw)

    def test_exact_priority_total_spellings_and_unknowns_remain_valid(self):
        cases = (
            ([1] * 6, ('1', '1.0', '1e0', '10e-1', '1.0000000000000000000000')),
            ([5] * 6, ('5.000e0', '50e-1')),
            ([1, 2, 3, 4, 5, 1], ('2.45', '2.4500', '245e-2', '245000e-5')),
            ([None, 1, 2, 3, 4, 5], ('null',)),
        )
        for scores, tokens in cases:
            data = deepcopy(self.data)
            data['research-backlog.json'][0].update(scores=scores, score='RAW_TOTAL')
            for token in tokens:
                raw = json.dumps(data['research-backlog.json']).replace('"RAW_TOTAL"', token)
                for optimized in (False, True):
                    with self.subTest(token=token, optimized=optimized):
                        result = self.run_validator(data, optimized,
                                                    raw_json={'research-backlog.json': raw})
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertIn('Market integrity OK', result.stdout)
                        for name, value in data.items():
                            expected = raw if name == 'research-backlog.json' else json.dumps(value)
                            self.assertEqual((self.base / name).read_text(), expected)

    def test_raw_factor_tokens_keep_the_accepted_integer_only_rule(self):
        tokens = ('1.0', '1e0', '5.000e0', '10e-1',
                  '1.0000000000000000000001', '0.999999999999999999999999',
                  '4.999999999999999999999999', '5.000000000000000000000001')
        for position in range(6):
            for token in tokens:
                data = deepcopy(self.data)
                scores = [1] * 6
                scores[position] = 'RAW_FACTOR'
                data['research-backlog.json'][0]['scores'] = scores
                raw = json.dumps(data['research-backlog.json']).replace('"RAW_FACTOR"', token)
                for optimized in (False, True):
                    with self.subTest(position=position, token=token, optimized=optimized):
                        result = self.run_validator(data, optimized,
                                                    raw_json={'research-backlog.json': raw})
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        self.assertIn('six ordinal JSON integers from 1 to 5 or null', result.stderr)
                        self.assertNotIn('Market integrity OK', result.stdout)

    def test_priority_token_check_preserves_unrelated_numeric_readback(self):
        data = deepcopy(self.data)
        data['research-backlog.json'][0]['unrelated'] = 'RAW_NUMBERS'
        raw = json.dumps(data['research-backlog.json']).replace(
            '"RAW_NUMBERS"', '{"decimal":1.25,"rounded":1.0000000000000000000001,"tiny":1e-10000}')
        result = self.run_validator(data, False, raw_json={'research-backlog.json': raw})
        self.assertEqual(result.returncode, 0, result.stderr)
        spec = importlib.util.spec_from_file_location('synthetic_market_reader', self.script)
        reader = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reader)
        actual = reader.read('research-backlog.json')
        self.assertEqual(actual, json.loads(raw))
        self.assertIs(type(actual[0]['scores'][0]), int)
        self.assertIs(type(actual[0]['score']), float)
        for value in actual[0]['unrelated'].values():
            self.assertIs(type(value), float)
        self.assertEqual((self.base / 'research-backlog.json').read_text(), raw)

    def test_backlog_duplicate_missing_parent_and_cycles_still_fail(self):
        baseline = self.data['research-backlog.json']
        self.assert_invalid_backlog(baseline + deepcopy(baseline), 'duplicate backlog issue')
        records = deepcopy(baseline)
        records[0]['parent_number'] = 2
        self.assert_invalid_backlog(records, 'market integrity check failed')
        child = deepcopy(records[0])
        child.update(number=2, parent_number=1)
        records.append(child)
        self.assert_invalid_backlog(records, 'cyclic parent links')

    def completion_backlog(self, statuses, parents):
        records = []
        for number, (status, parent) in enumerate(zip(statuses, parents), 1):
            item = deepcopy(self.data['research-backlog.json'][0])
            item.update(number=number, status=status, parent_number=parent)
            if status == 'Done':
                item['completion_evidence'] = {
                    'accepted_commit': 'synthetic accepted commit',
                    'review_url': 'https://example.com/synthetic-review',
                    'handoff_acceptance': 'Synthetic fixture, not real acceptance',
                }
            records.append(item)
        return records

    def test_done_parent_rejects_each_unfinished_child_status(self):
        for status in ('Backlog', 'Ready', 'In Progress', 'In Review', 'Blocked'):
            with self.subTest(child_status=status):
                records = self.completion_backlog(['Done', status], [None, 1])
                self.assert_invalid_backlog(
                    records, 'backlog #1: Done requires recorded child #2 to be Done')

    def test_done_ancestors_do_not_hide_unfinished_grandchildren(self):
        records = self.completion_backlog(
            ['Done', 'Done', 'In Progress'], [None, 1, 2])
        self.assert_invalid_backlog(
            records, 'backlog #2: Done requires recorded child #3 to be Done')

    def test_done_parent_child_check_is_independent_of_record_order(self):
        records = self.completion_backlog(['Done', 'Blocked'], [None, 1])
        self.assert_invalid_backlog(
            list(reversed(records)),
            'backlog #1: Done requires recorded child #2 to be Done')

    def test_completed_and_independent_incomplete_trees_remain_valid(self):
        cases = (
            (['Done'], [None]),
            (['Done', 'Done', 'Done'], [None, 1, 2]),
            (['Done', 'Done', 'In Progress', 'Blocked'], [None, 1, None, 3]),
            (['In Progress', 'Done', 'Blocked'], [None, 1, 1]),
        )
        for statuses, parents in cases:
            for reverse in (False, True):
                data = deepcopy(self.data)
                records = self.completion_backlog(statuses, parents)
                data['research-backlog.json'] = records[::-1] if reverse else records
                for optimized in (False, True):
                    with self.subTest(statuses=statuses, reverse=reverse,
                                      optimized=optimized):
                        result = self.run_validator(data, optimized)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertIn('Market integrity OK', result.stdout)
                        for name, value in data.items():
                            self.assertEqual((self.base / name).read_text(),
                                             json.dumps(value))

    def test_done_child_still_requires_its_own_acceptance_evidence(self):
        records = self.completion_backlog(['Done', 'Done'], [None, 1])
        del records[1]['completion_evidence']
        self.assert_invalid_backlog(records, 'Done requires recorded acceptance evidence')

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
