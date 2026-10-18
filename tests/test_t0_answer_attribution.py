"""Explicit preset/assumption metadata, isolated from the historical 0.1 input."""

from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator

from tests.selection_quantifier_prototype import Outcome
from tests.t0_answer_state_prototype import (
    AnswerIndex, AnswerRule, PredicateResult, RulePolicy, State,
)
from tests.t0_answer_attribution_prototype import (
    ATTRIBUTION, AttributedAnswerIndex, AttributedPredicate,
    evaluate_attributed_rule,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/t0-answer-attribution.json"
COUNT = {"type": "integer", "minimum": 0}


def encoded(answers, version="cd1-0.2"):
    return json.dumps({"x_t0_answer_states": {
        "proposal_version": version, "answers": answers,
    }}).encode("utf-8")


def provided(value=0, assumption=True, **extra):
    return {"state": "provided", "value": value, "assumption": assumption, **extra}


class AttributionAdmission(unittest.TestCase):
    def test_schema_and_dated_synthetic_fixture(self):
        Draft202012Validator.check_schema(ATTRIBUTION.schema)
        raw = FIXTURE.read_bytes()
        answers = AttributedAnswerIndex(raw)
        count = answers.read("/synthetic/workload/requests/count", COUNT)
        self.assertEqual((count.value, count.source, count.assumption, count.source_path),
                         (0, "preset:synthetic-zero-demand", True, "/synthetic/workload/requests"))
        network = answers.read("/synthetic/workload/network", {"type": "string"})
        self.assertIs(network.assumption, False)
        self.assertEqual(network.source, "preset:synthetic-offline")
        self.assertEqual(answers.original_bytes, raw)

    def test_true_false_and_missing_source_are_independent_explicit_metadata(self):
        for flag in (True, False):
            for source in (None, "preset:synthetic"):
                record = provided(False, flag, **({"source": source} if source else {}))
                answers = AttributedAnswerIndex(encoded({"/synthetic": record}))
                answer = answers.read("/synthetic", {"type": "boolean"})
                with self.subTest(flag=flag, source=source):
                    self.assertIs(answer.value, False)
                    self.assertIs(answer.assumption, flag)
                    self.assertEqual(answer.source, source)
                    self.assertTrue(answer.provided)

    def test_assumption_is_required_and_never_coerced_or_defaulted(self):
        for flag in (None, 0, 1, 0.0, 1.0, "true", "false", [], {}):
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                AttributedAnswerIndex(encoded({"/synthetic": provided(0, flag)}))
        for source in (None, "preset:synthetic"):
            record = {"state": "provided", "value": 0}
            if source is not None:
                record["source"] = source
            with self.subTest(source=source), self.assertRaises(ValueError):
                AttributedAnswerIndex(encoded({"/synthetic": record}))

    def test_source_uses_whole_preset_name_profile(self):
        valid = ("preset:x", "preset:Demo_v2.1-safe", "preset:" + "a" * 64)
        invalid = ("preset:", "preset: ", "preset:x y", "preset:x\n", "preset:x\t",
                   "preset:x\x00", " preset:x", "Preset:x", "manual", "published",
                   "https://example.org", "preset:https://example.org", "preset:/path",
                   "preset:-name", "preset:" + "a" * 65, "preset:café", "preset:x:y",
                   1, True, None, [], {})
        for source in valid:
            with self.subTest(source=source):
                answer = AttributedAnswerIndex(encoded({"/synthetic": provided(source=source)}))
                self.assertEqual(answer.read("/synthetic", COUNT).source, source)
        for source in invalid:
            with self.subTest(source=source), self.assertRaises(ValueError):
                AttributedAnswerIndex(encoded({"/synthetic": provided(source=source)}))

    def test_unresolved_records_cannot_carry_provided_attribution(self):
        for state in ("unknown", "missing", "withheld", "not_applicable"):
            raw = encoded({"/synthetic": {"state": state}})
            answer = AttributedAnswerIndex(raw).read("/synthetic", {})
            with self.subTest(state=state):
                self.assertEqual(answer.state, State(state))
                self.assertIsNone(answer.source)
                self.assertIsNone(answer.assumption)
                self.assertIsNone(answer.value)
            for extra in ({"source": "preset:synthetic"}, {"assumption": False},
                          {"assumption": True}, {"value": "synthetic"}):
                with self.subTest(state=state, extra=extra), self.assertRaises(ValueError):
                    AttributedAnswerIndex(encoded({"/synthetic": {"state": state, **extra}}))

    def test_new_version_is_opt_in_and_does_not_reinterpret_legacy_bytes(self):
        legacy_path = ROOT / "tests/fixtures/t0-answer-states.json"
        original = legacy_path.read_bytes()
        AnswerIndex(original)
        with self.assertRaises(ValueError):
            AttributedAnswerIndex(original)
        with self.assertRaises(ValueError):
            AnswerIndex(FIXTURE.read_bytes())
        # Permissive historical source syntax stays confined to the old reader.
        old = encoded({"/synthetic": {"state": "provided", "value": 0,
                                      "source": "historical-free-text"}}, version="cd1-0.1")
        self.assertEqual(AnswerIndex(old).read("/synthetic", COUNT).source, "historical-free-text")
        self.assertEqual(legacy_path.read_bytes(), original)

    def test_duplicate_nonfinite_and_nonunicode_inputs_fail_before_normalization(self):
        records = ('{"state":"provided","value":0,"assumption":true,"assumption":false}',
                   '{"state":"provided","value":{"x":0,"x":1},"assumption":true}',
                   '{"state":"provided","value":NaN,"assumption":true}',
                   '{"state":"provided","value":1e999,"assumption":true}',
                   '{"state":"provided","value":"\\ud800","assumption":true}')
        for record in records:
            raw = ('{"x_t0_answer_states":{"proposal_version":"cd1-0.2","answers":'
                   '{"/synthetic":' + record + '}}}').encode()
            with self.subTest(record=record), self.assertRaises(ValueError):
                AttributedAnswerIndex(raw)
        for raw in (b"\xff", "not-original-bytes", bytearray(b"{}")):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                AttributedAnswerIndex(raw)

    def test_original_lossy_number_tokens_are_rejected_before_the_private_reader_view(self):
        tokens = ("1e-400", "-1e-400", "9007199254740993.0", "0.99999999999999999",
                  "0.10000000000000000001", "1e23", "1e999")
        for token in tokens:
            for value in (token, '{"unread":[{"number":' + token + '}]}'):
                raw = ('{"x_t0_answer_states":{"proposal_version":"cd1-0.2","answers":'
                       '{"/synthetic":{"state":"provided","value":' + value +
                       ',"assumption":false}}}}').encode()
                with self.subTest(token=token, value=value):
                    with patch("tests.t0_answer_attribution_prototype.AnswerIndex") as reader:
                        with self.assertRaisesRegex(ValueError, "invalid attribution JSON"):
                            AttributedAnswerIndex(raw)
                        reader.assert_not_called()

    def test_supported_original_number_tokens_retain_values_and_explicit_attribution(self):
        tokens = (("0.1", 0.1, float), ("1.25", 1.25, float), ("1e3", 1000.0, float),
                  ("1e-300", 1e-300, float), ("5e-324", 5e-324, float),
                  ("9007199254740992.0", 9007199254740992.0, float),
                  ("9007199254740993", 9007199254740993, int))
        for token, value, kind in tokens:
            raw = ('{"x_t0_answer_states":{"proposal_version":"cd1-0.2","answers":'
                   '{"/synthetic":{"state":"provided","value":{"number":' + token +
                   '},"source":"preset:numeric-control","assumption":false}}}}').encode()
            with self.subTest(token=token):
                answers = AttributedAnswerIndex(raw)
                answer = answers.read("/synthetic/number", {"type": "number"})
                self.assertEqual(answer.value, value)
                self.assertIs(type(answer.value), kind)
                self.assertIs(answer.assumption, False)
                self.assertEqual(answer.source, "preset:numeric-control")
                self.assertEqual(answers.original_bytes, raw)


class AttributionReadAndPolicy(unittest.TestCase):
    def test_nested_attribution_follows_actual_record_but_does_not_fill_missing_members(self):
        answers = AttributedAnswerIndex(encoded({"/synthetic": provided(
            {"a/b~c": [{"count": 0}]}, False, source="preset:synthetic-nested")}))
        answer = answers.read("/synthetic/a~1b~0c/0/count", COUNT)
        self.assertEqual(answer.source_path, "/synthetic")
        self.assertEqual(answer.source, "preset:synthetic-nested")
        self.assertIs(answer.assumption, False)
        for pointer in ("/synthetic/absent", "/synthetic/a~1b~0c/1"):
            with self.subTest(pointer=pointer):
                missing = answers.read(pointer, {})
                self.assertEqual(missing.state, State.MISSING)
                self.assertIsNone(missing.assumption)
                self.assertIsNone(missing.source)
        for pointer in ("/synthetic/a~1b~0c/00", "/synthetic/a~1b~0c/0/count/child"):
            with self.subTest(pointer=pointer), self.assertRaises(ValueError):
                answers.read(pointer, {})

    def test_current_parent_visibility_and_overlap_policy_are_reused(self):
        records = {"/synthetic/private/value": {"state": "withheld"},
                   "/synthetic/visible/value": provided(0, False)}
        answers = AttributedAnswerIndex(encoded(records))
        legacy = deepcopy(records)
        legacy["/synthetic/visible/value"].pop("assumption")
        base = AnswerIndex(encoded(legacy, version="cd1-0.1"))
        for pointer in ("/synthetic", "/synthetic/private", "/synthetic/private/value",
                        "/synthetic/visible", "/elsewhere"):
            with self.subTest(pointer=pointer):
                actual, expected = answers.read(pointer, {}), base.read(pointer, {})
                self.assertEqual((actual.state, actual.source_path),
                                 (expected.state, expected.source_path))
                self.assertIsNone(actual.assumption)
        # A withheld child supplies the actual parent cause; an unrelated
        # provided sibling cannot lend its flag or source to that result.
        parent = answers.read("/synthetic", {})
        self.assertEqual((parent.state, parent.source_path, parent.source, parent.assumption),
                         (State.WITHHELD, "/synthetic/private/value", None, None))
        for policy in RulePolicy:
            calls = []
            result = evaluate_attributed_rule(AnswerRule(
                "synthetic.parent", "warning", policy,
                lambda: answers.predicate("/synthetic", {}, lambda _: calls.append("value") or True),
                lambda: calls.append("assertion") or AttributedPredicate(State.PROVIDED, True, assumption=False),
            ))
            self.assertEqual(result.finding.outcome, Outcome.SKIPPED
                             if policy is RulePolicy.RECOMMENDATION else Outcome.UNKNOWN)
            self.assertEqual((result.finding.reason, result.finding.source_path),
                             ("answer_withheld", "/synthetic/private/value"))
            self.assertIsNone(result.source)
            self.assertIsNone(result.assumption)
            self.assertEqual(calls, [])
        records["/synthetic"] = provided({}, True)
        with self.assertRaisesRegex(ValueError, "overlapping"):
            AttributedAnswerIndex(encoded(records))

    def test_read_value_mutations_cannot_change_original_bytes_or_later_attribution(self):
        raw = encoded({"/synthetic": provided({"count": 0}, True, source="preset:synthetic")})
        answers = AttributedAnswerIndex(raw)
        exposed = answers.read("/synthetic", {})
        exposed.value["count"] = 100
        copied = asdict(exposed)
        copied["assumption"] = False
        self.assertEqual(answers.read("/synthetic/count", COUNT).value, 0)
        self.assertIs(answers.read("/synthetic/count", COUNT).assumption, True)
        self.assertEqual(answers.original_bytes, raw)

    def test_typed_value_validation_and_safe_negation_preserve_explicit_flags(self):
        for flag in (True, False):
            answers = AttributedAnswerIndex(encoded({"/synthetic": provided(0, flag, source="preset:test")}))
            called = []
            value = answers.predicate("/synthetic", COUNT, lambda v: called.append(v) or True)
            negated = value.negated()
            with self.subTest(flag=flag):
                self.assertIs(negated.compatibility_value(), False)
                self.assertIs(negated.assumption, flag)
                self.assertEqual(negated.source, "preset:test")
                self.assertEqual(negated.negated(), value)
                self.assertEqual(called, [0])
                with self.assertRaises(TypeError):
                    bool(negated)
            with self.assertRaisesRegex(ValueError, "invalid provided value"):
                answers.predicate("/synthetic", {"type": "string"}, lambda _: True)

    def test_causal_terminal_attribution_is_visible_without_qualifying_evidence(self):
        for flag in (True, False):
            for truth, outcome in ((True, Outcome.PASS), (False, Outcome.FAIL),
                                   (None, Outcome.UNKNOWN)):
                answers = AttributedAnswerIndex(encoded({"/synthetic": provided(0, flag, source="preset:test")}))
                calls = []
                rule = AnswerRule(
                    "synthetic.attribution", "warning", RulePolicy.COMPATIBILITY,
                    lambda: AttributedPredicate(State.PROVIDED, True, "/applicability", None, False),
                    lambda: answers.predicate("/synthetic", COUNT, lambda v: calls.append(v) or truth),
                )
                result = evaluate_attributed_rule(rule)
                with self.subTest(flag=flag, truth=truth):
                    self.assertEqual(result.finding.outcome, outcome)
                    self.assertEqual(result.finding.severity, "warning")
                    self.assertEqual(result.finding.position, "assertion")
                    self.assertEqual(result.finding.source_path, "/synthetic")
                    self.assertIs(result.assumption, flag)
                    self.assertEqual(result.source, "preset:test")
                    self.assertEqual(calls, [0])
                    self.assertNotIn("verified", asdict(result))
                    with self.assertRaises(TypeError):
                        bool(result)

    def test_unresolved_and_false_applicability_remain_lazy_with_their_actual_attribution(self):
        for policy in RulePolicy:
            for state in (State.UNKNOWN, State.MISSING, State.WITHHELD, State.NOT_APPLICABLE):
                answer = AttributedAnswerIndex(encoded({"/synthetic": {"state": state}}))
                calls = []
                rule = AnswerRule(
                    "synthetic.lazy", "error", policy,
                    lambda: answer.predicate("/synthetic", {}, lambda _: calls.append("value") or True),
                    lambda: calls.append("assertion") or AttributedPredicate(State.PROVIDED, True, assumption=False),
                )
                result = evaluate_attributed_rule(rule)
                with self.subTest(policy=policy, state=state):
                    expected = (Outcome.SKIPPED if state is State.NOT_APPLICABLE
                                or policy is RulePolicy.RECOMMENDATION else Outcome.UNKNOWN)
                    self.assertEqual(result.finding.outcome, expected)
                    self.assertIsNone(result.source)
                    self.assertIsNone(result.assumption)
                    self.assertEqual(calls, [])
            calls = []
            result = evaluate_attributed_rule(AnswerRule(
                "synthetic.false", "info", policy,
                lambda: AttributedPredicate(State.PROVIDED, False, "/false", "preset:control", True),
                lambda: calls.append("assertion") or AttributedPredicate(State.PROVIDED, True, assumption=False),
            ))
            self.assertEqual(result.finding.reason, "applicability_false")
            self.assertEqual(result.source, "preset:control")
            self.assertIs(result.assumption, True)
            self.assertEqual(calls, [])

    def test_terminal_wrapper_rejects_callbacks_that_drop_attribution(self):
        for position in ("applies_when", "assertion"):
            with self.subTest(position=position), self.assertRaisesRegex(ValueError, "AttributedPredicate"):
                evaluate_attributed_rule(AnswerRule(
                    "synthetic.bad", "error", RulePolicy.COMPATIBILITY,
                    lambda: (PredicateResult(State.PROVIDED, True) if position == "applies_when"
                             else AttributedPredicate(State.PROVIDED, True, assumption=False)),
                    lambda: PredicateResult(State.PROVIDED, True),
                ))


if __name__ == "__main__":
    unittest.main()
