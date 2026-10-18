"""Synthetic typed CD-3/CD-1 query/result tests; no source or runtime evidence."""

from copy import deepcopy
import itertools
import json
from pathlib import Path
import unittest

from tests.support_membership_binding_prototype import (
    ELIGIBILITY, RESULT, SCHEMA, WIRE, SupportQueryRecord, answer_path, digest,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures"
BINDING_RAW = (FIXTURES / "support-membership-binding.json").read_bytes()
ANSWERS_RAW = (FIXTURES / "support-membership-answers.json").read_bytes()
RESULT_RAW = (FIXTURES / "support-membership-result.json").read_bytes()
STATES = ("unknown", "missing", "withheld", "not_applicable")
QUALIFIED = dict.fromkeys(ELIGIBILITY, True)


def encode(value):
    return (json.dumps(value, indent=2, allow_nan=False) + "\n").encode("utf-8")


class SupportBindingTests(unittest.TestCase):
    def setUp(self):
        self.binding = json.loads(BINDING_RAW)
        self.proposal = self.binding["x_t0_support_query"]
        self.answers = json.loads(ANSWERS_RAW)
        self.values = self.answers["x_t0_answer_states"]["answers"]

    def fact(self, field, value=None, *, state="provided"):
        self.values[answer_path(self.proposal, field)] = (
            {"state": state, "value": value} if state == "provided" else {"state": state})

    def raw(self):
        answers = encode(self.answers)
        self.proposal["answer_states_sha256"] = digest(answers)
        return encode(self.binding), answers

    def record(self):
        return SupportQueryRecord(*self.raw())

    def result(self, **context):
        record = self.record()
        context = {"enabled": True, "eligible_inputs": QUALIFIED, **context}
        return record.evaluate(record.scope, **context)["x_t0_support_result"]

    def test_committed_query_result_bytes_and_canonical_kinds(self):
        WIRE.check_schema(SCHEMA)
        WIRE.validate(json.loads(BINDING_RAW))
        RESULT.validate(json.loads(RESULT_RAW))
        record = SupportQueryRecord(BINDING_RAW, ANSWERS_RAW)
        result = record.verify_result(RESULT_RAW, record.scope, enabled=True, eligible_inputs=QUALIFIED)
        self.assertEqual(record.original_bytes, (BINDING_RAW, ANSWERS_RAW))
        self.assertEqual(result, json.loads(RESULT_RAW))
        self.assertEqual(result["x_t0_support_result"]["decision"]["outcome"], "pass")
        self.assertEqual(record.scope["catalog_sha256"], digest((ROOT / "contracts/v1/examples/catalog.json").read_bytes()))
        self.assertEqual(record.scope["conditions_sha256"], digest((ROOT / "contracts/v1/examples/build.json").read_bytes()))
        registry = json.loads((ROOT / "contracts/v1/schemas/component-registry.json").read_bytes())
        self.assertEqual(set(SCHEMA["$defs"]["kind"]["enum"]), set(registry["kinds"]))

    def test_any_and_all_retain_all_positive_negative_unknown_and_disputed_rows(self):
        self.fact("requested", ["safetensors", "onnx", "gguf", "future-format"])
        self.fact("unsupported", ["gguf", "onnx"])
        any_result = self.result()
        self.assertEqual(any_result["decision"]["outcome"], "pass")
        self.proposal["query"]["requirement"] = "all"
        all_result = self.result()
        self.assertEqual(all_result["decision"]["outcome"], "fail")
        self.assertEqual(all_result["decision"]["findings"], any_result["decision"]["findings"])
        self.assertEqual([(f["value"], f["outcome"], f["reason"]) for f in all_result["decision"]["findings"]], [
            ("future-format", "unknown", "unmarked_absence"),
            ("gguf", "unknown", "opposite_equal_rank_claims"),
            ("onnx", "fail", "explicit_unsupported"),
            ("safetensors", "pass", "documented_member"),
        ])
        self.assertTrue(all_result["decision"]["disputed"])
        self.assertEqual(all_result["decision"]["evidence_label"], "unverified")
        self.assertEqual(all_result["query"]["severity"], "error")

    def test_any_all_negative_findings_need_explicit_requested_completeness(self):
        self.fact("requested", ["onnx", "future-format"])
        self.fact("unsupported", ["onnx"])
        self.fact("exhaustive", True)
        for complete, outcome, reason in (
            (False, "unknown", "requested_set_incomplete"),
            (True, "fail", "any_membership"),
        ):
            with self.subTest(complete=complete):
                self.fact("requested_complete", complete)
                result = self.result()
                self.assertEqual((result["decision"]["outcome"], result["decision"]["reason"]),
                                 (outcome, reason))
                self.assertEqual([(f["value"], f["outcome"], f["reason"])
                                  for f in result["decision"]["findings"]],
                                 [("future-format", "fail", "exhaustive_absence"),
                                  ("onnx", "fail", "explicit_unsupported")])
                self.assertIs(result["inputs"]["requested_complete"]["value"], complete)

    def test_all_positive_findings_need_explicit_requested_completeness(self):
        self.proposal["query"]["requirement"] = "all"
        self.fact("requested", ["safetensors", "gguf"])
        self.fact("unsupported", [])
        for complete, outcome, reason in (
            (False, "unknown", "requested_set_incomplete"),
            (True, "pass", "all_membership"),
        ):
            with self.subTest(complete=complete):
                self.fact("requested_complete", complete)
                result = self.result()
                self.assertEqual((result["decision"]["outcome"], result["decision"]["reason"]),
                                 (outcome, reason))
                self.assertTrue(all(f["outcome"] == "pass" for f in result["decision"]["findings"]))

    def test_each_unresolved_requested_completeness_state_retains_unknown_verdict(self):
        for requirement, state in itertools.product(("any", "all"), (*STATES, "absent")):
            with self.subTest(requirement=requirement, state=state):
                self.setUp(); self.proposal["query"]["requirement"] = requirement
                self.fact("requested", ["onnx"])
                self.fact("supported", ["onnx"] if requirement == "all" else [])
                self.fact("unsupported", ["onnx"] if requirement == "any" else [])
                if state == "absent":
                    del self.values[answer_path(self.proposal, "requested_complete")]
                else:
                    self.fact("requested_complete", state=state)
                result = self.result()
                self.assertEqual((result["decision"]["outcome"], result["decision"]["reason"]),
                                 ("unknown", "requested_completeness_unknown"))
                marker = result["inputs"]["requested_complete"]
                self.assertEqual(marker["state"], "missing" if state == "absent" else state)
                self.assertNotIn("value", marker)
                self.assertEqual(result["decision"]["findings"][0]["outcome"],
                                 "fail" if requirement == "any" else "pass")

    def test_requested_completeness_needs_its_own_caller_qualification(self):
        for requirement, flag in itertools.product(("any", "all"), (False, None, "omitted")):
            with self.subTest(requirement=requirement, flag=flag):
                self.setUp(); self.proposal["query"]["requirement"] = requirement
                self.fact("requested", ["onnx"])
                self.fact("supported", ["onnx"] if requirement == "all" else [])
                self.fact("unsupported", ["onnx"] if requirement == "any" else [])
                self.fact("requested_complete", True)
                flags = dict(QUALIFIED)
                if flag == "omitted": del flags["requested_complete"]
                else: flags["requested_complete"] = flag
                result = self.result(eligible_inputs=flags)
                self.assertEqual((result["decision"]["outcome"], result["decision"]["reason"]),
                                 ("unknown", "requested_completeness_unknown"))
                self.assertIs(result["inputs"]["requested_complete"]["value"], True)
                self.assertIs(result["evaluation"]["eligible_inputs"]["requested_complete"],
                              None if flag == "omitted" else flag)

    def test_witness_and_counterexample_do_not_require_completeness_qualification(self):
        for requirement, state, flag in itertools.product(("any", "all"),
                ("provided", *STATES), (False, None, True)):
            with self.subTest(requirement=requirement, state=state, flag=flag):
                self.setUp(); self.proposal["query"]["requirement"] = requirement
                self.fact("requested", ["safetensors", "onnx", "gguf", "future-format"])
                self.fact("unsupported", ["gguf", "onnx"])
                self.fact("requested_complete", False, state=state)
                result = self.result(eligible_inputs={**QUALIFIED, "requested_complete": flag})
                self.assertEqual(result["decision"]["outcome"], "pass" if requirement == "any" else "fail")
                self.assertEqual(len(result["decision"]["findings"]), 4)
                self.assertTrue(result["decision"]["disputed"])
                self.assertEqual(result["inputs"]["requested_complete"]["state"], state)

    def test_known_empty_requests_are_unknown_with_all_marker_states_and_quantifiers(self):
        for requirement, complete in itertools.product(("any", "all"), (False, True, None)):
            with self.subTest(requirement=requirement, complete=complete):
                self.setUp(); self.proposal["query"]["requirement"] = requirement
                self.fact("requested", [])
                self.fact("requested_complete", complete, state="unknown" if complete is None else "provided")
                result = self.result()
                self.assertEqual((result["decision"]["outcome"], result["decision"]["reason"]),
                                 ("unknown", "requirement_empty"))
                self.assertEqual(result["decision"]["findings"], [])
                self.assertEqual(result["inputs"]["requested"]["value"], [])
                self.assertEqual(result["inputs"]["requested"]["state"], "provided")
                self.fact("applies_when", False)
                self.assertEqual(self.result()["decision"]["outcome"], "skipped")

    def test_old_proposal_versions_are_rejected_without_silent_upgrade(self):
        self.assertEqual(self.proposal["proposal_version"], "cd3-0.2")
        self.assertEqual(self.proposal["query"]["version"], "0.2.0")
        for version in ("cd3-0.1", "cd3-0.3"):
            with self.subTest(version=version):
                self.setUp(); self.proposal["proposal_version"] = version
                with self.assertRaisesRegex(ValueError, "invalid CD-3 query"):
                    self.record()

    def test_current_query_does_not_reuse_prior_version_answer_paths(self):
        before = dict(self.values)
        self.values.clear()
        self.values.update({path.replace('/rule.fixture.engine.formats/0.2.0/',
                                         '/rule.fixture.engine.formats/0.1.0/'): value
                            for path, value in before.items()})
        result = self.result()
        self.assertEqual((result["decision"]["outcome"], result["decision"]["reason"]),
                         ("unknown", "applicability_unknown"))
        self.assertTrue(all(value == {"state": "missing"} for value in result["inputs"].values()))
        self.assertIsNone(result["inputs"]["requested_complete"].get("value"))

    def test_known_empty_exhaustive_list_differs_from_unmarked_or_missing_list(self):
        self.fact("requested", ["onnx"])
        self.fact("supported", [])
        self.fact("unsupported", [])
        for value, expected in ((False, "unknown"), (True, "fail")):
            self.fact("exhaustive", value)
            self.assertEqual(self.result()["decision"]["outcome"], expected)
        for state in STATES:
            with self.subTest(state=state):
                self.fact("supported", state=state)
                result = self.result()
                self.assertEqual(result["decision"]["outcome"], "unknown")
                self.assertEqual(result["decision"]["findings"][0]["reason"], "support_list_missing")
                self.assertEqual(result["inputs"]["supported"]["state"], state)

    def test_explicit_negative_can_fail_without_any_positive_inventory(self):
        self.fact("requested", ["onnx"])
        self.fact("unsupported", ["onnx"])
        for state in STATES:
            with self.subTest(state=state):
                self.fact("supported", state=state)
                self.fact("exhaustive", state=state)
                result = self.result()
                self.assertEqual(result["decision"]["outcome"], "fail")
                self.assertEqual(result["decision"]["findings"][0]["reason"], "explicit_unsupported")

    def test_documented_positive_needs_no_exhaustiveness_claim(self):
        self.fact("requested", ["safetensors"])
        self.fact("unsupported", [])
        for state in STATES:
            with self.subTest(state=state):
                self.fact("exhaustive", state=state)
                result = self.result()
                self.assertEqual(result["decision"]["outcome"], "pass")
                self.assertEqual(result["inputs"]["exhaustive"]["state"], state)

    def test_unknown_negative_claim_inventory_cannot_become_an_empty_set(self):
        self.fact("requested", ["safetensors"])
        for state in STATES:
            with self.subTest(state=state):
                self.fact("unsupported", state=state)
                result = self.result()
                self.assertEqual((result["decision"]["outcome"], result["decision"]["reason"]),
                                 ("unknown", "unsupported_claims_unresolved"))
                self.assertEqual(result["inputs"]["unsupported"]["state"], state)
                self.assertNotIn("value", result["inputs"]["unsupported"])
        del self.values[answer_path(self.proposal, "unsupported")]
        self.assertEqual(self.result()["decision"]["reason"], "unsupported_claims_unresolved")
        self.fact("unsupported", [])
        self.assertEqual(self.result()["decision"]["outcome"], "pass")

    def test_each_request_or_applicability_state_remains_distinct_and_unknown(self):
        for field, state in itertools.product(("requested", "applies_when"), STATES):
            with self.subTest(field=field, state=state):
                self.setUp(); self.fact(field, state=state)
                result = self.result()
                self.assertEqual(result["decision"]["outcome"], "unknown")
                self.assertEqual(result["inputs"][field]["state"], state)
                self.assertEqual(result["decision"]["reason"],
                                 "requirement_unknown" if field == "requested" else "applicability_unknown")

    def test_false_applicability_needs_its_own_eligibility_to_skip(self):
        self.fact("applies_when", False)
        self.fact("requested", state="withheld")
        self.fact("unsupported", state="missing")
        for flag, expected in ((True, "skipped"), (False, "unknown"), (None, "unknown")):
            with self.subTest(flag=flag):
                result = self.result(eligible_inputs={"applies_when": flag})
                self.assertEqual(result["decision"]["outcome"], expected)
                self.assertIs(result["inputs"]["applies_when"]["value"], False)
                self.assertEqual(result["inputs"]["requested"]["state"], "withheld")

    def test_required_input_eligibility_is_independent_and_omission_is_unresolved(self):
        record = self.record()
        for field, flag in itertools.product(("applies_when", "requested", "cohort"), (False, None)):
            with self.subTest(field=field, flag=flag):
                flags = {**QUALIFIED, field: flag}
                result = record.evaluate(record.scope, enabled=True, eligible_inputs=flags)["x_t0_support_result"]
                self.assertEqual(result["decision"]["outcome"], "unknown")
                self.assertIs(result["evaluation"]["eligible_inputs"][field], flag)
                self.assertEqual(result["decision"]["reason"],
                                 field + ("_evidence_unresolved" if flag is None else "_evidence_ineligible"))
        self.assertEqual(record.evaluate(record.scope, enabled=True, eligible_inputs=QUALIFIED)
                         ["x_t0_support_result"]["decision"]["outcome"], "pass")
        self.assertEqual(record.evaluate(record.scope, enabled=True)
                         ["x_t0_support_result"]["decision"]["reason"], "applies_when_evidence_unresolved")
        for field in ("applies_when", "requested", "cohort"):
            flags = dict(QUALIFIED); del flags[field]
            self.assertEqual(self.result(eligible_inputs=flags)["decision"]["reason"],
                             field + "_evidence_unresolved")

    def test_activation_scope_and_applicability_have_separate_dispositions(self):
        record = self.record()
        for enabled, outcome, reason in ((False, "skipped", "selection_not_enabled"),
                                          (None, "unknown", "selection_activation_unknown")):
            result = record.evaluate(None, enabled=enabled)["x_t0_support_result"]
            self.assertEqual((result["decision"]["outcome"], result["decision"]["reason"]), (outcome, reason))
            self.assertEqual(len(result["inputs"]), 6)
        result = record.evaluate(None, enabled=True, eligible_inputs=QUALIFIED)["x_t0_support_result"]
        self.assertEqual(result["decision"]["reason"], "selection_scope_missing")

    def test_every_scope_dimension_must_match_exactly(self):
        record = self.record()
        for field in record.scope:
            for part in (("id", "version", "kind") if field == "item" else (None,)):
                with self.subTest(field=field, part=part):
                    selected = record.scope
                    if part == "kind": selected[field][part] = "model"
                    elif part is not None: selected[field][part] += "-other"
                    elif field.endswith("sha256"): selected[field] = "0" * 64
                    else: selected[field] += "-other"
                    result = record.evaluate(selected, enabled=True, eligible_inputs=QUALIFIED)["x_t0_support_result"]
                    self.assertEqual((result["decision"]["outcome"], result["decision"]["reason"]),
                                     ("unknown", "support_scope_mismatch"))
                    self.assertEqual(result["evaluation"]["selected_scope"], selected)

    def test_versioned_paths_do_not_reuse_another_query_cohort_or_selection(self):
        for section, field in (("query", "id"), ("query", "version"), ("cohort", "id"),
                               ("cohort", "version"), ("scope", "selection_id")):
            with self.subTest(section=section, field=field):
                self.setUp(); self.proposal[section][field] += "-other"
                result = self.result()
                self.assertEqual(result["decision"]["outcome"], "unknown")
                self.assertTrue(all(value == {"state": "missing"} for value in result["inputs"].values()))

    def test_opaque_tokens_and_requested_values_are_literal_and_case_sensitive(self):
        self.proposal["query"]["version"] = "v1/~candidate"
        self.proposal["cohort"]["version"] = "cohort/~v1"
        self.values.clear()
        for field, value in (("applies_when", True), ("requested", ["GGUF", "gguf", "format/~.1"]),
                              ("supported", ["format/~.1", "gguf"]), ("unsupported", []), ("exhaustive", False)):
            self.fact(field, value)
        result = self.result()
        self.assertEqual([f["outcome"] for f in result["decision"]["findings"]], ["unknown", "pass", "pass"])
        self.assertIn("v1~1~0candidate", result["inputs"]["requested"]["source_path"])
        self.assertIn("cohort~1~0v1", result["inputs"]["requested"]["source_path"])

    def test_unresolved_and_grouped_provided_parents_preserve_source_paths(self):
        parent = answer_path(self.proposal, "requested").rsplit("/", 1)[0]
        for state in STATES:
            with self.subTest(state=state):
                self.values.clear(); self.values[parent] = {"state": state}
                result = self.result()
                self.assertEqual(result["decision"]["outcome"], "unknown")
                self.assertTrue(all(v == {"state": state, "source_path": parent} for v in result["inputs"].values()))
        self.values[parent] = {"state": "provided", "source": "synthetic:grouped", "value": {
            "applies_when": True, "requested": ["gguf"], "requested_complete": True, "supported": ["gguf"],
            "unsupported": [], "exhaustive": False}}
        result = self.result()
        self.assertEqual(result["decision"]["outcome"], "pass")
        self.assertTrue(all(v["source_path"] == parent and v["source"] == "synthetic:grouped"
                            for v in result["inputs"].values()))
        del self.values[parent]["value"]["unsupported"]
        result = self.result()
        self.assertEqual(result["inputs"]["unsupported"], {"state": "missing", "source_path": parent})

    def test_duplicate_and_malformed_fields_reject_before_short_circuits(self):
        cases = [(f, v) for f in ("applies_when", "requested_complete", "exhaustive") for v in (0, 1, 1.0, "true", None, [], {})]
        cases += [(f, v) for f in ("requested", "supported", "unsupported")
                  for v in (None, "gguf", False, [None], [False], [0], [1.0], [""], ["   "], ["gguf", "gguf"])]
        for (field, value), applicable in itertools.product(cases, (False, None)):
            with self.subTest(field=field, value=value, applicable=applicable):
                self.setUp(); self.fact("applies_when", applicable, state="unknown" if applicable is None else "provided")
                self.fact(field, value)
                with self.assertRaisesRegex(ValueError, "invalid provided value"):
                    self.record()

    def test_input_identity_wire_rejects_unknown_fields_types_and_terminal_controls(self):
        for section, field, value in (("query", "id", "a"*120+"\n"), ("cohort", "id", "cohort.fixture\n"),
                ("query", "version", "v1\n"), ("cohort", "version", 1), ("scope", "selection_id", "sel_fixture\n"),
                ("query", "requirement", "contains"), ("query", "severity", "critical"),
                ("scope", "catalog_sha256", "a"*64+"\n"), ("scope", "conditions_sha256", "A"*64)):
            with self.subTest(section=section, field=field, value=value):
                self.setUp(); self.proposal[section][field] = value
                self.assertFalse(WIRE.is_valid(self.binding))
                with self.assertRaises(ValueError): self.record()
        self.setUp(); self.proposal["scope"]["item"]["kind"] = "invented_kind"
        with self.assertRaises(ValueError): self.record()
        self.setUp(); self.proposal["scope"]["item"]["version"] = "v1\x00"
        with self.assertRaises(ValueError): self.record()
        self.setUp(); self.proposal["extra"] = True
        with self.assertRaises(ValueError): self.record()

    def test_pointer_and_caller_shape_validation_precedes_disabled_skip(self):
        record = self.record()
        for pointer in ("", "spec.model_formats", "#/spec/model_formats", "/spec/~2", "/spec/~", "/spec\n"):
            with self.subTest(pointer=pointer):
                self.setUp(); self.proposal["scope"]["property"] = pointer
                self.assertFalse(WIRE.is_valid(self.binding))
                with self.assertRaises(ValueError): self.record()
                selected = record.scope; selected["property"] = pointer
                with self.assertRaises(ValueError): record.evaluate(selected, enabled=False)
        for value in (0, 1, 1.0, "true", [], {}):
            with self.subTest(value=value):
                with self.assertRaises(ValueError): record.evaluate(record.scope, enabled=value)
                with self.assertRaises(ValueError):
                    record.evaluate(record.scope, enabled=False, eligible_inputs={"cohort": value})
        for flags in ([], True, {"supported": True}, {"extra": None}):
            with self.subTest(flags=flags):
                with self.assertRaises(ValueError): record.evaluate(record.scope, enabled=False, eligible_inputs=flags)

    def test_overlapping_or_invalid_parent_traversals_are_not_missing_facts(self):
        parent = answer_path(self.proposal, "requested").rsplit("/", 1)[0]
        self.values[parent] = {"state": "unknown"}
        with self.assertRaisesRegex(ValueError, "overlapping"): self.record()
        for value in ([], False, "provided scalar", 0):
            with self.subTest(value=value):
                self.values.clear(); self.values[parent] = {"state": "provided", "value": value}
                with self.assertRaisesRegex(ValueError, "array index|scalar answer"): self.record()

    def test_strict_json_rejects_duplicates_nonfinite_and_invalid_unicode(self):
        invalid = [
            b'{"duplicate":1,"dupli\\u0063ate":1}',
            b'{"nested":{"duplicate":1,"duplicate":2}}',
            b'{"unrelated":NaN}', b'{"unrelated":Infinity}', b'{"unrelated":1e999}',
            b'{"unrelated":"\\ud800"}', b'{"\\udfff":"unrelated"}', b'\xff',
        ]
        for raw in invalid:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError): SupportQueryRecord(raw, ANSWERS_RAW)
                self.setUp(); self.proposal["answer_states_sha256"] = digest(raw)
                with self.assertRaises(ValueError): SupportQueryRecord(encode(self.binding), raw)
        for binding, answers in ((BINDING_RAW.decode(), ANSWERS_RAW), (BINDING_RAW, ANSWERS_RAW.decode())):
            with self.assertRaises(ValueError): SupportQueryRecord(binding, answers)

    def test_complete_answer_bytes_include_whitespace_and_unrelated_content(self):
        with self.assertRaisesRegex(ValueError, "answer bytes do not match"):
            SupportQueryRecord(BINDING_RAW, ANSWERS_RAW+b"\n")
        self.values["/unrelated"] = {"state": "provided", "value": True}
        with self.assertRaisesRegex(ValueError, "answer bytes do not match"):
            SupportQueryRecord(BINDING_RAW, encode(self.answers))

    def test_result_recomputation_rejects_tampering_that_shape_alone_accepts(self):
        record = SupportQueryRecord(BINDING_RAW, ANSWERS_RAW)
        mutations = [
            lambda r: r.update(binding_sha256="0"*64),
            lambda r: r.update(answer_states_sha256="0"*64),
            lambda r: r["query"].update(version="new-version"),
            lambda r: r["query"].update(severity="warning"),
            lambda r: r["cohort"].update(version="new-cohort"),
            lambda r: r["scope"]["item"].update(version="new-item"),
            lambda r: r["evaluation"]["eligible_inputs"].update(cohort=False),
            lambda r: r["evaluation"]["eligible_inputs"].update(requested_complete=False),
            lambda r: r["evaluation"]["eligible_inputs"].update(requested_complete=None),
            lambda r: r["inputs"]["requested_complete"].update(value=False),
            lambda r: r["inputs"].update(requested_complete={"state": "withheld",
                "source_path": r["inputs"]["requested_complete"]["source_path"]}),
            lambda r: r["inputs"]["requested"]["value"].append("fabricated-format"),
            lambda r: r["inputs"]["supported"].update(source="fabricated:source"),
            lambda r: r["decision"].update(outcome="fail"),
            lambda r: r["decision"].update(disputed=False),
            lambda r: r["decision"].update(source_id="another.cohort"),
            lambda r: r["decision"]["findings"].pop(),
            lambda r: r["decision"]["findings"].reverse(),
            lambda r: r["decision"]["findings"][1].update(outcome="pass", reason="documented_member", disputed=False),
        ]
        for mutate in mutations:
            result = json.loads(RESULT_RAW); mutate(result["x_t0_support_result"])
            with self.subTest(result=result):
                self.assertTrue(RESULT.is_valid(result))
                with self.assertRaisesRegex(ValueError, "does not match retained inputs"):
                    record.verify_result(encode(result), record.scope, enabled=True, eligible_inputs=QUALIFIED)

    def test_result_flags_cannot_supply_the_callers_missing_eligibility_or_scope(self):
        record = SupportQueryRecord(BINDING_RAW, ANSWERS_RAW)
        for enabled, flags, scope in ((True, None, record.scope), (True, QUALIFIED, None),
                                      (False, QUALIFIED, record.scope), (None, QUALIFIED, record.scope),
                                      (True, {**QUALIFIED, "cohort": False}, record.scope),
                                      (True, {**QUALIFIED, "requested_complete": None}, record.scope)):
            with self.subTest(enabled=enabled, flags=flags, scope=scope):
                with self.assertRaisesRegex(ValueError, "does not match retained inputs"):
                    record.verify_result(RESULT_RAW, scope, enabled=enabled, eligible_inputs=flags)

    def test_result_reader_rejects_wrong_wire_shapes_and_ambiguous_json(self):
        record = SupportQueryRecord(BINDING_RAW, ANSWERS_RAW)
        for mutate in (lambda r: r.update(extra=True), lambda r: r.update(proposal_version="cd3-0.1"),
                       lambda r: r["decision"].update(evidence_label="verified"),
                       lambda r: r["evaluation"].update(enabled=1),
                       lambda r: r["inputs"]["supported"].update(state="withheld")):
            result = json.loads(RESULT_RAW); mutate(result["x_t0_support_result"])
            self.assertFalse(RESULT.is_valid(result))
            with self.assertRaisesRegex(ValueError, "invalid CD-3 result"):
                record.verify_result(encode(result), record.scope, enabled=True, eligible_inputs=QUALIFIED)
        duplicate = RESULT_RAW.replace(b'"outcome": "pass"', b'"outcome": "pass", "outcome": "pass"', 1)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            record.verify_result(duplicate, record.scope, enabled=True, eligible_inputs=QUALIFIED)

    def test_full_query_hash_prevents_replay_but_result_formatting_can_differ(self):
        record = SupportQueryRecord(BINDING_RAW+b"\n", ANSWERS_RAW)
        with self.assertRaisesRegex(ValueError, "does not match retained inputs"):
            record.verify_result(RESULT_RAW, record.scope, enabled=True, eligible_inputs=QUALIFIED)
        original = SupportQueryRecord(BINDING_RAW, ANSWERS_RAW)
        reformatted = json.dumps(json.loads(RESULT_RAW), sort_keys=True).encode("utf-8")
        self.assertEqual(original.verify_result(reformatted, original.scope, enabled=True, eligible_inputs=QUALIFIED),
                         json.loads(RESULT_RAW))

    def test_returned_scopes_values_and_decisions_are_detached_from_record(self):
        record = SupportQueryRecord(BINDING_RAW, ANSWERS_RAW)
        first = record.evaluate(record.scope, enabled=True, eligible_inputs=QUALIFIED)
        mutated = first["x_t0_support_result"]
        mutated["inputs"]["supported"]["value"].clear()
        mutated["inputs"]["requested_complete"]["value"] = False
        mutated["evaluation"]["eligible_inputs"]["requested_complete"] = None
        mutated["scope"]["item"]["version"] = "edited"
        mutated["evaluation"]["selected_scope"]["item"]["id"] = "edited"
        mutated["query"]["severity"] = "warning"
        mutated["decision"]["findings"].clear()
        selected = record.scope; selected["item"]["id"] = "detached"
        self.assertEqual(record.evaluate(record.scope, enabled=True, eligible_inputs=QUALIFIED), json.loads(RESULT_RAW))


if __name__ == "__main__":
    unittest.main()
