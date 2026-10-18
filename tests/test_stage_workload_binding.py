"""Synthetic boundary cases for CD-5, without real workload/source admission."""

from copy import deepcopy
from decimal import Decimal, localcontext
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from tests.stage_workload_binding_prototype import (
    SCHEMA, StageWorkloadRecord, Status, answer_path, descriptor_digest, digest,
    inventory_path,
)
from tests.t0_answer_state_prototype import State


FIXTURES = Path(__file__).with_name("fixtures")


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def provided(value):
    return {"state": "provided", "value": value, "source": "synthetic:fixture-only"}


class StageWorkloadBindingTests(unittest.TestCase):
    def setUp(self):
        self.binding, self.build, self.answers = (
            json.loads((FIXTURES / name).read_bytes()) for name in (
                "stage-workload-binding.json", "stage-workload-build.json",
                "stage-workload-answers.json"))
        self.p = self.binding["x_t0_stage_workload"]
        self.facts = self.answers["x_t0_answer_states"]["answers"]

    def stage(self, sid):
        return next(stage for stage in self.p["stages"] if stage["id"] == sid)

    def path(self, sid, field):
        return answer_path(self.p, self.stage(sid), *field.split("/"))

    def set(self, sid, field, value=None, *, state="provided"):
        self.facts[self.path(sid, field)] = (provided(value) if state == "provided"
                                           else {"state": state})

    def record(self):
        binding = deepcopy(self.binding)
        build_raw, answers_raw = encode(self.build), encode(self.answers)
        p = binding["x_t0_stage_workload"]
        p["build_sha256"], p["answer_states_sha256"] = digest(build_raw), digest(answers_raw)
        return StageWorkloadRecord(encode(binding), build_raw, answers_raw)

    def evaluate(self, changes=None):
        record = self.record()
        # This test helper qualifies invented fixture facts only. The production
        # candidate never derives source eligibility from these labels.
        eligible = {path: True for path in record.answer_paths}
        eligible.update(changes or {})
        return record.evaluate(eligible)

    def result_stage(self, result, sid):
        return next(stage for stage in result.stages if stage.scope["id"] == sid)

    def metric(self, result, sid, name):
        return next(metric for metric in self.result_stage(result, sid).metrics
                    if metric.name == name)

    def fresh_stage_facts(self, old, new, *, except_fields=()):
        """Explicitly issue new synthetic facts after a test's scope change."""
        old_prefix = answer_path(self.p, old, "")
        new_prefix = answer_path(self.p, new, "")
        for path, answer in list(self.facts.items()):
            if path.startswith(old_prefix):
                field = path[len(old_prefix):]
                if field not in except_fields:
                    self.facts[new_prefix + field] = deepcopy(answer)

    def fresh_build_facts(self):
        """Reissue only synthetic fixture facts for a deliberately edited Build."""
        old = self.p["build_sha256"]
        self.p["build_sha256"] = digest(encode(self.build))
        previous = "/stage_workloads/" + old + "/"
        current = "/stage_workloads/" + self.p["build_sha256"] + "/"
        for path, answer in list(self.facts.items()):
            if path.startswith(previous):
                self.facts[current + path[len(previous):]] = deepcopy(answer)

    def test_committed_shape_and_separate_stage_values(self):
        Draft202012Validator.check_schema(SCHEMA)
        result = self.evaluate()
        self.assertEqual(result.status, Status.READY)
        self.assertEqual(len(result.stages), 4)
        draft = self.metric(result, "draft", "input_tokens").value
        classify = self.metric(result, "classify", "input_tokens").value
        self.assertEqual((draft.mean, draft.maximum), (Decimal("4096.125"), 8000))
        self.assertEqual((classify.mean, classify.maximum), (Decimal("200.25"), 1024))
        self.assertEqual(self.stage("draft")["selection_id"], self.stage("classify")["selection_id"])
        self.assertNotEqual(self.path("draft", "input_tokens"), self.path("classify", "input_tokens"))

    def test_requests_keep_their_period_and_zero_never_disables_a_stage(self):
        result = self.evaluate()
        daily = self.metric(result, "classify", "requests").value
        monthly = self.metric(result, "audio-score", "requests").value
        self.assertEqual((daily.count, daily.period), (2000, "day"))
        self.assertEqual((monthly.count, monthly.period), (0, "month"))
        self.assertEqual(self.result_stage(result, "audio-score").status, Status.READY)
        self.assertEqual(self.metric(result, "draft", "peak_concurrency").value, 2)
        self.assertEqual(self.metric(result, "classify", "peak_concurrency").value, 4)

    def test_global_and_sibling_lengths_do_not_fill_missing_stage_answers(self):
        del self.facts[self.path("draft", "input_tokens")]
        del self.facts[self.path("draft", "output_tokens")]
        del self.facts[self.path("draft", "requests")]
        result = self.evaluate()
        for name in ("input_tokens", "output_tokens", "requests"):
            self.assertIsNone(self.metric(result, "draft", name).value)
        self.assertEqual(self.metric(result, "classify", "output_tokens").value.maximum, 8)
        self.assertEqual(result.status, Status.INCOMPLETE)
        self.assertEqual(self.build["objectives"]["avg_input_tokens"], 700)
        self.assertEqual(self.facts["/workload/input_tokens"]["value"]["max"], 2222)

    def test_source_labels_and_default_eligibility_supply_no_qualification(self):
        record = self.record()
        result = record.evaluate()
        self.assertEqual(result.status, Status.INCOMPLETE)
        self.assertTrue(all(stage.reason == "stage_activation_unresolved" for stage in result.stages))
        self.assertTrue(any(answer.source == "synthetic:fixture-only" for _, answer in result.answers))
        self.assertTrue(all(value is None for _, value in result.eligibility))

    def test_each_fact_has_independent_eligibility(self):
        target = self.path("draft", "requests")
        for eligible in (False, None):
            with self.subTest(eligible=eligible):
                result = self.evaluate({target: eligible})
                self.assertEqual(self.metric(result, "draft", "requests").status, Status.INCOMPLETE)
                self.assertEqual(self.metric(result, "draft", "input_tokens").status, Status.READY)
                self.assertEqual(self.result_stage(result, "classify").status, Status.READY)
                self.assertEqual(dict(result.eligibility)[target], eligible)

    def test_unresolved_states_are_retained_without_zero_or_skip(self):
        for state in ("unknown", "missing", "withheld", "not_applicable"):
            with self.subTest(state=state):
                self.set("draft", "requests", state=state)
                result = self.evaluate()
                self.assertEqual(self.metric(result, "draft", "requests").status, Status.INCOMPLETE)
                self.assertIsNone(self.metric(result, "draft", "requests").value)
                self.assertEqual(dict(result.answers)[self.path("draft", "requests")].state, State(state))

    def test_explicit_non_generating_operation_needs_qualified_nonapplicability(self):
        result = self.evaluate()
        self.assertEqual(self.metric(result, "retrieve", "output_tokens").status, Status.NOT_APPLICABLE)
        target = self.path("retrieve", "output_tokens")
        self.assertEqual(self.metric(self.evaluate({target: None}), "retrieve", "output_tokens").status,
                         Status.INCOMPLETE)
        for state in ("missing", "unknown", "withheld"):
            self.set("retrieve", "output_tokens", state=state)
            self.assertEqual(self.metric(self.evaluate(), "retrieve", "output_tokens").status,
                             Status.INCOMPLETE)

    def test_task_or_stage_label_cannot_turn_generated_classification_into_nonapplicable(self):
        self.set("classify", "output_tokens", state="not_applicable")
        result = self.evaluate()
        self.assertEqual(self.metric(result, "classify", "output_tokens").status, Status.INCOMPLETE)
        self.assertEqual(self.metric(result, "retrieve", "output_tokens").status, Status.NOT_APPLICABLE)
        self.set("classify", "output_generates_tokens", state="unknown")
        self.assertEqual(self.metric(self.evaluate(), "classify", "output_tokens").reason,
                         "token_operation_unresolved")

    def test_generating_operation_zero_is_known_and_non_generating_counts_conflict(self):
        self.set("classify", "output_tokens", {"mean": "0.0", "max": 0})
        result = self.evaluate()
        self.assertEqual(self.metric(result, "classify", "output_tokens").status, Status.READY)
        self.assertEqual(self.metric(result, "classify", "output_tokens").value.maximum, 0)
        self.set("classify", "output_generates_tokens", False)
        result = self.evaluate()
        self.assertEqual(self.metric(result, "classify", "output_tokens").status, Status.INCOMPLETE)
        self.assertEqual(dict(result.answers)[self.path("classify", "output_tokens")].value["max"], 0)

    def test_input_token_applicability_is_independent_of_output(self):
        self.set("draft", "input_uses_tokens", False)
        result = self.evaluate()
        self.assertEqual(self.metric(result, "draft", "input_tokens").status, Status.INCOMPLETE)
        self.assertEqual(self.metric(result, "draft", "output_tokens").status, Status.READY)
        self.set("draft", "input_tokens", state="not_applicable")
        self.assertEqual(self.metric(self.evaluate(), "draft", "input_tokens").status, Status.NOT_APPLICABLE)

    def test_pure_native_stage_needs_no_tokenizer_but_keeps_exact_native_units(self):
        result = self.evaluate()
        audio = self.metric(result, "audio-score", "native_input_units/audio_seconds").value
        self.assertEqual((audio.mean, audio.maximum, audio.unit),
                         (Decimal("1.500"), Decimal("3.25"), "audio_seconds"))
        self.assertIsNone(self.stage("audio-score")["tokenizer"])
        self.assertEqual(self.metric(result, "audio-score", "input_tokens").status, Status.NOT_APPLICABLE)
        self.assertEqual(self.metric(result, "audio-score", "output_tokens").status, Status.NOT_APPLICABLE)

    def test_missing_tokenizer_cannot_expose_counts_as_ready(self):
        stage = self.stage("draft")
        old = deepcopy(stage)
        stage["tokenizer"] = None
        self.fresh_stage_facts(old, stage)
        result = self.evaluate()
        for field in ("input_tokens", "output_tokens"):
            metric = self.metric(result, "draft", field)
            self.assertEqual(metric.reason, "tokenizer_scope_missing")
            self.assertIsNone(metric.value)
        self.assertEqual(self.metric(result, "draft", "requests").status, Status.READY)

    def test_native_inventory_unknown_keeps_known_lengths_and_other_dimensions(self):
        self.set("audio-score", "native_input_units_complete", False)
        result = self.evaluate()
        self.assertEqual(self.metric(result, "audio-score", "native_input_units").status, Status.INCOMPLETE)
        self.assertEqual(self.metric(result, "audio-score", "native_output_units").status, Status.READY)
        self.assertEqual(self.metric(result, "audio-score", "native_input_units/audio_seconds").status,
                         Status.READY)
        self.assertEqual(self.result_stage(result, "audio-score").status, Status.INCOMPLETE)

    def test_missing_native_length_is_not_zero_or_a_token_conversion(self):
        self.set("audio-score", "native_input_units/audio_seconds", state="withheld")
        result = self.evaluate()
        metric = self.metric(result, "audio-score", "native_input_units/audio_seconds")
        self.assertEqual(metric.status, Status.INCOMPLETE)
        self.assertIsNone(metric.value)
        self.assertEqual(self.metric(result, "audio-score", "requests").value.count, 0)
        self.assertEqual(self.metric(result, "audio-score", "input_tokens").status, Status.NOT_APPLICABLE)

    def test_stage_completeness_does_not_replace_native_inventory_completeness(self):
        self.set("draft", "native_input_units_complete", state="unknown")
        result = self.evaluate()
        self.assertEqual(result.inventory.status, Status.READY)
        self.assertEqual(self.metric(result, "draft", "native_input_units").status, Status.INCOMPLETE)
        self.assertEqual(result.status, Status.INCOMPLETE)
        self.set("draft", "native_input_units_complete", True)
        self.facts[inventory_path(self.p)] = provided(False)
        result = self.evaluate()
        self.assertTrue(all(stage.status is Status.READY for stage in result.stages))
        self.assertEqual(result.status, Status.INCOMPLETE)

    def test_adding_stage_cannot_reuse_the_old_complete_inventory(self):
        new = deepcopy(self.stage("draft"))
        new["id"] = "another-call"
        self.p["stages"].append(new)
        self.set("another-call", "active", False)
        result = self.evaluate()
        self.assertEqual(result.inventory.status, Status.INCOMPLETE)
        self.assertEqual(self.result_stage(result, "draft").status, Status.READY)
        self.assertEqual(self.result_stage(result, "another-call").status, Status.INACTIVE)
        self.facts[inventory_path(self.p)] = provided(True)
        self.assertEqual(self.evaluate().status, Status.READY)

    def test_reordering_stage_inventory_changes_no_fact_scope_or_numeric_value(self):
        before = inventory_path(self.p)
        self.p["stages"].reverse()
        self.assertEqual(inventory_path(self.p), before)
        self.assertEqual(self.evaluate().status, Status.READY)
        reordered = dict(reversed(tuple(self.stage("draft").items())))
        self.assertEqual(descriptor_digest(reordered), descriptor_digest(self.stage("draft")))

    def test_empty_inventory_has_no_vacuous_readiness(self):
        self.p["stages"] = []
        self.facts[inventory_path(self.p)] = provided(True)
        result = self.evaluate()
        self.assertEqual(result.status, Status.INCOMPLETE)
        self.assertEqual(result.reason, "no_stage_records")
        self.assertEqual(result.stages, ())

    def test_explicit_inactive_requires_eligible_false_and_does_not_infer_zero(self):
        self.set("draft", "active", False)
        result = self.evaluate()
        stage = self.result_stage(result, "draft")
        self.assertEqual((stage.status, stage.metrics), (Status.INACTIVE, ()))
        result = self.evaluate({self.path("draft", "active"): False})
        self.assertEqual(self.result_stage(result, "draft").status, Status.INCOMPLETE)
        for stage in self.p["stages"]:
            self.set(stage["id"], "active", False)
        self.assertEqual(self.evaluate().status, Status.INACTIVE)

    def test_disabled_build_selection_is_authoritative_after_input_validation(self):
        for selection in self.build["selections"]:
            selection["enabled"] = False
        self.fresh_build_facts()
        result = self.evaluate()
        self.assertEqual(result.status, Status.INACTIVE)
        self.assertTrue(all(stage.reason == "selection_disabled" for stage in result.stages))
        self.set("draft", "requests", {"count": 1.0, "period": "day"})
        with self.assertRaisesRegex(ValueError, "exact JSON integer"):
            self.record()

    def test_changed_descriptor_cannot_reuse_old_actual_association(self):
        stage = self.stage("draft")
        old = deepcopy(stage)
        stage["operation"]["version"] = "2"
        self.fresh_stage_facts(old, stage, except_fields=("scope_confirmed",))
        result = self.evaluate()
        self.assertEqual(self.result_stage(result, "draft").reason, "stage_scope_unconfirmed")
        self.assertEqual(self.result_stage(result, "draft").metrics, ())
        self.set("draft", "scope_confirmed", True)
        self.facts[inventory_path(self.p)] = provided(True)
        self.assertEqual(self.evaluate().status, Status.READY)

    def test_every_configuration_dimension_changes_stage_fact_identity(self):
        for field, value in (
                ("id", "another-stage"),
                ("selection_id", "sel_inference_engine"),
                ("operation", {"id": "generate", "version": "2"}),
                ("configuration_id", "another-configuration"),
                ("tokenizer", {"id": "fixture.text-tokenizer", "version": "2"}),
                ("native_input_units", ["images_per_request"]),
                ("native_output_units", ["audio_seconds"])):
            with self.subTest(field=field):
                old = self.path("draft", "scope_confirmed")
                changed = deepcopy(self.stage("draft"))
                changed[field] = value
                self.assertNotEqual(answer_path(self.p, changed, "scope_confirmed"), old)

    def test_exact_reference_versions_are_not_trimmed_or_coerced(self):
        stage = self.stage("draft")
        old = deepcopy(stage)
        stage["operation"]["version"] = "v1.0.0+fixture-cuda"
        stage["tokenizer"]["version"] = " fixture tokenizer v2 "
        self.fresh_stage_facts(old, stage)
        self.facts[inventory_path(self.p)] = provided(True)
        result = self.evaluate()
        self.assertEqual(result.status, Status.READY)
        self.assertEqual(self.result_stage(result, "draft").scope["tokenizer"]["version"],
                         " fixture tokenizer v2 ")
        for value in ("", " ", "v2\n", "v2\t", True, 2):
            stage["operation"]["version"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.record()

    def test_changed_build_cannot_reuse_old_stage_or_complete_inventory_facts(self):
        self.build["selections"][0]["settings"]["temperature"] = 0.9
        result = self.evaluate()
        self.assertEqual(result.inventory.status, Status.INCOMPLETE)
        self.assertTrue(all(stage.reason == "stage_activation_unresolved" for stage in result.stages))
        self.fresh_build_facts()
        self.assertEqual(self.evaluate().status, Status.READY)

    def test_false_or_unresolved_scope_confirmation_never_qualifies_a_route(self):
        for state, value in (("provided", False), ("unknown", None), ("withheld", None)):
            self.set("draft", "scope_confirmed", value, state=state)
            result = self.evaluate()
            stage = self.result_stage(result, "draft")
            self.assertEqual((stage.reason, stage.metrics), ("stage_scope_unconfirmed", ()))
            self.assertEqual(self.result_stage(result, "classify").status, Status.READY)

    def test_withheld_stage_parent_preserves_all_answer_states(self):
        prefix = answer_path(self.p, self.stage("draft"), "")
        for path in list(self.facts):
            if path.startswith(prefix):
                del self.facts[path]
        self.facts[prefix[:-1]] = {"state": "withheld"}
        result = self.evaluate()
        stage_answers = [answer for path, answer in result.answers if path.startswith(prefix)]
        self.assertTrue(stage_answers)
        self.assertTrue(all(answer.state is State.WITHHELD for answer in stage_answers))
        self.assertTrue(all(answer.source_path == prefix[:-1] for answer in stage_answers))
        self.assertEqual(self.result_stage(result, "classify").status, Status.READY)

    def test_original_bytes_and_hashes_are_preserved_exactly(self):
        paths = ("stage-workload-binding.json", "stage-workload-build.json", "stage-workload-answers.json")
        raws = tuple((FIXTURES / name).read_bytes() for name in paths)
        record = StageWorkloadRecord(*raws)
        self.assertEqual(record.original_bytes, raws)
        result = record.evaluate()
        self.assertEqual((result.binding_sha256, result.build_sha256, result.answer_states_sha256),
                         tuple(digest(raw) for raw in raws))
        for position in (1, 2):
            changed = list(raws)
            changed[position] += b" "
            with self.assertRaisesRegex(ValueError, "bytes do not match"):
                StageWorkloadRecord(*changed)
        for position in range(3):
            changed = list(raws)
            changed[position] = changed[position].decode()
            with self.assertRaises(ValueError):
                StageWorkloadRecord(*changed)

    def test_integer_token_and_machine_count_boundaries(self):
        for field, value in (("requests", {"count": 9007199254740993, "period": "day"}),
                             ("peak_concurrency", 9223372036854775807)):
            self.set("draft", field, value)
        result = self.evaluate()
        self.assertEqual(self.metric(result, "draft", "requests").value.count, 9007199254740993)
        self.assertEqual(self.metric(result, "draft", "peak_concurrency").value, 9223372036854775807)
        for value in (True, 1.0, -1, 9223372036854775808):
            self.set("draft", "requests", {"count": value, "period": "day"})
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.record()

    def test_decimal_tokens_and_range_boundaries_are_exact(self):
        self.set("draft", "input_tokens", {"mean": "1.000000000000000001", "max": 1})
        with localcontext() as context:
            context.prec = 1
            with self.assertRaisesRegex(ValueError, "mean cannot exceed"):
                self.record()
        for value in ("NaN", "Infinity", "-0", "1e3", "01", ".5", "1.", "1\n",
                      "1.0000000000000000000", "10000000000000000000", 1.5, True):
            self.set("draft", "input_tokens", {"mean": value, "max": 2})
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.record()
        self.set("draft", "input_tokens", {"mean": "0.999", "max": 1})
        with self.assertRaisesRegex(ValueError, "at least one"):
            self.record()

    def test_image_maxima_are_exact_counts_and_duration_maxima_are_decimal_text(self):
        audio = self.stage("audio-score")
        audio["native_input_units"].append("images_per_request")
        for value in (1.0, True, "1"):
            self.set("audio-score", "native_input_units/images_per_request", {"mean": "1", "max": value})
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.record()
        self.set("audio-score", "native_input_units/images_per_request", {"mean": "0.5", "max": 1})
        self.set("audio-score", "native_input_units/audio_seconds", {"mean": "1.5", "max": 2.0})
        with self.assertRaises(ValueError):
            self.record()

    def test_invalid_known_values_cannot_hide_behind_inactive_or_nonapplicable_states(self):
        self.set("draft", "active", False)
        self.set("draft", "input_uses_tokens", False)
        self.set("draft", "input_tokens", {"mean": "20", "max": 10})
        with self.assertRaisesRegex(ValueError, "mean cannot exceed"):
            self.record()
        self.set("draft", "input_tokens", {"mean": "1", "max": 1})
        self.set("retrieve", "output_tokens", {"mean": "1", "max": -1})
        with self.assertRaises(ValueError):
            self.record()

    def test_duplicate_missing_and_ambiguous_selection_identities_reject(self):
        self.p["stages"].append(deepcopy(self.stage("draft")))
        with self.assertRaisesRegex(ValueError, "duplicate stage"):
            self.record()
        self.p["stages"].pop()
        self.stage("draft")["selection_id"] = "sel_missing"
        with self.assertRaisesRegex(ValueError, "unknown selection"):
            self.record()
        self.stage("draft")["selection_id"] = "sel_model"
        extra = deepcopy(self.build["selections"][0])
        self.build["selections"].append(extra)
        with self.assertRaises(ValueError):
            self.record()
        extra["id"] = "sel_another_model"
        with self.assertRaises(ValueError):
            self.record()

    def test_wire_identity_inventory_and_revision_aliases_reject(self):
        original = deepcopy(self.p)
        for value in (True, 1.0, "", "a\n", "a/b", "a b", "é"):
            self.p["inventory_id"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.record()
        self.p.update(original)
        self.stage("draft")["native_input_units"] = ["images_per_request", "images_per_request"]
        with self.assertRaises(ValueError):
            self.record()
        self.stage("draft")["native_input_units"] = []
        self.build["revision"] = 1.0
        with self.assertRaisesRegex(ValueError, "JSON integer"):
            self.record()
        self.build["revision"] = 1
        self.build["selections"][0]["id"] += "\n"
        with self.assertRaises(ValueError):
            self.record()

    def test_raw_json_ambiguity_nonfinite_and_overflow_are_rejected(self):
        build_raw, answers_raw = encode(self.build), encode(self.answers)
        for malformed in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e9999}'):
            with self.subTest(raw=malformed):
                with self.assertRaises(ValueError):
                    StageWorkloadRecord(malformed, build_raw, answers_raw)
                binding = deepcopy(self.binding)
                binding["x_t0_stage_workload"]["build_sha256"] = digest(malformed)
                with self.assertRaises(ValueError):
                    StageWorkloadRecord(encode(binding), malformed, answers_raw)
                binding = deepcopy(self.binding)
                binding["x_t0_stage_workload"]["answer_states_sha256"] = digest(malformed)
                with self.assertRaises(ValueError):
                    StageWorkloadRecord(encode(binding), build_raw, malformed)

    def test_eligibility_aliases_and_stale_scope_keys_are_rejected(self):
        record = self.record()
        for invalid in ([], True, {record.answer_paths[0]: 1}, {record.answer_paths[0]: "true"},
                        {"/stage_workloads/old": True}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                record.evaluate(invalid)

    def test_repeat_evaluation_and_returned_mutation_do_not_change_input_scope(self):
        record = self.record()
        eligible = {path: True for path in record.answer_paths}
        first = record.evaluate(eligible)
        self.result_stage(first, "draft").scope["operation"]["version"] = "changed"
        dict(first.answers)[self.path("draft", "requests")].value["count"] = 123
        eligible[self.path("draft", "requests")] = False
        second = record.evaluate(eligible)
        self.assertEqual(self.metric(second, "draft", "requests").status, Status.INCOMPLETE)
        self.assertEqual(dict(second.answers)[self.path("draft", "requests")].value["count"], 1000)
        third = record.evaluate({path: True for path in record.answer_paths})
        self.assertEqual(self.result_stage(third, "draft").scope["operation"]["version"], "1")
        self.assertEqual(third.status, Status.READY)


if __name__ == "__main__":
    unittest.main()
