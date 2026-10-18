"""Synthetic required-presence regressions; no final wire or runtime claims."""

import copy
from dataclasses import replace
import importlib.util
import itertools
import json
from pathlib import Path
import unittest

from tests.required_presence_prototype import (
    PresenceRule, PresenceSelection, evaluate_required_presence,
)
from tests.selection_quantifier_prototype import Outcome, Rule, Selection, evaluate


PRIMARY = PresenceSelection("fixture.model.primary", "model", "primary", True)
SECONDARY = PresenceSelection("fixture.model.secondary", "model", "secondary", False)
THIRD = PresenceSelection("fixture.model.third", "model", "third", None)
REQUIRED = PresenceRule("rule.fixture.required", "model", "primary", "error")


def check(selections, rule=REQUIRED):
    # Every test tuple is a deliberately complete synthetic inventory. This
    # declaration does not establish completeness for any real Build.
    return evaluate_required_presence(selections, rule, inventory_complete=True)


class RequiredPresenceCases(unittest.TestCase):
    def test_known_absence_and_inactive_required_scope_never_skip(self):
        for selections in ((), (replace(PRIMARY, active=False),)):
            with self.subTest(selections=selections):
                result = check(selections)
                self.assertEqual((result.outcome, result.reason), (Outcome.FAIL, "not_selected"))
                self.assertNotEqual(result.outcome, Outcome.SKIPPED)
                self.assertEqual(
                    [(row.selection_id, row.active) for row in result.activations],
                    [(entry.id, entry.active) for entry in selections],
                )

    def test_unresolved_activation_is_not_disabled_or_absent(self):
        for selections, scoped_rule in (
            ((replace(PRIMARY, active=None),), REQUIRED),
            ((SECONDARY, THIRD), replace(REQUIRED, role=None)),
        ):
            with self.subTest(selections=selections):
                result = check(selections, scoped_rule)
                self.assertEqual((result.outcome, result.reason), (Outcome.UNKNOWN, "not_selected"))
                self.assertTrue(any(row.active is None for row in result.activations))
                self.assertNotEqual(result.outcome, Outcome.SKIPPED)

    def test_positive_witness_retains_other_scoped_activation_states(self):
        result = check((PRIMARY, SECONDARY, THIRD), replace(REQUIRED, role=None))
        self.assertEqual((result.outcome, result.reason), (Outcome.PASS, "selected"))
        self.assertEqual(
            [(row.selection_id, row.active) for row in result.activations],
            [(PRIMARY.id, True), (SECONDARY.id, False), (THIRD.id, None)],
        )
        # Only the known active witness establishes existence. The other
        # observations are retained; neither is converted into a passing fact.
        without_witness = check((SECONDARY, THIRD), replace(REQUIRED, role=None))
        self.assertEqual(without_witness.outcome, Outcome.UNKNOWN)

    def test_exact_primary_scope_cannot_borrow_other_kind_or_role(self):
        unrelated = PresenceSelection("fixture.tool.primary", "tool", "primary", True)
        active_secondary = replace(SECONDARY, active=True)
        for other_active in (True, False, None):
            others = (active_secondary, replace(unrelated, active=other_active))
            with self.subTest(other_active=other_active):
                absent = check(others)
                self.assertEqual((absent.outcome, absent.reason), (Outcome.FAIL, "not_selected"))
                self.assertEqual(absent.activations, ())
                inactive = check((replace(PRIMARY, active=False), *others))
                self.assertEqual(inactive.outcome, Outcome.FAIL)
                unresolved = check((replace(PRIMARY, active=None), *others))
                self.assertEqual(unresolved.outcome, Outcome.UNKNOWN)
                self.assertEqual([row.selection_id for row in unresolved.activations], [PRIMARY.id])

    def test_required_scope_can_explicitly_name_a_nonprimary_role(self):
        active_secondary = replace(SECONDARY, active=True)
        self.assertEqual(check((active_secondary,)).outcome, Outcome.FAIL)
        result = check((active_secondary,), replace(REQUIRED, role="secondary"))
        self.assertEqual(result.outcome, Outcome.PASS)
        self.assertEqual(result.role, "secondary")
        self.assertEqual(check((active_secondary,), replace(REQUIRED, role=None)).outcome, Outcome.PASS)

    def test_existing_universal_empty_and_inapplicable_scopes_still_skip(self):
        optional = Rule("rule.fixture.optional", "model", "warning", lambda s: False, lambda s: True)
        for selections in ((), (Selection(PRIMARY.id, "model", "primary", False),)):
            result = evaluate(selections, optional)
            self.assertEqual((result.outcome, result.reason), (Outcome.SKIPPED, "no_enabled_selections"))
        result = evaluate((Selection(PRIMARY.id, "model", "primary"),), optional)
        self.assertEqual((result.outcome, result.reason), (Outcome.SKIPPED, "none_applicable"))
        self.assertEqual(check(()).outcome, Outcome.FAIL)

    def test_rule_identity_scope_and_fixed_severity_survive_each_outcome(self):
        for severity in ("info", "warning", "error"):
            for active, expected in ((True, Outcome.PASS), (False, Outcome.FAIL), (None, Outcome.UNKNOWN)):
                with self.subTest(severity=severity, active=active):
                    scoped_rule = replace(REQUIRED, severity=severity)
                    result = check((replace(PRIMARY, active=active),), scoped_rule)
                    self.assertEqual(result.outcome, expected)
                    self.assertEqual((result.rule_id, result.kind, result.role, result.severity),
                                     (scoped_rule.id, scoped_rule.kind, scoped_rule.role, severity))

    def test_input_order_cannot_change_presence_or_activation_attribution(self):
        scoped_rule = replace(REQUIRED, role=None)
        expected = check((PRIMARY, SECONDARY, THIRD), scoped_rule)
        for selections in itertools.permutations((PRIMARY, SECONDARY, THIRD)):
            with self.subTest(order=[selection.id for selection in selections]):
                self.assertEqual(check(selections, scoped_rule), expected)

    def test_duplicate_ids_reject_before_a_known_witness_can_pass(self):
        for active in (True, False, None):
            with self.subTest(active=active):
                duplicate = PresenceSelection(PRIMARY.id, "tool", "secondary", active)
                with self.assertRaisesRegex(ValueError, "duplicate selection id"):
                    check((PRIMARY, duplicate))

    def test_strict_role_preflight_keeps_disabled_and_unrelated_ambiguity(self):
        for active in (True, False, None):
            with self.subTest(active=active):
                duplicate = replace(SECONDARY, role="primary", active=active)
                with self.assertRaisesRegex(ValueError, "ambiguous kind/role: model/primary"):
                    check((PRIMARY, duplicate))
                unrelated = (
                    PresenceSelection("fixture.tool.one", "tool", "backup", False),
                    PresenceSelection("fixture.tool.two", "tool", "backup", active),
                )
                with self.assertRaisesRegex(ValueError, "ambiguous kind/role: tool/backup"):
                    check((PRIMARY, *unrelated))

    def test_activation_never_accepts_boolean_aliases_or_generic_falsiness(self):
        for value in (0, 1, 0.0, 1.0, "true", "false", "unknown", "", [], {}, ()):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "activation must be exact"):
                    replace(PRIMARY, active=value)

    def test_malformed_identity_and_rule_text_are_precondition_errors(self):
        for field in ("id", "kind", "role"):
            for value in (None, 0, False, [], {}, "", " ", " model", "primary\n"):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(ValueError, "normalized text"):
                        replace(PRIMARY, **{field: value})
                    if field != "role" or value is not None:
                        with self.assertRaisesRegex(ValueError, "normalized text"):
                            replace(REQUIRED, **{field: value})
        for value in (None, 0, False, [], {}, "", "critical", " error"):
            with self.subTest(severity=value):
                with self.assertRaisesRegex(ValueError, "rule severity"):
                    replace(REQUIRED, severity=value)

    def test_activation_role_and_completeness_have_no_implicit_defaults(self):
        with self.assertRaises(TypeError):
            PresenceSelection(id=PRIMARY.id, kind=PRIMARY.kind, role=PRIMARY.role)
        with self.assertRaises(TypeError):
            PresenceRule(id=REQUIRED.id, kind=REQUIRED.kind, severity=REQUIRED.severity)
        with self.assertRaises(TypeError):
            evaluate_required_presence((), REQUIRED)

    def test_incomplete_or_malformed_inventory_cannot_prove_absence_or_presence(self):
        for complete in (False, None, 0, 1, "true", [], {}):
            for selections in ((), (PRIMARY,)):
                with self.subTest(complete=complete, selections=selections):
                    with self.assertRaisesRegex(ValueError, "explicitly complete"):
                        evaluate_required_presence(selections, REQUIRED, inventory_complete=complete)
        for selections in (None, "", [], [PRIMARY], ({"id": PRIMARY.id},),
                           (Selection(PRIMARY.id, PRIMARY.kind, PRIMARY.role),)):
            with self.subTest(selections=selections):
                with self.assertRaisesRegex(ValueError, "tuple of PresenceSelection"):
                    check(selections)
        with self.assertRaisesRegex(ValueError, "needs a PresenceRule"):
            check((), Rule("rule.fixture.optional", "model", "error", lambda s: True, lambda s: True))

    def test_frozen_foundation_style_reports_each_known_missing_primary(self):
        contract = Path(__file__).resolve().parents[1] / "contracts/v1"
        spec = importlib.util.spec_from_file_location("required_presence_frozen", contract / "reference/evaluate.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        build = json.loads((contract / "examples/build.json").read_text())
        catalog = json.loads((contract / "examples/catalog.json").read_text())
        ruleset = json.loads((contract / "baseline/core-ruleset.json").read_text())
        foundation = next(rule for rule in ruleset["rules"] if rule["id"] == "rule.required.foundation")
        ruleset["rules"] = [foundation]
        scopes = tuple((arg["value"]["ref"]["kind"], arg["value"]["ref"]["role"])
                       for arg in foundation["assert"]["args"])
        self.assertEqual(scopes, (("workload", "primary"), ("deployment_mode", "primary"),
                                  ("model", "primary"), ("context_policy", "primary")))

        def presence_rows(current):
            inventory = tuple(PresenceSelection(s["id"], s["kind"], s["role"], s["enabled"])
                              for s in current["selections"])
            return tuple(check(inventory, PresenceRule(foundation["id"], kind, role, foundation["severity"]))
                         for kind, role in scopes)

        self.assertEqual(module.Evaluator(build, catalog, ruleset).evaluate()["findings"][0]["outcome"], "pass")
        self.assertTrue(all(row.outcome == Outcome.PASS for row in presence_rows(build)))
        for kind, role in scopes:
            for mutation in ("absent", "disabled"):
                with self.subTest(kind=kind, role=role, mutation=mutation):
                    changed = copy.deepcopy(build)
                    if mutation == "absent":
                        changed["selections"] = [s for s in changed["selections"]
                                                 if not (s["kind"] == kind and s["role"] == role)]
                    else:
                        for selection in changed["selections"]:
                            if selection["kind"] == kind and selection["role"] == role:
                                selection["enabled"] = False
                    frozen = module.Evaluator(changed, catalog, ruleset).evaluate()["findings"][0]
                    self.assertEqual(frozen["outcome"], "fail")
                    rows = presence_rows(changed)
                    for row in rows:
                        expected = Outcome.FAIL if row.kind == kind else Outcome.PASS
                        self.assertEqual(row.outcome, expected)
                        if row.kind == kind:
                            self.assertEqual(row.reason, "not_selected")
                    # The existing universal mode still supplies its different,
                    # optional-component answer; it is not the presence mode.
                    old = evaluate(tuple(Selection(s["id"], s["kind"], s["role"], s["enabled"])
                                         for s in changed["selections"]),
                                   Rule(foundation["id"], kind, foundation["severity"], lambda s: True, lambda s: True))
                    self.assertEqual((old.outcome, old.reason), (Outcome.SKIPPED, "no_enabled_selections"))

    def test_foundation_style_preserves_unresolved_activation_per_required_kind(self):
        kinds = ("workload", "deployment_mode", "model", "context_policy")
        for unknown_kind in kinds:
            with self.subTest(unknown_kind=unknown_kind):
                inventory = tuple(PresenceSelection("fixture." + kind, kind, "primary",
                                                   None if kind == unknown_kind else True)
                                  for kind in kinds)
                for kind in kinds:
                    result = check(inventory, PresenceRule("rule.required.foundation", kind, "primary", "error"))
                    expected = Outcome.UNKNOWN if kind == unknown_kind else Outcome.PASS
                    self.assertEqual(result.outcome, expected)
                    if kind == unknown_kind:
                        self.assertEqual(result.reason, "not_selected")
                        self.assertIsNone(result.activations[0].active)


if __name__ == "__main__":
    unittest.main()
