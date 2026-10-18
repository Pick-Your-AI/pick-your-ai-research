"""Synthetic membership evidence cases; list support is not joint runtime fit."""

import importlib.util
import json
from dataclasses import replace
from pathlib import Path
import unittest

from tests.support_membership_prototype import Evidence, Outcome, Requirement, evaluate

SOURCE = Evidence("fixture.source", True, frozenset({"gguf"}))


class SupportMembershipCases(unittest.TestCase):
    def test_documented_member_passes_without_exhaustiveness_or_verification(self):
        for complete in (None, False, True):
            with self.subTest(complete=complete):
                result = evaluate(
                    frozenset({"gguf"}), replace(SOURCE, exhaustive=complete)
                )
                self.assertEqual(result.outcome, Outcome.PASS)
                self.assertEqual(result.evidence_label, "unverified")
                self.assertEqual(result.source_id, SOURCE.source_id)

    def test_unmarked_omission_is_unknown_instead_of_unsupported(self):
        for complete in (None, False):
            with self.subTest(complete=complete):
                result = evaluate(
                    frozenset({"safetensors"}), replace(SOURCE, exhaustive=complete)
                )
                self.assertEqual(result.outcome, Outcome.UNKNOWN)
                self.assertEqual(result.findings[0].reason, "unmarked_absence")

    def test_exhaustive_omission_supplies_negative_evidence(self):
        result = evaluate(frozenset({"safetensors"}), replace(SOURCE, exhaustive=True))
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertEqual(result.findings[0].reason, "exhaustive_absence")

    def test_missing_list_is_not_a_known_empty_exhaustive_list(self):
        for supported, expected in (
            (None, Outcome.UNKNOWN),
            (frozenset(), Outcome.FAIL),
        ):
            with self.subTest(supported=supported):
                result = evaluate(
                    frozenset({"gguf"}),
                    replace(SOURCE, supported=supported, exhaustive=True),
                )
                self.assertEqual(result.outcome, expected)

    def test_empty_unmarked_list_has_no_negative_claim(self):
        result = evaluate(frozenset({"gguf"}), replace(SOURCE, supported=frozenset()))
        self.assertEqual(result.outcome, Outcome.UNKNOWN)

    def test_explicit_unsupported_needs_no_exhaustive_inventory(self):
        for supported in (None, frozenset(), frozenset({"gguf"})):
            with self.subTest(supported=supported):
                evidence = replace(
                    SOURCE, supported=supported, unsupported=frozenset({"safetensors"})
                )
                result = evaluate(frozenset({"safetensors"}), evidence)
                self.assertEqual(result.outcome, Outcome.FAIL)
                self.assertEqual(result.findings[0].reason, "explicit_unsupported")

    def test_known_out_of_scope_or_unresolved_evidence_cannot_decide_support(self):
        for eligible in (False, None):
            for value in ("gguf", "safetensors"):
                with self.subTest(eligible=eligible, value=value):
                    evidence = replace(SOURCE, eligible=eligible, exhaustive=True)
                    result = evaluate(frozenset({value}), evidence)
                    self.assertEqual(result.outcome, Outcome.UNKNOWN)
                    self.assertEqual(result.reason, "no_eligible_evidence")

    def test_any_accepts_one_documented_alternative_and_retains_unknown_others(self):
        result = evaluate(frozenset({"gguf", "safetensors"}), SOURCE)
        self.assertEqual(result.outcome, Outcome.PASS)
        self.assertEqual(
            [(f.value, f.outcome) for f in result.findings],
            [("gguf", Outcome.PASS), ("safetensors", Outcome.UNKNOWN)],
        )

    def test_any_rejects_only_when_every_alternative_has_negative_evidence(self):
        evidence = replace(SOURCE, unsupported=frozenset({"pytorch"}))
        requested = frozenset({"pytorch", "safetensors"})
        self.assertEqual(evaluate(requested, evidence).outcome, Outcome.UNKNOWN)
        self.assertEqual(
            evaluate(requested, replace(evidence, exhaustive=True)).outcome,
            Outcome.FAIL,
        )

    def test_all_requires_every_member_and_keeps_unmarked_gaps_unknown(self):
        requested = frozenset({"gguf", "safetensors"})
        self.assertEqual(
            evaluate(requested, SOURCE, Requirement.ALL).outcome, Outcome.UNKNOWN
        )
        self.assertEqual(
            evaluate(
                requested, replace(SOURCE, exhaustive=True), Requirement.ALL
            ).outcome,
            Outcome.FAIL,
        )
        self.assertEqual(
            evaluate(
                requested, replace(SOURCE, supported=requested), Requirement.ALL
            ).outcome,
            Outcome.PASS,
        )

    def test_all_negative_counterexample_does_not_remove_other_unknown_rows(self):
        evidence = replace(SOURCE, unsupported=frozenset({"pytorch"}))
        result = evaluate(
            frozenset({"pytorch", "safetensors"}), evidence, Requirement.ALL
        )
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertEqual(
            [f.outcome for f in result.findings], [Outcome.FAIL, Outcome.UNKNOWN]
        )

    def test_opposite_equal_rank_claims_remain_disputed_unknown(self):
        result = evaluate(
            frozenset({"gguf"}), replace(SOURCE, unsupported=frozenset({"gguf"}))
        )
        self.assertEqual(result.outcome, Outcome.UNKNOWN)
        self.assertTrue(result.disputed)
        self.assertEqual(result.findings[0].reason, "opposite_equal_rank_claims")

    def test_known_alternative_does_not_erase_dispute_in_another_member(self):
        evidence = replace(
            SOURCE,
            supported=frozenset({"gguf", "safetensors"}),
            unsupported=frozenset({"safetensors"}),
        )
        result = evaluate(frozenset({"gguf", "safetensors"}), evidence)
        self.assertEqual(result.outcome, Outcome.PASS)
        self.assertTrue(result.disputed)
        self.assertEqual(
            [f.outcome for f in result.findings], [Outcome.PASS, Outcome.UNKNOWN]
        )

    def test_applicability_and_missing_requirements_are_distinct(self):
        self.assertEqual(
            evaluate(None, SOURCE, applicable=False).outcome, Outcome.SKIPPED
        )
        self.assertEqual(
            evaluate(None, SOURCE, applicable=None).reason, "applicability_unknown"
        )
        self.assertEqual(evaluate(None, SOURCE).reason, "requirement_unknown")
        with self.assertRaisesRegex(ValueError, "nonempty requirement"):
            evaluate(frozenset(), SOURCE)

    def test_markers_cannot_be_inferred_from_truthy_text_or_numeric_values(self):
        for value in ("false", "unknown", 0, 1):
            for marker in ("eligible", "exhaustive"):
                with self.subTest(value=value, marker=marker):
                    with self.assertRaisesRegex(ValueError, "normalized bool or None"):
                        evaluate(
                            frozenset({"gguf"}), replace(SOURCE, **{marker: value})
                        )

    def test_frozen_contains_and_intersects_false_is_not_a_completeness_claim(self):
        contract = Path(__file__).resolve().parents[1] / "contracts/v1"
        spec = importlib.util.spec_from_file_location(
            "cd3_frozen_evaluator", contract / "reference/evaluate.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        evaluator = module.Evaluator(
            json.loads((contract / "examples/build.json").read_text()),
            json.loads((contract / "examples/catalog.json").read_text()),
            json.loads((contract / "baseline/core-ruleset.json").read_text()),
        )
        self.assertIs(evaluator.compare("contains", ["float16"], "int4"), False)
        self.assertIs(evaluator.compare("intersects", ["gguf"], ["safetensors"]), False)
        precision = replace(SOURCE, supported=frozenset({"float16"}))
        self.assertEqual(
            evaluate(frozenset({"int4"}), precision).outcome, Outcome.UNKNOWN
        )
        self.assertEqual(
            evaluate(frozenset({"safetensors"}), SOURCE).outcome, Outcome.UNKNOWN
        )


if __name__ == "__main__":
    unittest.main()
