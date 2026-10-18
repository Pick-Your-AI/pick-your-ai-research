"""Synthetic saved-input associations remain visible without unrelated replay inputs."""

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
import test_t0_historical_replay as fixtures
import t0_historical_replay_prototype as replay


IDENTITY_CASES = (
    ('resource_estimate', 'build_id', 'build.synthetic.other', 'build_identity_mismatch'),
    ('resource_estimate', 'build_revision', 2, 'build_identity_mismatch'),
    ('cost_estimate', 'build_id', 'build.synthetic.other', 'build_identity_mismatch'),
    ('cost_estimate', 'build_revision', 2, 'build_identity_mismatch'),
    ('ruleset', 'id', 'rules.synthetic.other', 'build_lock_mismatch'),
    ('ruleset', 'version', '2.0.0', 'build_lock_mismatch'),
    ('dependency_graph', 'id', 'graph.synthetic.other', 'build_lock_mismatch'),
    ('dependency_graph', 'revision', 2, 'build_lock_mismatch'),
)


def changed_record(kind, field, value):
    records = dict(fixtures.RECORDS)
    document = json.loads(records[kind])
    document[field] = value
    records[kind] = replay.encoded(document)
    sidecar, manifest = fixtures.repin(records)
    return records, sidecar, manifest


def cost_case(mutation):
    document = json.loads(fixtures.RECORDS['cost_estimate'])
    if mutation == 'pricebook':
        document['pricebook_id'] = 'prices.synthetic.other'
    elif mutation == 'unpriced':
        document['unpriced_selection_ids'] = ['sel_absent']
    else:
        field, value = {
            'selection': ('selection_id', 'sel_absent'),
            'rate': ('price_rate_id', 'rate.absent'),
            'rate_selection': ('selection_id', 'sel_storage'),
            'meter': ('meter', 'request'),
        }[mutation]
        document['line_items'][0][field] = value
    records = dict(fixtures.RECORDS)
    records['cost_estimate'] = replay.encoded(document)
    sidecar, manifest = fixtures.repin(records)
    return records, sidecar, manifest


class SavedInputAssociations(unittest.TestCase):
    def blocked(self, records, sidecar, manifest, *, build=fixtures.BUILD, profile=False):
        original = tuple(records.items()), build, sidecar, manifest
        evaluator = Mock(side_effect=AssertionError('blocked replay must not evaluate'))
        loader = (patch.object(replay, '_local_evaluator', side_effect=replay.ReplayError(
            'local_evaluator_or_schemas_unavailable')) if profile else
            patch.object(replay, '_local_evaluator', return_value=evaluator))
        with loader:
            result = replay.ReplayArchive(records.items()).replay(build, sidecar, manifest)
        evaluator.assert_not_called()
        self.assertIsNone(result.generated_report)
        self.assertEqual(tuple(records.items()), original[0])
        self.assertIs(result.original_build_bytes, original[1])
        self.assertIs(result.original_sidecar_bytes, original[2])
        self.assertIs(result.original_manifest_bytes, original[3])
        self.assertEqual(set(result.qualification.values()), {'not_established'})
        for binding in result.bindings:
            if binding.status == 'resolved':
                self.assertIs(binding.raw, records[binding.kind])
        self.assertEqual(len(result.issues), len(set(result.issues)))
        return result

    def test_each_retained_identity_survives_every_missing_other_record(self):
        for kind, field, value, reason in IDENTITY_CASES:
            records, sidecar, manifest = changed_record(kind, field, value)
            for missing in set(records) - {kind}:
                with self.subTest(kind=kind, field=field, missing=missing):
                    available = {key: raw for key, raw in records.items() if key != missing}
                    result = self.blocked(available, sidecar, manifest)
                    self.assertEqual(result.status, 'inputs_unavailable')
                    self.assertEqual(result.issues[0][0], missing)
                    self.assertIn((kind, reason), result.issues)

    def test_complete_identity_controls_keep_existing_rejection_without_duplicates(self):
        for kind, field, value, reason in IDENTITY_CASES:
            with self.subTest(kind=kind, field=field):
                records, sidecar, manifest = changed_record(kind, field, value)
                result = self.blocked(records, sidecar, manifest)
                self.assertEqual(result.status, 'input_identity_mismatch')
                self.assertIn((kind, reason), result.issues)

    def test_independent_associations_survive_digest_and_profile_failures(self):
        for kind, field, value, reason in IDENTITY_CASES:
            for profile in (False, True):
                with self.subTest(kind=kind, field=field, profile=profile):
                    records, sidecar, manifest = changed_record(kind, field, value)
                    records['catalog_snapshot'] += b'\n'
                    result = self.blocked(records, sidecar, manifest, profile=profile)
                    self.assertEqual(result.status, 'profile_unavailable' if profile
                                     else 'input_digest_mismatch')
                    self.assertEqual(result.issues[0][0], 'evaluator' if profile else 'catalog_snapshot')
                    self.assertIn(('catalog_snapshot', 'content_digest_mismatch'), result.issues)
                    self.assertIn((kind, reason), result.issues)

    def test_absent_sidecar_does_not_erase_independent_build_associations(self):
        records, _, manifest = changed_record('cost_estimate', 'build_revision', 2)
        value = json.loads(manifest)
        value['x_t0_historical_replay']['revision_locks_sha256'] = None
        result = self.blocked(records, None, replay.encoded(value))
        self.assertEqual(result.status, 'inputs_unavailable')
        self.assertIn(('catalog_snapshot', 'revision_pin_missing'), result.issues)
        self.assertIn(('pricebook', 'revision_pin_missing'), result.issues)
        self.assertIn(('cost_estimate', 'build_identity_mismatch'), result.issues)

    def test_resource_selection_association_needs_no_catalog_or_pricebook(self):
        document = json.loads(fixtures.RECORDS['resource_estimate'])
        document['estimates'][0]['selection_ids'] = ['sel_absent']
        records = dict(fixtures.RECORDS)
        records['resource_estimate'] = replay.encoded(document)
        sidecar, manifest = fixtures.repin(records)
        del records['catalog_snapshot']
        del records['pricebook']
        result = self.blocked(records, sidecar, manifest)
        self.assertIn(('resource_estimate', 'selection_identity_mismatch'), result.issues)

    def test_cost_line_and_price_associations_survive_unrelated_catalog_absence(self):
        for mutation, reason in (
            ('pricebook', 'pricebook_identity_mismatch'),
            ('selection', 'line_identity_mismatch'), ('rate', 'line_identity_mismatch'),
            ('rate_selection', 'line_identity_mismatch'), ('meter', 'line_identity_mismatch'),
            ('unpriced', 'selection_identity_mismatch'),
        ):
            with self.subTest(mutation=mutation):
                records, sidecar, manifest = cost_case(mutation)
                del records['catalog_snapshot']
                result = self.blocked(records, sidecar, manifest)
                self.assertIn(('cost_estimate', reason), result.issues)

    def test_cost_build_lock_and_selection_facts_remain_known_without_pricebook_bytes(self):
        for mutation, reason in (('pricebook', 'pricebook_identity_mismatch'),
                                 ('selection', 'line_identity_mismatch'),
                                 ('unpriced', 'selection_identity_mismatch')):
            with self.subTest(mutation=mutation):
                records, sidecar, manifest = cost_case(mutation)
                del records['pricebook']
                result = self.blocked(records, sidecar, manifest)
                self.assertIn(('cost_estimate', reason), result.issues)

    def test_missing_or_wrong_digest_pricebook_cannot_supply_rate_comparison(self):
        for mutation in ('rate', 'rate_selection', 'meter'):
            for unavailable in ('missing', 'digest'):
                with self.subTest(mutation=mutation, unavailable=unavailable):
                    records, sidecar, manifest = cost_case(mutation)
                    if unavailable == 'missing':
                        del records['pricebook']
                    else:
                        records['pricebook'] += b'\n'
                    result = self.blocked(records, sidecar, manifest)
                    self.assertFalse(any(kind == 'cost_estimate' for kind, _ in result.issues))
                    self.assertIsNone(next(b.raw for b in result.bindings if b.kind == 'pricebook'))

    def test_pricebook_catalog_association_requires_both_exact_inputs(self):
        prices = json.loads(fixtures.RECORDS['pricebook'])
        prices['rates'][0]['catalog_item_version'] = 'absent-fixture'
        records = dict(fixtures.RECORDS)
        records['pricebook'] = replay.encoded(prices)
        sidecar, manifest = fixtures.repin(records)
        for missing in ('ruleset', 'catalog_snapshot'):
            with self.subTest(missing=missing):
                selected = {key: raw for key, raw in records.items() if key != missing}
                result = self.blocked(selected, sidecar, manifest)
                self.assertEqual(('pricebook', 'rate_catalog_mismatch') in result.issues,
                                 missing == 'ruleset')

    def test_unresolved_input_cannot_supply_its_own_association_claims(self):
        for kind, field, value, _ in IDENTITY_CASES:
            for unavailable in ('missing', 'digest', 'null_pin'):
                with self.subTest(kind=kind, field=field, unavailable=unavailable):
                    records, sidecar, manifest = changed_record(kind, field, value)
                    if unavailable == 'missing':
                        del records[kind]
                    elif unavailable == 'digest':
                        records[kind] += b'\n'
                    else:
                        value = json.loads(manifest)
                        value['x_t0_historical_replay']['inputs'][kind] = None
                        manifest = replay.encoded(value)
                    del records['catalog_snapshot']
                    result = self.blocked(records, sidecar, manifest)
                    binding = next(b for b in result.bindings if b.kind == kind)
                    self.assertIsNone(binding.raw)
                    self.assertFalse(any(issue_kind == kind and reason.endswith('_mismatch')
                                         and reason != 'content_digest_mismatch'
                                         for issue_kind, reason in result.issues))

    def test_unselected_foreign_estimates_never_replace_matching_pinned_records(self):
        records = list(fixtures.RECORDS.items())
        for kind in ('resource_estimate', 'cost_estimate'):
            foreign = json.loads(fixtures.RECORDS[kind])
            foreign.update(id=foreign['id'] + '.foreign', build_id='build.synthetic.other')
            records.append((kind, replay.encoded(foreign)))
        records = [record for record in records if record[0] != 'catalog_snapshot']
        for ordered in (records, list(reversed(records))):
            with self.subTest(reversed=ordered is not records):
                evaluator = Mock(side_effect=AssertionError('unavailable catalog must not evaluate'))
                with patch.object(replay, '_local_evaluator', return_value=evaluator):
                    result = replay.ReplayArchive(ordered).replay(
                        fixtures.BUILD, fixtures.SIDECAR, fixtures.MANIFEST)
                evaluator.assert_not_called()
                self.assertFalse(any(kind in replay.OPTIONAL_INPUTS for kind, _ in result.issues))
                for kind in replay.OPTIONAL_INPUTS:
                    self.assertIs(next(b.raw for b in result.bindings if b.kind == kind), fixtures.RECORDS[kind])

    def test_all_available_mismatches_are_retained_once_alongside_original_report(self):
        records = dict(fixtures.RECORDS)
        for kind in ('resource_estimate', 'cost_estimate', 'evaluation_report'):
            document = json.loads(records[kind])
            document['build_revision'] = 2
            records[kind] = replay.encoded(document)
        sidecar, manifest = fixtures.repin(records)
        del records['catalog_snapshot']
        result = self.blocked(records, sidecar, manifest)
        for kind in ('resource_estimate', 'cost_estimate', 'evaluation_report'):
            self.assertIn((kind, 'build_identity_mismatch'), result.issues)
        self.assertIs(next(b.raw for b in result.bindings if b.kind == 'evaluation_report'), records['evaluation_report'])

    def test_selection_failure_keeps_primary_reason_and_independent_estimate_mismatch(self):
        build = json.loads(fixtures.BUILD)
        build['selections'][0]['catalog_item_version'] = 'absent-fixture'
        raw = replay.encoded(build)
        records, _, _ = changed_record('resource_estimate', 'build_revision', 2)
        sidecar, manifest = fixtures.repin(records, raw)
        result = self.blocked(records, sidecar, manifest, build=raw)
        self.assertEqual(result.status, 'input_identity_mismatch')
        self.assertTrue(result.issues[0][0].startswith('selection:'))
        self.assertIn(('resource_estimate', 'build_identity_mismatch'), result.issues)


if __name__ == '__main__':
    unittest.main()
