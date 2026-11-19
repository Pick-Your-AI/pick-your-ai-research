"""Negative controls for the actual closed-cohort T1 research assessment."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('t1_crosswalk', ROOT / 'scripts/validate_t1_identity_crosswalk.py')
CROSSWALK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CROSSWALK)


class T1IdentityCrosswalkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        for relative in (*CROSSWALK.INPUTS, CROSSWALK.DIRECTORY + 'manifest.json',
                         CROSSWALK.DIRECTORY + 'rows.jsonl'):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        self.path = self.root / CROSSWALK.DIRECTORY / 'rows.jsonl'
        self.rows = [json.loads(line) for line in self.path.read_text().splitlines()]

    def write_rows(self):
        self.path.write_text(''.join(json.dumps(row) + '\n' for row in self.rows))

    def reject(self, message):
        with self.assertRaisesRegex(ValueError, message):
            CROSSWALK.validate(self.root)

    def test_committed_full_cohort_and_qualified_examples(self):
        self.assertEqual(CROSSWALK.validate(ROOT), 248)
        by_name = {row['candidate']: row for row in self.rows}
        self.assertEqual(by_name['BAAI/bge-m3']['identity_refs'][0]['state'],
                         'recorded_repository_locator')
        self.assertEqual(by_name['Marble2 Developer API']['assessment'],
                         'service_requires_release_binding')
        self.assertEqual(by_name['Graphormer model/backbone recipes']['next_action'],
                         'select_fitted_artifact')
        snapshot = by_name['omni-moderation-2024-09-26']
        self.assertEqual(snapshot['assessment'], 'recorded_snapshot_name')
        self.assertEqual(snapshot['known_unknowns'], 'snapshot_route_unresolved')
        self.assertEqual(sum(row['recorded_type'] != 'model' for row in self.rows), 15)

    def test_input_byte_change_is_stale_even_when_json_meaning_is_unchanged(self):
        source = self.root / CROSSWALK.INPUTS[1]
        source.write_bytes(source.read_bytes() + b'\n')
        self.reject('input bytes changed')

    def test_missing_extra_and_reordered_rows_are_not_a_smaller_denominator(self):
        original = self.rows[:]
        for changed in (original[:-1], original + [original[0]], original[::-1]):
            with self.subTest(length=len(changed)):
                self.rows = changed
                self.write_rows()
                self.reject('cohort row count|row identity/order')

    def test_row_binding_cannot_change_candidate_source_or_hash(self):
        original = json.loads(json.dumps(self.rows[0]))
        for key, value in [('candidate', 'different'), ('source_ids', ['R26']),
                           ('row_sha256', '0' * 64), ('row_index', False)]:
            with self.subTest(key=key):
                self.rows[0] = {**original, key: value}
                self.write_rows()
                self.reject('inventory binding|record hash|row identity/order')

    def test_claim_pointer_and_boolean_line_alias_are_rejected(self):
        self.rows[0]['note_refs'][0]['line'] = 1
        self.write_rows()
        self.reject('claim-note references')
        self.rows[0]['note_refs'][0]['line'] = True
        self.write_rows()
        self.reject('claim-note references|note line')

    def test_document_revision_cannot_be_promoted_to_weight_pin(self):
        locator = next(row for row in self.rows if row['identity_refs']
                       and row['identity_refs'][0]['state'] == 'recorded_repository_locator')
        locator['identity_refs'][0]['checkpoint_sha256'] = '0' * 64
        self.write_rows()
        self.reject('source-document locator differs')

    def test_wrong_repository_or_revision_is_not_a_matching_locator(self):
        locator = next(row for row in self.rows if row['assessment'] == 'recorded_repository_locator')
        locator['identity_refs'][0]['document_revision'] = '0' * 40
        self.write_rows()
        self.reject('source-document locator differs')

    def test_unverified_row_cannot_claim_verification_or_rights(self):
        self.rows[0]['verification'] = 'independently_verified'
        self.write_rows()
        self.reject('verification upgraded')
        self.rows[0]['verification'] = 'local_derivation_only'
        self.rows[0]['publication_eligible'] = True
        self.write_rows()
        self.reject('invalid keys')

    def test_recipe_cannot_be_relabelled_as_a_release(self):
        row = next(row for row in self.rows if row['recorded_type'] == 'architecture_recipe')
        row['assessment'] = 'recorded_repository_locator'
        self.write_rows()
        self.reject('unsupported assessment')

    def test_unknown_profile_and_required_disposition_cannot_disappear(self):
        self.rows[0]['known_unknowns'] = ''
        self.write_rows()
        self.reject('unresolved fields')
        self.rows = [json.loads(line) for line in (ROOT / CROSSWALK.DIRECTORY / 'rows.jsonl').read_text().splitlines()]
        row = next(row for row in self.rows if row['recorded_type'] != 'model')
        row['disposition_note'] = ' '
        self.write_rows()
        self.reject('specific disposition')

    def test_duplicate_keys_and_nonfinite_numbers_are_rejected_before_interpretation(self):
        self.path.write_text('{"row_index":0,"row_index":1}\n')
        self.reject('duplicate JSON key')
        self.path.write_text('{"row_index":NaN}\n')
        self.reject('non-finite JSON number')
        self.path.write_text('{"row_index":1e999}\n')
        self.reject('non-finite JSON number')

    def test_manifest_cannot_read_extra_paths_or_shrink_the_cohort(self):
        path = self.root / CROSSWALK.DIRECTORY / 'manifest.json'
        manifest = json.loads(path.read_text())
        manifest['inputs']['../../outside.json'] = '0' * 64
        path.write_text(json.dumps(manifest))
        self.reject('exactly the eight declared inputs')
        del manifest['inputs']['../../outside.json']
        manifest['row_count'] = 247
        path.write_text(json.dumps(manifest))
        self.reject('all 248 rows')


if __name__ == '__main__':
    unittest.main()
