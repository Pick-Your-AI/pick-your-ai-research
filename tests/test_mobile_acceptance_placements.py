"""Real register integrity and adversarial placement/source preservation checks."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MOBILE = ROOT / 'prompts/mobile'
spec = importlib.util.spec_from_file_location(
    'mobile_accepted_placements', MOBILE / 'acceptance_placements.py')
placements = importlib.util.module_from_spec(spec)
spec.loader.exec_module(placements)


class AcceptedPlacementsTests(unittest.TestCase):
    def setUp(self):
        self.register = placements.read_json(MOBILE / 'acceptance-placements.json')
        self.records = placements.read_json(MOBILE / 'coverage.json')['issues']
        self.index = (MOBILE / 'INDEX.md').read_text(encoding='utf-8')

    def row(self, number, platform='android'):
        return next(r for r in self.records
                    if r['platform'] == platform and r['number'] == number)

    def validate(self):
        return placements.validate_placements(self.register, self.records, self.index)

    def test_complete_register_and_no_input_mutation(self):
        original = copy.deepcopy((self.register, self.records, self.index))
        self.assertEqual(7, self.validate())
        self.assertEqual(original, (self.register, self.records, self.index))
        self.assertEqual(placements.WEBSITE, self.row(48)['acceptance_repository'])
        self.assertEqual('docs/delivery/android/work-packages/02.01.md',
                         self.row(48)['acceptance_path'])

    def test_raw_json_duplicate_keys_constants_and_overflow(self):
        samples = [
            '{"schema_version":1,"schema_version":1}',
            '{"amendments":[{"review_url":"pending","review_url":"accepted"}]}',
            '{"nested":{"value":NaN}}', '{"value":Infinity}',
            '{"value":-Infinity}', '{"value":1e9999}',
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.json'
            for sample in samples:
                with self.subTest(sample=sample):
                    path.write_text(sample, encoding='utf-8')
                    with self.assertRaises(ValueError):
                        placements.read_json(path)

    def test_closed_shapes_and_exact_integer_versions(self):
        original = copy.deepcopy(self.register)
        for value in (True, 1.0, '1', 2, None):
            with self.subTest(version=value):
                self.register = copy.deepcopy(original)
                self.register['schema_version'] = value
                with self.assertRaises(ValueError):
                    self.validate()
        for path, key in [((), 'extra'), (('source_snapshot',), 'extra'),
                          (('amendments', 0), 'extra'),
                          (('amendments', 0, 'decision_record'), 'extra'),
                          (('amendments', 0, 'placements', 0), 'extra')]:
            with self.subTest(path=path):
                self.register = copy.deepcopy(original)
                target = self.register
                for part in path:
                    target = target[part]
                target[key] = 'undeclared'
                with self.assertRaises(ValueError):
                    self.validate()

    def test_source_snapshot_identity_and_shapes(self):
        original = copy.deepcopy(self.register)
        for key, value in [('repository', placements.WEBSITE),
                           ('ledger_path', 'docs/delivery/unreviewed.json'),
                           ('ledger_schema_version', 6.0),
                           ('ledger_schema_version', True), ('commit', 'main'),
                           ('tree', 'g' * 40), ('ledger_sha256', 'a' * 63)]:
            with self.subTest(key=key, value=value):
                self.register = copy.deepcopy(original)
                self.register['source_snapshot'][key] = value
                with self.assertRaises(ValueError):
                    self.validate()

    def test_missing_duplicate_and_unsupported_amendments(self):
        original = copy.deepcopy(self.register)
        for change in ('missing', 'duplicate', 'unsupported'):
            with self.subTest(change=change):
                self.register = copy.deepcopy(original)
                if change == 'missing':
                    self.register['amendments'].pop()
                elif change == 'duplicate':
                    self.register['amendments'].append(self.register['amendments'][0])
                else:
                    self.register['amendments'][0]['id'] = 'android-adr-unaccepted'
                with self.assertRaises(ValueError):
                    self.validate()

    def test_exact_pr_review_and_accepted_commit(self):
        original = copy.deepcopy(self.register)
        for key, value in [('decision_issue', placements.ANDROID + '#48'),
                           ('source_repository', placements.WEBSITE),
                           ('pull_request', 279.0), ('pull_request', True),
                           ('pull_request', 382), ('accepted_commit', 'main'),
                           ('accepted_commit', 'a' * 40), ('accepted_tree', 'b' * 40),
                           ('review_url', placements.BASE + '/pull/382#pullrequestreview-1')]:
            with self.subTest(key=key, value=value):
                self.register = copy.deepcopy(original)
                self.register['amendments'][0][key] = value
                with self.assertRaises(ValueError):
                    self.validate()

    def test_exact_adr_and_receipt_bindings(self):
        original = copy.deepcopy(self.register)
        for target_path in [('decision_record',), ('placements', 0)]:
            for key, value in [('path', 'docs/decisions/unaccepted.md'),
                               ('url', placements.BASE + '/blob/main/record.md'),
                               ('sha256', 'F' * 64)]:
                with self.subTest(target=target_path, key=key):
                    self.register = copy.deepcopy(original)
                    target = self.register['amendments'][0]
                    for part in target_path:
                        target = target[part]
                    target[key] = value
                    with self.assertRaises(ValueError):
                        self.validate()
        self.register = copy.deepcopy(original)
        self.register['amendments'][0]['placements'][0]['url'] += '?raw=1'
        with self.assertRaises(ValueError):
            self.validate()

    def test_exact_nonoverlapping_adr_record_sets(self):
        original = copy.deepcopy(self.register)
        for change in ('missing', 'duplicate', 'other_adr', 'extra'):
            with self.subTest(change=change):
                self.register = copy.deepcopy(original)
                records = self.register['amendments'][1]['placements']
                if change == 'missing':
                    records.pop()
                elif change == 'duplicate':
                    records.append(records[0])
                elif change == 'other_adr':
                    records[0] = self.register['amendments'][0]['placements'][0]
                else:
                    records.append(dict(records[0], issue=placements.ANDROID + '#48'))
                with self.assertRaises(ValueError):
                    self.validate()

    def test_registered_coordinate_and_marker_must_match(self):
        original = copy.deepcopy(self.records)
        for key, value in [('number', 20.0), ('platform', 'apple'),
                           ('acceptance_placement_amendment', 'android-adr-0001'),
                           ('acceptance_repository', placements.WEBSITE),
                           ('acceptance_path', 'docs/delivery/android/work-packages/01.02.md'),
                           ('acceptance_output', 'other output')]:
            with self.subTest(key=key):
                self.records = copy.deepcopy(original)
                self.row(20)[key] = value
                with self.assertRaises(ValueError):
                    self.validate()

    def test_unregistered_issue_cannot_move_or_borrow_authority(self):
        original = copy.deepcopy(self.records)
        for key, value in [('acceptance_repository', placements.ANDROID),
                           ('acceptance_placement_amendment', 'android-adr-0002')]:
            with self.subTest(key=key):
                self.records = copy.deepcopy(original)
                self.row(48)[key] = value
                with self.assertRaises(ValueError):
                    self.validate()

    def test_empty_path_does_not_hide_android_or_apple_relocation(self):
        for platform, number in [('android', 48), ('apple', 20)]:
            with self.subTest(platform=platform):
                self.setUp()
                row = self.row(number, platform)
                row['acceptance_path'] = None
                row['acceptance_repository'] = placements.ANDROID
                with self.assertRaises(ValueError):
                    self.validate()

    def test_historical_fields_and_order_are_preserved(self):
        original = copy.deepcopy(self.records)
        for field, value in [('source_body_sha256', 'a' * 64),
                             ('acceptance_criteria', ['replacement']),
                             ('assignees', ['invented-owner'])]:
            with self.subTest(field=field):
                self.records = copy.deepcopy(original)
                self.row(48)[field] = value
                with self.assertRaisesRegex(ValueError, 'captured issue fields'):
                    self.validate()
        self.records = list(reversed(original))
        with self.assertRaisesRegex(ValueError, 'captured issue fields'):
            self.validate()

    def test_coordinated_boundary_and_website_filename_changes_fail(self):
        row = self.row(20)
        row['delivery_review_boundary'] += '\nChanged receiving authority.'
        receipt = self.register['amendments'][1]['placements'][0]
        receipt['previous_boundary_sha256'] = hashlib.sha256(
            row['delivery_review_boundary'].encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'captured issue fields'):
            self.validate()
        self.setUp()
        row = self.row(48)
        old, new = row['acceptance_path'], 'docs/delivery/android/work-packages/99.99.md'
        row['acceptance_path'] = row['acceptance_output'] = new
        row['delivery_review_boundary'] = row['delivery_review_boundary'].replace(old, new)
        self.index = self.index.replace(f'`{old}`', f'`{new}`')
        with self.assertRaisesRegex(ValueError, 'captured issue fields'):
            self.validate()

    def test_missing_duplicate_coverage_and_missing_marker(self):
        original = copy.deepcopy(self.records)
        for change in ('missing', 'duplicate', 'marker'):
            with self.subTest(change=change):
                self.records = copy.deepcopy(original)
                if change == 'missing':
                    self.records.remove(self.row(20))
                elif change == 'duplicate':
                    self.records.append(self.row(20))
                else:
                    del self.row(20)['acceptance_placement_amendment']
                with self.assertRaises(ValueError):
                    self.validate()

    def test_index_requires_one_exact_pinned_destination(self):
        original = self.index
        receipt = self.register['amendments'][1]['placements'][0]
        line = next(line for line in self.index.splitlines()
                    if 'id="issue-android-20"' in line)
        for replacement in [line.replace(receipt['url'], receipt['url'] + '?raw=1'),
                            line.replace(receipt['url'], placements.BASE + '/blob/main/' + receipt['path']),
                            line.replace('in `' + placements.ANDROID + '`', 'in `' + placements.WEBSITE + '`'),
                            line + '\n' + line, '']:
            with self.subTest(replacement=replacement[-80:]):
                self.index = original.replace(line, replacement)
                with self.assertRaises(ValueError):
                    self.validate()

    def test_optimized_cli_rejects_ambiguous_inputs_and_unregistered_moves(self):
        with tempfile.TemporaryDirectory() as directory:
            mobile = Path(directory) / 'mobile'
            mobile.mkdir()
            for name in ['acceptance_placements.py', 'validate_prompts.py',
                         'acceptance-placements.json', 'coverage.json',
                         'project-fields.json', 'INDEX.md']:
                shutil.copyfile(MOBILE / name, mobile / name)
            originals = {name: (mobile / name).read_text(encoding='utf-8')
                         for name in ['acceptance-placements.json', 'coverage.json']}
            cases = [
                ('acceptance-placements.json', '{"schema_version":1,"schema_version":1}'),
                ('coverage.json', '{"issues":[],"issues":[]}'),
            ]
            self.row(48)['acceptance_repository'] = placements.ANDROID
            cases.append(('coverage.json', json.dumps({'issues': self.records})))
            for name, invalid in cases:
                with self.subTest(name=name, invalid=invalid[:80]):
                    for source, text in originals.items():
                        (mobile / source).write_text(text, encoding='utf-8')
                    (mobile / name).write_text(invalid, encoding='utf-8')
                    result = subprocess.run(
                        [sys.executable, '-O', str(mobile / 'validate_prompts.py')],
                        capture_output=True, text=True, check=False)
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn('Acceptance placements:', result.stderr)


if __name__ == '__main__':
    unittest.main()
