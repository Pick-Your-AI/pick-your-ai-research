"""Synthetic CD-11 wire, exact scope and CD-1 integration; no vendor/model run."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from tests.context_budget_binding_prototype import ContextRecord, Outcome, State, digest


FIXTURES = Path(__file__).with_name("fixtures")


class ContextBindingTests(unittest.TestCase):
    def setUp(self):
        self.proposal_raw = (FIXTURES / "context-budget-binding.json").read_bytes()
        self.answers_raw = (FIXTURES / "context-budget-answers.json").read_bytes()
        self.proposal = json.loads(self.proposal_raw)
        self.answers = json.loads(self.answers_raw)
        self.values = self.answers["x_t0_answer_states"]["answers"]

    def answer(self, field, state="provided", value=None):
        answer = {"state": state}
        if state == "provided":
            answer["value"] = value
        self.values["/context/" + field] = answer

    def record(self):
        raw = json.dumps(self.answers).encode()
        self.proposal["x_t0_context_budget"]["answer_states_sha256"] = digest(raw)
        return ContextRecord(json.dumps(self.proposal).encode(), raw)

    def result(self):
        record = self.record()
        return record.evaluate(record.scope, enabled=True, evidence_eligible=True)

    def make_fit(self):
        self.answer("input_tokens", value={"lower": 5000, "upper": 6000})

    def test_committed_shared_window_fails_and_preserves_bytes(self):
        record = ContextRecord(self.proposal_raw, self.answers_raw)
        result = record.evaluate(record.scope, enabled=True, evidence_eligible=True)
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertFalse(result.may_not_fit)
        self.assertEqual(record.original_bytes, self.proposal_raw)
        self.assertEqual(record.answer_bytes, self.answers_raw)
        self.assertEqual([c.name for c in result.checks], ["output", "combined"])

    def test_separate_limits_pass_without_inventing_a_shared_window(self):
        self.answer("semantics", value="separate")
        self.answer("input_cap_tokens", value=8000)
        self.answer("shared_cap_tokens", state="not_applicable")
        result = self.result()
        self.assertEqual(result.outcome, Outcome.PASS)
        combined = next(c for c in result.checks if c.name == "combined")
        self.assertEqual((combined.lower, combined.upper), (Outcome.SKIPPED, Outcome.SKIPPED))
        self.answer("shared_cap_tokens", value=12000)
        with self.assertRaises(ValueError):
            self.record()

    def test_upper_boundary_and_straddling_decisions_reuse_existing_policy(self):
        for upper, expected, uncertain in ((6000, Outcome.PASS, False),
                                           (6500, Outcome.FAIL, True)):
            self.answer("input_tokens", value={"lower": 5000, "upper": upper})
            result = self.result()
            self.assertEqual((result.outcome, result.may_not_fit), (expected, uncertain))
        self.answer("output_cap_tokens", value=1000)
        self.assertEqual((self.result().outcome, self.result().may_not_fit), (Outcome.FAIL, False))

    def test_zero_is_known_output_and_policy_data(self):
        self.answer("input_tokens", value={"lower": 8000, "upper": 8000})
        self.answer("reserved_output_tokens", value=0)
        self.answer("output_cap_tokens", value=0)
        self.assertEqual(self.result().outcome, Outcome.PASS)
        self.answer("policy_total_cap_tokens", value=0)
        result = self.result()
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertEqual(next(c.upper for c in result.checks if c.name == "policy_total"), Outcome.FAIL)

    def test_bad_count_types_and_negative_counts_reject_before_evaluation(self):
        original = deepcopy(self.values)
        for field in ("reserved_output_tokens", "output_cap_tokens", "shared_cap_tokens",
                      "input_cap_tokens", "policy_total_cap_tokens"):
            for value in (True, False, 1.0, "1", None, -1):
                with self.subTest(field=field, value=value):
                    self.values.clear(); self.values.update(deepcopy(original))
                    self.answer(field, value=value)
                    with self.assertRaises(ValueError):
                        self.record()

    def test_invalid_ranges_reject_and_large_integers_do_not_round(self):
        for value in ({"lower": 1.0, "upper": 2}, {"lower": 1, "upper": True},
                      {"lower": 2, "upper": 1}, {"lower": 0, "upper": 1},
                      {"lower": 1}, {"lower": 1, "upper": 2, "mean": 1.5}, None):
            with self.subTest(value=value):
                self.answer("input_tokens", value=value)
                with self.assertRaises(ValueError):
                    self.record()
        self.answer("input_tokens", value={"lower": 2**80, "upper": 2**80})
        self.answer("shared_cap_tokens", value=2**80 + 1999)
        self.assertEqual(self.result().outcome, Outcome.FAIL)
        self.answer("shared_cap_tokens", value=2**80 + 2000)
        self.assertEqual(self.result().outcome, Outcome.PASS)

    def test_each_exact_scope_dimension_must_match(self):
        record = self.record()
        for key in ("selection_id", "operation", "settings_sha256", "model", "route", "tokenizer"):
            for part in (("id", "version") if key in ("model", "route", "tokenizer") else (None,)):
                with self.subTest(key=key, part=part):
                    selected = record.scope
                    if part is not None:
                        selected[key][part] += "-other"
                    else:
                        selected[key] = "0" * 64 if key == "settings_sha256" else selected[key] + "-other"
                    result = record.evaluate(selected, enabled=True, evidence_eligible=True)
                    self.assertEqual((result.outcome, result.reason, result.checks),
                                     (Outcome.UNKNOWN, "route_scope_mismatch", ()))
        result = record.evaluate(None, enabled=True, evidence_eligible=True)
        self.assertEqual(result.reason, "selection_scope_missing")

    def test_scope_schema_rejects_control_characters_and_type_aliases(self):
        original = deepcopy(self.proposal)
        for path, value in (("selection_id", "a"*120 + "\n"), ("operation", "generate-text\n"),
                            ("settings_sha256", "a"*64 + "\n"), ("settings_sha256", "A"*64),
                            ("model", {"id": "model.synthetic", "version": 1.0}),
                            ("route", {"id": "route.synthetic", "version": "v1\u0000"})):
            with self.subTest(path=path, value=value):
                self.proposal = deepcopy(original)
                self.proposal["x_t0_context_budget"]["scope"][path] = value
                with self.assertRaises(ValueError):
                    self.record()
        self.proposal = original
        record = self.record()
        scope = record.scope; scope["operation"] += "\n"
        with self.assertRaises(ValueError):
            record.evaluate(scope, enabled=False, evidence_eligible=False)

    def test_unresolved_output_state_is_neither_zero_nor_skip(self):
        self.make_fit()
        for state in ("unknown", "missing", "withheld", "not_applicable"):
            with self.subTest(state=state):
                self.answer("reserved_output_tokens", state=state)
                result = self.result()
                self.assertEqual(result.outcome, Outcome.UNKNOWN)
                answer = dict(result.answers)["reserved_output_tokens"]
                self.assertEqual(answer.state, State(state))
                self.assertIsNone(answer.value)

    def test_optional_constraints_require_explicit_absence(self):
        self.make_fit()
        self.assertEqual(self.result().outcome, Outcome.PASS)
        for field in ("input_cap_tokens", "policy_total_cap_tokens"):
            for state in ("unknown", "missing", "withheld"):
                with self.subTest(field=field, state=state):
                    self.answer(field, state=state)
                    self.assertEqual(self.result().outcome, Outcome.UNKNOWN)
            self.values.pop("/context/" + field)
            self.assertEqual(self.result().outcome, Outcome.UNKNOWN)
            self.answer(field, state="not_applicable")
        self.answer("policy_total_cap_tokens", state="withheld")
        self.answer("reserved_output_tokens", value=5000)
        self.assertEqual(self.result().outcome, Outcome.FAIL)

    def test_unknown_semantics_retains_known_input_failure(self):
        self.answer("semantics", state="unknown")
        self.answer("input_cap_tokens", value=6000)
        self.assertEqual(self.result().outcome, Outcome.FAIL)
        self.answer("input_cap_tokens", value=8000)
        self.assertEqual(self.result().outcome, Outcome.UNKNOWN)

    def test_parent_withheld_state_propagates_to_every_context_operand(self):
        self.values.clear()
        self.values["/context"] = {"state": "withheld"}
        result = self.result()
        self.assertEqual(result.outcome, Outcome.UNKNOWN)
        self.assertTrue(all(answer.state is State.WITHHELD for _, answer in result.answers))
        self.assertTrue(all(answer.source_path == "/context" for _, answer in result.answers))

    def test_source_eligibility_and_activation_are_separate_from_arithmetic(self):
        record = self.record()
        for eligible, reason in ((False, "source_evidence_ineligible"),
                                 (None, "source_evidence_unresolved")):
            result = record.evaluate(record.scope, enabled=True, evidence_eligible=eligible)
            self.assertEqual((result.outcome, result.reason, result.checks), (Outcome.UNKNOWN, reason, ()))
        self.assertEqual(record.evaluate(record.scope, enabled=False, evidence_eligible=None).outcome,
                         Outcome.SKIPPED)
        self.assertEqual(record.evaluate(record.scope, enabled=None, evidence_eligible=True).outcome,
                         Outcome.UNKNOWN)
        for enabled, eligible in ((1, True), (True, 1), (False, "false")):
            with self.assertRaises(ValueError):
                record.evaluate(record.scope, enabled=enabled, evidence_eligible=eligible)

    def test_answer_hash_binds_original_bytes_including_whitespace(self):
        raw = self.answers_raw + b"\n"
        with self.assertRaises(ValueError):
            ContextRecord(self.proposal_raw, raw)
        self.proposal["x_t0_context_budget"]["answer_states_sha256"] = digest(raw)
        record = ContextRecord(json.dumps(self.proposal).encode(), raw)
        self.assertEqual(record.answer_bytes, raw)
        self.assertEqual(record.evaluate(record.scope, enabled=True, evidence_eligible=True).outcome,
                         Outcome.FAIL)

    def test_duplicate_and_nonfinite_json_are_rejected_after_hash_binding(self):
        for raw in (self.answers_raw.replace(b'"lower": 7000', b'"lower": 6000,"lower": 7000'),
                    self.answers_raw.replace(b'"lower": 7000', b'"lower": NaN'),
                    self.answers_raw.replace(b'"lower": 7000', b'"lower": 1e999')):
            with self.subTest(raw=raw):
                self.proposal["x_t0_context_budget"]["answer_states_sha256"] = digest(raw)
                with self.assertRaises(ValueError):
                    ContextRecord(json.dumps(self.proposal).encode(), raw)
        raw = self.proposal_raw.replace(b'"proposal_version": "cd11-0.1"',
                                       b'"proposal_version": "cd11-0.2", "proposal_version": "cd11-0.1"')
        with self.assertRaises(ValueError):
            ContextRecord(raw, self.answers_raw)

    def test_overlapping_answer_paths_remain_invalid(self):
        self.values["/context"] = {"state": "withheld"}
        with self.assertRaises(ValueError):
            self.record()

    def test_detached_scope_and_answer_output_cannot_change_later_evaluation(self):
        record = self.record()
        scope = record.scope; scope["model"]["version"] = "mutated"
        result = record.evaluate(record.scope, enabled=True, evidence_eligible=True)
        dict(result.answers)["input_tokens"].value["upper"] = 1
        again = record.evaluate(record.scope, enabled=True, evidence_eligible=True)
        self.assertEqual(again.outcome, Outcome.FAIL)
        self.assertEqual(dict(again.answers)["input_tokens"].value["upper"], 7000)
        self.assertEqual(record.scope["model"]["version"], "v1")


if __name__ == "__main__":
    unittest.main()
