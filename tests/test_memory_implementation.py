"""Synthetic recovery-scope cases; no SDK, service or durability experiment."""

from dataclasses import replace
import json
from pathlib import Path
import unittest

from tests.memory_implementation_prototype import (
    PROPOSAL_VERSION,
    MemoryImplementation,
    MemoryRequirementRecord,
    RecoveryEvidence,
    evaluate_memory_requirement,
)
from tests.selection_quantifier_prototype import Outcome, Selection
from tests.t0_answer_state_prototype import (
    Answer,
    AnswerIndex,
    PredicateResult,
    RulePolicy,
    State,
)


SCOPE = "synthetic:preferences:subject-a:process-restart:v1"
CONFIG = "synthetic:application-configuration:v1"
LAYERS = "synthetic:retained-layer-inventory:v1"


def answer(value, path):
    return Answer(State.PROVIDED, value, "synthetic:fixture", path)


def missing(state, path):
    return Answer(state, source_path=path)


def fact(value, path="/evidence/fact"):
    return PredicateResult(State.PROVIDED, value, path)


def unresolved(state, path="/evidence/fact"):
    return PredicateResult(state, None, path)


def implementation(name="application", *, via="application", owner=None):
    evidence = RecoveryEvidence(
        name, owner, "persistent",
        SCOPE, CONFIG, LAYERS, "synthetic:recovery-witness:" + name,
        fact(True, "/evidence/eligible"), fact(True, "/evidence/support"),
    )
    return MemoryImplementation(
        name, via, owner,
        answer(CONFIG, "/implementation/configuration"),
        answer(LAYERS, "/implementation/layers"),
        fact(True, "/implementation/layers_complete"), evidence,
    )


def record(items=None, *, selections=()):
    if items is None:
        items = (implementation(),)
    return MemoryRequirementRecord(
        PROPOSAL_VERSION,
        answer("persistent", "/requirement/need"),
        answer(SCOPE, "/requirement/recovery"),
        answer(items, "/declaration"),
        fact(True, "/declaration_complete"),
        selections,
        True,
    )


def evaluate(value, policy=RulePolicy.COMPATIBILITY):
    return evaluate_memory_requirement(value, policy=policy)


class MemoryImplementationTests(unittest.TestCase):
    def assert_outcome(self, value, outcome, *, policy=RulePolicy.COMPATIBILITY):
        result = evaluate(value, policy)
        self.assertIs(result.rule.outcome, outcome)
        self.assertEqual(result.proposal_version, PROPOSAL_VERSION)
        return result

    def test_application_recovery_witness_needs_no_memory_or_framework_selection(self):
        value = record(selections=(Selection("unrelated-database", "storage", "primary"),))
        result = self.assert_outcome(value, Outcome.PASS)
        self.assertEqual(result.reason, "memory_implementation_witness")
        self.assertIsNone(result.findings[0].owner_selection_id)
        self.assertEqual(result.rule.rule_id, "rule.t4.memory.persistence.required")
        self.assertEqual((result.rule.severity, result.on_unknown), ("error", "review"))

    def test_framework_recovery_witness_needs_no_separate_memory_store(self):
        item = implementation("framework-path", via="agent_framework", owner="framework")
        result = self.assert_outcome(
            record((item,), selections=(Selection("framework", "agent_framework", "agent"),)),
            Outcome.PASS,
        )
        self.assertEqual(result.findings[0].owner_selection_id, "framework")

    def test_store_uses_qualified_configuration_evidence_without_backing_label_operand(self):
        item = implementation("configured-memory-path", via="memory_store", owner="store")
        result = self.assert_outcome(
            record((item,), selections=(Selection("store", "memory_store", "secondary"),)),
            Outcome.PASS,
        )
        self.assertEqual(result.findings[0].evidence_id, item.recovery.evidence_id)

    def test_store_or_relational_long_term_name_cannot_supply_missing_recovery_evidence(self):
        item = replace(
            implementation("long-term-relational-label", via="memory_store", owner="store"),
            recovery=None,
        )
        result = self.assert_outcome(
            record((item,), selections=(Selection("store", "memory_store", "primary"),)),
            Outcome.UNKNOWN,
        )
        self.assertEqual(result.findings[0].reason, "recovery_evidence_missing")

    def test_qualified_negative_recovery_counterexample_survives_unknown_layer_completeness(self):
        item = implementation("documented-volatile-only-configuration")
        item = replace(
            item,
            layers_complete=unresolved(State.UNKNOWN, "/layers/complete"),
            recovery=replace(item.recovery, supports_recovery=fact(False, "/recovery/counterexample")),
        )
        result = self.assert_outcome(record((item,)), Outcome.FAIL)
        self.assertEqual(result.reason, "memory_capability_mismatch")
        self.assertEqual(result.findings[0].reason, "recovery_scope_not_supported")

    def test_positive_recovery_needs_complete_retained_layers(self):
        inputs = [fact(False), fact(None)] + [
            unresolved(state) for state in
            (State.UNKNOWN, State.MISSING, State.WITHHELD, State.NOT_APPLICABLE)
        ]
        for completeness in inputs:
            with self.subTest(state=completeness.state, value=completeness.compatibility_value()):
                item = replace(implementation(), layers_complete=completeness)
                result = self.assert_outcome(record((item,)), Outcome.UNKNOWN)
                self.assertEqual(result.findings[0].reason, "layer_inventory_not_complete")
                self.assertIs(result.responsible_state, completeness.state)

    def test_positive_witness_does_not_require_complete_alternative_inventory(self):
        for completeness in (
            fact(False), fact(None), unresolved(State.UNKNOWN), unresolved(State.WITHHELD)
        ):
            with self.subTest(completeness=completeness):
                self.assert_outcome(
                    replace(record(), declaration_complete=completeness), Outcome.PASS
                )

    def test_negative_candidates_cannot_prove_absence_outside_incomplete_declaration(self):
        item = implementation()
        item = replace(item, recovery=replace(item.recovery, supports_recovery=fact(False)))
        for completeness in (
            fact(False), fact(None), unresolved(State.MISSING),
            unresolved(State.UNKNOWN), unresolved(State.NOT_APPLICABLE),
        ):
            with self.subTest(completeness=completeness):
                result = self.assert_outcome(
                    replace(record((item,)), declaration_complete=completeness), Outcome.UNKNOWN
                )
                self.assertEqual(result.reason, "implementation_inventory_not_complete")
                self.assertIs(result.findings[0].outcome, Outcome.FAIL)

    def test_complete_known_absence_fails_before_missing_recovery_boundary(self):
        for state in (State.UNKNOWN, State.MISSING, State.WITHHELD, State.NOT_APPLICABLE):
            with self.subTest(state=state):
                value = replace(record(()), requirement=missing(state, "/requirement/recovery"))
                result = self.assert_outcome(value, Outcome.FAIL)
                self.assertEqual(result.reason, "memory_implementation_missing")
                self.assertEqual(result.source_path, "/declaration")

    def test_empty_unqualified_declaration_is_unknown_without_default_completeness(self):
        for completeness in (
            fact(False), fact(None), unresolved(State.UNKNOWN),
            unresolved(State.MISSING), unresolved(State.WITHHELD),
            unresolved(State.NOT_APPLICABLE),
        ):
            with self.subTest(completeness=completeness):
                result = self.assert_outcome(
                    replace(record(()), declaration_complete=completeness), Outcome.UNKNOWN
                )
                self.assertEqual(result.reason, "implementation_inventory_not_complete")
                self.assertIs(result.responsible_state, completeness.state)

    def test_unrelated_enabled_store_is_not_a_declared_implementation_witness(self):
        value = record((), selections=(Selection("store", "memory_store", "primary"),))
        self.assert_outcome(value, Outcome.FAIL)

    def test_disabled_owner_cannot_witness_presence_and_scope_unknown_cannot_hide_absence(self):
        item = implementation("store-path", via="memory_store", owner="store")
        value = replace(
            record((item,), selections=(Selection("store", "memory_store", "primary", False),)),
            requirement=missing(State.UNKNOWN, "/requirement/recovery"),
        )
        result = self.assert_outcome(value, Outcome.FAIL)
        self.assertIs(result.findings[0].outcome, Outcome.SKIPPED)
        self.assertEqual(result.findings[0].reason, "owner_selection_disabled")

    def test_positive_alternative_retains_other_path_failure_and_unknown(self):
        good, bad, unknown = (implementation(name) for name in ("good", "bad", "unknown"))
        bad = replace(bad, recovery=replace(bad.recovery, supports_recovery=fact(False)))
        unknown = replace(unknown, recovery=None)
        result = self.assert_outcome(record((unknown, good, bad)), Outcome.PASS)
        self.assertEqual(
            [(item.implementation_id, item.outcome) for item in result.findings],
            [("bad", Outcome.FAIL), ("good", Outcome.PASS), ("unknown", Outcome.UNKNOWN)],
        )

    def test_unresolved_alternative_prevents_false_failure_when_no_path_passes(self):
        bad, unknown = implementation("bad"), implementation("unknown")
        bad = replace(bad, recovery=replace(bad.recovery, supports_recovery=fact(False)))
        unknown = replace(unknown, recovery=None)
        result = self.assert_outcome(record((bad, unknown)), Outcome.UNKNOWN)
        self.assertEqual(
            [item.outcome for item in result.findings], [Outcome.FAIL, Outcome.UNKNOWN]
        )

    def test_each_scope_identity_mismatch_withholds_positive_and_negative_evidence(self):
        for field in ("requirement_key", "configuration_key", "layer_inventory_key"):
            for support in (True, False):
                with self.subTest(field=field, support=support):
                    item = implementation()
                    evidence = replace(
                        item.recovery,
                        **{field: "synthetic:other-revision"},
                        supports_recovery=fact(support),
                    )
                    result = self.assert_outcome(
                        record((replace(item, recovery=evidence),)), Outcome.UNKNOWN
                    )
                    self.assertEqual(result.findings[0].reason, "recovery_evidence_scope_mismatch")

    def test_recovery_fact_cannot_be_retargeted_to_another_implementation(self):
        original = implementation("original")
        retargeted = replace(original, id="different-implementation")
        result = self.assert_outcome(record((retargeted,)), Outcome.UNKNOWN)
        self.assertEqual(result.findings[0].reason, "recovery_evidence_scope_mismatch")

    def test_recovery_fact_cannot_be_retargeted_to_another_same_kind_selected_owner(self):
        original = implementation("framework-path", via="agent_framework", owner="framework-a")
        retargeted = replace(original, owner_selection_id="framework-b")
        selections = (
            Selection("framework-a", "agent_framework", "a"),
            Selection("framework-b", "agent_framework", "b"),
        )
        result = self.assert_outcome(record((retargeted,), selections=selections), Outcome.UNKNOWN)
        self.assertEqual(result.findings[0].reason, "recovery_evidence_scope_mismatch")

    def test_recovery_fact_cannot_be_transferred_between_need_classes(self):
        value = replace(record(), need=answer("session", "/requirement/need"))
        result = self.assert_outcome(value, Outcome.UNKNOWN)
        self.assertEqual(result.findings[0].reason, "recovery_evidence_scope_mismatch")

    def test_ineligible_or_unresolved_evidence_supplies_no_recovery_verdict(self):
        eligibility = [fact(False), fact(None)] + [
            unresolved(state) for state in
            (State.UNKNOWN, State.MISSING, State.WITHHELD, State.NOT_APPLICABLE)
        ]
        for eligible in eligibility:
            for support in (True, False):
                with self.subTest(eligible=eligible, support=support):
                    item = implementation()
                    item = replace(
                        item,
                        recovery=replace(
                            item.recovery, eligible=eligible, supports_recovery=fact(support)
                        ),
                    )
                    result = self.assert_outcome(record((item,)), Outcome.UNKNOWN)
                    self.assertEqual(result.findings[0].reason, "recovery_evidence_not_eligible")
                    self.assertIs(result.responsible_state, eligible.state)

    def test_unresolved_recovery_support_cannot_skip_a_known_requirement(self):
        for support in [fact(None)] + [
            unresolved(state, "/recovery/support") for state in
            (State.UNKNOWN, State.MISSING, State.WITHHELD, State.NOT_APPLICABLE)
        ]:
            with self.subTest(support=support):
                item = implementation()
                item = replace(item, recovery=replace(item.recovery, supports_recovery=support))
                result = self.assert_outcome(record((item,)), Outcome.UNKNOWN)
                self.assertIs(result.responsible_state, support.state)

    def test_required_configuration_and_layers_preserve_unresolved_states(self):
        for field in ("configuration", "layer_inventory"):
            for state in (State.UNKNOWN, State.MISSING, State.WITHHELD, State.NOT_APPLICABLE):
                with self.subTest(field=field, state=state):
                    item = replace(
                        implementation(), **{field: missing(state, "/implementation/" + field)}
                    )
                    result = self.assert_outcome(record((item,)), Outcome.UNKNOWN)
                    self.assertIs(result.responsible_state, state)
                    self.assertEqual(result.source_path, "/implementation/" + field)

    def test_unknown_recovery_scope_retains_every_declared_path_finding(self):
        app = implementation()
        disabled = implementation("disabled", via="memory_store", owner="disabled-store")
        for state in (State.UNKNOWN, State.MISSING, State.WITHHELD, State.NOT_APPLICABLE):
            with self.subTest(state=state):
                value = replace(
                    record(
                        (app, disabled),
                        selections=(Selection("disabled-store", "memory_store", "primary", False),),
                    ),
                    requirement=missing(state, "/requirement/recovery"),
                )
                result = self.assert_outcome(value, Outcome.UNKNOWN)
                self.assertIs(result.responsible_state, state)
                self.assertEqual(
                    [finding.outcome for finding in result.findings],
                    [Outcome.UNKNOWN, Outcome.SKIPPED],
                )

    def test_need_answer_state_selects_compatibility_or_recommendation_policy(self):
        for state in (State.UNKNOWN, State.MISSING, State.WITHHELD):
            value = replace(record(), need=missing(state, "/requirement/need"))
            with self.subTest(state=state):
                compatibility = self.assert_outcome(value, Outcome.UNKNOWN)
                recommendation = self.assert_outcome(
                    value, Outcome.SKIPPED, policy=RulePolicy.RECOMMENDATION
                )
                self.assertIs(compatibility.rule.answer_state, state)
                self.assertIs(recommendation.rule.answer_state, state)
                self.assertEqual((recommendation.rule.severity, recommendation.on_unknown), ("warning", "defer"))
                self.assertEqual(recommendation.rule.rule_id, "W-R11")
                self.assertEqual(compatibility.findings, ())
                self.assertEqual(recommendation.findings, ())

    def test_explicit_no_need_or_inapplicable_need_skips_only_this_rule(self):
        for need in (
            answer("none", "/requirement/need"),
            missing(State.NOT_APPLICABLE, "/requirement/need"),
        ):
            for policy in RulePolicy:
                with self.subTest(need=need, policy=policy):
                    result = self.assert_outcome(
                        replace(record(), need=need), Outcome.SKIPPED, policy=policy
                    )
                    self.assertEqual(result.rule.position, "applies_when")
                    self.assertEqual(result.findings, ())

    def test_known_need_keeps_unresolved_declaration_unknown_for_both_policies(self):
        for state in (State.UNKNOWN, State.MISSING, State.WITHHELD, State.NOT_APPLICABLE):
            for policy in RulePolicy:
                with self.subTest(state=state, policy=policy):
                    value = replace(record(), declaration=missing(state, "/declaration"))
                    result = self.assert_outcome(value, Outcome.UNKNOWN, policy=policy)
                    self.assertIs(result.responsible_state, state)
                    self.assertEqual(result.rule.position, "assertion")

    def test_session_and_persistent_use_their_exact_required_scope(self):
        for need in ("session", "persistent"):
            scope = "synthetic:" + need + ":exact-boundary:v2"
            item = implementation()
            item = replace(
                item, recovery=replace(item.recovery, requirement_key=scope, memory_need=need)
            )
            value = replace(
                record((item,)),
                need=answer(need, "/requirement/need"),
                requirement=answer(scope, "/requirement/recovery"),
            )
            self.assert_outcome(value, Outcome.PASS)

    def test_no_implicit_truthiness_or_answer_values_in_terminal_report(self):
        result = self.assert_outcome(record(), Outcome.PASS)
        with self.assertRaises(TypeError):
            bool(result)
        with self.assertRaises(TypeError):
            bool(result.rule)
        report = repr(result)
        self.assertNotIn(SCOPE, report)
        self.assertNotIn(CONFIG, report)
        self.assertNotIn(LAYERS, report)

    def test_input_order_is_stable_and_original_records_are_not_mutated(self):
        a, b = implementation("a"), replace(implementation("b"), recovery=None)
        left, right = record((a, b)), record((b, a))
        before = repr((left, right))
        self.assertEqual(evaluate(left), evaluate(right))
        self.assertEqual(repr((left, right)), before)

    def test_version_record_and_policy_are_explicit_and_typed(self):
        for version in ("0.1.0", "memory-implementation/0.2.0", None, True):
            with self.subTest(version=version), self.assertRaises(ValueError):
                evaluate(replace(record(), proposal_version=version))
        with self.assertRaises(ValueError):
            evaluate({})
        with self.assertRaises(ValueError):
            evaluate(record(), "compatibility")

    def test_selection_inventory_completeness_rejects_false_unknown_and_numeric_aliases(self):
        for complete in (False, None, 0, 1, 1.0, "true"):
            with self.subTest(complete=complete), self.assertRaises(ValueError):
                evaluate(replace(record(), selection_inventory_complete=complete))

    def test_duplicate_disabled_or_unrelated_selection_ids_fail_before_applicability(self):
        selections = (
            Selection("same", "storage", "primary"),
            Selection("same", "model", "secondary", False),
        )
        value = replace(
            record(selections=selections), need=answer("none", "/requirement/need")
        )
        with self.assertRaisesRegex(ValueError, "duplicate selection id"):
            evaluate(value)

    def test_ambiguous_kind_role_is_invalid_even_when_both_selections_are_disabled(self):
        selections = (
            Selection("a", "storage", "primary", False),
            Selection("b", "storage", "primary", False),
        )
        with self.assertRaisesRegex(ValueError, "ambiguous kind/role"):
            evaluate(record(selections=selections))

    def test_duplicate_implementation_ids_are_input_errors(self):
        with self.assertRaisesRegex(ValueError, "duplicate memory implementation id"):
            evaluate(record((implementation(), implementation())))

    def test_missing_or_wrong_kind_owner_is_not_treated_as_incompatible_memory(self):
        item = implementation(via="agent_framework", owner="owner")
        for selections in (
            (), (Selection("owner", "memory_store", "primary"),),
            (Selection("another", "agent_framework", "primary"),),
        ):
            with self.subTest(selections=selections), self.assertRaisesRegex(ValueError, "exact selected kind"):
                evaluate(record((item,), selections=selections))

    def test_application_path_cannot_fabricate_a_selected_owner(self):
        with self.assertRaisesRegex(ValueError, "must not invent"):
            implementation(owner="fake-application-selection")

    def test_malformed_selection_enablement_and_collection_are_input_errors(self):
        for enabled in (None, 0, 1, 1.0, "true"):
            with self.subTest(enabled=enabled), self.assertRaises(ValueError):
                evaluate(record(selections=(Selection("x", "storage", "primary", enabled),)))
        for selections in ([], "store", (object(),)):
            with self.subTest(selections=selections), self.assertRaises(ValueError):
                evaluate(record(selections=selections))

    def test_malformed_provided_and_unresolved_answers_are_input_errors(self):
        for value in (None, True, 0, "long_term", [], {}):
            with self.subTest(need=value), self.assertRaises(ValueError):
                evaluate(replace(record(), need=answer(value, "/requirement/need")))
        for value in (None, [], "store", (object(),)):
            with self.subTest(declaration=value), self.assertRaises(ValueError):
                evaluate(replace(record(), declaration=answer(value, "/declaration")))
        with self.assertRaises(ValueError):
            evaluate(replace(record(), declaration=Answer(State.UNKNOWN, (implementation(),))))
        with self.assertRaises(ValueError):
            evaluate(replace(record(), need=Answer("provided", "persistent")))

    def test_recovery_and_completeness_facts_cannot_be_bare_booleans(self):
        item = implementation()
        with self.assertRaises(ValueError):
            replace(item, layers_complete=True)
        with self.assertRaises(ValueError):
            replace(item.recovery, eligible=True)
        with self.assertRaises(ValueError):
            replace(item.recovery, supports_recovery=False)
        with self.assertRaises(ValueError):
            evaluate(replace(record(), declaration_complete=True))

    def test_invalid_identity_and_scope_text_cannot_alias_a_valid_binding(self):
        for text in ("", " x", "x ", "\x00x", "x\n", "\ud800", "\udfff", True, 1):
            with self.subTest(text=repr(text)):
                with self.assertRaises(ValueError):
                    replace(implementation(), id=text)
                with self.assertRaises(ValueError):
                    replace(implementation().recovery, requirement_key=text)
                with self.assertRaises(ValueError):
                    replace(implementation().recovery, owner_selection_id=text)
                with self.assertRaises(ValueError):
                    evaluate(replace(record(), requirement=answer(text, "/requirement/recovery")))
        with self.assertRaises(ValueError):
            evaluate(replace(record(), need=answer("persistent", "/invalid~escape")))
        for need in (None, True, "none", "long_term"):
            with self.subTest(evidence_need=need), self.assertRaises(ValueError):
                replace(implementation().recovery, memory_need=need)

    def test_unicode_owner_and_scope_identity_are_exact_without_normalization(self):
        owner = "framework-α😀"
        item = implementation("記憶", via="agent_framework", owner=owner)
        self.assert_outcome(
            record((item,), selections=(Selection(owner, "agent_framework", "primary"),)),
            Outcome.PASS,
        )
        item = replace(item, recovery=replace(item.recovery, requirement_key="é"))
        value = replace(
            record((item,), selections=(Selection(owner, "agent_framework", "primary"),)),
            requirement=answer("e\u0301", "/requirement/recovery"),
        )
        self.assert_outcome(value, Outcome.UNKNOWN)

    def test_actual_cd1_reader_preserves_need_state_and_scoped_provided_answer(self):
        original = Path(__file__).with_name("fixtures") / "t0-answer-states.json"
        baseline = original.read_bytes()
        document = json.loads(baseline)
        document["x_t0_answer_states"]["answers"] = {
            "/synthetic_memory_need": {
                "state": "provided", "value": "persistent", "source": "user"
            }
        }
        raw = json.dumps(document)
        index = AnswerIndex(raw)
        schema = {"type": "string", "enum": ["none", "session", "persistent"]}
        known = index.read("/synthetic_memory_need", schema)
        absent = index.read("/different_synthetic_memory_need", schema)
        self.assert_outcome(replace(record(), need=known), Outcome.PASS)
        result = self.assert_outcome(replace(record(), need=absent), Outcome.UNKNOWN)
        self.assertIs(result.rule.answer_state, State.MISSING)
        self.assertEqual(result.rule.source_path, absent.source_path)
        self.assertIsNone(absent.source_path)
        self.assertEqual(original.read_bytes(), baseline)


if __name__ == "__main__":
    unittest.main()
