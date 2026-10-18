"""Synthetic selection membership stays visible without unrelated replay inputs."""

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import test_t0_historical_replay as fixtures
import t0_historical_replay_prototype as replay


def selection_case(mismatch):
    build = json.loads(fixtures.BUILD)
    selected = next(s for s in build["selections"] if s["kind"] == "monitoring_stack")
    if mismatch == "version":
        selected["catalog_item_version"] = "synthetic.absent"
        code = "selected_version_absent"
    else:
        other = next(s for s in build["selections"] if s["kind"] == "workload")
        selected["catalog_item_id"] = other["catalog_item_id"]
        selected["catalog_item_version"] = other["catalog_item_version"]
        code = "selected_kind_mismatch"
    raw = replay.encoded(build)
    records = dict(fixtures.RECORDS)
    sidecar, manifest = fixtures.repin(records, raw)
    return records, raw, sidecar, manifest, ("selection:" + selected["id"], code)


class SavedSelectionDiagnosticsTests(unittest.TestCase):
    def blocked(self, records, build, sidecar, manifest, *, profile=False):
        artifacts = tuple(records.items()) if isinstance(records, dict) else tuple(records)
        original = artifacts, build, sidecar, manifest
        evaluator = Mock(side_effect=AssertionError("blocked replay must not evaluate"))
        loader = (patch.object(replay, "_local_evaluator", side_effect=replay.ReplayError(
            "local_evaluator_or_schemas_unavailable")) if profile else
            patch.object(replay, "_local_evaluator", return_value=evaluator))
        with loader:
            result = replay.ReplayArchive(artifacts).replay(build, sidecar, manifest)
        evaluator.assert_not_called()
        self.assertIsNone(result.generated_report)
        self.assertEqual((artifacts, build, sidecar, manifest), original)
        if isinstance(records, dict):
            self.assertEqual(tuple(records.items()), original[0])
        else:
            self.assertEqual(tuple(records), original[0])
        self.assertIs(result.original_build_bytes, build)
        self.assertIs(result.original_sidecar_bytes, sidecar)
        self.assertIs(result.original_manifest_bytes, manifest)
        self.assertEqual(set(result.qualification.values()), {"not_established"})
        self.assertEqual(len(result.issues), len(set(result.issues)))
        for binding in result.bindings:
            if binding.status == "resolved":
                self.assertTrue(any(binding.raw is raw for kind, raw in artifacts
                                    if kind == binding.kind))
        return result

    def test_known_selection_mismatches_survive_every_missing_other_record(self):
        for mismatch in ("version", "kind"):
            for missing in set(fixtures.RECORDS) - {"catalog_snapshot"}:
                with self.subTest(mismatch=mismatch, missing=missing):
                    records, build, sidecar, manifest, expected = selection_case(mismatch)
                    del records[missing]
                    result = self.blocked(records, build, sidecar, manifest)
                    self.assertEqual(result.status, "inputs_unavailable")
                    self.assertEqual(result.issues[0][0], missing)
                    self.assertIn(expected, result.issues)

    def test_known_selection_mismatches_survive_every_other_record_digest_failure(self):
        for mismatch in ("version", "kind"):
            for changed in set(fixtures.RECORDS) - {"catalog_snapshot"}:
                with self.subTest(mismatch=mismatch, changed=changed):
                    records, build, sidecar, manifest, expected = selection_case(mismatch)
                    records[changed] += b"\n"
                    result = self.blocked(records, build, sidecar, manifest)
                    self.assertEqual(result.status, "input_digest_mismatch")
                    self.assertEqual(result.issues[0], (changed, "content_digest_mismatch"))
                    self.assertIn(expected, result.issues)
                    self.assertIsNone(next(b.raw for b in result.bindings if b.kind == changed))

    def test_known_selection_mismatches_survive_required_null_pins(self):
        for mismatch in ("version", "kind"):
            for kind in ("ruleset", "dependency_graph", "evaluation_report"):
                with self.subTest(mismatch=mismatch, kind=kind):
                    records, build, sidecar, manifest, expected = selection_case(mismatch)
                    packet = json.loads(manifest)
                    packet["x_t0_historical_replay"]["inputs"][kind] = None
                    result = self.blocked(records, build, sidecar, replay.encoded(packet))
                    self.assertEqual(result.status, "inputs_unavailable")
                    self.assertEqual(result.issues[0], (kind, "required_pin_missing"))
                    self.assertIn(expected, result.issues)
                    self.assertIsNone(next(b.raw for b in result.bindings if b.kind == kind))

    def test_reader_unavailability_preserves_primary_and_selection_diagnostics(self):
        for mismatch in ("version", "kind"):
            for unavailable in (None, "missing", "digest"):
                with self.subTest(mismatch=mismatch, unavailable=unavailable):
                    records, build, sidecar, manifest, expected = selection_case(mismatch)
                    if unavailable == "missing":
                        del records["pricebook"]
                    elif unavailable == "digest":
                        records["ruleset"] += b"\n"
                    result = self.blocked(records, build, sidecar, manifest, profile=True)
                    self.assertEqual(result.status, "profile_unavailable")
                    self.assertEqual(result.issues[0], ("evaluator", "local_evaluator_or_schemas_unavailable"))
                    self.assertIn(expected, result.issues)
                    if unavailable == "missing":
                        self.assertEqual(result.issues[1], ("pricebook", "pinned_revision_unavailable"))
                    elif unavailable == "digest":
                        self.assertEqual(result.issues[1], ("ruleset", "content_digest_mismatch"))

    def test_unresolved_catalog_cannot_supply_a_known_selection_mismatch(self):
        for mismatch in ("version", "kind"):
            for unavailable in ("missing", "digest", "revision", "sidecar"):
                with self.subTest(mismatch=mismatch, unavailable=unavailable):
                    records, build, sidecar, manifest, _ = selection_case(mismatch)
                    if unavailable == "missing":
                        del records["catalog_snapshot"]
                    elif unavailable == "digest":
                        records["catalog_snapshot"] += b"\n"
                    else:
                        packet = json.loads(manifest)
                        if unavailable == "revision":
                            pins = json.loads(sidecar)
                            pins["x_t0_revision_locks"]["artifacts"]["catalog_snapshot"]["revision"] += 1
                            sidecar = replay.encoded(pins)
                        else:
                            sidecar = None
                        packet["x_t0_historical_replay"]["revision_locks_sha256"] = (
                            replay.digest(sidecar) if sidecar is not None else None)
                        manifest = replay.encoded(packet)
                    del records["resource_estimate"]
                    result = self.blocked(records, build, sidecar, manifest)
                    self.assertFalse(any(kind.startswith("selection:") for kind, _ in result.issues))
                    self.assertIsNone(next(b.raw for b in result.bindings if b.kind == "catalog_snapshot"))

    def test_disabled_unresolved_membership_does_not_add_identity_diagnostics(self):
        for mismatch in ("version", "kind"):
            for profile in (False, True):
                with self.subTest(mismatch=mismatch, profile=profile):
                    records, raw, _, _, _ = selection_case(mismatch)
                    build = json.loads(raw)
                    next(s for s in build["selections"] if s["kind"] == "monitoring_stack")["enabled"] = False
                    raw = replay.encoded(build)
                    sidecar, manifest = fixtures.repin(records, raw)
                    del records["ruleset"]
                    result = self.blocked(records, raw, sidecar, manifest, profile=profile)
                    self.assertEqual(result.status, "profile_unavailable" if profile else "inputs_unavailable")
                    self.assertFalse(any(kind.startswith("selection:") for kind, _ in result.issues))

    def test_complete_input_diagnostics_keep_order_without_duplicates(self):
        for mismatch in ("version", "kind"):
            with self.subTest(mismatch=mismatch):
                records, build, _, _, expected = selection_case(mismatch)
                resource = json.loads(records["resource_estimate"])
                resource["build_revision"] = 2
                records["resource_estimate"] = replay.encoded(resource)
                sidecar, manifest = fixtures.repin(records, build)
                result = self.blocked(records, build, sidecar, manifest)
                self.assertEqual(result.status, "input_identity_mismatch")
                self.assertEqual(result.issues, (expected, ("resource_estimate", "build_identity_mismatch")))

    def test_all_known_selection_and_record_mismatches_survive_together(self):
        records, raw, _, _, first = selection_case("version")
        build = json.loads(raw)
        tool = next(s for s in build["selections"] if s["kind"] == "tool")
        workload = next(s for s in build["selections"] if s["kind"] == "workload")
        tool["catalog_item_id"] = workload["catalog_item_id"]
        tool["catalog_item_version"] = workload["catalog_item_version"]
        raw = replay.encoded(build)
        resource = json.loads(records["resource_estimate"])
        resource["build_revision"] = 2
        records["resource_estimate"] = replay.encoded(resource)
        sidecar, manifest = fixtures.repin(records, raw)
        del records["cost_estimate"]
        result = self.blocked(records, raw, sidecar, manifest)
        self.assertEqual(result.status, "inputs_unavailable")
        expected_selections = {first, ("selection:" + tool["id"], "selected_kind_mismatch")}
        self.assertEqual(set(result.issues), {
            ("cost_estimate", "pinned_artifact_unavailable"),
            ("resource_estimate", "build_identity_mismatch"), *expected_selections,
        })
        self.assertEqual(result.issues[0], ("cost_estimate", "pinned_artifact_unavailable"))
        self.assertEqual(result.issues[-1], ("resource_estimate", "build_identity_mismatch"))
        self.assertIs(next(b.raw for b in result.bindings if b.kind == "evaluation_report"),
                      records["evaluation_report"])

    def test_foreign_newer_catalog_never_supplies_or_suppresses_pinned_diagnosis(self):
        for pinned_mismatch in (False, True):
            if pinned_mismatch:
                records, build, sidecar, manifest, expected = selection_case("version")
            else:
                records, build = dict(fixtures.RECORDS), fixtures.BUILD
                sidecar, manifest = fixtures.SIDECAR, fixtures.MANIFEST
                expected = None
            foreign = json.loads(records["catalog_snapshot"])
            foreign["revision"] += 1
            item = next(item for item in foreign["items"] if item["kind"] == "monitoring_stack")
            item["version"] = "synthetic.absent"
            artifacts = [(kind, raw) for kind, raw in records.items() if kind != "ruleset"]
            artifacts.append(("catalog_snapshot", replay.encoded(foreign)))
            for ordered in (artifacts, list(reversed(artifacts))):
                with self.subTest(pinned_mismatch=pinned_mismatch, reversed=ordered is not artifacts):
                    result = self.blocked(ordered, build, sidecar, manifest)
                    self.assertEqual(result.status, "inputs_unavailable")
                    actual = [issue for issue in result.issues if issue[0].startswith("selection:")]
                    self.assertEqual(actual, [expected] if expected is not None else [])
                    self.assertIs(next(b.raw for b in result.bindings if b.kind == "catalog_snapshot"),
                                  records["catalog_snapshot"])

    def test_optional_null_estimates_keep_absence_and_known_mismatch(self):
        records, build, sidecar, manifest, expected = selection_case("version")
        packet = json.loads(manifest)
        for kind in replay.OPTIONAL_INPUTS:
            packet["x_t0_historical_replay"]["inputs"][kind] = None
        result = self.blocked(records, build, sidecar, replay.encoded(packet))
        self.assertEqual((result.status, result.issues), ("input_identity_mismatch", (expected,)))
        for binding in result.bindings:
            if binding.kind in replay.OPTIONAL_INPUTS:
                self.assertEqual((binding.status, binding.raw), ("not_supplied", None))

    def test_valid_replay_uses_the_real_frozen_evaluator_without_changing_report(self):
        result = fixtures.run()
        self.assertEqual((result.status, result.issues), ("reproduced", ()))
        self.assertEqual(result.generated_report, json.loads(fixtures.RECORDS["evaluation_report"]))
        self.assertEqual(len(result.generated_report["findings"]), 45)
        self.assertIs(result.original_build_bytes, fixtures.BUILD)
        self.assertIs(result.original_sidecar_bytes, fixtures.SIDECAR)
        self.assertIs(result.original_manifest_bytes, fixtures.MANIFEST)
        self.assertEqual(set(result.qualification.values()), {"not_established"})
        for binding in result.bindings:
            self.assertIs(binding.raw, fixtures.RECORDS[binding.kind])


if __name__ == "__main__":
    unittest.main()
