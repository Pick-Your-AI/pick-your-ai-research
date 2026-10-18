"""Synthetic CD-1 wire/normalization cases; no real answers or owner receipts."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from tests.selection_quantifier_prototype import Outcome, Rule, Selection, evaluate
from tests.t0_answer_state_prototype import AnswerIndex, ENCODING, State


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/t0-answer-states.json"
NETWORK = {"type": "string", "enum": ["online", "private_network", "air_gapped"]}
COUNT = {"type": "integer", "minimum": 0}
SELECTION = Selection("synthetic.model", "model", "primary")


def encoded(answers, version="cd1-0.1"):
    return json.dumps({"x_t0_answer_states": {"proposal_version": version, "answers": answers}})


def index(answer, path="/workload/network"):
    return AnswerIndex(encoded({path: answer}))


class AnswerEncodingCases(unittest.TestCase):
    def test_schema_and_documented_fixture(self):
        Draft202012Validator.check_schema(ENCODING.schema)
        answers = AnswerIndex(FIXTURE.read_bytes())
        self.assertEqual(answers.read("/workload/network", NETWORK).state, State.UNKNOWN)
        count = answers.read("/workload/requests/count", COUNT)
        self.assertEqual(count.value, 0)
        self.assertEqual(count.source, "preset:synthetic-zero-demand")
        self.assertEqual(count.source_path, "/workload/requests")
        self.assertEqual(answers.read("/workload/budgets", {}).state, State.MISSING)
        self.assertEqual(answers.read("/workload/organization/revenue", {}).state, State.WITHHELD)
        self.assertEqual(answers.read("/workload/output_tokens/max", COUNT).state, State.NOT_APPLICABLE)

    def test_false_zero_empty_and_nullable_values_are_explicit_provided_data(self):
        for value, schema in ((0, COUNT), (False, {"type": "boolean"}),
                              ([], {"type": "array"}), ({}, {"type": "object"}),
                              ("", {"type": "string"}), (None, {"type": "null"})):
            with self.subTest(value=value):
                answer = index({"state": "provided", "value": value}).read("/workload/network", schema)
                self.assertTrue(answer.provided)
                self.assertIs(type(answer.value), type(value))
                self.assertEqual(answer.value, value)

    def test_field_type_validation_precedes_predicates(self):
        for value in (None, True, -1, 1.5, "0"):
            with self.subTest(value=value):
                called = []
                answers = index({"state": "provided", "value": value})
                with self.assertRaisesRegex(ValueError, "invalid provided value"):
                    answers.predicate("/workload/network", COUNT, lambda v: called.append(v) or True)
                self.assertEqual(called, [])

    def test_unknown_string_is_not_implicitly_an_answer_state(self):
        answers = index({"state": "provided", "value": "unknown"})
        self.assertTrue(answers.predicate("/workload/network", {"type": "string"}, lambda v: v == "unknown"))
        with self.assertRaisesRegex(ValueError, "invalid provided value"):
            answers.read("/workload/network", NETWORK)
        with self.assertRaisesRegex(ValueError, "invalid CD-1 answer encoding"):
            AnswerIndex(encoded({"/workload/network": "unknown"}))

    def test_all_nonprovided_states_preserve_reason_without_running_predicates(self):
        for state in (State.MISSING, State.UNKNOWN, State.WITHHELD, State.NOT_APPLICABLE):
            with self.subTest(state=state):
                answers = index({"state": state}, "/workload")
                called = []
                resolved = answers.read("/workload/network", NETWORK)
                self.assertEqual(resolved.state, state)
                self.assertEqual(resolved.source_path, "/workload")
                self.assertIsNone(resolved.value)
                self.assertIsNone(resolved.source)
                self.assertIsNone(answers.predicate("/workload/network", NETWORK, lambda v: called.append(v) or True))
                self.assertEqual(called, [])

    def test_nonprovided_states_cannot_retain_a_value_or_source(self):
        for state in ("missing", "unknown", "withheld", "not_applicable"):
            for extra in ({"value": "synthetic-sensitive-answer"}, {"source": "preset:synthetic"}):
                with self.subTest(state=state, extra=extra), self.assertRaises(ValueError):
                    index({"state": state, **extra})

    def test_nested_objects_arrays_and_pointer_escape_order(self):
        answers = index({"state": "provided", "value": {
            "a/b~c": [{"value": 0}], "~1": False, "": "synthetic-empty-key"}}, "/workload")
        self.assertEqual(answers.read("/workload/a~1b~0c/0/value", COUNT).value, 0)
        self.assertIs(answers.read("/workload/~01", {"type": "boolean"}).value, False)
        self.assertEqual(answers.read("/workload/", {"type": "string"}).value, "synthetic-empty-key")
        for path in ("/workload/absent", "/workload/a~1b~0c/1", "/another_field"):
            with self.subTest(path=path):
                self.assertEqual(answers.read(path, {}).state, State.MISSING)
        for path in ("/workload/a~1b~0c/00", "/workload/a~1b~0c/-", "/workload/a~1b~0c/-1",
                     "/workload/a~1b~0c/0/value/child"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                answers.read(path, {})

    def test_overlapping_paths_are_rejected_in_both_input_orders(self):
        entries = [("/workload", {"state": "withheld"}),
                   ("/workload/network", {"state": "provided", "value": "air_gapped"})]
        for order in (entries, list(reversed(entries))):
            with self.subTest(order=order), self.assertRaisesRegex(ValueError, "overlapping"):
                AnswerIndex(encoded(dict(order)))
        independent = AnswerIndex(encoded({"/a": {"state": "unknown"}, "/ab": {"state": "missing"}}))
        self.assertEqual(independent.read("/a", {}).state, State.UNKNOWN)

    def test_nonpointer_paths_and_unreviewed_encoding_are_rejected(self):
        for path in ("", "workload.network", "#/workload", "/bad~", "/bad~2name"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                index({"state": "unknown"}, path)
        for state in ("not_selected", "unanswered", False):
            with self.subTest(state=state), self.assertRaises(ValueError):
                index({"state": state})
        with self.assertRaises(ValueError):
            AnswerIndex(encoded({}, version="cd1-0.2"))
        with self.assertRaises(ValueError):
            index({"state": "provided"})

    def test_duplicate_and_nonfinite_json_are_rejected_at_every_depth(self):
        cases = (
            '{"state":"unknown","state":"provided","value":0}',
            '{"state":"unknown","\\u0073tate":"unknown"}',
            '{"state":"provided","value":{"count":0,"count":1}}',
            '{"state":"provided","value":NaN}',
            '{"state":"provided","value":Infinity}',
            '{"state":"provided","value":1e999}',
        )
        for raw in cases:
            document = '{"x_t0_answer_states":{"proposal_version":"cd1-0.1","answers":{"/x":' + raw + '}}}'
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                AnswerIndex(document)

    def test_read_results_cannot_mutate_the_retained_answers(self):
        raw = encoded({"/workload": {"state": "provided", "value": {"requests": [0]}}}).encode()
        before = bytes(raw)
        answers = AnswerIndex(raw)
        exposed = answers.read("/workload", {"type": "object"})
        exposed.value["requests"].append(100)
        self.assertEqual(answers.read("/workload/requests", {"type": "array"}).value, [0])
        self.assertEqual(raw, before)

    def test_invalid_predicate_values_are_not_coerced(self):
        answers = index({"state": "provided", "value": "air_gapped"})
        for value in ("unknown", 0, 1, [], {}):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "normalized bool or None"):
                answers.predicate("/workload/network", NETWORK, lambda _: value)


class AnswerRuleBoundaryCases(unittest.TestCase):
    def test_compatibility_unknown_and_recommendation_skip_are_deliberately_distinct(self):
        for state in ("missing", "unknown", "withheld", "not_applicable"):
            answers = index({"state": state})
            compatibility = Rule("synthetic.isolation", "model", "error",
                                 lambda _: answers.predicate("/workload/network", NETWORK, lambda v: v == "air_gapped"),
                                 lambda _: False)
            recommendation = Rule("synthetic.recommendation", "model", "warning",
                                  lambda _: answers.read("/workload/network", NETWORK).provided
                                  and answers.predicate("/workload/network", NETWORK, lambda v: v == "air_gapped"),
                                  lambda _: False)
            with self.subTest(state=state):
                unresolved = evaluate((SELECTION,), compatibility)
                skipped = evaluate((SELECTION,), recommendation)
                self.assertEqual(unresolved.outcome, Outcome.UNKNOWN)
                self.assertEqual(unresolved.findings[0].reason, "applicability_unknown")
                self.assertEqual(skipped.outcome, Outcome.SKIPPED)
                self.assertEqual(skipped.findings[0].reason, "not_applicable")
                # CD-1 retains why the known-answer gate was false; a renderer
                # must not discard this when showing CD-13's aggregate finding.
                self.assertEqual(answers.read("/workload/network", NETWORK).state, State(state))
                self.assertEqual(unresolved.severity, "error")
                self.assertEqual(skipped.severity, "warning")

    def test_known_false_applicability_and_missing_selection_keep_distinct_findings(self):
        for value, expected in (("air_gapped", Outcome.FAIL), ("online", Outcome.SKIPPED),
                                ("private_network", Outcome.SKIPPED)):
            answers = index({"state": "provided", "value": value})
            rule = Rule("synthetic.isolation", "model", "error",
                        lambda _: answers.predicate("/workload/network", NETWORK, lambda v: v == "air_gapped"),
                        lambda _: False)
            with self.subTest(value=value):
                result = evaluate((SELECTION,), rule)
                self.assertEqual(result.outcome, expected)
                self.assertEqual(len(result.findings), 1)
                absent = evaluate((), rule)
                self.assertEqual(absent.outcome, Outcome.SKIPPED)
                self.assertEqual(absent.reason, "no_enabled_selections")
                self.assertEqual(absent.findings, ())

    def test_frozen_unknown_string_probe_and_historical_evaluation_are_preserved(self):
        contract = ROOT / "contracts/v1"
        spec = importlib.util.spec_from_file_location("cd1_frozen_evaluator", contract / "reference/evaluate.py")
        frozen = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(frozen)
        build = json.loads((contract / "examples/build.json").read_bytes())
        catalog = json.loads((contract / "examples/catalog.json").read_bytes())
        ruleset = json.loads((contract / "examples/ruleset.json").read_bytes())
        evaluator = frozen.Evaluator(build, catalog, ruleset)
        self.assertIs(evaluator.compare("eq", "unknown", "air_gapped"), False)
        self.assertIs(evaluator.compare("eq", frozen.UNKNOWN, "air_gapped"), frozen.UNKNOWN)
        before = evaluator.evaluate()
        augmented = copy.deepcopy(build)
        augmented.setdefault("extensions", {}).update(json.loads(FIXTURE.read_bytes()))
        self.assertEqual(frozen.Evaluator(augmented, catalog, ruleset).evaluate(), before)
        answers = AnswerIndex(FIXTURE.read_bytes())
        self.assertIsNone(answers.predicate("/workload/network", NETWORK, lambda v: v == "air_gapped"))


if __name__ == "__main__":
    unittest.main()
