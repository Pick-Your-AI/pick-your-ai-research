"""Synthetic actual-rule CD-3 gates; no vendor evidence or successor adoption."""

from copy import deepcopy
from dataclasses import replace
import itertools
import json
from pathlib import Path
import unittest

from contracts.v1.reference import evaluate as frozen
from tests.frozen_support_rule_adapter_prototype import (
    ELIGIBILITY, PROFILE, RULE_IDS, RULESET_SHA256,
    FrozenSupportRuleAdapter, RuleEvidence, digest,
)


ROOT = Path(__file__).resolve().parents[1]
BUILD_RAW = (ROOT / "contracts/v1/examples/build.json").read_bytes()
CATALOG_RAW = (ROOT / "contracts/v1/examples/catalog.json").read_bytes()
RULESET_RAW = (ROOT / "contracts/v1/baseline/core-ruleset.json").read_bytes()
FORMAT, PRECISION = RULE_IDS
QUALIFIED = dict.fromkeys(ELIGIBILITY, True)


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


class FrozenSupportRuleAdapterTests(unittest.TestCase):
    def setUp(self):
        self.build = json.loads(BUILD_RAW)
        self.catalog = json.loads(CATALOG_RAW)

    def selection(self, kind):
        return next(s for s in self.build["selections"] if s["kind"] == kind)

    def item(self, kind):
        return next(i for i in self.catalog["items"] if i["kind"] == kind)

    def adapter(self):
        return FrozenSupportRuleAdapter(encode(self.build), encode(self.catalog))

    def evidence(self, adapter, rule_id, **facts):
        return replace(RuleEvidence("cohort.synthetic.support", "0.1.0",
                                    adapter.support_scope(rule_id), frozenset()), **facts)

    def result(self, rule_id, *, facts=None, qualifications=None, checked_only=None):
        adapter = self.adapter()
        return adapter.evaluate(rule_id, self.evidence(adapter, rule_id, **(facts or {})),
                                eligible_inputs=QUALIFIED if qualifications is None else qualifications,
                                cohort_checked_only=checked_only)

    def test_actual_named_rules_keep_definitions_severity_refs_and_original_bytes(self):
        adapter = FrozenSupportRuleAdapter(BUILD_RAW, CATALOG_RAW)
        expected = {r["id"]: r for r in json.loads(RULESET_RAW)["rules"]}
        for rule_id in RULE_IDS:
            with self.subTest(rule=rule_id):
                result = adapter.evaluate(rule_id, self.evidence(adapter, rule_id),
                                          eligible_inputs=QUALIFIED)
                self.assertEqual(result["profile"], PROFILE)
                self.assertEqual(result["rule"], expected[rule_id])
                self.assertEqual(result["rule"]["severity"], "error")
                self.assertEqual(result["rule"]["on_unknown"], "block")
                self.assertEqual(result["ruleset"]["sha256"], RULESET_SHA256)
                self.assertEqual(result["decision"]["outcome"], "pass")
                for side in ("left", "right"):
                    operand = result["operands"][side]
                    self.assertEqual(operand["ref"], expected[rule_id]["assert"][side]["ref"])
                    source = self.build if operand["ref"]["scope"] == "selection" else self.catalog
                    self.assertEqual(frozen.pointer_get(source, operand["source_path"]), operand["value"])
        self.assertEqual(adapter.original_bytes, (BUILD_RAW, CATALOG_RAW, RULESET_RAW))

    def test_three_actual_frozen_omission_cases_keep_history_and_gate_four_failures(self):
        for omit_precision, omit_format in ((True, False), (False, True), (True, True)):
            with self.subTest(precision=omit_precision, formats=omit_format):
                self.setUp()
                engine = self.item("inference_engine")["spec"]
                if omit_precision:
                    engine["supported_precisions"] = ["int8"]
                if omit_format:
                    engine["model_formats"] = ["gguf"]
                adapter = self.adapter()  # These are admitted full frozen-format inputs.
                before = {f["rule_id"]: f for f in frozen.Evaluator(
                    self.build, self.catalog, json.loads(RULESET_RAW)).evaluate()["findings"]}
                for rule_id, omitted in ((PRECISION, omit_precision), (FORMAT, omit_format)):
                    self.assertEqual(before[rule_id]["outcome"], "fail" if omitted else "pass")
                    after = adapter.evaluate(rule_id, self.evidence(adapter, rule_id),
                                             eligible_inputs=QUALIFIED)
                    self.assertEqual(after["decision"]["outcome"], "unknown" if omitted else "pass")
                    self.assertEqual(after["decision"]["findings"][0]["reason"],
                                     "unmarked_absence" if omitted else "documented_member")
                    self.assertEqual(after["rule"]["severity"], before[rule_id]["severity"])

    def test_exhaustive_precision_negative_has_an_admitted_scalar_request(self):
        self.item("inference_engine")["spec"]["supported_precisions"] = ["int8"]
        for marker in (None, False, True):
            result = self.result(PRECISION, facts={"exhaustive": True, "requested_complete": marker})
            self.assertEqual(result["decision"]["outcome"], "fail")
            self.assertEqual(result["decision"]["findings"][0]["reason"], "exhaustive_absence")
            self.assertEqual(result["requested_completeness"],
                             {"effective": True, "basis": "admitted_selected_scalar"})
            self.assertIs(result["evidence"]["requested_complete"], marker)

    def test_exhaustive_format_absence_needs_separately_qualified_request_completeness(self):
        self.item("inference_engine")["spec"]["model_formats"] = ["gguf"]
        cases = ((None, True, "unknown"), (False, True, "unknown"), (True, None, "unknown"),
                 (True, False, "unknown"), (True, True, "fail"))
        for complete, qualified, expected in cases:
            with self.subTest(complete=complete, qualified=qualified):
                result = self.result(FORMAT, facts={"exhaustive": True, "requested_complete": complete},
                                     qualifications=QUALIFIED | {"requested_complete": qualified})
                self.assertEqual(result["decision"]["outcome"], expected)
                self.assertEqual(result["decision"]["findings"][0]["reason"], "exhaustive_absence")
                self.assertNotEqual(result["requested_completeness"]["basis"], "admitted_selected_scalar")

    def test_explicit_negatives_do_not_require_publisher_exhaustiveness(self):
        engine = self.item("inference_engine")["spec"]
        engine["supported_precisions"], engine["model_formats"] = ["int8"], ["gguf"]
        for rule_id, value, complete, expected in (
                (PRECISION, "fp16", None, "fail"), (FORMAT, "safetensors", None, "unknown"),
                (FORMAT, "safetensors", True, "fail")):
            result = self.result(rule_id, facts={"unsupported": frozenset({value}),
                                                "requested_complete": complete})
            self.assertEqual(result["decision"]["outcome"], expected)
            self.assertEqual(result["decision"]["findings"][0]["reason"], "explicit_unsupported")

    def test_positive_format_witness_retains_other_unknown_and_disputed_rows(self):
        self.item("model")["spec"]["model_formats"] = ["onnx", "gguf", "safetensors"]
        self.item("inference_engine")["spec"]["model_formats"] = ["safetensors", "gguf"]
        result = self.result(FORMAT, facts={"unsupported": frozenset({"gguf"}),
                                           "requested_complete": False}, checked_only=True)
        decision = result["decision"]
        self.assertEqual(decision["outcome"], "pass")
        self.assertTrue(decision["disputed"])
        self.assertEqual([(f["value"], f["outcome"], f["reason"]) for f in decision["findings"]], [
            ("gguf", "unknown", "opposite_equal_rank_claims"),
            ("onnx", "unknown", "unmarked_absence"),
            ("safetensors", "pass", "documented_member"),
        ])
        self.assertEqual(decision["evidence_label"], "unverified")
        self.assertEqual(result["operands"]["left"]["value"], ["onnx", "gguf", "safetensors"])

    def test_precision_equal_rank_dispute_stays_unknown_at_fixed_severity(self):
        result = self.result(PRECISION, facts={"unsupported": frozenset({"fp16"})}, checked_only=True)
        self.assertEqual(result["decision"]["outcome"], "unknown")
        self.assertTrue(result["decision"]["disputed"])
        self.assertEqual(result["decision"]["findings"][0]["reason"], "opposite_equal_rank_claims")
        self.assertEqual(result["rule"]["severity"], "error")

    def test_actual_applicability_has_distinct_inactive_and_unresolved_controls(self):
        cases = ("api", "disabled_engine", "missing_engine", "missing_deployment_version",
                 "unknown_mode_and_disabled_engine")
        for case in cases:
            with self.subTest(case=case):
                self.setUp()
                if case == "api":
                    self.item("deployment_mode")["spec"]["mode"] = "api"
                if case in ("disabled_engine", "unknown_mode_and_disabled_engine"):
                    self.selection("inference_engine")["enabled"] = False
                if case == "missing_engine":
                    self.build["selections"].remove(self.selection("inference_engine"))
                if case in ("missing_deployment_version", "unknown_mode_and_disabled_engine"):
                    self.selection("deployment_mode")["catalog_item_version"] = "unavailable"
                before = {f["rule_id"]: f for f in frozen.Evaluator(
                    self.build, self.catalog, json.loads(RULESET_RAW)).evaluate()["findings"]}
                for rule_id in RULE_IDS:
                    result = self.result(rule_id, checked_only=True)
                    self.assertEqual(result["decision"]["outcome"], before[rule_id]["outcome"])
                    self.assertIsNone(result["decision"]["evidence_label"])
                    self.assertFalse(result["decision"]["findings"])

    def test_missing_precision_is_not_a_complete_empty_or_default_scalar(self):
        del self.selection("model")["settings"]["precision"]
        result = self.result(PRECISION, facts={"requested_complete": True})
        self.assertEqual(result["decision"]["reason"], "requirement_unknown")
        self.assertEqual(result["operands"]["right"]["reason"], "property_missing")
        self.assertNotIn("value", result["operands"]["right"])
        self.assertIsNone(result["requested_completeness"]["effective"])
        self.assertEqual(self.result(FORMAT)["decision"]["outcome"], "pass")

    def test_exact_catalog_item_version_kind_and_snapshot_are_required(self):
        for case, expected in (("missing", "catalog_item_missing"),
                               ("version", "catalog_version_mismatch"),
                               ("kind", "catalog_kind_mismatch")):
            with self.subTest(case=case):
                self.setUp()
                engine = self.selection("inference_engine")
                if case == "missing":
                    engine["catalog_item_id"] = "cat.engine.missing"
                elif case == "version":
                    engine["catalog_item_version"] = "unavailable"
                else:
                    engine["catalog_item_id"] = self.item("model")["id"]
                result = self.result(FORMAT)
                self.assertEqual(result["decision"]["reason"], "support_operand_unresolved")
                self.assertEqual(result["operands"]["right"]["reason"], expected)
                self.assertIsNone(result["support_scope"])
        self.setUp()
        self.build["locks"]["catalog_snapshot_id"] = "catalog.different"
        self.assertEqual(self.result(FORMAT)["decision"]["reason"], "catalog_snapshot_mismatch")

    def test_all_seven_scope_dimensions_and_missing_scope_stay_unknown(self):
        adapter = self.adapter()
        changes = (("selection_id", "sel_other"), ("catalog_sha256", "a" * 64),
                   ("item.id", "cat.other.item"), ("item.version", "other"),
                   ("item.kind", "model"), ("property", "/spec/other"),
                   ("conditions_sha256", "b" * 64))
        for rule_id in RULE_IDS:
            original = self.evidence(adapter, rule_id)
            for key, value in changes:
                with self.subTest(rule=rule_id, dimension=key):
                    scope = deepcopy(original.scope)
                    if key.startswith("item."):
                        scope["item"][key[5:]] = value
                    else:
                        scope[key] = value
                    result = adapter.evaluate(rule_id, replace(original, scope=scope),
                                              eligible_inputs=QUALIFIED, cohort_checked_only=True)
                    self.assertEqual(result["decision"]["reason"], "support_scope_mismatch")
                    self.assertIsNone(result["decision"]["evidence_label"])
            self.assertEqual(adapter.evaluate(rule_id, replace(original, scope=None),
                                              eligible_inputs=QUALIFIED)["decision"]["outcome"], "unknown")

    def test_raw_byte_scope_and_order_are_preserved_without_reusing_old_cohorts(self):
        original = FrozenSupportRuleAdapter(BUILD_RAW, CATALOG_RAW)
        changed = FrozenSupportRuleAdapter(BUILD_RAW + b"\n", CATALOG_RAW + b" ")
        for rule_id in RULE_IDS:
            stale = self.evidence(original, rule_id)
            self.assertEqual(changed.evaluate(rule_id, stale, eligible_inputs=QUALIFIED)
                             ["decision"]["reason"], "support_scope_mismatch")
            current = self.evidence(changed, rule_id)
            result = changed.evaluate(rule_id, current, eligible_inputs=QUALIFIED)
            self.assertEqual(result["decision"]["outcome"], "pass")
            self.assertEqual(result["build_sha256"], digest(BUILD_RAW + b"\n"))
        self.assertEqual(changed.original_bytes[:2], (BUILD_RAW + b"\n", CATALOG_RAW + b" "))

    def test_qualification_omission_or_ineligibility_cannot_self_qualify(self):
        adapter = self.adapter()
        for rule_id in RULE_IDS:
            evidence = self.evidence(adapter, rule_id)
            self.assertEqual(adapter.evaluate(rule_id, evidence)["decision"]["outcome"], "unknown")
            for field, value in itertools.product(("applies_when", "requested", "cohort"), (False, None)):
                result = adapter.evaluate(rule_id, evidence, eligible_inputs=QUALIFIED | {field: value},
                                          cohort_checked_only=True)
                self.assertEqual(result["decision"]["outcome"], "unknown")
                self.assertIsNone(result["decision"]["evidence_label"])
                if field == "requested" and rule_id == PRECISION:
                    self.assertIsNone(result["requested_completeness"]["effective"])
        self.item("deployment_mode")["spec"]["mode"] = "api"
        self.assertEqual(self.result(FORMAT, qualifications={})["decision"]["outcome"], "unknown")

    def test_recorded_empty_negative_inventory_differs_from_unresolved(self):
        for rule_id in RULE_IDS:
            missing = self.result(rule_id, facts={"unsupported": None, "exhaustive": True}, checked_only=True)
            self.assertEqual(missing["decision"]["reason"], "unsupported_claims_unresolved")
            self.assertIsNone(missing["decision"]["evidence_label"])
            self.assertIsNone(missing["evidence"]["unsupported"])
            self.assertEqual(self.result(rule_id)["decision"]["outcome"], "pass")

    def test_checked_only_is_separate_and_an_absent_label_never_becomes_verified(self):
        for flag, label in ((None, None), (False, None), (True, "unverified")):
            for rule_id in RULE_IDS:
                result = self.result(rule_id, checked_only=flag)
                self.assertEqual(result["decision"]["outcome"], "pass")
                self.assertEqual(result["decision"]["evidence_label"], label)
                self.assertIs(result["evaluation"]["cohort_checked_only"], flag)

    def test_malformed_markers_reject_before_known_nonapplicability(self):
        self.item("deployment_mode")["spec"]["mode"] = "api"
        adapter = self.adapter()
        for value in (0, 1, "true", [], {}):
            for rule_id in RULE_IDS:
                evidence = self.evidence(adapter, rule_id)
                for field in ("exhaustive", "requested_complete"):
                    with self.subTest(value=value, rule=rule_id, field=field):
                        with self.assertRaises(ValueError):
                            adapter.evaluate(rule_id, replace(evidence, **{field: value}),
                                             eligible_inputs=QUALIFIED)
                with self.assertRaises(ValueError):
                    adapter.evaluate(rule_id, evidence, eligible_inputs=QUALIFIED, cohort_checked_only=value)
                for field in ELIGIBILITY:
                    with self.assertRaises(ValueError):
                        adapter.evaluate(rule_id, evidence, eligible_inputs=QUALIFIED | {field: value})
        with self.assertRaises(ValueError):
            adapter.evaluate(FORMAT, self.evidence(adapter, FORMAT), eligible_inputs={"verified": True})

    def test_malformed_negative_lists_and_cohort_identity_reject_before_shortcuts(self):
        self.item("deployment_mode")["spec"]["mode"] = "api"
        adapter = self.adapter()
        evidence = self.evidence(adapter, PRECISION)
        for value in ("fp16", ["fp16"], {"fp16"}, frozenset({1}), frozenset({""}), frozenset({" "})):
            with self.subTest(unsupported=value), self.assertRaises(ValueError):
                adapter.evaluate(PRECISION, replace(evidence, unsupported=value), eligible_inputs=QUALIFIED)
        for change in ({"cohort_id": "cohort.bad\n"}, {"cohort_id": ""}, {"cohort_version": 1},
                       {"scope": {}}, {"scope": []}, {"cohort_version": "\ud800"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                adapter.evaluate(PRECISION, replace(evidence, **change), eligible_inputs=QUALIFIED)

    def test_full_shape_rejects_invalid_scalar_activations_and_required_arrays(self):
        for value in ("unknown", " fp16", [], None):
            self.setUp()
            self.selection("model")["settings"]["precision"] = value
            self.item("deployment_mode")["spec"]["mode"] = "api"
            with self.subTest(precision=value), self.assertRaises(ValueError):
                self.adapter()
        for value in (0, 1, "true", None):
            self.setUp()
            self.selection("tool")["enabled"] = value
            with self.subTest(enabled=value), self.assertRaises(ValueError):
                self.adapter()
        for kind, field in (("model", "model_formats"), ("inference_engine", "model_formats"),
                            ("inference_engine", "supported_precisions")):
            for value in ("absent", [], "fp16"):
                self.setUp()
                if value == "absent":
                    del self.item(kind)["spec"][field]
                else:
                    self.item(kind)["spec"][field] = value
                with self.subTest(kind=kind, field=field, value=value), self.assertRaises(ValueError):
                    self.adapter()

    def test_duplicate_build_roles_ids_and_catalog_ids_never_choose_one(self):
        for case in ("role", "id", "catalog"):
            self.setUp()
            if case == "catalog":
                duplicate = deepcopy(self.item("inference_engine"))
                duplicate["version"] = "other-version"
                self.catalog["items"].append(duplicate)
            else:
                duplicate = deepcopy(self.selection("inference_engine"))
                duplicate["enabled"] = False
                duplicate["id" if case == "role" else "role"] = "alternative"
                self.build["selections"].append(duplicate)
            with self.subTest(case=case), self.assertRaises(ValueError):
                self.adapter()

    def test_only_two_rule_ids_and_unambiguous_retained_json_are_admitted(self):
        adapter = self.adapter()
        for rule_id in ("rule.precision.engine\n", "rule.context.window", "contains", None):
            with self.subTest(rule=rule_id), self.assertRaises(ValueError):
                adapter.evaluate(rule_id, self.evidence(adapter, PRECISION), eligible_inputs=QUALIFIED)
        for raw in (BUILD_RAW.replace(b'"revision": 1', b'"revision": 1, "revision": 1', 1),
                    BUILD_RAW.replace(b'"revision": 1', b'"revision": NaN', 1),
                    BUILD_RAW.replace(b'"revision": 1', b'"revision": 1.0', 1)):
            self.assertNotEqual(raw, BUILD_RAW)
            with self.assertRaises(ValueError):
                FrozenSupportRuleAdapter(raw, CATALOG_RAW)

    def test_returned_receipts_and_input_order_do_not_change_original_sources(self):
        adapter = self.adapter()
        evidence = self.evidence(adapter, FORMAT)
        original = adapter.evaluate(FORMAT, evidence, eligible_inputs=QUALIFIED)
        changed = adapter.evaluate(FORMAT, evidence, eligible_inputs=QUALIFIED)
        changed["rule"]["severity"] = "info"
        changed["operands"]["left"]["value"].append("gguf")
        changed["evidence"]["scope"]["item"]["version"] = "tampered"
        changed["evaluation"]["eligible_inputs"]["cohort"] = False
        self.assertEqual(adapter.evaluate(FORMAT, evidence, eligible_inputs=QUALIFIED), original)
        self.build["selections"].reverse()
        self.catalog["items"].reverse()
        reordered = self.result(FORMAT)
        self.assertEqual(reordered["decision"], original["decision"])
        self.assertNotEqual(reordered["build_sha256"], original["build_sha256"])
        self.assertNotEqual(reordered["operands"]["left"]["source_path"],
                            original["operands"]["left"]["source_path"])


if __name__ == "__main__":
    unittest.main()
