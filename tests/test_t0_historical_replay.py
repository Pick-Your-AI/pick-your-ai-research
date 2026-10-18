"""Synthetic saved-report replay; these fixtures are not measured evidence."""

from copy import deepcopy
from decimal import getcontext, localcontext
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import t0_historical_replay_prototype as replay

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "contracts/v1/examples"
BUILD = (EXAMPLES / "build.json").read_bytes()
SIDECAR = (ROOT / "tests/fixtures/t0-revision-locks.json").read_bytes()
MANIFEST = (ROOT / "tests/fixtures/t0-historical-replay.json").read_bytes()
FILENAMES = {
    "catalog_snapshot": "catalog.json", "pricebook": "pricebook.json",
    "ruleset": "ruleset.json", "dependency_graph": "dependency-graph.json",
    "resource_estimate": "resource-estimate.json", "cost_estimate": "cost-estimate.json",
    "evaluation_report": "evaluation-report.json",
}
RECORDS = {kind: (EXAMPLES / filename).read_bytes() for kind, filename in FILENAMES.items()}


def packet():
    return json.loads(MANIFEST)["x_t0_historical_replay"]


def manifest(value):
    return replay.encoded({"x_t0_historical_replay": value})


def repin(records, build=BUILD):
    """Explicitly bind a synthetic mutation; never repair the retained report."""
    value = packet()
    value["build_sha256"] = replay.digest(build)
    sidecar = json.loads(SIDECAR)
    pins = sidecar["x_t0_revision_locks"]
    pins["build_sha256"] = replay.digest(build)
    for kind in ("catalog_snapshot", "pricebook"):
        document = json.loads(records[kind])
        pins["artifacts"][kind] = {name: document[name] for name in ("id", "revision")}
        pins["artifacts"][kind]["sha256"] = replay.digest(records[kind])
    sidecar_raw = replay.encoded(sidecar)
    value["revision_locks_sha256"] = replay.digest(sidecar_raw)
    for kind in replay.INPUT_SCHEMAS:
        document = json.loads(records[kind])
        fields = (("id", "version") if kind == "ruleset" else ("id", "revision")
                  if kind == "dependency_graph" else ("id", "build_id", "build_revision"))
        value["inputs"][kind] = {name: document[name] for name in fields}
        value["inputs"][kind]["sha256"] = replay.digest(records[kind])
    return sidecar_raw, manifest(value)


def run(records=None, build=BUILD, sidecar=SIDECAR, replay_manifest=MANIFEST):
    records = RECORDS if records is None else records
    return replay.ReplayArchive(records.items()).replay(build, sidecar, replay_manifest)


class HistoricalReplayTests(unittest.TestCase):
    def test_exported_manifest_reproduces_complete_frozen_report_and_preserves_bytes(self):
        result = run()
        self.assertEqual((result.status, result.issues), ("reproduced", ()))
        self.assertEqual(result.generated_report, json.loads(RECORDS["evaluation_report"]))
        self.assertEqual(result.generated_report["summary"],
                         {"passed": 41, "failed": 0, "unknown": 0, "skipped": 4})
        self.assertIs(result.original_build_bytes, BUILD)
        self.assertIs(result.original_sidecar_bytes, SIDECAR)
        self.assertIs(result.original_manifest_bytes, MANIFEST)
        for binding in result.bindings:
            self.assertEqual(binding.status, "resolved")
            self.assertIs(binding.raw, RECORDS[binding.kind])
        self.assertEqual(set(result.qualification.values()), {"not_established"})

    def test_returned_report_mutation_cannot_change_retained_bytes_or_later_replay(self):
        archive = replay.ReplayArchive(RECORDS.items())
        result = archive.replay(BUILD, SIDECAR, MANIFEST)
        result.generated_report["findings"].clear()
        result.qualification["authenticity"] = "approved"
        again = archive.replay(BUILD, SIDECAR, MANIFEST)
        self.assertEqual(again.status, "reproduced")
        self.assertEqual(len(again.generated_report["findings"]), 45)
        self.assertEqual(again.qualification["authenticity"], "not_established")

    def test_newer_or_unrelated_candidates_are_ignored_in_either_archive_order(self):
        records = list(RECORDS.items())
        for kind, raw in RECORDS.items():
            document = json.loads(raw)
            if kind in {"catalog_snapshot", "pricebook", "dependency_graph"}:
                document["revision"] += 1
            elif kind == "ruleset":
                document["version"] = "2.0.0"
            else:
                document["id"] += ".alternative"
            records.append((kind, replay.encoded(document)))
        for ordered in (records, list(reversed(records))):
            result = replay.ReplayArchive(ordered).replay(BUILD, SIDECAR, MANIFEST)
            self.assertEqual(result.status, "reproduced")
            self.assertTrue(all(binding.raw == RECORDS[binding.kind] for binding in result.bindings))

    def test_every_pinned_artifact_is_required_before_evaluation(self):
        for kind in RECORDS:
            records = {key: raw for key, raw in RECORDS.items() if key != kind}
            evaluator = Mock(side_effect=AssertionError("must not evaluate missing bytes"))
            with self.subTest(kind=kind), patch.object(replay, "_local_evaluator", return_value=evaluator):
                result = run(records)
                self.assertEqual(result.status, "inputs_unavailable")
                self.assertEqual(result.issues[0][0], kind)
                self.assertIsNone(result.generated_report)
                evaluator.assert_not_called()

    def test_semantically_identical_bytes_still_need_the_exact_content_digest(self):
        for kind in RECORDS:
            records = dict(RECORDS)
            records[kind] += b"\n"
            with self.subTest(kind=kind):
                result = run(records)
                self.assertEqual(result.status, "input_digest_mismatch")
                self.assertIn((kind, "content_digest_mismatch"), result.issues)
                self.assertIsNone(next(b.raw for b in result.bindings if b.kind == kind))

    def test_required_null_pins_and_absent_sidecar_never_choose_a_sole_candidate(self):
        for kind in set(replay.INPUT_SCHEMAS) - replay.OPTIONAL_INPUTS:
            value = packet()
            value["inputs"][kind] = None
            with self.subTest(kind=kind):
                result = run(replay_manifest=manifest(value))
                self.assertEqual(result.status, "inputs_unavailable")
                self.assertIn((kind, "required_pin_missing"), result.issues)
        value = packet()
        value["revision_locks_sha256"] = None
        result = run(sidecar=None, replay_manifest=manifest(value))
        self.assertEqual(result.status, "inputs_unavailable")
        self.assertIn(("catalog_snapshot", "revision_pin_missing"), result.issues)
        self.assertIn(("pricebook", "revision_pin_missing"), result.issues)

    def test_explicit_null_estimates_are_not_loaded_even_when_archived(self):
        value = packet()
        for kind in replay.OPTIONAL_INPUTS:
            value["inputs"][kind] = None
        without = {kind: raw for kind, raw in RECORDS.items() if kind not in replay.OPTIONAL_INPUTS}
        present = run(replay_manifest=manifest(value))
        absent = run(without, replay_manifest=manifest(value))
        self.assertEqual(present.status, "report_mismatch")
        self.assertEqual(present.generated_report, absent.generated_report)
        self.assertGreater(present.generated_report["summary"]["unknown"], 0)
        self.assertTrue(all(b.status == "not_supplied" and b.raw is None
                            for b in present.bindings if b.kind in replay.OPTIONAL_INPUTS))

    def test_missing_exact_input_keys_do_not_use_other_versions_or_builds(self):
        for kind in replay.INPUT_SCHEMAS:
            records = dict(RECORDS)
            document = json.loads(records[kind])
            field = "version" if kind == "ruleset" else "revision" if kind == "dependency_graph" else "build_revision"
            document[field] = "2.0.0" if field == "version" else 2
            records[kind] = replay.encoded(document)
            with self.subTest(kind=kind):
                result = run(records)
                self.assertEqual(result.status, "inputs_unavailable")
                self.assertIn((kind, "pinned_artifact_unavailable"), result.issues)

    def test_manifest_is_bound_to_original_build_and_sidecar_bytes(self):
        for build, sidecar, code in ((BUILD + b"\n", SIDECAR, "manifest_build_mismatch"),
                                     (BUILD, SIDECAR + b"\n", "manifest_sidecar_mismatch"),
                                     (BUILD, None, "manifest_sidecar_mismatch")):
            with self.subTest(code=code), self.assertRaisesRegex(replay.ReplayError, code):
                run(build=build, sidecar=sidecar)

    def test_ruleset_and_graph_cannot_be_rebound_to_different_build_locks(self):
        for kind, field, value in (("ruleset", "id", "rules.different"),
                                   ("ruleset", "version", "2.0.0"),
                                   ("dependency_graph", "id", "graph.different"),
                                   ("dependency_graph", "revision", 2)):
            records = dict(RECORDS)
            document = json.loads(records[kind])
            document[field] = value
            records[kind] = replay.encoded(document)
            sidecar, replay_manifest = repin(records)
            with self.subTest(kind=kind, field=field):
                result = run(records, sidecar=sidecar, replay_manifest=replay_manifest)
                self.assertEqual(result.status, "input_identity_mismatch")
                self.assertIn((kind, "build_lock_mismatch"), result.issues)

    def test_derived_inputs_cannot_cross_build_identity_or_revision(self):
        for kind in ("resource_estimate", "cost_estimate", "evaluation_report"):
            for field, value in (("build_id", "build.different"), ("build_revision", 2)):
                records = dict(RECORDS)
                document = json.loads(records[kind])
                document[field] = value
                records[kind] = replay.encoded(document)
                sidecar, replay_manifest = repin(records)
                with self.subTest(kind=kind, field=field):
                    result = run(records, sidecar=sidecar, replay_manifest=replay_manifest)
                    self.assertEqual(result.status, "input_identity_mismatch")
                    self.assertIn((kind, "build_identity_mismatch"), result.issues)

    def test_retained_report_must_match_every_build_lock(self):
        for field in ("catalog_snapshot_id", "ruleset_id", "ruleset_version",
                      "dependency_graph_id", "dependency_graph_revision"):
            records = dict(RECORDS)
            report = json.loads(records["evaluation_report"])
            report[field] = 2 if field.endswith("revision") else "2.0.0" if field.endswith("version") else "different.fixture"
            records["evaluation_report"] = replay.encoded(report)
            sidecar, replay_manifest = repin(records)
            with self.subTest(field=field):
                result = run(records, sidecar=sidecar, replay_manifest=replay_manifest)
                self.assertEqual(result.status, "input_identity_mismatch")
                self.assertIn(("evaluation_report", "build_lock_mismatch"), result.issues)

    def test_report_comparison_covers_findings_order_summary_timestamp_and_json_number_types(self):
        for mutation in ("finding", "order", "summary", "timestamp", "float"):
            records = dict(RECORDS)
            report = json.loads(records["evaluation_report"])
            if mutation == "finding":
                report["findings"][0]["message"] = "Unverified replacement finding"
            elif mutation == "order":
                report["findings"].reverse()
            elif mutation == "summary":
                report["summary"]["passed"] = 40
            elif mutation == "timestamp":
                report["evaluated_at"] = "2026-10-18T00:00:00Z"
            else:
                report["summary"]["passed"] = 41.0
            records["evaluation_report"] = replay.encoded(report)
            sidecar, replay_manifest = repin(records)
            with self.subTest(mutation=mutation):
                result = run(records, sidecar=sidecar, replay_manifest=replay_manifest)
                self.assertEqual(result.status, "report_mismatch")
                self.assertEqual(result.generated_report, json.loads(RECORDS["evaluation_report"]))

    def test_report_json_whitespace_is_preserved_and_does_not_change_typed_comparison(self):
        records = dict(RECORDS)
        records["evaluation_report"] += b"\n"
        sidecar, replay_manifest = repin(records)
        result = run(records, sidecar=sidecar, replay_manifest=replay_manifest)
        self.assertEqual(result.status, "reproduced")
        self.assertEqual(next(b.raw for b in result.bindings if b.kind == "evaluation_report"),
                         records["evaluation_report"])

    def test_resource_and_cost_selection_and_rate_associations_are_checked(self):
        cases = (("resource_estimate", "resource_selection", "selection_identity_mismatch"),
                 ("cost_estimate", "pricebook", "pricebook_identity_mismatch"),
                 ("cost_estimate", "selection", "line_identity_mismatch"),
                 ("cost_estimate", "rate", "line_identity_mismatch"),
                 ("cost_estimate", "rate_selection", "line_identity_mismatch"),
                 ("cost_estimate", "meter", "line_identity_mismatch"),
                 ("cost_estimate", "unpriced", "selection_identity_mismatch"),
                 ("pricebook", "catalog", "rate_catalog_mismatch"))
        for kind, mutation, code in cases:
            records = dict(RECORDS)
            document = json.loads(records[kind])
            if mutation == "resource_selection":
                document["estimates"][0]["selection_ids"] = ["sel_absent"]
            elif mutation == "pricebook":
                document["pricebook_id"] = "prices.different"
            elif mutation == "selection":
                document["line_items"][0]["selection_id"] = "sel_absent"
            elif mutation == "rate":
                document["line_items"][0]["price_rate_id"] = "rate.absent"
            elif mutation == "rate_selection":
                document["line_items"][0]["selection_id"] = "sel_storage"
            elif mutation == "meter":
                document["line_items"][0]["meter"] = "request"
            elif mutation == "unpriced":
                document["unpriced_selection_ids"] = ["sel_absent"]
            else:
                document["rates"][0]["catalog_item_version"] = "absent-fixture"
            records[kind] = replay.encoded(document)
            sidecar, replay_manifest = repin(records)
            with self.subTest(mutation=mutation):
                result = run(records, sidecar=sidecar, replay_manifest=replay_manifest)
                self.assertEqual(result.status, "input_identity_mismatch")
                self.assertIn((kind, code), result.issues)

    def test_partial_nonmonthly_and_other_currency_costs_remain_unknown(self):
        for field, value in (("coverage", "partial"), ("period_days", 7), ("currency", "EUR")):
            records = dict(RECORDS)
            cost = json.loads(records["cost_estimate"])
            cost[field] = value
            records["cost_estimate"] = replay.encoded(cost)
            sidecar, replay_manifest = repin(records)
            with self.subTest(field=field):
                result = run(records, sidecar=sidecar, replay_manifest=replay_manifest)
                self.assertEqual(result.status, "report_mismatch")
                self.assertGreater(result.generated_report["summary"]["unknown"], 0)

    def test_multi_version_catalogs_are_explicitly_unsupported_by_the_frozen_evaluator(self):
        for newer_last in (False, True):
            records = dict(RECORDS)
            catalog = json.loads(records["catalog_snapshot"])
            newer = deepcopy(catalog["items"][0])
            newer["version"] = "synthetic-next"
            catalog["items"].insert(len(catalog["items"]) if newer_last else 0, newer)
            records["catalog_snapshot"] = replay.encoded(catalog)
            sidecar, replay_manifest = repin(records)
            result = run(records, sidecar=sidecar, replay_manifest=replay_manifest)
            self.assertEqual(result.status, "profile_unsupported")
            self.assertIn(("catalog_snapshot", "multiple_versions_per_item_id"), result.issues)
            self.assertIsNone(result.generated_report)

    def test_absent_enabled_tool_version_is_rejected_even_when_frozen_findings_would_pass(self):
        records = dict(RECORDS)
        catalog = json.loads(records["catalog_snapshot"])
        catalog["revision"] = 2
        item = next(item for item in catalog["items"] if item["kind"] == "tool")
        item["version"] = "different-retained-version"
        records["catalog_snapshot"] = replay.encoded(catalog)
        sidecar, replay_manifest = repin(records)
        # This metric path ignores the selected version in the frozen source.
        # The original complete report remains the oracle for that behavior.
        frozen = replay._local_evaluator(packet()["evaluator"])
        historical = frozen(json.loads(BUILD), catalog, json.loads(records["ruleset"]),
                            cost_estimate=json.loads(records["cost_estimate"]),
                            resource_estimate=json.loads(records["resource_estimate"])).evaluate()
        self.assertEqual(historical, json.loads(RECORDS["evaluation_report"]))
        evaluator = Mock(side_effect=AssertionError("must not evaluate an unresolved selected version"))
        with patch.object(replay, "_local_evaluator", return_value=evaluator):
            result = run(records, sidecar=sidecar, replay_manifest=replay_manifest)
            self.assertEqual(result.status, "input_identity_mismatch")
            self.assertIn(("selection:sel_tool", "selected_version_absent"), result.issues)
            self.assertIsNone(result.generated_report)
            self.assertIs(next(b.raw for b in result.bindings if b.kind == "evaluation_report"),
                          RECORDS["evaluation_report"])
            evaluator.assert_not_called()

    def test_wrong_enabled_monitoring_kind_is_rejected_even_when_frozen_findings_would_pass(self):
        build = json.loads(BUILD)
        selection = next(s for s in build["selections"] if s["kind"] == "monitoring_stack")
        other = next(s for s in build["selections"] if s["kind"] == "workload")
        selection["catalog_item_id"] = other["catalog_item_id"]
        selection["catalog_item_version"] = other["catalog_item_version"]
        build_bytes = replay.encoded(build)
        sidecar, replay_manifest = repin(RECORDS, build_bytes)
        frozen = replay._local_evaluator(packet()["evaluator"])
        historical = frozen(build, json.loads(RECORDS["catalog_snapshot"]), json.loads(RECORDS["ruleset"]),
                            cost_estimate=json.loads(RECORDS["cost_estimate"]),
                            resource_estimate=json.loads(RECORDS["resource_estimate"])).evaluate()
        self.assertEqual(historical, json.loads(RECORDS["evaluation_report"]))
        evaluator = Mock(side_effect=AssertionError("must not evaluate a mismatched selected kind"))
        with patch.object(replay, "_local_evaluator", return_value=evaluator):
            result = run(build=build_bytes, sidecar=sidecar, replay_manifest=replay_manifest)
            self.assertEqual(result.status, "input_identity_mismatch")
            self.assertIn(("selection:sel_monitoring_stack", "selected_kind_mismatch"), result.issues)
            self.assertIsNone(result.generated_report)
            self.assertIs(result.original_build_bytes, build_bytes)
            evaluator.assert_not_called()

    def test_disabled_unresolved_selection_is_not_an_enabled_identity_failure(self):
        for mismatch in ("version", "kind"):
            build = json.loads(BUILD)
            selection = next(s for s in build["selections"] if s["kind"] == "monitoring_stack")
            selection["enabled"] = False
            if mismatch == "version":
                selection["catalog_item_version"] = "absent-disabled-version"
            else:
                other = next(s for s in build["selections"] if s["kind"] == "workload")
                selection["catalog_item_id"] = other["catalog_item_id"]
                selection["catalog_item_version"] = other["catalog_item_version"]
            build_bytes = replay.encoded(build)
            sidecar, replay_manifest = repin(RECORDS, build_bytes)
            with self.subTest(mismatch=mismatch):
                result = run(build=build_bytes, sidecar=sidecar, replay_manifest=replay_manifest)
                # The old report still mentions the formerly enabled selection;
                # evaluating its disabled state legitimately changes findings.
                self.assertEqual(result.status, "report_mismatch")
                self.assertIsNotNone(result.generated_report)
                self.assertFalse(any(slot.startswith("selection:") for slot, _ in result.issues))

    def test_invalid_and_unknown_historical_results_reproduce_without_becoming_valid(self):
        for outcome in ("fail", "unknown"):
            records = dict(RECORDS)
            rules = json.loads(records["ruleset"])
            rule = rules["rules"][0]
            rule["assert"] = ({"op": "eq", "left": {"literal": True}, "right": {"literal": False}}
                              if outcome == "fail" else {"op": "gte", "left": {"ref": {
                                  "scope": "build", "pointer": "/x_fixture_missing"}}, "right": {"literal": 1}})
            rules["rules"] = [rule]
            report = json.loads(records["evaluation_report"])
            finding = report["findings"][0]
            finding.update(outcome=outcome, message=rule["message"], remediation=rule["remediation"])
            report.update(findings=[finding], result="invalid" if outcome == "fail" else "indeterminate",
                          deployment_readiness="blocked", summary={"passed": 0, "failed": int(outcome == "fail"),
                                                                  "unknown": int(outcome == "unknown"), "skipped": 0})
            records["ruleset"], records["evaluation_report"] = replay.encoded(rules), replay.encoded(report)
            sidecar, replay_manifest = repin(records)
            with self.subTest(outcome=outcome):
                result = run(records, sidecar=sidecar, replay_manifest=replay_manifest)
                self.assertEqual(result.status, "reproduced")
                self.assertEqual(result.generated_report["result"], report["result"])
                self.assertEqual(result.generated_report["deployment_readiness"], "blocked")

    def test_evaluator_and_schema_pin_disagreements_never_run_an_arbitrary_evaluator(self):
        for field, value in (("profile", "untrusted-evaluator"), ("sha256", "0" * 64),
                             ("schemas_sha256", "0" * 64)):
            value_packet = packet()
            value_packet["evaluator"][field] = value
            with self.subTest(field=field):
                result = run(replay_manifest=manifest(value_packet))
                self.assertEqual(result.status, "profile_unavailable")
                self.assertIn(("evaluator", "evaluator_pin_unsupported"), result.issues)
                self.assertIsNone(result.generated_report)
                self.assertEqual({binding.kind for binding in result.bindings}, set(RECORDS))
                self.assertIs(next(b.raw for b in result.bindings if b.kind == "evaluation_report"),
                              RECORDS["evaluation_report"])

    def test_missing_or_modified_local_evaluator_cannot_execute(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evaluate.py"
            with patch.object(replay, "EVALUATOR_PATH", path):
                missing = run()
                self.assertEqual(missing.issues, (("evaluator", "local_evaluator_or_schemas_unavailable"),))
                self.assertIs(next(b.raw for b in missing.bindings if b.kind == "evaluation_report"),
                              RECORDS["evaluation_report"])
                path.write_bytes(b"raise AssertionError('untrusted evaluator executed')\n")
                result = run()
                self.assertEqual(result.issues, (("evaluator", "local_evaluator_digest_mismatch"),))
                self.assertIs(next(b.raw for b in result.bindings if b.kind == "evaluation_report"),
                              RECORDS["evaluation_report"])

    def test_unavailable_reader_retains_independent_missing_and_tampered_input_diagnostics(self):
        cases = (("resource_estimate", "missing", "pinned_artifact_unavailable"),
                 ("dependency_graph", "changed", "content_digest_mismatch"),
                 ("catalog_snapshot", "missing", "pinned_revision_unavailable"))
        for kind, mutation, code in cases:
            records = dict(RECORDS)
            if mutation == "missing":
                del records[kind]
            else:
                records[kind] += b"\n"
            value = packet()
            value["evaluator"]["profile"] = "unavailable-retained-reader"
            with self.subTest(kind=kind):
                result = run(records, replay_manifest=manifest(value))
                self.assertEqual(result.status, "profile_unavailable")
                self.assertEqual(result.issues, (("evaluator", "evaluator_pin_unsupported"), (kind, code)))
                self.assertIsNone(result.generated_report)
                self.assertIs(next(b.raw for b in result.bindings if b.kind == "evaluation_report"),
                              RECORDS["evaluation_report"])
                self.assertIsNone(next(b.raw for b in result.bindings if b.kind == kind))

    def test_unavailable_reader_never_fabricates_missing_or_tampered_report_bytes(self):
        for mutation, code in (("missing", "pinned_artifact_unavailable"),
                               ("changed", "content_digest_mismatch")):
            records = dict(RECORDS)
            if mutation == "missing":
                del records["evaluation_report"]
            else:
                records["evaluation_report"] += b"\n"
            value = packet(); value["evaluator"]["profile"] = "unavailable-retained-reader"
            with self.subTest(mutation=mutation):
                result = run(records, replay_manifest=manifest(value))
                self.assertEqual(result.status, "profile_unavailable")
                self.assertIn(("evaluation_report", code), result.issues)
                binding = next(b for b in result.bindings if b.kind == "evaluation_report")
                self.assertEqual(binding.status, code)
                self.assertIsNone(binding.raw)
                self.assertIsNone(result.generated_report)

    def test_unavailable_reader_keeps_report_identity_disagreement_explicit(self):
        records = dict(RECORDS); report = json.loads(records["evaluation_report"])
        report["build_revision"] = 2
        records["evaluation_report"] = replay.encoded(report)
        sidecar, replay_manifest = repin(records)
        value = json.loads(replay_manifest)["x_t0_historical_replay"]
        value["evaluator"]["profile"] = "unavailable-retained-reader"
        result = run(records, sidecar=sidecar, replay_manifest=manifest(value))
        self.assertEqual(result.status, "profile_unavailable")
        self.assertIn(("evaluation_report", "build_identity_mismatch"), result.issues)
        self.assertIs(next(b.raw for b in result.bindings if b.kind == "evaluation_report"),
                      records["evaluation_report"])
        self.assertIsNone(result.generated_report)

    def test_changed_or_missing_schema_bytes_cannot_claim_the_pinned_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            for original in replay.SCHEMA_DIRECTORY.glob("*.schema.json"):
                (path / original.name).write_bytes(original.read_bytes())
            for mutation in ("changed", "missing"):
                target = path / "build.schema.json"
                if mutation == "changed":
                    target.write_bytes(target.read_bytes() + b"\n")
                else:
                    target.unlink()
                with self.subTest(mutation=mutation), patch.object(replay, "SCHEMA_DIRECTORY", path):
                    self.assertEqual(run().issues, (("evaluator", "local_schema_digest_mismatch"),))

    def test_decimal_context_is_fixed_without_changing_the_callers_context(self):
        with localcontext() as context:
            context.prec = 2
            result = run()
            self.assertEqual(result.status, "reproduced")
            self.assertEqual(getcontext().prec, 2)

    def test_unsupported_interpreter_is_explicitly_unreproducible(self):
        with patch.object(replay.sys, "version_info", (3, 13, 0)):
            result = run()
            self.assertEqual(result.status, "profile_unavailable")
            self.assertIn(("evaluator", "interpreter_profile_unsupported"), result.issues)

    def test_unsupported_frozen_expression_fails_without_replacing_the_report(self):
        records = dict(RECORDS)
        rules = json.loads(records["ruleset"])
        # The frozen schema permits object array literals; its reference
        # evaluator's set conversion cannot evaluate unhashable objects.
        rules["rules"][0]["assert"] = {"op": "subset_of", "left": {"literal": [{}]},
                                           "right": {"literal": []}}
        records["ruleset"] = replay.encoded(rules)
        sidecar, replay_manifest = repin(records)
        result = run(records, sidecar=sidecar, replay_manifest=replay_manifest)
        self.assertEqual(result.status, "evaluation_failed")
        self.assertIsNone(result.generated_report)
        self.assertEqual(next(b.raw for b in result.bindings if b.kind == "evaluation_report"),
                         RECORDS["evaluation_report"])

    def test_optional_pricebook_absence_cannot_admit_a_retained_cost(self):
        build = json.loads(BUILD)
        del build["locks"]["pricebook_id"]
        build_bytes = replay.encoded(build)
        sidecar, replay_manifest = repin(RECORDS, build_bytes)
        sidecar_value = json.loads(sidecar)
        del sidecar_value["x_t0_revision_locks"]["artifacts"]["pricebook"]
        sidecar = replay.encoded(sidecar_value)
        value = json.loads(replay_manifest)["x_t0_historical_replay"]
        value["revision_locks_sha256"] = replay.digest(sidecar)
        result = run(build=build_bytes, sidecar=sidecar, replay_manifest=manifest(value))
        self.assertEqual(result.status, "input_identity_mismatch")
        self.assertIn(("cost_estimate", "pricebook_identity_mismatch"), result.issues)
        self.assertEqual(next(b.status for b in result.bindings if b.kind == "pricebook"), "not_supplied")

    def test_sidecar_revisions_share_the_signed_64_bit_profile_bound(self):
        sidecar = json.loads(SIDECAR)
        sidecar["x_t0_revision_locks"]["artifacts"]["catalog_snapshot"]["revision"] = 2**63
        raw = replay.encoded(sidecar)
        value = packet()
        value["revision_locks_sha256"] = replay.digest(raw)
        with self.assertRaisesRegex(replay.ReplayError, "integer_representation_unsupported"):
            run(sidecar=raw, replay_manifest=manifest(value))

    def test_manifest_rejects_ambiguous_revisions_ids_and_unpinned_override_fields(self):
        cases = []
        for number in (True, 1.0, 0, 2**63):
            value = packet()
            value["inputs"]["dependency_graph"]["revision"] = number
            cases.append(value)
        for kind, field in (("ruleset", "id"), ("ruleset", "version"),
                            ("resource_estimate", "build_id")):
            value = packet()
            value["inputs"][kind][field] += "\n"
            cases.append(value)
        for field in ("path", "metrics"):
            value = packet()
            value["evaluator"][field] = "/tmp/untrusted.py" if field == "path" else {"cost.monthly_total_amount": 0}
            cases.append(value)
        value = packet()
        del value["inputs"]["resource_estimate"]
        cases.append(value)
        for index, value in enumerate(cases):
            with self.subTest(index=index), self.assertRaises(replay.ReplayError):
                run(replay_manifest=manifest(value))

    def test_retained_identity_fields_require_exact_integer_tokens_and_full_ids(self):
        for kind in RECORDS:
            for mutation in ("id", "revision"):
                if kind == "ruleset" and mutation == "revision":
                    continue
                records = dict(RECORDS)
                document = json.loads(records[kind])
                if mutation == "id":
                    document["id"] += "\n"
                else:
                    field = "revision" if "revision" in document else "build_revision"
                    document[field] = 1.0
                records[kind] = replay.encoded(document)
                with self.subTest(kind=kind, mutation=mutation), self.assertRaises(ValueError):
                    replay.ReplayArchive(records.items())

    def test_duplicate_archive_keys_malformed_json_and_resource_limits_are_rejected(self):
        for kind, raw in RECORDS.items():
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                replay.ReplayArchive([(kind, raw), (kind, raw)])
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}', b'"\xff"', b'"\\ud800"'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                run(replay_manifest=raw)
        with self.assertRaisesRegex(ValueError, "byte_limit_exceeded"):
            run(replay_manifest=MANIFEST + b" " * replay.MAX_ENVELOPE_BYTES)
        with patch.object(replay, "MAX_RECORDS", 1), self.assertRaisesRegex(replay.ReplayError, "archive_limit_exceeded"):
            replay.ReplayArchive(RECORDS.items())
        with patch.object(replay, "MAX_ARCHIVE_BYTES", 1), self.assertRaisesRegex(replay.ReplayError, "archive_limit_exceeded"):
            replay.ReplayArchive(RECORDS.items())
        with self.assertRaisesRegex(replay.ReplayError, "unsupported_artifact_kind"):
            replay.ReplayArchive([("evaluator", b"pass")])


if __name__ == "__main__":
    unittest.main()
