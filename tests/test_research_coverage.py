"""Synthetic coverage counts preserve denominator and input-byte identity."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import research_coverage as coverage


class ResearchCoverageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write('contracts/v1/schemas/component-registry.json',
                   {'kinds': {kind: {'tier': 'T0', 'cardinality': 'many',
                                     'activation': 'optional', 'notes': 'Synthetic kind.'}
                              for kind in ('model', 'tool', 'storage')}})
        self.write('catalog/proposals/model.json', {'kind': 'model'})
        self.write('catalog/proposals/tool.json', {'kind': 'tool'})
        self.write('pricing/proposals/prices.json', {'rates': [{'id': 'a'}, {'id': 'b'}]})
        self.write('research/market/competitors.json', [{'id': 'synthetic'}])
        self.features = {'definitions': {'a': 'A', 'b': 'B'}, 'cells': [
            {'product_id': 'synthetic', 'feature': 'a', 'status': 'Documented'},
            {'product_id': 'synthetic', 'feature': 'b', 'status': 'Unknown'},
        ]}
        self.write('research/market/features.json', self.features)

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding='utf-8')

    def test_counts_retain_zero_kinds_and_unknown_cells(self):
        result = coverage.snapshot(self.root)
        self.assertEqual(result['catalog']['proposals_by_kind'],
                         {'model': 1, 'tool': 1, 'storage': 0})
        self.assertEqual(result['catalog']['kinds_with_proposals'], 2)
        self.assertEqual(result['pricing'], {'pricebook_count': 1, 'rate_count': 2})
        self.assertEqual(result['market']['cell_count'], 2)
        self.assertEqual(result['market']['cells_by_status'],
                         {'Exercised': 0, 'Documented': 1, 'Unsupported': 0, 'Unknown': 1})

    def test_hashes_pin_bytes_and_ignore_unrelated_files(self):
        before = coverage.snapshot(self.root)
        self.write('research/unrelated.json', {'extra': True})
        self.assertEqual(before, coverage.snapshot(self.root))
        path = self.root / 'catalog/proposals/model.json'
        path.write_bytes(path.read_bytes() + b'\n')
        after = coverage.snapshot(self.root)
        self.assertEqual(before['catalog'], after['catalog'])
        self.assertNotEqual(before['input_sha256'], after['input_sha256'])
        self.assertEqual(after['input_sha256']['catalog/proposals/model.json'],
                         hashlib.sha256(path.read_bytes()).hexdigest())

    def test_added_proposal_changes_snapshot(self):
        before = coverage.snapshot(self.root)
        self.write('catalog/proposals/second-model.json', {'kind': 'model'})
        after = coverage.snapshot(self.root)
        self.assertEqual(after['catalog']['proposal_count'], before['catalog']['proposal_count'] + 1)
        self.assertIn('catalog/proposals/second-model.json', after['input_sha256'])

    def test_nested_proposals_and_pricebooks_match_intake_discovery(self):
        self.write('catalog/proposals/nested/second-model.json', {'kind': 'model'})
        self.write('pricing/proposals/nested/second-book.json', {'rates': [{'id': 'a'}]})
        result = coverage.snapshot(self.root)
        self.assertEqual(result['catalog']['proposals_by_kind']['model'], 2)
        self.assertEqual(result['pricing'], {'pricebook_count': 2, 'rate_count': 3})
        self.assertIn('catalog/proposals/nested/second-model.json', result['input_sha256'])
        self.assertIn('pricing/proposals/nested/second-book.json', result['input_sha256'])

    def test_ambiguous_json_is_rejected(self):
        path = self.root / 'catalog/proposals/model.json'
        for raw in ('{"kind":"model","kind":"tool"}', '{"kind":"model","value":NaN}'):
            with self.subTest(raw=raw):
                path.write_text(raw)
                with self.assertRaises(ValueError):
                    coverage.snapshot(self.root)

    def test_unknown_catalog_kind_is_rejected(self):
        self.write('catalog/proposals/model.json', {'kind': 'invented'})
        with self.assertRaisesRegex(ValueError, 'unknown catalog kind'):
            coverage.snapshot(self.root)

    def test_invalid_market_denominators_are_rejected(self):
        for mutation in ('missing', 'duplicate', 'unknown-product', 'unknown-feature', 'unknown-status'):
            with self.subTest(mutation=mutation):
                value = json.loads(json.dumps(self.features))
                if mutation == 'missing':
                    value['cells'].pop()
                elif mutation == 'duplicate':
                    value['cells'].append(value['cells'][0])
                else:
                    key, invalid = {'unknown-product': ('product_id', 'other'),
                                    'unknown-feature': ('feature', 'other'),
                                    'unknown-status': ('status', 'supported')}[mutation]
                    value['cells'][0][key] = invalid
                self.write('research/market/features.json', value)
                with self.assertRaises(ValueError):
                    coverage.snapshot(self.root)

    def test_duplicate_products_are_rejected(self):
        self.write('research/market/competitors.json', [{'id': 'synthetic'}, {'id': 'synthetic'}])
        with self.assertRaisesRegex(ValueError, 'duplicate market product'):
            coverage.snapshot(self.root)

    def test_malformed_denominator_shapes_are_rejected(self):
        cases = {
            'contracts/v1/schemas/component-registry.json': [
                {'kinds': value} for value in ([], ['model'], {}, {'': {}},
                    {'model': {}}, {'model': None}, {'  ': {}}, {'model': 'description'},
                    {'model': {'tier': 'T0', 'cardinality': 'many',
                               'activation': 'optional', 'notes': '  '}})],
            'research/market/competitors.json': [
                [], {}, ['synthetic'], [{}], [{'id': ''}], [{'id': '  '}],
                [{'id': 1}], [{'id': True}], [{'id': []}]],
            'pricing/proposals/prices.json': [
                {'rates': value} for value in ({}, ['a'], [{}], [{'id': ''}],
                    [{'id': '  '}], [{'id': False}], [{'id': []}],
                    [{'id': 'a'}, {'id': 'a'}])],
            'research/market/features.json': [
                {'definitions': value, 'cells': []} for value in (
                    {}, [], ['a'], {'': 'A'}, {'  ': 'A'}, {'a': ''},
                    {'a': '  '}, {'a': None}, {'a': {}}, {'a': False})],
        }
        for name, values in cases.items():
            original = (self.root / name).read_bytes()
            for value in values:
                with self.subTest(name=name, value=value):
                    self.write(name, value)
                    with self.assertRaises(ValueError):
                        coverage.snapshot(self.root)
            (self.root / name).write_bytes(original)

    def test_kind_definition_requires_each_recorded_text_field(self):
        definition = {'tier': 'T0', 'cardinality': 'many',
                      'activation': 'optional', 'notes': 'Synthetic kind.'}
        for field in definition:
            for invalid in (None, False, 1, [], {}, '', '  '):
                with self.subTest(field=field, invalid=invalid):
                    value = dict(definition, **{field: invalid})
                    self.write('contracts/v1/schemas/component-registry.json',
                               {'kinds': {'model': value}})
                    with self.assertRaisesRegex(ValueError, 'kind definition'):
                        coverage.snapshot(self.root)
            value = dict(definition)
            del value[field]
            self.write('contracts/v1/schemas/component-registry.json',
                       {'kinds': {'model': value}})
            with self.assertRaisesRegex(ValueError, 'kind definition'):
                coverage.snapshot(self.root)

    def test_empty_rates_remain_valid_and_ids_are_scoped_to_each_book(self):
        self.write('pricing/proposals/empty.json', {'rates': []})
        self.write('pricing/proposals/another.json', {'rates': [{'id': 'a'}]})
        self.assertEqual(coverage.snapshot(self.root)['pricing'],
                         {'pricebook_count': 3, 'rate_count': 3})

    def test_check_command_detects_stale_input(self):
        path = self.root / 'snapshot.json'
        path.write_text(coverage.render(coverage.snapshot(self.root)))
        with patch.object(coverage, 'ROOT', self.root), contextlib.redirect_stdout(io.StringIO()):
            coverage.main(['--check', str(path)])
            self.write('catalog/proposals/second-model.json', {'kind': 'model'})
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                coverage.main(['--check', str(path)])
        self.assertEqual(raised.exception.code, 1)

    def test_committed_snapshot_matches_repository_inputs(self):
        path = coverage.ROOT / 'research/coverage/repository-snapshot.json'
        self.assertEqual(path.read_text(encoding='utf-8'),
                         coverage.render(coverage.snapshot(coverage.ROOT)))


if __name__ == '__main__':
    unittest.main()
