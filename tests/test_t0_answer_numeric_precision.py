"""Raw synthetic CD-1 number boundaries; no real answers or released schema."""

from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import unittest

from tests.selection_quantifier_prototype import Outcome
from tests.t0_answer_state_prototype import (
    AnswerIndex, AnswerRule, PredicateResult, RulePolicy, State, evaluate_answer_rule,
)


ROOT = Path(__file__).resolve().parents[1]
FIELD = "/workload/count"
NUMBER = {"type": "number"}


def encoded(token, *, nested=False):
    value = '{"values":[' + token + ']}' if nested else token
    return ('{"x_t0_answer_states":{"proposal_version":"cd1-0.1","answers":{'
            '"/workload/count":{"state":"provided","source":"preset:synthetic",'
            '"value":' + value + '}}}}').encode("utf-8")


class AnswerNumericPrecisionCases(unittest.TestCase):
    def test_raw_fractional_numbers_cannot_satisfy_rounded_integer_bounds(self):
        cases = (
            ("1.0000000000000000000001", {"type": "integer", "minimum": 1, "maximum": 1}),
            ("0.999999999999999999999999", {"type": "integer", "minimum": 1, "maximum": 1}),
            ("9007199254740993.0", {"type": "integer", "maximum": 9007199254740992}),
            ("9007199254740993e0", {"type": "integer", "maximum": 9007199254740992}),
        )
        for token, schema in cases:
            raw = encoded(token)
            before, calls = bytes(raw), []
            with self.subTest(token=token), self.assertRaisesRegex(ValueError, "numeric precision"):
                AnswerIndex(raw).predicate(FIELD, schema, lambda value: calls.append(value) or True)
            self.assertEqual(calls, [])
            self.assertEqual(raw, before)

    def test_inexact_decimals_and_underflow_never_reach_an_unconstrained_predicate(self):
        for token in ("0.100000000000000000000001", "1.234567890123456789",
                      "1e-10000", "-1e-10000", "1e-99999999999999999999999999",
                      "1e23", "100000000000000000000000.0"):
            calls = []
            with self.subTest(token=token), self.assertRaisesRegex(ValueError, "numeric precision"):
                AnswerIndex(encoded(token)).predicate(FIELD, NUMBER,
                                                       lambda value: calls.append(value) or True)
            self.assertEqual(calls, [])

    def test_nested_raw_numbers_are_checked_before_value_traversal(self):
        for token in ("1.0000000000000000000001", "9007199254740993.0", "1e-10000"):
            calls = []
            with self.subTest(token=token), self.assertRaisesRegex(ValueError, "numeric precision"):
                AnswerIndex(encoded(token, nested=True)).predicate(
                    FIELD + "/values/0", NUMBER, lambda value: calls.append(value) or True)
            self.assertEqual(calls, [])

    def test_supported_decimal_and_exponent_spellings_preserve_float_values(self):
        for token in ("0.0", "-0.0", "1.0", "1e0", "10e-1", "5.000e0",
                      "0.1", "1.2500", "125e-2", "1e20", "1.5e-300"):
            raw = encoded(token)
            calls = []
            answers = AnswerIndex(raw)
            answer = answers.read(FIELD, NUMBER)
            result = answers.predicate(FIELD, NUMBER, lambda value: calls.append(value) or True)
            with self.subTest(token=token):
                self.assertIs(type(answer.value), float)
                self.assertEqual(Decimal(str(answer.value)), Decimal(token))
                if answer.value.is_integer():
                    self.assertEqual(int(answer.value), Decimal(token))
                self.assertEqual(calls, [answer.value])
                self.assertIs(type(calls[0]), float)
                self.assertIs(result.compatibility_value(), True)
                self.assertEqual(answer.source, "preset:synthetic")
                self.assertEqual(answer.source_path, FIELD)
                self.assertEqual(raw, encoded(token))
        for token in ("1.0", "1e0", "10e-1", "5.000e0"):
            answer = AnswerIndex(encoded(token)).read(FIELD, {"type": "integer", "minimum": 1, "maximum": 5})
            self.assertIs(type(answer.value), float)

    def test_exact_large_integer_tokens_keep_their_value_and_type(self):
        for token in ("0", "9007199254740993", "100000000000000000000001"):
            expected = int(token)
            calls = []
            result = AnswerIndex(encoded(token)).predicate(
                FIELD, {"type": "integer", "minimum": expected, "maximum": expected},
                lambda value: calls.append(value) or value == expected)
            with self.subTest(token=token):
                self.assertIs(result.compatibility_value(), True)
                self.assertEqual(calls, [expected])
                self.assertIs(type(calls[0]), int)

    def test_numeric_looking_strings_remain_literal_field_values(self):
        for value in ("1.0000000000000000000001", "1e-10000", "NaN"):
            answers = AnswerIndex(encoded(json.dumps(value)))
            self.assertEqual(answers.read(FIELD, {"type": "string"}).value, value)
            calls = []
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "invalid provided value"):
                answers.predicate(FIELD, NUMBER, lambda received: calls.append(received) or True)
            self.assertEqual(calls, [])

    def test_typed_rule_boundary_cannot_pass_from_a_rounded_raw_answer(self):
        for policy in RulePolicy:
            for position in ("applies_when", "assertion"):
                calls = []
                raw = encoded("1.0000000000000000000001")
                known = lambda: PredicateResult(State.PROVIDED, True, "/synthetic/known")
                candidate = lambda: AnswerIndex(raw).predicate(
                    FIELD, {"type": "integer", "minimum": 1, "maximum": 1},
                    lambda value: calls.append(value) or True)
                rule = AnswerRule("synthetic.precision", "error", policy,
                                  candidate if position == "applies_when" else known,
                                  candidate if position == "assertion" else known)
                with self.subTest(policy=policy, position=position), \
                        self.assertRaisesRegex(ValueError, "numeric precision"):
                    evaluate_answer_rule(rule)
                self.assertEqual(calls, [])
        answers = AnswerIndex(encoded("1.0"))
        result = evaluate_answer_rule(AnswerRule(
            "synthetic.exact", "warning", RulePolicy.COMPATIBILITY, known,
            lambda: answers.predicate(FIELD, NUMBER, lambda value: value == 1.0)))
        self.assertEqual(result.outcome, Outcome.PASS)
        self.assertEqual(result.answer_state, State.PROVIDED)
        self.assertEqual(result.source_path, FIELD)

    def test_raw_api_boundary_is_enforced_in_normal_and_optimized_python(self):
        program = (
            "import json, sys\n"
            "from tests.t0_answer_state_prototype import AnswerIndex\n"
            "calls=[]\n"
            "r=AnswerIndex(sys.stdin.buffer.read()).predicate('/workload/count', {'type':'number'}, "
            "lambda v: calls.append(v) or True)\n"
            "print(json.dumps({'value':calls[0], 'type':type(calls[0]).__name__, "
            "'result':r.compatibility_value()}))\n"
        )
        for optimized in (False, True):
            for token, valid in (("1.0000000000000000000001", False), ("1e23", False),
                                 ("1e-10000", False), ("0.1", True), ("9007199254740993", True)):
                result = subprocess.run(
                    [sys.executable, *(["-O"] if optimized else []), "-c", program],
                    cwd=ROOT, input=encoded(token), capture_output=True, timeout=10)
                with self.subTest(token=token, optimized=optimized):
                    if valid:
                        self.assertEqual(result.returncode, 0, result.stderr)
                        value = json.loads(result.stdout)
                        self.assertEqual(Decimal(str(value["value"])), Decimal(token))
                        self.assertEqual(value["type"], "float" if token == "0.1" else "int")
                        self.assertIs(value["result"], True)
                    else:
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        self.assertIn(b"numeric precision", result.stderr)
                        self.assertEqual(result.stdout, b"")


if __name__ == "__main__":
    unittest.main()
