"""Synthetic opt-in role-policy cases; no frozen or native policy adoption."""

from dataclasses import replace
import itertools
from types import SimpleNamespace
import unittest

from tests.required_presence_prototype import (
    PresenceRule, PresenceSelection, evaluate_required_presence,
)
from tests.selection_quantifier_prototype import (
    Outcome, RolePolicy, Rule, Selection, evaluate, validate_identities,
)


PRIMARY = Selection("fixture.primary", "tool", "primary", True)
ALTERNATIVE = Selection("fixture.alternative", "tool", "primary", False)


def rule(calls, *, kind="tool", severity="error", applicable=True, assertion=True):
    return Rule(
        "synthetic.role-policy", kind, severity,
        lambda selection: calls.append(("applies", selection.id)) or applicable,
        lambda selection: calls.append(("assertion", selection.id)) or assertion,
    )


class SelectionRolePolicyCases(unittest.TestCase):
    def test_default_and_explicit_build_wide_policy_preserve_strict_role_history(self):
        for flags in itertools.product((False, True), repeat=2):
            selections = (replace(PRIMARY, enabled=flags[0]),
                          replace(ALTERNATIVE, enabled=flags[1]))
            for keywords in ({}, {"role_policy": RolePolicy.BUILD_WIDE}):
                calls = []
                with self.subTest(flags=flags, keywords=keywords):
                    with self.assertRaisesRegex(ValueError, "ambiguous kind/role: tool/primary"):
                        evaluate(selections, rule(calls), **keywords)
                    self.assertEqual(calls, [])

    def test_selected_enabled_policy_allows_disabled_alternatives_in_every_order(self):
        for flags in ((False, False), (False, True), (True, False)):
            original = (replace(PRIMARY, enabled=flags[0]),
                        replace(ALTERNATIVE, enabled=flags[1]))
            for selections in itertools.permutations(original):
                calls = []
                before = tuple(selections)
                observed = evaluate(selections, rule(calls), role_policy=RolePolicy.ENABLED_ONLY)
                expected_ids = sorted(s.id for s in selections if s.enabled)
                with self.subTest(flags=flags, order=[s.id for s in selections]):
                    self.assertEqual(observed.outcome, Outcome.PASS if expected_ids else Outcome.SKIPPED)
                    self.assertEqual(observed.reason, "all_applicable_pass" if expected_ids
                                     else "no_enabled_selections")
                    self.assertEqual([f.selection_id for f in observed.findings], expected_ids)
                    self.assertEqual(calls, [(stage, sid) for sid in expected_ids
                                             for stage in ("applies", "assertion")])
                    self.assertEqual(selections, before)

    def test_enabling_a_same_role_alternative_rejects_before_any_predicate(self):
        original = (PRIMARY, ALTERNATIVE)
        first = evaluate(original, rule([]), role_policy=RolePolicy.ENABLED_ONLY)
        calls = []
        changed = (PRIMARY, replace(ALTERNATIVE, enabled=True))
        with self.assertRaisesRegex(ValueError, "ambiguous kind/role: tool/primary"):
            evaluate(changed, rule(calls), role_policy=RolePolicy.ENABLED_ONLY)
        self.assertEqual(calls, [])
        self.assertEqual(evaluate(original, rule([]), role_policy=RolePolicy.ENABLED_ONLY), first)
        self.assertFalse(ALTERNATIVE.enabled)

    def test_duplicate_ids_reject_globally_for_every_policy_and_activation_pair(self):
        for policy, flags in itertools.product(RolePolicy, itertools.product((False, True), repeat=2)):
            selections = (replace(PRIMARY, enabled=flags[0]),
                          Selection(PRIMARY.id, "model", "secondary", flags[1]))
            for order in itertools.permutations(selections):
                calls = []
                with self.subTest(policy=policy, flags=flags, order=[s.kind for s in order]):
                    with self.assertRaisesRegex(ValueError, "duplicate selection id"):
                        evaluate(order, rule(calls), role_policy=policy)
                    self.assertEqual(calls, [])

    def test_enabled_ambiguity_in_unqueried_kinds_and_nonprimary_roles_still_rejects(self):
        for role_name in ("primary", "secondary"):
            unrelated = (Selection("fixture.model.a", "model", role_name, True),
                         Selection("fixture.model.b", "model", role_name, True))
            for policy in RolePolicy:
                calls = []
                with self.subTest(role=role_name, policy=policy):
                    with self.assertRaisesRegex(ValueError, "ambiguous kind/role: model/" + role_name):
                        evaluate((PRIMARY, *unrelated), rule(calls), role_policy=policy)
                    self.assertEqual(calls, [])

    def test_roles_are_still_scoped_to_kind_and_all_enabled_roles_get_rows(self):
        selections = (PRIMARY, replace(ALTERNATIVE, role="secondary", enabled=True),
                      Selection("fixture.model", "model", "primary", True))
        for policy in RolePolicy:
            calls = []
            observed = evaluate(selections, rule(calls), role_policy=policy)
            with self.subTest(policy=policy):
                self.assertEqual(observed.outcome, Outcome.PASS)
                self.assertEqual([f.selection_id for f in observed.findings],
                                 [ALTERNATIVE.id, PRIMARY.id])
                self.assertNotIn(("applies", "fixture.model"), calls)

    def test_all_activation_inputs_validate_before_scope_and_predicate_shortcuts(self):
        for value in (None, 0, 1, 0.0, 1.0, "false", "unknown", "", [], {}, ()):
            malformed = Selection("fixture.unrelated", "model", "secondary", value)
            for selections in ((malformed,), (PRIMARY, malformed),
                               (replace(PRIMARY, enabled=False), malformed)):
                calls = []
                with self.subTest(value=value, ids=[s.id for s in selections]):
                    with self.assertRaisesRegex(ValueError, "exact Boolean enabled"):
                        evaluate(selections, rule(calls, applicable=False),
                                 role_policy=RolePolicy.ENABLED_ONLY)
                    self.assertEqual(calls, [])

    def test_new_policy_requires_normalized_tuple_records_without_consuming_an_iterator(self):
        iterator_calls = []

        def inventory():
            iterator_calls.append("iterated")
            yield PRIMARY

        records = SimpleNamespace(id="fixture.protocol-only", kind="tool", role="primary")
        for selections in ([PRIMARY], iter((PRIMARY,)), inventory(), (records,)):
            calls = []
            with self.subTest(type=type(selections).__name__):
                with self.assertRaisesRegex(ValueError, "tuple of Selection records"):
                    evaluate(selections, rule(calls), role_policy=RolePolicy.ENABLED_ONLY)
                self.assertEqual(calls, [])
        self.assertEqual(iterator_calls, [])

    def test_policy_choice_requires_the_typed_enum_and_never_uses_truthiness(self):
        for policy in (None, False, True, 0, 1, "build_wide", "enabled_only", [], {}):
            calls = []
            with self.subTest(policy=policy):
                with self.assertRaisesRegex(ValueError, "typed RolePolicy"):
                    evaluate((), rule(calls), role_policy=policy)
                self.assertEqual(calls, [])

    def test_policy_does_not_change_outcomes_reasons_severity_or_lazy_callbacks(self):
        for applicable, assertion, severity in itertools.product(
                (None, False, True), (None, False, True), ("info", "warning", "error")):
            current_calls, proposed_calls = [], []
            current = evaluate((PRIMARY, replace(ALTERNATIVE, role="alternative")),
                               rule(current_calls, severity=severity, applicable=applicable,
                                    assertion=assertion))
            proposed = evaluate((PRIMARY, ALTERNATIVE),
                                rule(proposed_calls, severity=severity, applicable=applicable,
                                     assertion=assertion), role_policy=RolePolicy.ENABLED_ONLY)
            with self.subTest(applicable=applicable, assertion=assertion, severity=severity):
                self.assertEqual(proposed, current)
                self.assertEqual(proposed_calls, current_calls)
                self.assertEqual(proposed.severity, severity)

    def test_selected_policy_preserves_counterexamples_unknown_rows_and_literal_id_order(self):
        selections = (PRIMARY, replace(ALTERNATIVE, role="secondary", enabled=True),
                      Selection("fixture.disabled", "tool", "primary", False))
        calls = []
        candidate = Rule("synthetic.mixed", "tool", "warning", lambda s: True,
                         lambda s: calls.append(s.id) or (False if s.id == PRIMARY.id else None))
        expected = evaluate(selections[:2], candidate)
        for order in itertools.permutations(selections):
            observed = evaluate(order, candidate, role_policy=RolePolicy.ENABLED_ONLY)
            self.assertEqual(observed, expected)
        self.assertEqual([f.outcome for f in expected.findings], [Outcome.UNKNOWN, Outcome.FAIL])
        self.assertEqual(expected.reason, "counterexample")
        self.assertNotIn("fixture.disabled", calls)

    def test_required_presence_keeps_its_existing_strict_tristate_policy(self):
        requirement = PresenceRule("rule.required.foundation", "model", "primary", "error")
        primary = PresenceSelection("fixture.model.a", "model", "primary", True)
        for active, outcome in ((True, Outcome.PASS), (False, Outcome.FAIL), (None, Outcome.UNKNOWN)):
            selection = replace(primary, active=active)
            observed = evaluate_required_presence((selection,), requirement, inventory_complete=True)
            with self.subTest(active=active):
                self.assertEqual(observed.outcome, outcome)
                duplicate = PresenceSelection("fixture.model.b", "model", "primary", active)
                with self.assertRaisesRegex(ValueError, "ambiguous kind/role"):
                    evaluate_required_presence((primary, duplicate), requirement, inventory_complete=True)
                with self.assertRaisesRegex(ValueError, "tuple of Selection records"):
                    validate_identities((selection,), role_policy=RolePolicy.ENABLED_ONLY)


if __name__ == "__main__":
    unittest.main()
