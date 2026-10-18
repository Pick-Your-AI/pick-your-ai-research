"""Synthetic terminal CD-1 rule outcomes; no real claims or released rules."""

from dataclasses import FrozenInstanceError
import json
import unittest

from tests.selection_quantifier_prototype import Outcome
from tests.t0_answer_state_prototype import (
    AnswerIndex, AnswerRule, PredicateResult, RulePolicy, State, evaluate_answer_rule,
)


FIELD = "/workload/network"
SCHEMA = {"type": "string", "enum": ["online", "private_network", "air_gapped"]}
SEVERITIES = ("info", "warning", "error")
STATES = ("withheld", "unknown", "missing", "not_applicable", "absent")


def answer(state, *, value="air_gapped", path="/workload"):
    record = {"state": state}
    if state == "provided":
        record["value"] = { "network": value } if path == "/workload" else value
    raw = json.dumps({
        "x_t0_answer_states": {
            "proposal_version": "cd1-0.1",
            "answers": {} if state == "absent" else {path: record},
        },
    }).encode()
    return AnswerIndex(raw), raw


def fact(value, path="/synthetic/known"):
    return PredicateResult(State.PROVIDED, value, path)


def rule(applicability, assertion, policy=RulePolicy.COMPATIBILITY, severity="error"):
    return AnswerRule("synthetic.cd1.outcome", severity, policy, applicability, assertion)


class AnswerRuleOutcomeCases(unittest.TestCase):
    def test_unresolved_applicability_preserves_each_reason_path_and_rule_policy(self):
        for policy in RulePolicy:
            for severity in SEVERITIES:
                for state in STATES:
                    with self.subTest(policy=policy, severity=severity, state=state):
                        answers, original = answer(state)
                        value_calls, assertion_calls = [], []
                        result = evaluate_answer_rule(rule(
                            lambda: answers.predicate(
                                FIELD, SCHEMA, lambda v: value_calls.append(v) or True),
                            lambda: assertion_calls.append("asserted") or fact(False),
                            policy, severity,
                        ))
                        normalized = "missing" if state == "absent" else state
                        expected = (Outcome.SKIPPED
                                    if state == "not_applicable" or policy is RulePolicy.RECOMMENDATION
                                    else Outcome.UNKNOWN)
                        self.assertEqual(result.outcome, expected)
                        self.assertEqual(result.reason, "answer_" + normalized)
                        self.assertEqual(result.answer_state, State(normalized))
                        self.assertEqual(result.source_path, None if state == "absent" else "/workload")
                        self.assertEqual(result.position, "applies_when")
                        self.assertEqual(result.severity, severity)
                        self.assertEqual(result.rule_id, "synthetic.cd1.outcome")
                        self.assertEqual(value_calls, [])
                        self.assertEqual(assertion_calls, [])
                        self.assertEqual(answers.read(FIELD, SCHEMA).state, State(normalized))
                        self.assertEqual(json.loads(original)["x_t0_answer_states"]["proposal_version"], "cd1-0.1")

    def test_unresolved_assertions_keep_their_state_in_both_policies(self):
        for policy in RulePolicy:
            for severity in SEVERITIES:
                for state in STATES:
                    with self.subTest(policy=policy, severity=severity, state=state):
                        answers, _ = answer(state)
                        calls = []
                        result = evaluate_answer_rule(rule(
                            lambda: fact(True),
                            lambda: answers.predicate(
                                FIELD, SCHEMA, lambda v: calls.append(v) or True),
                            policy, severity,
                        ))
                        normalized = "missing" if state == "absent" else state
                        self.assertEqual(result.outcome, Outcome.SKIPPED
                                         if state == "not_applicable" else Outcome.UNKNOWN)
                        self.assertEqual(result.reason, "answer_" + normalized)
                        self.assertEqual(result.answer_state, State(normalized))
                        self.assertEqual(result.source_path, None if state == "absent" else "/workload")
                        self.assertEqual(result.position, "assertion")
                        self.assertEqual(result.severity, severity)
                        self.assertEqual(calls, [])

    def test_not_applicable_and_known_false_applicability_have_different_reasons(self):
        for policy in RulePolicy:
            answers, _ = answer("not_applicable")
            for assertion_position in (False, True):
                with self.subTest(policy=policy, assertion_position=assertion_position):
                    not_applicable = lambda: answers.predicate(FIELD, SCHEMA, lambda _: True)
                    skipped = evaluate_answer_rule(rule(
                        (lambda: fact(True)) if assertion_position else not_applicable,
                        not_applicable if assertion_position else lambda: fact(True),
                        policy,
                    ))
                    false_gate = evaluate_answer_rule(rule(lambda: fact(False), lambda: fact(True), policy))
                    self.assertEqual(skipped.outcome, Outcome.SKIPPED)
                    self.assertEqual(skipped.reason, "answer_not_applicable")
                    self.assertEqual(skipped.answer_state, State.NOT_APPLICABLE)
                    self.assertEqual(false_gate.outcome, Outcome.SKIPPED)
                    self.assertEqual(false_gate.reason, "applicability_false")
                    self.assertEqual(false_gate.answer_state, State.PROVIDED)
                    self.assertNotEqual(skipped.reason, false_gate.reason)

    def test_known_conditions_evaluate_assertion_once_only_when_true(self):
        for policy in RulePolicy:
            for applicable in (True, False, None):
                for asserted in (True, False, None):
                    with self.subTest(policy=policy, applicable=applicable, asserted=asserted):
                        calls = []
                        result = evaluate_answer_rule(rule(
                            lambda: calls.append("applicability") or fact(applicable, "/need"),
                            lambda: calls.append("assertion") or fact(asserted, "/support"),
                            policy, "warning",
                        ))
                        if applicable is False:
                            expected = (Outcome.SKIPPED, "applicability_false", "applies_when", "/need")
                        elif applicable is None:
                            expected = (Outcome.UNKNOWN, "predicate_unknown", "applies_when", "/need")
                        elif asserted is None:
                            expected = (Outcome.UNKNOWN, "predicate_unknown", "assertion", "/support")
                        else:
                            expected = (Outcome.PASS if asserted else Outcome.FAIL,
                                        "assertion_true" if asserted else "assertion_false",
                                        "assertion", "/support")
                        self.assertEqual((result.outcome, result.reason, result.position, result.source_path), expected)
                        self.assertEqual(result.answer_state, State.PROVIDED)
                        self.assertEqual(result.severity, "warning")
                        self.assertEqual(calls, ["applicability", "assertion"]
                                         if applicable is True else ["applicability"])

    def test_provided_but_unresolved_predicate_is_not_an_unanswered_input(self):
        for policy in RulePolicy:
            for assertion_position in (False, True):
                answers, _ = answer("provided")
                calls = []
                uncertain = lambda: answers.predicate(FIELD, SCHEMA, lambda v: calls.append(v) or None)
                result = evaluate_answer_rule(rule(
                    (lambda: fact(True)) if assertion_position else uncertain,
                    uncertain if assertion_position else lambda: fact(False),
                    policy,
                ))
                with self.subTest(policy=policy, assertion_position=assertion_position):
                    self.assertEqual(result.outcome, Outcome.UNKNOWN)
                    self.assertEqual(result.reason, "predicate_unknown")
                    self.assertEqual(result.answer_state, State.PROVIDED)
                    self.assertEqual(result.source_path, "/workload")
                    self.assertEqual(calls, ["air_gapped"])

    def test_safe_negation_preserves_unresolved_reasons_and_known_controls(self):
        for policy in RulePolicy:
            for state in STATES:
                answers, _ = answer(state)
                predicate = answers.predicate(FIELD, SCHEMA, lambda _: True)
                for negated in (predicate.negated(), predicate.negated().negated()):
                    with self.subTest(policy=policy, state=state, negated=negated):
                        result = evaluate_answer_rule(rule(lambda: fact(True), lambda: negated, policy))
                        self.assertEqual(result.outcome, Outcome.SKIPPED
                                         if state == "not_applicable" else Outcome.UNKNOWN)
                        self.assertEqual(result.reason, "answer_" + ("missing" if state == "absent" else state))
                        self.assertEqual(result.source_path, predicate.source_path)
                        self.assertEqual(result.answer_state, predicate.state)
        for value, expected in ((True, Outcome.FAIL), (False, Outcome.PASS), (None, Outcome.UNKNOWN)):
            calls = []
            answers, _ = answer("provided")
            predicate = answers.predicate(FIELD, SCHEMA, lambda v: calls.append(v) or value)
            negated = predicate.negated()
            result = evaluate_answer_rule(rule(lambda: fact(True), lambda: negated))
            self.assertEqual(result.outcome, expected)
            self.assertEqual(calls, ["air_gapped"])
            self.assertEqual(negated.negated(), predicate)

    def test_callback_values_are_not_coerced_or_accepted_as_predicates(self):
        for invalid in (None, True, False, 0, 1, "unknown", [], {}):
            for assertion_position in (False, True):
                with self.subTest(invalid=invalid, assertion_position=assertion_position):
                    candidate = rule(
                        (lambda: fact(True)) if assertion_position else lambda: invalid,
                        (lambda: invalid) if assertion_position else lambda: fact(True),
                    )
                    with self.assertRaisesRegex(ValueError, "PredicateResult"):
                        evaluate_answer_rule(candidate)

    def test_bad_rule_metadata_is_rejected_before_any_predicate_runs(self):
        calls = []
        callback = lambda: calls.append("called") or fact(True)
        for field, value in (
            ("id", ""), ("id", " "), ("id", True), ("severity", "fatal"),
            ("severity", True), ("severity", None), ("policy", "compatibility"),
            ("policy", None), ("applies_when", fact(True)), ("assertion", None),
        ):
            with self.subTest(field=field, value=value):
                values = dict(id="synthetic.rule", severity="error", policy=RulePolicy.COMPATIBILITY,
                              applies_when=callback, assertion=callback)
                values[field] = value
                with self.assertRaises(ValueError):
                    AnswerRule(**values)
                self.assertEqual(calls, [])
        with self.assertRaisesRegex(ValueError, "typed answer rule"):
            evaluate_answer_rule(None)

    def test_unneeded_assertion_exceptions_are_not_triggered_and_needed_ones_propagate(self):
        def failure():
            raise RuntimeError("synthetic assertion failure")
        for policy in RulePolicy:
            for state in STATES:
                answers, _ = answer(state)
                result = evaluate_answer_rule(rule(
                    lambda: answers.predicate(FIELD, SCHEMA, lambda _: True), failure, policy,
                ))
                self.assertIn(result.outcome, (Outcome.UNKNOWN, Outcome.SKIPPED))
            self.assertEqual(evaluate_answer_rule(rule(lambda: fact(False), failure, policy)).outcome,
                             Outcome.SKIPPED)
            with self.assertRaisesRegex(RuntimeError, "synthetic assertion failure"):
                evaluate_answer_rule(rule(lambda: fact(True), failure, policy))
            with self.assertRaisesRegex(RuntimeError, "synthetic assertion failure"):
                evaluate_answer_rule(rule(failure, lambda: fact(True), policy))

    def test_final_outcomes_reject_boolean_shortcuts_and_remain_immutable(self):
        for predicate in (fact(True), fact(False), fact(None),
                          PredicateResult(State.NOT_APPLICABLE, None, "/not-applicable")):
            result = evaluate_answer_rule(rule(lambda: fact(True), lambda: predicate))
            for operation in (bool, lambda r: not r, lambda r: r and True, lambda r: r or True):
                with self.subTest(outcome=result.outcome, operation=operation):
                    with self.assertRaisesRegex(TypeError, "Boolean"):
                        operation(result)
            with self.assertRaises(FrozenInstanceError):
                result.reason = "synthetic-mutated"
            with self.assertRaises(FrozenInstanceError):
                result.severity = "info"

    def test_exact_escaped_source_path_and_original_answer_bytes_are_preserved(self):
        path = "/workload/a~1b~0c"
        answers, raw = answer("withheld", path=path)
        before = bytes(raw)
        result = evaluate_answer_rule(rule(
            lambda: fact(True),
            lambda: answers.predicate(path, SCHEMA, lambda _: True),
        ))
        self.assertEqual(result.source_path, path)
        self.assertEqual(result.answer_state, State.WITHHELD)
        self.assertEqual(result.reason, "answer_withheld")
        self.assertEqual(raw, before)
        self.assertIsNone(answers.read(path, SCHEMA).value)
        self.assertNotIn("value", result.__dataclass_fields__)


if __name__ == "__main__":
    unittest.main()
