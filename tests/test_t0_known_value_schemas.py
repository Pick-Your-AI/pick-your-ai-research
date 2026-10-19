"""Synthetic CD-1 known-value admission; no field or wire adoption evidence."""

from copy import deepcopy
import json
import unittest

from tests.t0_answer_state_prototype import (
    AnswerIndex, AnswerRule, PredicateResult, RulePolicy, State,
    evaluate_answer_rule,
)


PATH = "/synthetic/memory"
KNOWN = {"type": "string", "enum": ["none", "session", "persistent"]}
UNSAFE = {"type": "string", "enum": ["none", "session", "persistent", "unknown"]}


def encoded(value, state="provided"):
    record = {"state": state}
    if state == "provided":
        record.update(value=value, source="synthetic:explicit-input")
    return json.dumps({"x_t0_answer_states": {
        "proposal_version": "cd1-0.1", "answers": {PATH: record},
    }}, ensure_ascii=True).encode("utf-8")


class KnownValueSchemaCases(unittest.TestCase):
    def reject_schema(self, schema, value="unknown"):
        before = deepcopy(schema)
        raw = encoded(value)
        raw_before = bytes(raw)
        answers = AnswerIndex(raw)
        called = []
        with self.assertRaisesRegex(ValueError, "known-value schema"):
            answers.predicate(PATH, schema, lambda v: called.append(v) or True)
        self.assertEqual(called, [])
        self.assertEqual(raw, raw_before)
        self.assertEqual(schema, before)
        # Failed schema admission neither rewrites the retained value nor its state.
        answer = answers.read(PATH, {})
        self.assertIs(answer.state, State.PROVIDED)
        self.assertEqual(answer.value, value)
        self.assertEqual(answer.source, "synthetic:explicit-input")
        self.assertEqual(answer.source_path, PATH)

    def test_direct_enum_and_const_cannot_declare_unknown_known(self):
        for schema in (UNSAFE, {"const": "unknown"}):
            with self.subTest(schema=schema):
                self.reject_schema(schema)

    def test_unsafe_vocabulary_rejects_even_a_currently_known_answer(self):
        self.reject_schema(UNSAFE, "persistent")

    def test_typed_negation_cannot_turn_in_band_unknown_into_pass(self):
        raw = encoded("unknown")
        answers = AnswerIndex(raw)
        called = []
        rule = AnswerRule(
            id="synthetic.memory-required", severity="error",
            policy=RulePolicy.COMPATIBILITY,
            applies_when=lambda: PredicateResult(State.PROVIDED, True),
            assertion=lambda: answers.predicate(
                PATH, UNSAFE, lambda value: called.append(value) or value == "none",
            ).negated(),
        )
        with self.assertRaisesRegex(ValueError, "known-value schema"):
            evaluate_answer_rule(rule)
        self.assertEqual(called, [])
        self.assertEqual(raw, encoded("unknown"))

    def test_local_references_preserve_the_vocabulary_boundary(self):
        for name, ref in (("memory", "#/$defs/memory"),
                          ("a/b~c", "#/$defs/a~1b~0c"),
                          ("memory mode", "#/$defs/memory%20mode")):
            with self.subTest(ref=ref):
                self.reject_schema({"$ref": ref, "$defs": {name: UNSAFE}})

    def test_reference_jump_cannot_skip_a_nested_resource_ancestor(self):
        schema = {"$defs": {
            "safe": {"enum": ["persistent"]},
            "nested": {"$id": "https://example.invalid/child",
                       "$defs": {"safe": {"enum": ["unknown"]}},
                       "properties": {"selected": {"$ref": "#/$defs/safe"}}},
        }, "$ref": "#/$defs/nested/properties/selected"}
        for value in ("unknown", "persistent"):
            with self.subTest(value=value):
                self.reject_schema(schema, value)

    def test_schema_container_keys_named_id_are_not_resource_keywords(self):
        for schema in (
            {"$defs": {"$id": KNOWN}, "$ref": "#/$defs/$id"},
            {"properties": {"$id": KNOWN}, "$ref": "#/properties/$id"},
            {"$defs": {"group": {"properties": {"$id": KNOWN}}},
             "$ref": "#/$defs/group/properties/$id"},
        ):
            with self.subTest(schema=schema):
                before = deepcopy(schema)
                self.assertEqual(AnswerIndex(encoded("persistent")).read(PATH, schema).value, "persistent")
                self.assertEqual(schema, before)

    def test_reference_target_must_be_in_a_supported_schema_location(self):
        for schema in (
            {"default": KNOWN, "$ref": "#/default"},
            {"$defs": {"memory": KNOWN}, "$ref": "#/$defs"},
            {"examples": [KNOWN], "$ref": "#/examples/0"},
            {"contentSchema": KNOWN, "$ref": "#/contentSchema"},
        ):
            with self.subTest(schema=schema):
                self.reject_schema(schema, "persistent")

    def test_root_id_and_schema_array_references_keep_their_exact_target(self):
        for schema in (
            {"$id": "urn:synthetic:field", "$defs": {"memory": KNOWN}, "$ref": "#/$defs/memory"},
            {"allOf": [KNOWN], "$ref": "#/allOf/0"},
            {"$defs": {"any": True}, "$ref": "#/$defs/any"},
        ):
            with self.subTest(schema=schema):
                self.assertEqual(AnswerIndex(encoded("persistent")).read(PATH, schema).value, "persistent")

    def test_nested_object_and_array_values_are_checked(self):
        cases = (
            ({"type": "object", "properties": {"memory": UNSAFE}}, {"memory": "unknown"}),
            ({"type": "array", "items": UNSAFE}, ["unknown"]),
            ({"type": "array", "prefixItems": [UNSAFE]}, ["unknown"]),
            ({"type": "array", "contains": UNSAFE}, ["unknown"]),
            ({"type": "object", "additionalProperties": UNSAFE}, {"memory": "unknown"}),
            ({"type": "object", "patternProperties": {"^memory$": UNSAFE}}, {"memory": "unknown"}),
            ({"type": "object", "unevaluatedProperties": UNSAFE}, {"memory": "unknown"}),
            ({"type": "array", "unevaluatedItems": UNSAFE}, ["unknown"]),
        )
        for schema, value in cases:
            with self.subTest(schema=schema):
                self.reject_schema(schema, value)

    def test_finite_structured_values_do_not_hide_unknown_leaves(self):
        for value in ({"memory": "unknown"}, ["unknown"], {"nested": ["unknown"]}):
            for schema in ({"const": value}, {"enum": [value]}):
                with self.subTest(schema=schema):
                    self.reject_schema(schema, value)

    def test_combinators_and_conditional_schema_locations_are_checked(self):
        for keyword in ("allOf", "anyOf", "oneOf"):
            with self.subTest(keyword=keyword):
                self.reject_schema({keyword: [UNSAFE]})
        for keyword in ("if", "then", "else"):
            schema = {"if": {}, "then": {}, "else": {}, keyword: UNSAFE}
            with self.subTest(keyword=keyword):
                self.reject_schema(schema)
        self.reject_schema({"dependentSchemas": {"memory": {
            "properties": {"memory": UNSAFE},
        }}}, {"memory": "unknown"})

    def test_double_or_compound_negation_cannot_hide_finite_unknown(self):
        for schema in (
            {"not": {"not": {"const": "unknown"}}},
            {"not": {"oneOf": [{"const": "unknown"}, {"const": "unknown"}]}},
            {"not": {"$ref": "#/$defs/exclusion"},
             "$defs": {"exclusion": {"not": {"const": "unknown"}}}},
        ):
            with self.subTest(schema=schema):
                self.reject_schema(schema)

    def test_direct_finite_exclusions_keep_their_actual_not_semantics(self):
        for excluded in ({"const": "unknown"}, {"enum": ["unknown", "legacy"]}):
            schema = {"type": "string", "not": excluded}
            answer = AnswerIndex(encoded("persistent")).read(PATH, schema)
            self.assertEqual(answer.value, "persistent")
            called = []
            with self.assertRaisesRegex(ValueError, "invalid provided value"):
                AnswerIndex(encoded("unknown")).predicate(
                    PATH, schema, lambda v: called.append(v) or True,
                )
            self.assertEqual(called, [])

    def test_known_values_and_free_text_are_not_implicit_answer_states(self):
        for value in KNOWN["enum"]:
            answer = AnswerIndex(encoded(value)).read(PATH, KNOWN)
            self.assertIs(answer.state, State.PROVIDED)
            self.assertEqual(answer.value, value)
        for value in ("unknown", "", "Unknown", "UNKNOWN", "unknownish", " unknown ", "未知"):
            answer = AnswerIndex(encoded(value)).read(PATH, {"type": "string"})
            self.assertIs(answer.state, State.PROVIDED)
            self.assertEqual(answer.value, value)
        for value in ("Unknown", "UNKNOWN", "unknownish", " unknown ", "未知"):
            self.assertEqual(AnswerIndex(encoded(value)).read(PATH, {"const": value}).value, value)

    def test_false_zero_empty_and_null_keep_exact_known_value_types(self):
        for value in (False, 0, 0.0, None, [], {}, ""):
            with self.subTest(value=value):
                answer = AnswerIndex(encoded(value)).read(PATH, {"const": value})
                self.assertIs(type(answer.value), type(value))
                self.assertEqual(answer.value, value)

    def test_annotations_and_property_names_are_not_answer_values(self):
        schema = {"type": "string", "description": "unknown", "default": "unknown",
                  "examples": ["unknown"], "x-synthetic-note": {"const": "unknown"}}
        self.assertEqual(AnswerIndex(encoded("unknown")).read(PATH, schema).value, "unknown")
        schema = {"type": "object", "propertyNames": {"enum": ["unknown"]},
                  "properties": {"unknown": {"type": "string"}}, "required": ["unknown"]}
        value = {"unknown": "synthetic-known"}
        self.assertEqual(AnswerIndex(encoded(value)).read(PATH, schema).value, value)
        self.assertEqual(AnswerIndex(encoded(value)).read(PATH, {"const": value}).value, value)

    def test_safe_local_references_and_unused_state_definitions_remain_usable(self):
        schema = {"$ref": "#/$defs/memory", "$defs": {
            "memory": KNOWN, "unused_answer_state": {"enum": ["unknown", "withheld"]},
        }}
        before = deepcopy(schema)
        self.assertEqual(AnswerIndex(encoded("persistent")).read(PATH, schema).value, "persistent")
        self.assertEqual(schema, before)

    def test_reference_context_cannot_launder_values_through_property_names(self):
        schema = {"type": "object", "$defs": {"shared": {"const": "unknown"}},
                  "propertyNames": {"$ref": "#/$defs/shared"},
                  "properties": {"unknown": {"$ref": "#/$defs/shared"}}}
        self.reject_schema(schema, {"unknown": "unknown"})

    def test_unsupported_reference_forms_reject_without_predicates(self):
        for schema in (
            {"$ref": "https://example.invalid/field.schema.json"},
            {"$ref": "#memory", "$defs": {"memory": {"$anchor": "memory", **KNOWN}}},
            {"$dynamicRef": "#memory"},
            {"properties": {"memory": {"$id": "urn:synthetic:nested", **KNOWN}}},
            {"$schema": "http://json-schema.org/draft-07/schema#", **KNOWN},
            {"$ref": "#/$defs/missing"},
            {"$ref": "#/$defs/bad~2name", "$defs": {"bad~2name": KNOWN}},
            {"$ref": "#/$defs/memory%FF", "$defs": {"memory": KNOWN}},
            {"$ref": "#/enum/0", "enum": ["persistent"]},
        ):
            with self.subTest(schema=schema):
                self.reject_schema(schema, "persistent")

    def test_document_local_recursive_schema_is_checked_once_per_context(self):
        schema = {"type": "object", "properties": {
            "memory": KNOWN, "next": {"$ref": "#"},
        }}
        value = {"memory": "persistent", "next": {"memory": "session"}}
        self.assertEqual(AnswerIndex(encoded(value)).read(PATH, schema).value, value)
        schema["properties"]["memory"] = UNSAFE
        self.reject_schema(schema, value)

    def test_nonprogressing_recursive_application_is_a_controlled_input_error(self):
        self.reject_schema({"$ref": "#"}, "persistent")

    def test_unresolved_answers_keep_state_path_and_lazy_rule_policy(self):
        for state in (State.UNKNOWN, State.MISSING, State.WITHHELD, State.NOT_APPLICABLE):
            raw = encoded(None, state)
            called = []
            answer = AnswerIndex(raw).predicate(
                PATH, UNSAFE, lambda v: called.append(v) or True,
            )
            self.assertIs(answer.state, state)
            self.assertEqual(answer.source_path, PATH)
            self.assertIsNone(answer.compatibility_value())
            self.assertEqual(called, [])
            self.assertEqual(raw, encoded(None, state))


if __name__ == "__main__":
    unittest.main()
