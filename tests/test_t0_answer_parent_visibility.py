import itertools
import json
import unittest

from tests.selection_quantifier_prototype import Outcome
from tests.t0_answer_state_prototype import (
    AnswerIndex, AnswerRule, PredicateResult, RulePolicy, State, evaluate_answer_rule,
)


def encoded(answers):
    return json.dumps({"x_t0_answer_states": {"proposal_version": "cd1-0.1", "answers": answers}}).encode()


class WithheldParentVisibility(unittest.TestCase):
    def test_unrecorded_parent_preserves_withheld_child_reason_and_real_source_path(self):
        raw = encoded({"/synthetic/account/private": {"state": "withheld"}})
        index = AnswerIndex(raw)
        for path in ("/synthetic", "/synthetic/account"):
            with self.subTest(path=path):
                answer = index.read(path, {"type": "object"})
                self.assertEqual(answer.state, State.WITHHELD)
                self.assertEqual(answer.source_path, "/synthetic/account/private")
                self.assertIsNone(answer.value)
                self.assertIsNone(answer.source)
                self.assertFalse(answer.provided)

    def test_multiple_withheld_witnesses_are_deterministic_without_assembling_parent(self):
        entries = [
            ("/synthetic/account/z", {"state": "withheld"}),
            ("/synthetic/account/a", {"state": "withheld"}),
            ("/synthetic/account/name", {"state": "provided", "value": "synthetic"}),
        ]
        for order in itertools.permutations(entries):
            with self.subTest(order=[path for path, _ in order]):
                answer = AnswerIndex(encoded(dict(order))).read("/synthetic/account", {"type": "object"})
                self.assertEqual(answer.state, State.WITHHELD)
                self.assertEqual(answer.source_path, "/synthetic/account/a")
                self.assertIsNone(answer.value)

    def test_decoded_pointer_segments_do_not_capture_unrelated_prefixes(self):
        index = AnswerIndex(encoded({
            "/synthetic/a~1b/private": {"state": "withheld"},
            "/synthetic/~01/private": {"state": "withheld"},
            "//private": {"state": "withheld"},
        }))
        for path, source in (("/synthetic/a~1b", "/synthetic/a~1b/private"),
                             ("/synthetic/~01", "/synthetic/~01/private"),
                             ("/", "//private")):
            with self.subTest(path=path):
                answer = index.read(path, {})
                self.assertEqual(answer.state, State.WITHHELD)
                self.assertEqual(answer.source_path, source)
        for path in ("/synthetic/a", "/synthetic/a~1bc", "/synthetic/~1", "/other"):
            with self.subTest(path=path):
                answer = index.read(path, {})
                self.assertEqual(answer.state, State.MISSING)
                self.assertIsNone(answer.source_path)

    def test_child_and_sibling_reads_retain_their_own_values_and_states(self):
        raw = encoded({
            "/synthetic/account/private": {"state": "withheld"},
            "/synthetic/account/count": {"state": "provided", "value": 0},
            "/synthetic/accounting": {"state": "provided", "value": False},
            "/provided/child": {"state": "provided", "value": "withheld"},
        })
        index = AnswerIndex(raw)
        self.assertEqual(index.read("/synthetic/account/private", {}).source_path, "/synthetic/account/private")
        self.assertEqual(index.read("/synthetic/account/count", {"type": "integer"}).value, 0)
        self.assertIs(index.read("/synthetic/accounting", {"type": "boolean"}).value, False)
        self.assertEqual(index.read("/provided/child", {"type": "string"}).value, "withheld")
        self.assertEqual(index.read("/provided", {"type": "object"}).state, State.MISSING)
        self.assertEqual(index.read("/synthetic/account/absent", {}).state, State.MISSING)
        self.assertEqual(index.read("/synthetic/account/private/nested", {}).state, State.WITHHELD)

    def test_explicit_parent_record_and_provided_parent_traversal_remain_unchanged(self):
        for state in ("unknown", "missing", "withheld", "not_applicable"):
            index = AnswerIndex(encoded({"/synthetic/account": {"state": state}}))
            answer = index.read("/synthetic/account/private", {})
            self.assertEqual(answer.state, State(state))
            self.assertEqual(answer.source_path, "/synthetic/account")
        index = AnswerIndex(encoded({"/synthetic/account": {"state": "provided", "value": {"count": [0]}}}))
        self.assertEqual(index.read("/synthetic/account/count/0", {"type": "integer"}).value, 0)
        self.assertEqual(index.read("/synthetic/account/absent", {}).state, State.MISSING)
        with self.assertRaisesRegex(ValueError, "overlapping"):
            AnswerIndex(encoded({"/synthetic/account": {"state": "provided", "value": {}},
                                 "/synthetic/account/private": {"state": "withheld"}}))

    def test_typed_rule_gate_keeps_causal_withheld_reason_without_running_value_predicate(self):
        index = AnswerIndex(encoded({"/synthetic/account/private": {"state": "withheld"}}))
        calls = []
        parent = index.predicate("/synthetic/account", {"type": "object"}, lambda value: calls.append(value) or True)
        for policy in RulePolicy:
            for severity in ("info", "warning", "error"):
                for position in ("applies_when", "assertion"):
                    assertions = []
                    rule = AnswerRule(
                        "synthetic.parent-visibility", severity, policy,
                        lambda: parent if position == "applies_when" else PredicateResult(State.PROVIDED, True),
                        lambda: assertions.append("called") or parent,
                    )
                    observed = evaluate_answer_rule(rule)
                    with self.subTest(policy=policy, severity=severity, position=position):
                        expected = (Outcome.SKIPPED if position == "applies_when" and policy is RulePolicy.RECOMMENDATION
                                    else Outcome.UNKNOWN)
                        self.assertEqual(observed.outcome, expected)
                        self.assertEqual(observed.reason, "answer_withheld")
                        self.assertEqual(observed.answer_state, State.WITHHELD)
                        self.assertEqual(observed.source_path, "/synthetic/account/private")
                        self.assertEqual(observed.severity, severity)
                        self.assertEqual(assertions, ["called"] if position == "assertion" else [])
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
