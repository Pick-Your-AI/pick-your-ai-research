"""CD-3 labels describe used, caller-qualified evidence, never source strings."""

from dataclasses import replace
from copy import deepcopy
import json
from pathlib import Path
import unittest

from tests.support_membership_binding_prototype import (
    ELIGIBILITY, RESULT, SupportQueryRecord, answer_path, digest,
)
from tests.support_membership_prototype import Evidence, Requirement, evaluate


FIXTURES = Path(__file__).with_name("fixtures")
QUALIFIED = dict.fromkeys(ELIGIBILITY, True)
SOURCE = Evidence("fixture.source", True, frozenset({"gguf"}))


def encoded(value):
    return json.dumps(value, allow_nan=False).encode()


def record(changes=None):
    binding = json.loads((FIXTURES / "support-membership-binding.json").read_bytes())
    answers = json.loads((FIXTURES / "support-membership-answers.json").read_bytes())
    proposal = binding["x_t0_support_query"]
    for field, answer in (changes or {}).items():
        answers["x_t0_answer_states"]["answers"][answer_path(proposal, field)] = answer
    raw = encoded(answers)
    proposal["answer_states_sha256"] = digest(raw)
    return SupportQueryRecord(encoded(binding), raw)


class SupportEvidenceLabelTests(unittest.TestCase):
    def test_membership_eligibility_does_not_establish_a_checked_only_grade(self):
        decision = evaluate(frozenset({"gguf"}), SOURCE)
        self.assertEqual(decision.outcome, "pass")
        self.assertIsNone(decision.evidence_label)

    def test_unused_or_ineligible_cohort_has_no_evidence_label(self):
        cases = (
            (frozenset({"gguf"}), SOURCE, {"applicable": False}),
            (frozenset({"gguf"}), SOURCE, {"applicable": None}),
            (None, SOURCE, {}),
            (frozenset(), SOURCE, {}),
            (frozenset({"gguf"}), replace(SOURCE, eligible=False), {}),
            (frozenset({"gguf"}), replace(SOURCE, eligible=None), {}),
        )
        for requested, evidence, context in cases:
            for checked in (None, False, True):
                with self.subTest(requested=requested, evidence=evidence, context=context, checked=checked):
                    decision = evaluate(requested, replace(evidence, checked_only=checked), **context)
                    self.assertEqual(decision.findings, ())
                    self.assertIsNone(decision.evidence_label)

    def test_missing_cohort_claims_are_not_checked_only_evidence(self):
        for unsupported in (frozenset(), frozenset({"unrelated"})):
            for checked in (None, False, True):
                with self.subTest(unsupported=unsupported, checked=checked):
                    decision = evaluate(frozenset({"gguf"}), replace(
                        SOURCE, supported=None, unsupported=unsupported, checked_only=checked))
                    self.assertEqual(decision.findings[0].reason, "support_list_missing")
                    self.assertIsNone(decision.evidence_label)

    def test_binding_does_not_label_unused_unqualified_or_merely_eligible_evidence(self):
        query = record()
        for enabled, eligible in ((False, QUALIFIED), (None, QUALIFIED),
                                  (True, None), (True, {**QUALIFIED, "cohort": False}),
                                  (True, QUALIFIED)):
            with self.subTest(enabled=enabled, eligible=eligible):
                result = query.evaluate(query.scope, enabled=enabled, eligible_inputs=eligible)
                self.assertIsNone(result["x_t0_support_result"]["decision"]["evidence_label"])

    def test_only_qualified_used_cohort_claims_receive_unverified_without_changing_findings(self):
        cases = (
            (SOURCE, frozenset({"gguf"}), Requirement.ANY, "pass"),
            (replace(SOURCE, unsupported=frozenset({"onnx"})), frozenset({"onnx"}), Requirement.ALL, "fail"),
            (replace(SOURCE, supported=frozenset(), exhaustive=True), frozenset({"gguf"}), Requirement.ANY, "fail"),
            (SOURCE, frozenset({"onnx"}), Requirement.ANY, "unknown"),
            (replace(SOURCE, unsupported=frozenset({"gguf"})), frozenset({"gguf"}), Requirement.ANY, "unknown"),
            (replace(SOURCE, supported=None, unsupported=frozenset({"onnx"})),
             frozenset({"onnx", "gguf"}), Requirement.ANY, "unknown"),
        )
        for evidence, requested, requirement, outcome in cases:
            baseline = evaluate(requested, evidence, requirement, requested_complete=True)
            for checked in (None, False, True):
                with self.subTest(evidence=evidence, requirement=requirement, checked=checked):
                    decision = evaluate(requested, replace(evidence, checked_only=checked),
                                        requirement, requested_complete=True)
                    self.assertEqual(decision.outcome, outcome)
                    self.assertEqual(decision.evidence_label, "unverified" if checked is True else None)
                    self.assertEqual(replace(decision, evidence_label=None), baseline)

    def test_checked_only_fact_cannot_bypass_binding_preconditions_or_missing_claims(self):
        query = record()
        cases = ((False, query.scope, QUALIFIED), (None, query.scope, QUALIFIED),
                 (True, None, QUALIFIED), (True, query.scope, None),
                 (True, query.scope, {**QUALIFIED, "cohort": False}),
                 (True, query.scope, {**QUALIFIED, "cohort": None}))
        for enabled, scope, eligible in cases:
            with self.subTest(enabled=enabled, scope=scope, eligible=eligible):
                result = query.evaluate(scope, enabled=enabled, eligible_inputs=eligible,
                                        cohort_checked_only=True)["x_t0_support_result"]
                self.assertIsNone(result["decision"]["evidence_label"])
                self.assertEqual(result["decision"]["findings"], [])
        for changes in (
            {"applies_when": {"state": "provided", "value": False}},
            {"requested": {"state": "missing"}},
            {"requested": {"state": "provided", "value": []}},
            {"unsupported": {"state": "withheld"}},
            {"supported": {"state": "missing"}, "unsupported": {"state": "provided", "value": []}},
        ):
            with self.subTest(changes=changes):
                changed = record(changes)
                result = changed.evaluate(changed.scope, enabled=True, eligible_inputs=QUALIFIED,
                                          cohort_checked_only=True)["x_t0_support_result"]
                self.assertIsNone(result["decision"]["evidence_label"])

    def test_caller_provenance_is_recomputed_for_each_invocation_and_retained_in_context(self):
        query = record()
        for checked in (None, False, True, None):
            with self.subTest(checked=checked):
                result = query.evaluate(query.scope, enabled=True, eligible_inputs=QUALIFIED,
                                        cohort_checked_only=checked)
                value = result["x_t0_support_result"]
                self.assertEqual(value["decision"]["outcome"], "pass")
                self.assertTrue(value["decision"]["disputed"])
                self.assertIs(value["evaluation"]["cohort_checked_only"], checked)
                self.assertEqual(value["decision"]["evidence_label"], "unverified" if checked is True else None)
                self.assertEqual(query.verify_result(encoded(result), query.scope, enabled=True,
                                                     eligible_inputs=QUALIFIED, cohort_checked_only=checked), result)

    def test_source_strings_and_untrusted_answer_fields_cannot_qualify_themselves(self):
        for label in ("verified", "unverified", "user_supplied"):
            with self.subTest(label=label):
                direct = evaluate(frozenset({"gguf"}), replace(SOURCE, source_id=label))
                self.assertIsNone(direct.evidence_label)
                query = record({
                    "supported": {"state": "provided", "value": ["gguf"], "source": label},
                    "cohort_checked_only": {"state": "provided", "value": True},
                })
                result = query.evaluate(query.scope, enabled=True, eligible_inputs=QUALIFIED)["x_t0_support_result"]
                self.assertIsNone(result["evaluation"]["cohort_checked_only"])
                self.assertIsNone(result["decision"]["evidence_label"])

    def test_grade_and_context_tampering_cannot_validate_themselves(self):
        query = record()
        ungraded = query.evaluate(query.scope, enabled=True, eligible_inputs=QUALIFIED)
        for change_label, change_context in ((True, False), (False, True), (True, True)):
            forged = deepcopy(ungraded)
            value = forged["x_t0_support_result"]
            if change_label:
                value["decision"]["evidence_label"] = "unverified"
            if change_context:
                value["evaluation"]["cohort_checked_only"] = True
            with self.subTest(change_label=change_label, change_context=change_context):
                self.assertTrue(RESULT.is_valid(forged))
                with self.assertRaisesRegex(ValueError, "does not match retained inputs"):
                    query.verify_result(encoded(forged), query.scope, enabled=True, eligible_inputs=QUALIFIED)
        checked = query.evaluate(query.scope, enabled=True, eligible_inputs=QUALIFIED, cohort_checked_only=True)
        for actual in (None, False):
            with self.subTest(actual=actual), self.assertRaisesRegex(ValueError, "does not match retained inputs"):
                query.verify_result(encoded(checked), query.scope, enabled=True,
                                    eligible_inputs=QUALIFIED, cohort_checked_only=actual)
        forged = deepcopy(ungraded)
        forged["x_t0_support_result"]["decision"]["evidence_label"] = "verified"
        self.assertFalse(RESULT.is_valid(forged))

    def test_malformed_or_stronger_grade_inputs_are_rejected_before_shortcuts(self):
        query = record()
        for invalid in (0, 1, "unverified", "verified", [], {}):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, "normalized bool"):
                    evaluate(None, replace(SOURCE, checked_only=invalid), applicable=False)
                with self.assertRaisesRegex(ValueError, "checked-only qualification"):
                    query.evaluate(None, enabled=False, cohort_checked_only=invalid)


if __name__ == "__main__":
    unittest.main()
