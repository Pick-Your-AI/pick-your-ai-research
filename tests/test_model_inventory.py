"""Synthetic T1 note integrity regressions; these fixtures are not research."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('model_inventory_validator', ROOT / 'scripts/validate_research.py')
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ModelInventoryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.directory = self.root / 'research/T1-model-selection'
        self.directory.mkdir(parents=True)
        self.inventory = {
            'format': 'research-notes-not-catalog', 'status': 'in_progress',
            'scope': 'Synthetic unresolved candidate.', 'accessed_on': '2026-10-17',
            'records': [{
                'model': 'Synthetic family', 'publisher': 'Synthetic publisher',
                'task_families': ['synthetic_task'], 'input_output': 'Unknown',
                'access': 'Unknown', 'license_evidence': 'Unknown',
                'selection_caveat': 'Unpinned, not deployable or independently verified.',
                'source_ids': ['S1'], 'artifact_type': 'synthetic_family_unpinned',
            }],
        }
        self.sources = {
            'format': 'research-source-register', 'status': 'in_progress',
            'policy': 'Synthetic fixture; not evidence.',
            'sources': [{
                'id': 'S1', 'publisher': 'Synthetic publisher',
                'urls': ['https://example.org/synthetic'], 'accessed_on': '2026-10-17',
                'evidence_grade': 'Unknown', 'observer_group': 'synthetic',
                'verification': 'Blocked access; no independent inference.',
            }],
        }

    def write(self):
        for name, document in (('inventory', self.inventory), ('sources', self.sources)):
            (self.directory / f'model-research-{name}.json').write_text(
                json.dumps(document), encoding='utf-8')

    def check(self):
        self.write()
        before = {p.name: p.read_bytes() for p in self.directory.iterdir()}
        errors = VALIDATOR.model_inventory_errors(self.root)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.directory.iterdir()})
        return errors

    def test_current_repository_notes_pass_without_mutation(self):
        paths = sorted((ROOT / 'research/T1-model-selection').glob('model-research-*.json'))
        before = [p.read_bytes() for p in paths]
        self.assertEqual(VALIDATOR.model_inventory_errors(ROOT), [])
        self.assertEqual(before, [p.read_bytes() for p in paths])

    def test_unknowns_unpinned_families_and_future_text_values_remain_valid(self):
        self.assertEqual(self.check(), [])

    def test_unresolved_and_repeated_source_references_are_rejected(self):
        self.inventory['records'][0]['source_ids'] = ['missing', 'missing']
        errors = '\n'.join(self.check())
        self.assertIn('source_ids: repeated entry', errors)
        self.assertIn('unresolved source ID missing', errors)

    def test_duplicate_source_id_is_rejected_even_with_different_metadata(self):
        duplicate = deepcopy(self.sources['sources'][0])
        duplicate['publisher'] = 'Different publisher'
        self.sources['sources'].append(duplicate)
        self.assertIn('duplicate source ID S1', '\n'.join(self.check()))

    def test_shared_source_and_multiple_distinct_sources_are_valid(self):
        self.inventory['records'].append(deepcopy(self.inventory['records'][0]))
        source = deepcopy(self.sources['sources'][0])
        source['id'] = 'S2'
        self.sources['sources'].append(source)
        self.inventory['records'][0]['source_ids'].append('S2')
        self.assertEqual(self.check(), [])

    def test_missing_or_malformed_documents_have_diagnostics(self):
        self.assertEqual(len(VALIDATOR.model_inventory_errors(self.root)), 2)
        self.write()
        for name, raw in (('inventory', '[]'), ('sources', '{')):
            with self.subTest(name=name):
                self.write()
                path = self.directory / f'model-research-{name}.json'
                path.write_text(raw, encoding='utf-8')
                self.assertIn(path.name, '\n'.join(VALIDATOR.model_inventory_errors(self.root)))

    def test_raw_ambiguous_json_is_rejected_in_both_documents_and_python_modes(self):
        for name in ('inventory', 'sources'):
            for raw in ('{"status":"first","status":"second"}',
                        '{"nested":{"id":1,"id":2}}', '{"value":NaN}',
                        '{"value":Infinity}', '{"value":1e9999}'):
                for optimized in (False, True):
                    with self.subTest(name=name, raw=raw, optimized=optimized):
                        self.write()
                        path = self.directory / f'model-research-{name}.json'
                        path.write_text(raw, encoding='utf-8')
                        code = (
                            'import sys; from pathlib import Path; '
                            'sys.path.insert(0, sys.argv[1]); '
                            'from validate_research import model_inventory_errors; '
                            'errors = model_inventory_errors(Path(sys.argv[2])); '
                            'print("\\n".join(errors)); sys.exit(1 if errors else 0)'
                        )
                        result = subprocess.run(
                            [sys.executable, *(['-O'] if optimized else []), '-c', code,
                             str(ROOT / 'scripts'), str(self.root)],
                            capture_output=True, text=True, timeout=30)
                        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                        self.assertIn(path.name, result.stdout)
                        self.assertEqual(result.stderr, '')

    def test_required_text_fields_reject_missing_blank_and_nontext(self):
        targets = ((self.inventory, ('status', 'scope')),
                   (self.inventory['records'][0], ('model', 'publisher', 'input_output',
                    'access', 'license_evidence', 'selection_caveat', 'artifact_type')),
                   (self.sources, ('status', 'policy')),
                   (self.sources['sources'][0], ('id', 'publisher', 'evidence_grade',
                    'observer_group', 'verification')))
        for target, fields in targets:
            for field in fields:
                original = target[field]
                for value in (None, False, 0, [], {}, ' \t'):
                    with self.subTest(field=field, value=value):
                        target[field] = value
                        self.assertIn(f'/{field}:', '\n'.join(self.check()))
                del target[field]
                self.assertIn(f'/{field}:', '\n'.join(self.check()))
                target[field] = original

    def test_arrays_and_rows_reject_wrong_shapes_without_tracebacks(self):
        for document, key in ((self.inventory, 'records'), (self.sources, 'sources')):
            original = document[key]
            for value in (None, {}, 'text', [], [None], [[]], [False]):
                with self.subTest(key=key, value=value):
                    document[key] = value
                    self.assertIn(f'/{key}', '\n'.join(self.check()))
            document[key] = original
        for target, key in ((self.inventory['records'][0], 'source_ids'),
                            (self.inventory['records'][0], 'task_families'),
                            (self.sources['sources'][0], 'urls')):
            original = target[key]
            for value in (None, {}, 'text', [], [''], [False], [['nested']]):
                with self.subTest(key=key, value=value):
                    target[key] = value
                    self.assertIn(f'/{key}', '\n'.join(self.check()))
            target[key] = original

    def test_dates_and_source_url_syntax_are_checked_without_fetching(self):
        for target in (self.inventory, self.sources['sources'][0]):
            for value in ('2026-02-30', '2026-1-02', '２０２６-10-17', False, None):
                target['accessed_on'] = value
                self.assertIn('/accessed_on:', '\n'.join(self.check()))
            target['accessed_on'] = '2024-02-29'
        for url in ('file:///tmp/test', 'https://', 'https://user@example.org',
                    'https://example.org:bad', 'https://example.org/a\nb'):
            self.sources['sources'][0]['urls'] = [url]
            self.assertIn('/urls:', '\n'.join(self.check()))
        self.sources['sources'][0]['urls'] = ['https://example.org/synthetic']
        self.assertEqual(self.check(), [])

    def test_formats_preserve_research_note_boundary(self):
        self.inventory['format'] = 'catalog'
        self.sources['format'] = 'catalog'
        errors = '\n'.join(self.check())
        self.assertIn('expected research-notes-not-catalog', errors)
        self.assertIn('expected research-source-register', errors)

    def test_standard_tree_validation_checks_notes_but_accepts_minimal_proposal_trees(self):
        self.inventory['records'][0]['source_ids'] = ['missing']
        self.write()
        self.assertIn('unresolved source ID missing', '\n'.join(VALIDATOR.validate_tree(self.root)[0]))
        with tempfile.TemporaryDirectory() as empty:
            self.assertEqual(VALIDATOR.validate_tree(Path(empty)), ([], 0, 0))


if __name__ == '__main__':
    unittest.main()
