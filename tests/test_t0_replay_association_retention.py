"""Retained report association survives unrelated replay failures; synthetic only."""

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
import test_t0_historical_replay as fixtures
import t0_historical_replay_prototype as replay


def report_case(**changes):
    records = dict(fixtures.RECORDS)
    report = json.loads(records['evaluation_report'])
    report.update(changes)
    records['evaluation_report'] = replay.encoded(report)
    sidecar, manifest = fixtures.repin(records)
    return records, sidecar, manifest


class RetainedReportAssociation(unittest.TestCase):
    def check_result(self, records, sidecar, manifest, expected, *, profile=False):
        original = tuple(records.items()), fixtures.BUILD, sidecar, manifest
        evaluator = Mock(side_effect=AssertionError('unresolved inputs must not evaluate'))
        loader = (patch.object(replay, '_local_evaluator', side_effect=replay.ReplayError(
            'local_evaluator_or_schemas_unavailable')) if profile else
            patch.object(replay, '_local_evaluator', return_value=evaluator))
        with loader:
            result = replay.ReplayArchive(records.items()).replay(fixtures.BUILD, sidecar, manifest)
        evaluator.assert_not_called()
        self.assertIn(expected, result.issues)
        self.assertEqual(result.issues.count(expected), 1)
        self.assertIsNone(result.generated_report)
        self.assertEqual(tuple(records.items()), original[0])
        self.assertIs(result.original_build_bytes, original[1])
        self.assertIs(result.original_sidecar_bytes, original[2])
        self.assertIs(result.original_manifest_bytes, original[3])
        report = next(b for b in result.bindings if b.kind == 'evaluation_report')
        self.assertEqual(report.status, 'resolved')
        self.assertIs(report.raw, records['evaluation_report'])
        return result

    def test_wrong_report_build_remains_diagnostic_for_each_missing_other_record(self):
        for field, value in (('build_id', 'build.synthetic.other'), ('build_revision', 2)):
            records, sidecar, manifest = report_case(**{field: value})
            for missing in set(records) - {'evaluation_report'}:
                with self.subTest(field=field, missing=missing):
                    retained = {kind: raw for kind, raw in records.items() if kind != missing}
                    result = self.check_result(retained, sidecar, manifest,
                                               ('evaluation_report', 'build_identity_mismatch'))
                    self.assertEqual(result.status, 'inputs_unavailable')
                    self.assertEqual(result.issues[0][0], missing)

    def test_each_report_lock_mismatch_survives_an_unavailable_catalog(self):
        changes = (
            ('catalog_snapshot_id', 'catalog.synthetic.other'),
            ('ruleset_id', 'rules.synthetic.other'), ('ruleset_version', '2.0.0'),
            ('dependency_graph_id', 'graph.synthetic.other'), ('dependency_graph_revision', 2),
        )
        for field, value in changes:
            with self.subTest(field=field):
                records, sidecar, manifest = report_case(**{field: value})
                del records['catalog_snapshot']
                result = self.check_result(records, sidecar, manifest,
                                           ('evaluation_report', 'build_lock_mismatch'))
                self.assertEqual(result.status, 'inputs_unavailable')
                self.assertEqual(result.issues[0], ('catalog_snapshot', 'pinned_revision_unavailable'))

    def test_both_report_associations_survive_digest_failure_and_profile_failure(self):
        for unavailable_profile in (False, True):
            with self.subTest(profile=unavailable_profile):
                records, sidecar, manifest = report_case(
                    build_id='build.synthetic.other', ruleset_version='2.0.0')
                records['catalog_snapshot'] += b'\n'
                result = self.check_result(records, sidecar, manifest,
                                           ('evaluation_report', 'build_identity_mismatch'),
                                           profile=unavailable_profile)
                self.assertEqual(result.issues.count(('evaluation_report', 'build_lock_mismatch')), 1)
                self.assertIn(('catalog_snapshot', 'content_digest_mismatch'), result.issues)
                self.assertEqual(result.status, 'profile_unavailable' if unavailable_profile
                                 else 'input_digest_mismatch')
                if unavailable_profile:
                    self.assertEqual(result.issues[0][0], 'evaluator')

    def test_missing_revision_pins_do_not_hide_an_independent_report_mismatch(self):
        records, _, manifest = report_case(build_id='build.synthetic.other')
        value = json.loads(manifest)
        value['x_t0_historical_replay']['revision_locks_sha256'] = None
        raw = replay.encoded(value)
        result = self.check_result(records, None, raw,
                                   ('evaluation_report', 'build_identity_mismatch'))
        self.assertEqual(result.status, 'inputs_unavailable')
        self.assertIn(('catalog_snapshot', 'revision_pin_missing'), result.issues)
        self.assertIn(('pricebook', 'revision_pin_missing'), result.issues)

    def test_unresolved_report_bytes_do_not_supply_association_claims(self):
        for missing in (False, True):
            records, sidecar, manifest = report_case(build_id='build.synthetic.other')
            if missing:
                del records['evaluation_report']
            else:
                records['evaluation_report'] += b'\n'
            del records['catalog_snapshot']
            result = replay.ReplayArchive(records.items()).replay(fixtures.BUILD, sidecar, manifest)
            report = next(b for b in result.bindings if b.kind == 'evaluation_report')
            with self.subTest(missing=missing):
                self.assertIsNone(report.raw)
                self.assertNotIn(('evaluation_report', 'build_identity_mismatch'), result.issues)
                self.assertNotIn(('evaluation_report', 'build_lock_mismatch'), result.issues)
                self.assertIn(('evaluation_report', 'pinned_artifact_unavailable' if missing
                               else 'content_digest_mismatch'), result.issues)

    def test_matching_historical_report_survives_unrelated_unavailability_unchanged(self):
        for missing in set(fixtures.RECORDS) - {'evaluation_report'}:
            retained = {kind: raw for kind, raw in fixtures.RECORDS.items() if kind != missing}
            result = replay.ReplayArchive(retained.items()).replay(
                fixtures.BUILD, fixtures.SIDECAR, fixtures.MANIFEST)
            report = next(b for b in result.bindings if b.kind == 'evaluation_report')
            with self.subTest(missing=missing):
                self.assertEqual(result.status, 'inputs_unavailable')
                self.assertIs(report.raw, fixtures.RECORDS['evaluation_report'])
                self.assertFalse(any(kind == 'evaluation_report' for kind, _ in result.issues))
                self.assertIsNone(result.generated_report)

    def test_complete_wrong_report_keeps_original_failure_and_single_diagnostics(self):
        records, sidecar, manifest = report_case(
            build_id='build.synthetic.other', ruleset_version='2.0.0')
        result = self.check_result(records, sidecar, manifest,
                                   ('evaluation_report', 'build_identity_mismatch'))
        self.assertEqual(result.status, 'input_identity_mismatch')
        self.assertEqual(result.issues.count(('evaluation_report', 'build_lock_mismatch')), 1)

    def test_unselected_foreign_report_cannot_replace_the_pinned_historical_report(self):
        records = list(fixtures.RECORDS.items())
        foreign = json.loads(fixtures.RECORDS['evaluation_report'])
        foreign.update(id='report.synthetic.other', build_id='build.synthetic.other')
        records.append(('evaluation_report', replay.encoded(foreign)))
        records = [record for record in records if record[0] != 'catalog_snapshot']
        result = replay.ReplayArchive(records).replay(fixtures.BUILD, fixtures.SIDECAR, fixtures.MANIFEST)
        report = next(b for b in result.bindings if b.kind == 'evaluation_report')
        self.assertIs(report.raw, fixtures.RECORDS['evaluation_report'])
        self.assertFalse(any(kind == 'evaluation_report' for kind, _ in result.issues))


if __name__ == '__main__':
    unittest.main()
