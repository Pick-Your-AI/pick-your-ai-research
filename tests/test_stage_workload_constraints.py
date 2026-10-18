"""Actual synthetic owner-constraint boundaries for the CD-5 0.2 candidate."""

from copy import deepcopy
from decimal import Decimal, localcontext
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from tests import stage_workload_binding_prototype as legacy
from tests.stage_workload_constraints_prototype import (
    SCHEMA, StageWorkloadRecord, Status, TokenizerAssumption, answer_path,
    descriptor_digest, digest, inventory_path, rule_gate,
)
from tests.t0_answer_state_prototype import State


FIXTURES = Path(__file__).with_name("fixtures")


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def provided(value):
    return {"state": "provided", "value": value, "source": "synthetic:fixture-only"}


class StageWorkloadConstraintTests(unittest.TestCase):
    def setUp(self):
        self.binding, self.build, self.answers = (
            json.loads((FIXTURES / name).read_bytes()) for name in (
                "stage-workload-binding-v02.json", "stage-workload-build-v02.json",
                "stage-workload-answers-v02.json"))
        self.p = self.binding["x_t0_stage_workload"]
        self.facts = self.answers["x_t0_answer_states"]["answers"]

    def stage(self, sid):
        return next(stage for stage in self.p["stages"] if stage["id"] == sid)

    def path(self, sid, field):
        return answer_path(self.p, self.stage(sid), *field.split("/"))

    def set(self, sid, field, value=None, *, state="provided"):
        self.facts[self.path(sid, field)] = provided(value) if state == "provided" else {"state": state}

    def record(self):
        binding = deepcopy(self.binding)
        build_raw, answers_raw = encode(self.build), encode(self.answers)
        binding["x_t0_stage_workload"]["build_sha256"] = digest(build_raw)
        binding["x_t0_stage_workload"]["answer_states_sha256"] = digest(answers_raw)
        return StageWorkloadRecord(encode(binding), build_raw, answers_raw)

    def evaluate(self, changes=None):
        record = self.record()
        # This authoring helper qualifies only these invented fixtures. A real
        # qualifier must independently admit the complete current input binding.
        eligible = {path: True for path in record.answer_paths}
        eligible.update(changes or {})
        return record.evaluate(eligible)

    def result_stage(self, result, sid):
        return next(stage for stage in result.stages if stage.scope and stage.scope["id"] == sid)

    def metric(self, result, sid, name):
        return next(metric for metric in self.result_stage(result, sid).metrics if metric.name == name)

    def reissue_descriptor(self, sid, mutate, *, omit=()):
        stage = self.stage(sid)
        before = answer_path(self.p, stage, "")
        mutate(stage)
        after = answer_path(self.p, stage, "")
        for path, answer in list(self.facts.items()):
            if path.startswith(before) and path[len(before):] not in omit:
                self.facts[after + path[len(before):]] = deepcopy(answer)
        self.facts[inventory_path(self.p)] = provided(True)

    def reissue_build(self):
        before = "/stage_workloads/" + self.p["build_sha256"] + "/"
        self.p["build_sha256"] = digest(encode(self.build))
        after = "/stage_workloads/" + self.p["build_sha256"] + "/"
        for path, answer in list(self.facts.items()):
            if path.startswith(before):
                self.facts[after + path[len(before):]] = deepcopy(answer)

    def test_positive_control_preserves_separate_lengths_periods_and_idle_zero(self):
        Draft202012Validator.check_schema(SCHEMA)
        result = self.evaluate()
        self.assertEqual(result.status, Status.READY)
        self.assertEqual((result.inventory.name, result.inventory.value), ("stage_inventory", True))
        self.assertEqual(len(result.stages), 4)
        self.assertEqual(self.metric(result, "draft", "input_tokens").value.mean, Decimal("4096.125"))
        self.assertEqual(self.metric(result, "classify", "input_tokens").value.maximum, 1024)
        self.assertEqual(self.metric(result, "audio-score", "requests").value.period, "month")
        self.assertEqual(self.metric(result, "audio-score", "requests").value.count, 0)
        self.assertEqual(self.metric(result, "audio-score", "peak_concurrency").value, 0)
        self.assertEqual(self.result_stage(result, "audio-score").status, Status.READY)

    def test_original_false_ready_witness_is_preserved_and_corrected(self):
        raws = tuple((FIXTURES / name).read_bytes() for name in (
            "stage-workload-binding.json", "stage-workload-build.json", "stage-workload-answers.json"))
        old = legacy.StageWorkloadRecord(*raws)
        self.assertEqual(old.evaluate({path: True for path in old.answer_paths}).status, legacy.Status.READY)
        self.build = json.loads(raws[1])
        self.reissue_build()
        self.set("audio-score", "peak_concurrency", 1)
        record = self.record()
        self.assertEqual(record.original_bytes[1], raws[1])
        result = record.evaluate({path: True for path in record.answer_paths})
        self.assertEqual(result.status, Status.INCOMPLETE)
        self.assertEqual(self.result_stage(result, "draft").reason, "stage_output_exceeds_selection_maximum")
        for sid in ("retrieve", "classify"):
            self.assertEqual(self.result_stage(result, sid).reason, "stage_peak_exceeds_build_maximum")
        self.assertEqual(self.result_stage(result, "audio-score").reason, "zero_requests_with_positive_peak")
        self.assertTrue(all(stage.status is Status.REJECTED for stage in result.stages))
        self.assertEqual(old.original_bytes, raws)

    def test_unresolved_request_states_keep_distinct_reasons_and_rule_policies(self):
        for state in ("unknown", "missing", "withheld"):
            with self.subTest(state=state):
                self.set("draft", "requests", state=state)
                finding = self.metric(self.evaluate(), "draft", "requests")
                self.assertEqual((finding.status, finding.reason, finding.value),
                                 (Status.INCOMPLETE, "answer_" + state, None))
                self.assertEqual(finding.answer_state, State(state))
                self.assertEqual(finding.source_path, self.path("draft", "requests"))
                for policy, outcome in (("compatibility", "unknown"), ("recommendation", "skipped")):
                    gate = rule_gate(finding, policy=policy, severity="error")
                    self.assertEqual((gate.outcome, gate.reason, gate.severity),
                                     (outcome, "answer_" + state, "error"))

    def test_known_not_applicable_requests_skip_without_zero_or_incompleteness(self):
        self.set("draft", "requests", state="not_applicable")
        result = self.evaluate()
        finding = self.metric(result, "draft", "requests")
        self.assertEqual((finding.status, finding.reason, finding.value),
                         (Status.NOT_APPLICABLE, "answer_not_applicable", None))
        self.assertEqual(self.result_stage(result, "draft").status, Status.READY)
        for policy in ("compatibility", "recommendation"):
            self.assertEqual(rule_gate(finding, policy=policy, severity="warning").outcome, "skipped")
        denied = self.metric(self.evaluate({self.path("draft", "requests"): False}), "draft", "requests")
        self.assertEqual((denied.status, denied.answer_state), (Status.INCOMPLETE, State.NOT_APPLICABLE))

    def test_provided_readiness_never_becomes_a_compatibility_pass(self):
        result = self.evaluate()
        for finding in (result, self.result_stage(result, "draft"), self.metric(result, "draft", "requests")):
            for policy in ("compatibility", "recommendation"):
                gate = rule_gate(finding, policy=policy, severity="info")
                self.assertEqual((gate.outcome, gate.reason, gate.severity),
                                 (None, "predicate_not_evaluated", "info"))
        for policy, severity in (("other", "error"), ("compatibility", "fatal")):
            with self.assertRaises(ValueError):
                rule_gate(result, policy=policy, severity=severity)

    def test_same_role_selections_bind_only_their_unique_ids_even_when_enabled(self):
        for enabled in (False, True):
            with self.subTest(enabled=enabled):
                self.setUp()
                alternative = deepcopy(self.build["selections"][0])
                alternative["id"], alternative["enabled"] = "sel_alternative", enabled
                self.build["selections"].append(alternative)
                self.reissue_build()
                result = self.evaluate()
                self.assertEqual(result.status, Status.READY)
                self.assertEqual(self.result_stage(result, "draft").scope["selection_id"], "sel_model")

    def test_duplicate_selection_ids_reject_only_affected_stages(self):
        self.build["selections"].append(deepcopy(self.build["selections"][0]))
        self.reissue_build()
        result = self.evaluate()
        self.assertEqual(self.result_stage(result, "retrieve").status, Status.READY)
        for sid in ("draft", "classify", "audio-score"):
            stage = self.result_stage(result, sid)
            self.assertEqual((stage.status, stage.reason), (Status.REJECTED, "duplicate_selection_id"))
        self.assertEqual(result.status, Status.INCOMPLETE)

    def test_unknown_selection_and_duplicate_stage_ids_preserve_siblings(self):
        self.reissue_descriptor("draft", lambda stage: stage.update(selection_id="sel_absent"))
        result = self.evaluate()
        self.assertEqual(self.result_stage(result, "draft").reason, "selection_not_found")
        self.assertEqual(self.result_stage(result, "classify").status, Status.READY)
        self.setUp()
        self.p["stages"].append(deepcopy(self.stage("draft")))
        self.facts[inventory_path(self.p)] = provided(True)
        result = self.evaluate()
        duplicates = [stage for stage in result.stages if stage.scope["id"] == "draft"]
        self.assertEqual(len(result.stages), 5)
        self.assertEqual(len({stage.stage_index for stage in duplicates}), 2)
        self.assertTrue(all(stage.reason == "duplicate_stage_id" for stage in duplicates))
        self.assertEqual(self.result_stage(result, "retrieve").status, Status.READY)

    def test_malformed_stage_descriptors_are_local_even_without_valid_identity(self):
        for value in (None, "invalid", {"id": "private\ninvalid"}, {"id": []}):
            with self.subTest(value=value):
                self.setUp()
                self.p["stages"][1] = value
                result = self.evaluate()
                rejected = next(stage for stage in result.stages if stage.stage_index == 1)
                self.assertEqual((rejected.status, rejected.scope, rejected.reason),
                                 (Status.REJECTED, None, "invalid_stage_descriptor"))
                self.assertEqual(self.result_stage(result, "classify").status, Status.READY)

    def test_escaped_unpaired_surrogates_reject_only_their_original_stage(self):
        originals = tuple((FIXTURES / name).read_bytes() for name in (
            "stage-workload-binding-v02.json", "stage-workload-build-v02.json",
            "stage-workload-answers-v02.json"))
        for field in ("id", "operation_version", "tokenizer_source"):
            for surrogate in ("\ud800", "\udfff"):
                with self.subTest(field=field, surrogate=ascii(surrogate)):
                    binding = json.loads(originals[0])
                    stage = binding["x_t0_stage_workload"]["stages"][1]
                    if field == "operation_version":
                        stage["operation"]["version"] = surrogate
                    elif field == "tokenizer_source":
                        stage["tokenizer_assumption"]["source"] = surrogate
                    else:
                        stage[field] = surrogate
                    # The input itself is valid UTF-8 JSON. Its escaped lone
                    # surrogate must not abort hashing before local rejection.
                    raw = json.dumps(binding, ensure_ascii=True).encode("utf-8")
                    record = StageWorkloadRecord(raw, originals[1], originals[2])
                    result = record.evaluate({path: True for path in record.answer_paths})
                    rejected = result.stages[1]
                    self.assertEqual((rejected.stage_index, rejected.scope, rejected.status, rejected.reason),
                                     (1, None, Status.REJECTED, "invalid_stage_descriptor"))
                    self.assertEqual(rejected.problems[0].path, "/x_t0_stage_workload/stages/1")
                    self.assertTrue(all(stage.status is Status.READY for i, stage in enumerate(result.stages) if i != 1))
                    self.assertEqual(record.original_bytes, (raw, originals[1], originals[2]))

    def test_valid_unicode_and_escaped_pairs_keep_existing_descriptor_identity(self):
        version = "modèle 🚀 exact release"
        self.reissue_descriptor("draft", lambda stage: stage["operation"].update(version=version))
        expected = digest(("cd5-0.2\n" + json.dumps(self.stage("draft"), ensure_ascii=False,
                         sort_keys=True, separators=(",", ":"), allow_nan=False)).encode("utf-8"))
        self.assertEqual(descriptor_digest(self.stage("draft")), expected)
        direct = self.record()
        binding = json.loads(direct.original_bytes[0])
        escaped = json.dumps(binding, ensure_ascii=True).encode("utf-8")
        self.assertIn(b"\\ud83d\\ude80", escaped)
        record = StageWorkloadRecord(escaped, *direct.original_bytes[1:])
        result = record.evaluate({path: True for path in record.answer_paths})
        self.assertEqual(result.status, Status.READY)
        self.assertEqual(self.result_stage(result, "draft").scope["operation"]["version"], version)
        self.assertEqual(descriptor_digest(self.result_stage(result, "draft").scope), expected)
        self.assertEqual(inventory_path(binding["x_t0_stage_workload"]), inventory_path(self.p))
        self.assertEqual(record.original_bytes, (escaped, *direct.original_bytes[1:]))

    def test_malformed_surrogate_coverage_cannot_alias_literal_escape_text(self):
        for surrogate, literal in (("\ud800", "\\ud800"), ("\udfff", "\\udfff")):
            with self.subTest(surrogate=ascii(surrogate)):
                self.assertNotEqual(descriptor_digest({"id": surrogate}), descriptor_digest({"id": literal}))

    def test_invalid_known_values_reject_inactive_stages_without_dropping_others(self):
        for field, value, reason in (
                ("requests", {"count": 1.0, "period": "day"}, "exact_integer_required"),
                ("input_tokens", {"mean": "20", "max": 10}, "length_mean_exceeds_maximum"),
                ("output_tokens", {"mean": "1", "max": -1}, "invalid_provided_value")):
            with self.subTest(field=field):
                self.setUp()
                self.set("draft", "active", False)
                self.set("draft", field, value)
                result = self.evaluate()
                rejected = self.result_stage(result, "draft")
                self.assertEqual((rejected.status, rejected.reason), (Status.REJECTED, reason))
                self.assertEqual(rejected.problems[0].path, self.path("draft", field))
                self.assertEqual(self.result_stage(result, "classify").status, Status.READY)
                self.assertEqual(rule_gate(rejected, policy="compatibility", severity="error").outcome, "unknown")

    def test_disabled_malformed_stage_is_not_hidden_by_selection_state(self):
        self.build["selections"][0]["enabled"] = False
        self.reissue_build()
        self.set("draft", "requests", {"count": True, "period": "day"})
        result = self.evaluate()
        self.assertEqual(self.result_stage(result, "draft").status, Status.REJECTED)
        self.assertEqual(self.result_stage(result, "classify").status, Status.INACTIVE)
        self.assertEqual(self.result_stage(result, "retrieve").status, Status.READY)

    def test_inference_engine_cannot_be_a_serving_stage_even_when_inactive(self):
        self.reissue_descriptor("draft", lambda stage: stage.update(selection_id="sel_inference_engine"))
        self.set("draft", "active", False)
        result = self.evaluate()
        stage = self.result_stage(result, "draft")
        self.assertEqual((stage.status, stage.reason), (Status.REJECTED, "selection_is_not_serving_component"))
        self.assertEqual(self.result_stage(result, "classify").status, Status.READY)

    def test_full_fine_tuned_and_vector_selections_keep_the_serving_boundary(self):
        for kind, settings in (
                ("vector_database", {"index_dimension": 768, "similarity_metric": "cosine"}),
                ("fine_tuned_model", {"use_adapter": False})):
            with self.subTest(kind=kind):
                self.setUp()
                selection = self.build["selections"][0]
                selection["kind"], selection["settings"] = kind, settings
                self.reissue_build()
                # Explicit tokenizer assumptions need no inferred native model.
                self.assertEqual(self.result_stage(self.evaluate(), "draft").status, Status.READY)
        self.build["selections"][0]["settings"]["use_adapter"] = True
        self.reissue_build()
        self.assertEqual(self.result_stage(self.evaluate(), "draft").reason, "adapter_is_not_serving_component")
        self.build["selections"][0]["settings"] = {}
        self.reissue_build()
        stage = self.result_stage(self.evaluate(), "draft")
        self.assertEqual((stage.status, stage.reason), (Status.INCOMPLETE, "fine_tuned_serving_mode_unresolved"))

    def test_zero_requests_positive_peak_is_local_and_not_hidden_by_inactivity(self):
        self.set("audio-score", "peak_concurrency", 1)
        self.set("audio-score", "active", False)
        result = self.evaluate()
        self.assertEqual(self.result_stage(result, "audio-score").reason, "zero_requests_with_positive_peak")
        self.assertEqual(self.result_stage(result, "draft").status, Status.READY)

    def test_output_maximum_and_build_peak_conflicts_are_independently_flagged(self):
        self.set("draft", "output_tokens", {"mean": "500.5", "max": 2001})
        self.set("draft", "peak_concurrency", 5)
        result = self.evaluate()
        stage = self.result_stage(result, "draft")
        self.assertEqual(stage.status, Status.REJECTED)
        self.assertEqual({problem.reason for problem in stage.problems},
                         {"stage_output_exceeds_selection_maximum", "stage_peak_exceeds_build_maximum"})
        self.assertEqual(self.result_stage(result, "classify").status, Status.READY)
        self.assertEqual(dict(result.answers)[self.path("draft", "peak_concurrency")].value, 5)

    def test_ineligible_conflicting_values_are_unresolved_not_asserted_conflicts(self):
        self.set("draft", "peak_concurrency", 5)
        result = self.evaluate({self.path("draft", "peak_concurrency"): False})
        stage = self.result_stage(result, "draft")
        self.assertEqual((stage.status, stage.problems), (Status.INCOMPLETE, ()))
        self.assertEqual(self.metric(result, "draft", "peak_concurrency").reason, "evidence_ineligible")

    def test_selection_bound_rejection_names_the_original_build_array_position(self):
        self.build["selections"][0]["settings"]["max_output_tokens"] = 2000.0
        self.reissue_build()
        result = self.evaluate()
        rejected = self.result_stage(result, "draft")
        problem = rejected.problems[0]
        self.assertEqual((rejected.status, problem.reason, problem.document, problem.path),
                         (Status.REJECTED, "invalid_selection_output_bound", "build",
                          "/selections/0/settings/max_output_tokens"))
        self.assertEqual(self.result_stage(result, "retrieve").status, Status.READY)

    def test_no_stage_fact_inherits_build_profile_or_pipeline_answers(self):
        for field in ("requests", "input_tokens", "output_tokens"):
            del self.facts[self.path("draft", field)]
        self.facts["/pipeline/draft/input_tokens"] = provided({"mean": "999", "max": 1000})
        result = self.evaluate()
        for field in ("requests", "input_tokens", "output_tokens"):
            metric = self.metric(result, "draft", field)
            self.assertEqual((metric.value, metric.answer_state), (None, State.MISSING))
        self.assertEqual(self.metric(result, "classify", "output_tokens").value.maximum, 8)
        self.assertEqual(self.build["objectives"]["avg_input_tokens"], 700)

    def test_tokenizer_states_keep_exact_descriptor_binding_and_distinct_reasons(self):
        for state in ("unknown", "missing", "withheld", "not_applicable"):
            with self.subTest(state=state):
                self.setUp()
                old_path = self.path("draft", "input_tokens")
                self.reissue_descriptor("draft", lambda stage: stage.update(tokenizer_assumption={"state": state}))
                self.assertNotEqual(self.path("draft", "input_tokens"), old_path)
                result = self.evaluate()
                finding = self.metric(result, "draft", "tokenizer_assumption")
                reason = "tokenizer_required_but_not_applicable" if state == "not_applicable" else "answer_" + state
                self.assertEqual((finding.status, finding.reason, finding.answer_state),
                                 (Status.INCOMPLETE, reason, State(state)))
                self.assertEqual(finding.source_document, "binding")
                self.assertEqual(finding.source_path, "/x_t0_stage_workload/stages/1/tokenizer_assumption")
                self.assertIsNone(self.metric(result, "draft", "input_tokens").value)
                self.assertEqual(self.metric(result, "draft", "requests").status, Status.READY)

    def test_native_operations_keep_tokenizer_nonapplicability_without_conversion(self):
        self.reissue_descriptor("audio-score", lambda stage: stage.update(tokenizer_assumption={"state": "unknown"}))
        result = self.evaluate()
        finding = self.metric(result, "audio-score", "tokenizer_assumption")
        self.assertEqual((finding.status, finding.answer_state, finding.value),
                         (Status.NOT_APPLICABLE, State.UNKNOWN, None))
        self.assertEqual(finding.reason, "tokenizer_not_required_for_operation")
        amount = self.metric(result, "audio-score", "native_input_units/audio_seconds").value
        self.assertEqual((amount.mean, amount.maximum, amount.unit),
                         (Decimal("1.500"), Decimal("3.25"), "audio_seconds"))

    def test_model_native_is_an_explicit_assumption_bound_to_selected_version(self):
        result = self.evaluate()
        finding = self.metric(result, "classify", "tokenizer_assumption")
        self.assertEqual(finding.value, TokenizerAssumption("model_native", "cat.model.fixture", "2026.10-demo"))
        self.assertTrue(finding.value.assumption)
        self.build["selections"][0]["catalog_item_version"] = "new-model-version"
        stale = self.evaluate()
        self.assertEqual(self.result_stage(stale, "classify").status, Status.INCOMPLETE)
        self.reissue_build()
        self.assertEqual(self.metric(self.evaluate(), "classify", "tokenizer_assumption").value.reference_version,
                         "new-model-version")

    def test_native_model_basis_cannot_invent_a_model_for_vector_storage(self):
        self.build["selections"][0]["kind"] = "vector_database"
        self.build["selections"][0]["settings"] = {"index_dimension": 768, "similarity_metric": "cosine"}
        self.reissue_build()
        result = self.evaluate()
        finding = self.metric(result, "classify", "tokenizer_assumption")
        self.assertEqual((finding.status, finding.reason), (Status.INCOMPLETE, "model_native_reference_unresolved"))
        self.assertEqual(self.result_stage(result, "draft").status, Status.READY)

    def test_explicit_tokenizer_or_model_versions_are_preserved_with_assumptions(self):
        for basis in ("tokenizer", "model"):
            self.reissue_descriptor("draft", lambda stage: stage.update(tokenizer_assumption=provided(
                {"basis": basis, "reference": {"id": "fixture.reference", "version": " exact v2+fixture "},
                 "assumption": True})))
            finding = self.metric(self.evaluate(), "draft", "tokenizer_assumption")
            self.assertEqual(finding.value, TokenizerAssumption(basis, "fixture.reference", " exact v2+fixture "))
        self.assertEqual(finding.source_document, "binding")

    def test_untyped_tokenizer_sentinels_and_invalid_provided_states_reject_locally(self):
        for answer in (None, "unknown", {"state": "provided", "value": "unknown"},
                       provided({"basis": "model_native", "assumption": False}),
                       provided({"basis": "model_native", "assumption": 1}),
                       provided({"basis": "tokenizer", "reference": {"id": "fixture", "version": "v2\n"},
                                 "assumption": True})):
            with self.subTest(answer=answer):
                self.setUp()
                self.stage("draft")["tokenizer_assumption"] = answer
                result = self.evaluate()
                rejected = next(stage for stage in result.stages if stage.stage_index == 1)
                self.assertEqual(rejected.reason, "invalid_stage_descriptor")
                self.assertEqual(self.result_stage(result, "classify").status, Status.READY)

    def test_tokenizer_eligibility_is_independent_of_stage_scope_and_count_evidence(self):
        target = self.path("draft", "tokenizer_assumption")
        for eligibility in (False, None):
            result = self.evaluate({target: eligibility})
            self.assertEqual(self.metric(result, "draft", "tokenizer_assumption").status, Status.INCOMPLETE)
            self.assertIsNone(self.metric(result, "draft", "input_tokens").value)
            self.assertEqual(self.metric(result, "draft", "requests").status, Status.READY)

    def test_false_token_operation_needs_qualified_not_applicable_counts(self):
        self.set("classify", "output_tokens", state="not_applicable")
        result = self.evaluate()
        self.assertEqual(self.metric(result, "classify", "output_tokens").reason,
                         "token_count_required_but_not_applicable")
        self.set("classify", "output_generates_tokens", False)
        self.assertEqual(self.metric(self.evaluate(), "classify", "output_tokens").status, Status.NOT_APPLICABLE)
        self.set("classify", "output_tokens", {"mean": "0", "max": 0})
        self.assertEqual(self.metric(self.evaluate(), "classify", "output_tokens").reason,
                         "provided_tokens_conflict_with_operation")

    def test_unknown_token_operation_retains_its_state_specific_explanation(self):
        for state in ("unknown", "missing", "withheld"):
            self.set("draft", "input_uses_tokens", state=state)
            finding = self.metric(self.evaluate(), "draft", "input_tokens")
            self.assertEqual((finding.status, finding.reason, finding.value),
                             (Status.INCOMPLETE, "token_operation_answer_" + state, None))

    def test_known_lengths_survive_independent_native_or_inventory_gaps(self):
        self.set("audio-score", "native_input_units_complete", state="unknown")
        self.facts[inventory_path(self.p)] = provided(False)
        result = self.evaluate()
        self.assertEqual(result.inventory.name, "stage_inventory")
        self.assertEqual((result.inventory.status, result.inventory.value), (Status.INCOMPLETE, False))
        self.assertEqual(self.metric(result, "audio-score", "native_input_units").reason, "answer_unknown")
        self.assertEqual(self.metric(result, "audio-score", "native_input_units/audio_seconds").status, Status.READY)
        self.assertEqual(self.result_stage(result, "classify").status, Status.READY)

    def test_invalid_inventory_fact_does_not_discard_valid_stages(self):
        self.facts[inventory_path(self.p)] = provided(1)
        result = self.evaluate()
        self.assertEqual((result.status, result.inventory.status), (Status.INCOMPLETE, Status.REJECTED))
        self.assertTrue(all(stage.status is Status.READY for stage in result.stages))

    def test_edited_descriptor_requires_new_actual_scope_confirmation(self):
        self.reissue_descriptor("draft", lambda stage: stage["operation"].update(version="new"),
                                omit=("scope_confirmed",))
        result = self.evaluate()
        self.assertEqual(self.result_stage(result, "draft").reason, "stage_scope_answer_missing")
        self.assertEqual(self.result_stage(result, "classify").status, Status.READY)
        self.set("draft", "scope_confirmed", True)
        self.assertEqual(self.evaluate().status, Status.READY)

    def test_inventory_coverage_changes_with_membership_not_order(self):
        old = inventory_path(self.p)
        self.p["stages"].reverse()
        self.assertEqual(inventory_path(self.p), old)
        self.assertEqual(self.evaluate().status, Status.READY)
        self.p["stages"].pop()
        self.assertNotEqual(inventory_path(self.p), old)
        self.assertEqual(self.evaluate().inventory.status, Status.INCOMPLETE)

    def test_empty_and_all_inactive_inventories_never_invent_totals(self):
        for stage in self.p["stages"]:
            self.set(stage["id"], "active", False)
        result = self.evaluate()
        self.assertEqual(result.status, Status.INACTIVE)
        self.assertTrue(all(stage.metrics == () for stage in result.stages))
        self.p["stages"] = []
        self.facts[inventory_path(self.p)] = provided(True)
        result = self.evaluate()
        self.assertEqual((result.status, result.reason, result.stages),
                         (Status.INCOMPLETE, "no_stage_records", ()))

    def test_withheld_parent_keeps_state_and_origin_without_fallback(self):
        prefix = answer_path(self.p, self.stage("draft"), "")
        for path in list(self.facts):
            if path.startswith(prefix):
                del self.facts[path]
        self.facts[prefix[:-1]] = {"state": "withheld"}
        result = self.evaluate()
        stage = self.result_stage(result, "draft")
        self.assertEqual(stage.reason, "stage_activation_answer_withheld")
        finding = stage.metrics[0]
        self.assertEqual((finding.answer_state, finding.source_path), (State.WITHHELD, prefix[:-1]))
        self.assertEqual(self.result_stage(result, "classify").status, Status.READY)

    def test_native_numeric_and_token_boundaries_reject_without_float_coercion(self):
        for field, value in (
                ("requests", {"count": True, "period": "day"}),
                ("requests", {"count": 9223372036854775808, "period": "day"}),
                ("peak_concurrency", 1.0),
                ("input_tokens", {"mean": "NaN", "max": 1}),
                ("input_tokens", {"mean": "1.000000000000000001", "max": 1}),
                ("input_tokens", {"mean": "0.999", "max": 1}),
                ("output_tokens", {"mean": "0", "max": True})):
            with self.subTest(field=field, value=value), localcontext() as context:
                context.prec = 1
                self.setUp()
                self.set("draft", field, value)
                self.assertEqual(self.result_stage(self.evaluate(), "draft").status, Status.REJECTED)
        self.setUp()
        self.set("draft", "requests", {"count": 9007199254740993, "period": "day"})
        self.assertEqual(self.metric(self.evaluate(), "draft", "requests").value.count, 9007199254740993)
        self.set("audio-score", "native_input_units/audio_seconds", {"mean": "1.5", "max": 2.0})
        self.assertEqual(self.result_stage(self.evaluate(), "audio-score").status, Status.REJECTED)

    def test_original_bytes_hashes_and_private_output_copies_remain_exact(self):
        paths = ("stage-workload-binding-v02.json", "stage-workload-build-v02.json", "stage-workload-answers-v02.json")
        raws = tuple((FIXTURES / name).read_bytes() for name in paths)
        record = StageWorkloadRecord(*raws)
        result = record.evaluate({path: True for path in record.answer_paths})
        self.assertEqual(record.original_bytes, raws)
        self.assertEqual((result.binding_sha256, result.build_sha256, result.answer_states_sha256),
                         tuple(digest(raw) for raw in raws))
        self.result_stage(result, "draft").scope["operation"]["version"] = "mutated"
        dict(result.answers)[self.path("draft", "requests")].value["count"] = 5
        repeated = record.evaluate({path: True for path in record.answer_paths})
        self.assertEqual(self.result_stage(repeated, "draft").scope["operation"]["version"], "1")
        self.assertEqual(self.metric(repeated, "draft", "requests").value.count, 1000)
        for position in (1, 2):
            changed = list(raws)
            changed[position] += b" "
            with self.assertRaisesRegex(ValueError, "bytes do not match"):
                StageWorkloadRecord(*changed)

    def test_global_envelope_and_raw_document_errors_are_explicit(self):
        for invalid in ("cd5-0.1", "cd5-latest"):
            self.p["proposal_version"] = invalid
            with self.assertRaisesRegex(ValueError, "0.2 envelope"):
                self.record()
        self.setUp()
        self.p["stages"] *= 33
        with self.assertRaises(ValueError):
            self.record()
        self.setUp()
        for invalid in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e9999}'):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                StageWorkloadRecord(invalid, encode(self.build), encode(self.answers))
        self.build["revision"] = 1.0
        with self.assertRaisesRegex(ValueError, "JSON integer"):
            self.record()

    def test_eligibility_and_schema_validation_work_under_optimized_python(self):
        record = self.record()
        for invalid in ([], True, {record.answer_paths[0]: 1}, {record.answer_paths[0]: 1.0},
                        {record.answer_paths[0]: "true"}, {"/stale/binding": True}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                record.evaluate(invalid)
        default = record.evaluate()
        self.assertEqual(default.status, Status.INCOMPLETE)
        self.assertTrue(all(stage.reason == "stage_activation_evidence_unresolved" for stage in default.stages))


if __name__ == "__main__":
    unittest.main()
