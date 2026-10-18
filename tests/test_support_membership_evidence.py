"""Synthetic CD-3 labels: no vendor fact, source authentication or adoption."""

from dataclasses import asdict
import itertools
import json
from pathlib import Path
import unittest

from tests.support_membership_binding_prototype import (
    ELIGIBILITY, SCHEMA as HISTORICAL_SCHEMA, SupportQueryRecord, answer_path, digest,
)
from tests.support_membership_evidence_prototype import (
    RESULT, SCHEMA, WIRE, SupportEvidenceQueryRecord, evaluate,
)
from tests.support_membership_prototype import Evidence, Outcome, Requirement, evaluate as historical


FIXTURES = Path(__file__).with_name("fixtures")
BINDING_RAW = (FIXTURES / "support-membership-evidence-binding.json").read_bytes()
ANSWERS_RAW = (FIXTURES / "support-membership-evidence-answers.json").read_bytes()
RESULT_RAW = (FIXTURES / "support-membership-evidence-result.json").read_bytes()
QUALIFIED = dict.fromkeys(ELIGIBILITY, True)
STATES = ("unknown", "missing", "withheld", "not_applicable")


def encode(value):
    return (json.dumps(value, indent=2, allow_nan=False) + "\n").encode("utf-8")


class EvidenceLabelTests(unittest.TestCase):
    def test_original_no_evidence_counterexamples_have_no_successor_label(self):
        ordinary = Evidence("synthetic:cohort", True, frozenset({"a"}))
        cases = (
            (frozenset({"a"}), ordinary, {"applicable": False}, "skipped", "not_applicable"),
            (frozenset({"a"}), ordinary, {"applicable": None}, "unknown", "applicability_unknown"),
            (None, ordinary, {}, "unknown", "requirement_unknown"),
            (frozenset(), ordinary, {}, "unknown", "requirement_empty"),
            (frozenset({"a"}), Evidence("synthetic:cohort", False, frozenset({"a"})),
             {}, "unknown", "no_eligible_evidence"),
            (frozenset({"a"}), Evidence("synthetic:cohort", True, None), {}, "unknown", "any_membership"),
            (frozenset({"a"}), Evidence("synthetic:cohort", True, frozenset()),
             {}, "unknown", "any_membership"),
        )
        for requested, evidence, context, outcome, reason in cases:
            with self.subTest(reason=reason, evidence=evidence):
                original = historical(requested, evidence, **context)
                self.assertEqual(original.evidence_label, "unverified")
                result = evaluate(requested, evidence, cohort_checked_only=True, **context)
                self.assertEqual((result.outcome, result.reason), (outcome, reason))
                self.assertIsNone(result.evidence_label)
                self.assertTrue(all(f.evidence_label is None for f in result.findings))

    def test_checked_only_member_claims_have_individually_scoped_labels(self):
        cases = (
            (frozenset({"a"}), frozenset(), None, "pass", "documented_member", "unverified"),
            (None, frozenset({"a"}), None, "fail", "explicit_unsupported", "unverified"),
            (frozenset(), frozenset(), True, "fail", "exhaustive_absence", "unverified"),
            (frozenset({"a"}), frozenset({"a"}), True, "unknown", "opposite_equal_rank_claims", "unverified"),
            (None, frozenset(), True, "unknown", "support_list_missing", None),
            (frozenset(), frozenset(), False, "unknown", "unmarked_absence", None),
        )
        for supported, unsupported, exhaustive, outcome, reason, label in cases:
            with self.subTest(reason=reason):
                result = evaluate(frozenset({"a"}), Evidence("synthetic:cohort", True,
                    supported, exhaustive, unsupported), requested_complete=True, cohort_checked_only=True)
                self.assertEqual((result.outcome, result.reason), (outcome, "any_membership"))
                finding, = result.findings
                self.assertEqual((finding.reason, finding.evidence_label), (reason, label))
                self.assertEqual(finding.disputed, reason == "opposite_equal_rank_claims")
                self.assertEqual(result.evidence_label, "unverified" if outcome in ("pass", "fail") else None)

    def test_eligibility_and_source_labels_do_not_supply_checked_only_qualification(self):
        for source, flag in itertools.product(("unverified", "verified", "synthetic:checked-only"),
                                               (False, None)):
            with self.subTest(source=source, flag=flag):
                evidence = Evidence(source, True, frozenset({"a"}))
                result = evaluate(frozenset({"a"}), evidence, cohort_checked_only=flag)
                self.assertEqual(result.outcome, Outcome.PASS)
                self.assertIsNone(result.evidence_label)
                self.assertIsNone(result.findings[0].evidence_label)
                self.assertEqual(result.source_id, source)
        self.assertIsNone(evaluate(frozenset({"a"}), evidence).evidence_label)

    def test_checked_only_qualification_cannot_admit_an_ineligible_cohort(self):
        for eligible in (False, None):
            result = evaluate(frozenset({"a"}), Evidence("synthetic:cohort", eligible,
                              frozenset({"a"})), cohort_checked_only=True)
            self.assertEqual((result.outcome, result.reason), ("unknown", "no_eligible_evidence"))
            self.assertEqual(result.findings, ())
            self.assertIsNone(result.evidence_label)

    def test_unresolved_requested_completeness_preserves_only_member_labels(self):
        for requirement, complete in itertools.product(Requirement, (False, None)):
            evidence = Evidence("synthetic:cohort", True,
                frozenset({"a"}) if requirement is Requirement.ALL else frozenset(),
                True)
            result = evaluate(frozenset({"a"}), evidence, requirement,
                              requested_complete=complete, cohort_checked_only=True)
            self.assertEqual(result.outcome, Outcome.UNKNOWN)
            self.assertEqual(result.reason, "requested_set_incomplete" if complete is False
                             else "requested_completeness_unknown")
            self.assertIsNone(result.evidence_label)
            self.assertEqual(result.findings[0].evidence_label, "unverified")

    def test_any_witness_and_all_counterexample_keep_unknown_and_disputed_members(self):
        evidence = Evidence("synthetic:cohort", True, frozenset({"yes", "dispute"}),
                            False, frozenset({"no", "dispute"}))
        results = [evaluate(frozenset({"yes", "no", "dispute", "absent"}), evidence,
                            requirement, requested_complete=None, cohort_checked_only=True)
                   for requirement in Requirement]
        self.assertEqual([r.outcome for r in results], [Outcome.PASS, Outcome.FAIL])
        self.assertEqual(results[0].findings, results[1].findings)
        self.assertEqual([(f.value, f.evidence_label) for f in results[0].findings],
                         [("absent", None), ("dispute", "unverified"),
                          ("no", "unverified"), ("yes", "unverified")])
        self.assertTrue(all(r.disputed and r.evidence_label == "unverified" for r in results))

    def test_malformed_grade_is_rejected_before_disabled_or_unknown_shortcuts(self):
        for flag, applicable in itertools.product((0, 1, 1.0, "true", "unverified", [], {}),
                                                  (False, None, True)):
            with self.subTest(flag=flag, applicable=applicable):
                with self.assertRaisesRegex(ValueError, "normalized bool or None"):
                    evaluate(None, Evidence("synthetic:cohort", None, None),
                             applicable=applicable, cohort_checked_only=flag)

    def test_successor_does_not_change_membership_or_requested_completeness_semantics(self):
        sets = (frozenset(), frozenset({"a"}), frozenset({"b"}), frozenset({"a", "b"}))
        for requested, eligible, supported, exhaustive, unsupported, requirement, complete in itertools.product(
                (None, *sets), (False, None, True), (None, *sets), (False, None, True),
                sets, Requirement, (False, None, True)):
            evidence = Evidence("synthetic:cohort", eligible, supported, exhaustive, unsupported)
            expected = asdict(historical(requested, evidence, requirement, requested_complete=complete))
            del expected["evidence_label"]
            for flag in (False, None, True):
                actual = asdict(evaluate(requested, evidence, requirement,
                                        requested_complete=complete, cohort_checked_only=flag))
                del actual["evidence_label"]
                for finding in actual["findings"]:
                    del finding["evidence_label"]
                self.assertEqual(actual, expected)


class EvidenceBindingTests(unittest.TestCase):
    def setUp(self):
        self.binding = json.loads(BINDING_RAW)
        self.proposal = self.binding["x_t0_support_query"]
        self.answers = json.loads(ANSWERS_RAW)
        self.values = self.answers["x_t0_answer_states"]["answers"]

    def fact(self, field, value=None, *, state="provided"):
        self.values[answer_path(self.proposal, field)] = (
            {"state": state, "value": value} if state == "provided" else {"state": state})

    def record(self):
        answers = encode(self.answers)
        self.proposal["answer_states_sha256"] = digest(answers)
        return SupportEvidenceQueryRecord(encode(self.binding), answers)

    def result(self, **context):
        record = self.record()
        return record.evaluate(record.scope, **{
            "enabled": True, "eligible_inputs": QUALIFIED, "cohort_checked_only": True, **context,
        })["x_t0_support_result"]

    def test_versioned_fixture_replays_with_explicit_current_caller_qualification(self):
        WIRE.check_schema(SCHEMA)
        WIRE.validate(json.loads(BINDING_RAW))
        RESULT.validate(json.loads(RESULT_RAW))
        record = SupportEvidenceQueryRecord(BINDING_RAW, ANSWERS_RAW)
        actual = record.verify_result(RESULT_RAW, record.scope, enabled=True,
                                      eligible_inputs=QUALIFIED, cohort_checked_only=True)
        self.assertEqual(actual, json.loads(RESULT_RAW))
        self.assertEqual(record.original_bytes, (BINDING_RAW, ANSWERS_RAW))
        result = actual["x_t0_support_result"]
        self.assertEqual(result["proposal_version"], "cd3-0.3")
        self.assertEqual(result["query"]["version"], "0.3.0")
        self.assertEqual(result["query"]["severity"], "error")
        self.assertEqual(result["decision"]["evidence_label"], "unverified")
        self.assertEqual([f["evidence_label"] for f in result["decision"]["findings"]],
                         [None, "unverified", "unverified"])

    def test_historical_profile_remains_explicit_and_replays_its_original_result(self):
        old_binding = (FIXTURES / "support-membership-binding.json").read_bytes()
        old_answers = (FIXTURES / "support-membership-answers.json").read_bytes()
        old_result = (FIXTURES / "support-membership-result.json").read_bytes()
        record = SupportQueryRecord(old_binding, old_answers)
        self.assertEqual(record.verify_result(old_result, record.scope, enabled=True,
                         eligible_inputs=QUALIFIED), json.loads(old_result))
        self.assertEqual(record.evaluate(None, enabled=False)["x_t0_support_result"]
                         ["decision"]["evidence_label"], "unverified")
        for reader, binding, answers in ((SupportQueryRecord, BINDING_RAW, ANSWERS_RAW),
                                         (SupportEvidenceQueryRecord, old_binding, old_answers)):
            with self.assertRaisesRegex(ValueError, "invalid CD-3 query"):
                reader(binding, answers)

    def test_new_profile_preserves_all_input_and_scope_guards(self):
        changed_definitions = {"finding", "decision", "result"}
        self.assertEqual(SCHEMA.keys(), HISTORICAL_SCHEMA.keys())
        for name in SCHEMA["$defs"]:
            if name not in changed_definitions:
                self.assertEqual(SCHEMA["$defs"][name], HISTORICAL_SCHEMA["$defs"][name])

    def test_new_query_does_not_fall_back_to_historical_answer_paths(self):
        self.values.clear()
        self.values.update(json.loads((FIXTURES / "support-membership-answers.json")
                           .read_bytes())["x_t0_answer_states"]["answers"])
        result = self.result()
        self.assertEqual(result["decision"]["reason"], "applicability_unknown")
        self.assertIsNone(result["decision"]["evidence_label"])
        self.assertTrue(all(value == {"state": "missing"} for value in result["inputs"].values()))

    def test_omitted_or_false_grade_is_not_inferred_from_source_or_eligibility(self):
        record = SupportEvidenceQueryRecord(BINDING_RAW, ANSWERS_RAW)
        for flag in (False, None):
            result = self.result(cohort_checked_only=flag)
            self.assertEqual(result["decision"]["outcome"], "pass")
            self.assertIs(result["evaluation"]["cohort_checked_only"], flag)
            self.assertIsNone(result["decision"]["evidence_label"])
            self.assertTrue(all(f["evidence_label"] is None for f in result["decision"]["findings"]))
        implicit = record.evaluate(record.scope, enabled=True, eligible_inputs=QUALIFIED)
        self.assertIsNone(implicit["x_t0_support_result"]["decision"]["evidence_label"])

    def test_skipped_unknown_scope_and_each_ineligible_input_are_unlabeled(self):
        record = self.record()
        cases = [(False, record.scope, QUALIFIED, "selection_not_enabled"),
                 (None, record.scope, QUALIFIED, "selection_activation_unknown"),
                 (True, None, QUALIFIED, "selection_scope_missing")]
        mismatch = record.scope; mismatch["item"]["version"] += "-other"
        cases.append((True, mismatch, QUALIFIED, "support_scope_mismatch"))
        for field, flag in itertools.product(("applies_when", "requested", "cohort"), (False, None)):
            cases.append((True, record.scope, {**QUALIFIED, field: flag},
                          field + ("_evidence_unresolved" if flag is None else "_evidence_ineligible")))
        for enabled, selected, flags, reason in cases:
            with self.subTest(reason=reason):
                result = record.evaluate(selected, enabled=enabled, eligible_inputs=flags,
                                         cohort_checked_only=True)["x_t0_support_result"]
                self.assertEqual(result["decision"]["reason"], reason)
                self.assertIsNone(result["decision"]["evidence_label"])
                self.assertEqual(result["decision"]["findings"], [])
                self.assertEqual(len(result["inputs"]), 6)

    def test_each_unresolved_required_operand_and_known_inapplicability_have_no_label(self):
        for field, state in itertools.product(("applies_when", "requested", "unsupported"), STATES):
            with self.subTest(field=field, state=state):
                self.setUp(); self.fact(field, state=state)
                result = self.result()
                self.assertEqual(result["decision"]["outcome"], "unknown")
                self.assertEqual(result["inputs"][field]["state"], state)
                self.assertIsNone(result["decision"]["evidence_label"])
                self.assertEqual(result["decision"]["findings"], [])
        self.setUp(); self.fact("applies_when", False)
        result = self.result()
        self.assertEqual(result["decision"]["outcome"], "skipped")
        self.assertIsNone(result["decision"]["evidence_label"])

    def test_empty_missing_unmarked_and_disputed_cohorts_have_no_aggregate_grade(self):
        self.fact("requested", [])
        self.assertIsNone(self.result()["decision"]["evidence_label"])
        for state in ("provided", *STATES):
            with self.subTest(state=state):
                self.setUp(); self.fact("requested", ["a"]); self.fact("unsupported", [])
                self.fact("supported", [], state=state)
                result = self.result()
                self.assertEqual(result["decision"]["outcome"], "unknown")
                self.assertIsNone(result["decision"]["evidence_label"])
                self.assertIsNone(result["decision"]["findings"][0]["evidence_label"])
        self.setUp(); self.fact("requested", ["gguf"])
        result = self.result()
        self.assertIsNone(result["decision"]["evidence_label"])
        self.assertEqual(result["decision"]["findings"][0]["evidence_label"], "unverified")
        self.assertTrue(result["decision"]["disputed"])

    def test_requested_completeness_does_not_grade_an_unknown_aggregate(self):
        for requirement, state, flag in itertools.product(("any", "all"), STATES, (False, None, True)):
            with self.subTest(requirement=requirement, state=state, flag=flag):
                self.setUp(); self.proposal["query"]["requirement"] = requirement
                self.fact("requested", ["a"])
                self.fact("supported", ["a"] if requirement == "all" else [])
                self.fact("unsupported", ["a"] if requirement == "any" else [])
                self.fact("requested_complete", state=state)
                result = self.result(eligible_inputs={**QUALIFIED, "requested_complete": flag})
                self.assertEqual(result["decision"]["reason"], "requested_completeness_unknown")
                self.assertIsNone(result["decision"]["evidence_label"])
                self.assertEqual(result["decision"]["findings"][0]["evidence_label"], "unverified")

    def test_caller_grade_must_be_an_exact_boolean_or_null_even_when_disabled(self):
        record = self.record()
        for flag in (0, 1, 1.0, "true", "unverified", [], {}):
            with self.subTest(flag=flag):
                with self.assertRaisesRegex(ValueError, "normalized bool or None"):
                    record.evaluate(None, enabled=False, cohort_checked_only=flag)
                with self.assertRaisesRegex(ValueError, "normalized bool or None"):
                    record.verify_result(RESULT_RAW, record.scope, enabled=True,
                                         eligible_inputs=QUALIFIED, cohort_checked_only=flag)

    def test_malformed_provided_facts_still_reject_before_any_evaluation(self):
        for field, value in (("requested_complete", 1), ("exhaustive", "true"),
                             ("requested", "gguf"), ("supported", ["a", "a"]),
                             ("unsupported", [None])):
            with self.subTest(field=field):
                self.setUp(); self.fact("applies_when", False); self.fact(field, value)
                with self.assertRaisesRegex(ValueError, "invalid provided value"):
                    self.record()

    def test_recorded_qualification_cannot_supply_the_callers_missing_grade(self):
        record = SupportEvidenceQueryRecord(BINDING_RAW, ANSWERS_RAW)
        for flag in (False, None):
            with self.assertRaisesRegex(ValueError, "does not match retained inputs"):
                record.verify_result(RESULT_RAW, record.scope, enabled=True,
                                     eligible_inputs=QUALIFIED, cohort_checked_only=flag)
        with self.assertRaisesRegex(ValueError, "does not match retained inputs"):
            record.verify_result(RESULT_RAW, record.scope, enabled=True, eligible_inputs=QUALIFIED)
        # Caller context remains bound even when neither invocation earns a label.
        ungraded = record.evaluate(None, enabled=False, cohort_checked_only=True)
        with self.assertRaisesRegex(ValueError, "does not match retained inputs"):
            record.verify_result(encode(ungraded), None, enabled=False, cohort_checked_only=None)

    def test_schema_valid_grade_and_identity_forgeries_fail_recomputation(self):
        record = SupportEvidenceQueryRecord(BINDING_RAW, ANSWERS_RAW)
        mutations = (
            lambda r: r["evaluation"].update(cohort_checked_only=None),
            lambda r: r["evaluation"].update(cohort_checked_only=False),
            lambda r: r["decision"].update(evidence_label=None),
            lambda r: r["decision"]["findings"][0].update(evidence_label="unverified"),
            lambda r: r["decision"]["findings"][1].update(evidence_label=None),
            lambda r: r["decision"]["findings"][2].update(evidence_label=None),
            lambda r: r["evaluation"]["eligible_inputs"].update(cohort=False),
            lambda r: r["inputs"]["supported"].update(source="verified"),
            lambda r: r.update(binding_sha256="0" * 64),
            lambda r: r["scope"]["item"].update(version="other"),
        )
        for mutate in mutations:
            result = json.loads(RESULT_RAW); mutate(result["x_t0_support_result"])
            with self.subTest(result=result):
                self.assertTrue(RESULT.is_valid(result))
                with self.assertRaisesRegex(ValueError, "does not match retained inputs"):
                    record.verify_result(encode(result), record.scope, enabled=True,
                                         eligible_inputs=QUALIFIED, cohort_checked_only=True)

    def test_closed_wire_rejects_missing_labels_and_invented_grades(self):
        record = SupportEvidenceQueryRecord(BINDING_RAW, ANSWERS_RAW)
        mutations = (
            lambda r: r["evaluation"].pop("cohort_checked_only"),
            lambda r: r["evaluation"].update(cohort_checked_only=1),
            lambda r: r["decision"].pop("evidence_label"),
            lambda r: r["decision"]["findings"][0].pop("evidence_label"),
            lambda r: r["decision"].update(evidence_label="verified"),
            lambda r: r["decision"]["findings"][0].update(evidence_label="estimated"),
            lambda r: r["decision"]["findings"][0].update(evidence_label=False),
            lambda r: r.update(proposal_version="cd3-0.2"),
            lambda r: r["evaluation"].update(verified=True),
        )
        for mutate in mutations:
            result = json.loads(RESULT_RAW); mutate(result["x_t0_support_result"])
            with self.subTest(result=result):
                self.assertFalse(RESULT.is_valid(result))
                with self.assertRaisesRegex(ValueError, "invalid CD-3 result"):
                    record.verify_result(encode(result), record.scope, enabled=True,
                                         eligible_inputs=QUALIFIED, cohort_checked_only=True)

    def test_original_bytes_are_bound_but_result_whitespace_is_not(self):
        with self.assertRaisesRegex(ValueError, "answer bytes do not match"):
            SupportEvidenceQueryRecord(BINDING_RAW, ANSWERS_RAW + b"\n")
        record = SupportEvidenceQueryRecord(BINDING_RAW + b"\n", ANSWERS_RAW)
        with self.assertRaisesRegex(ValueError, "does not match retained inputs"):
            record.verify_result(RESULT_RAW, record.scope, enabled=True,
                                 eligible_inputs=QUALIFIED, cohort_checked_only=True)
        record = SupportEvidenceQueryRecord(BINDING_RAW, ANSWERS_RAW)
        reformatted = json.dumps(json.loads(RESULT_RAW), sort_keys=True).encode()
        self.assertEqual(record.verify_result(reformatted, record.scope, enabled=True,
                         eligible_inputs=QUALIFIED, cohort_checked_only=True), json.loads(RESULT_RAW))

    def test_duplicate_keys_nonfinite_and_invalid_unicode_still_reject(self):
        record = SupportEvidenceQueryRecord(BINDING_RAW, ANSWERS_RAW)
        for raw in (b'{"x":1,"x":1}', b'{"x":NaN}', b'{"x":1e999}', b'{"x":"\\ud800"}', b'\xff'):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError): SupportEvidenceQueryRecord(raw, ANSWERS_RAW)
                with self.assertRaises(ValueError):
                    record.verify_result(raw, record.scope, enabled=True,
                                         eligible_inputs=QUALIFIED, cohort_checked_only=True)

    def test_returned_grade_context_and_findings_are_detached(self):
        record = SupportEvidenceQueryRecord(BINDING_RAW, ANSWERS_RAW)
        actual = record.evaluate(record.scope, enabled=True, eligible_inputs=QUALIFIED,
                                 cohort_checked_only=True)
        edited = actual["x_t0_support_result"]
        edited["evaluation"]["cohort_checked_only"] = False
        edited["evaluation"]["eligible_inputs"]["cohort"] = False
        edited["decision"]["findings"][2]["evidence_label"] = None
        edited["inputs"]["supported"]["value"].clear()
        self.assertEqual(record.evaluate(record.scope, enabled=True, eligible_inputs=QUALIFIED,
                         cohort_checked_only=True), json.loads(RESULT_RAW))


if __name__ == "__main__":
    unittest.main()
