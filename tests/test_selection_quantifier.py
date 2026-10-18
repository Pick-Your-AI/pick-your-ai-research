"""Synthetic CD-13 counterexamples; no vendor support or final wire claims."""

import copy
import importlib.util
import itertools
import json
from dataclasses import replace
from pathlib import Path
import unittest

from tests.selection_quantifier_prototype import Outcome, Rule, Selection, evaluate

PRIMARY = Selection("fixture.tool.primary", "tool", "primary")
SECONDARY = Selection("fixture.tool.secondary", "tool", "secondary")
THIRD = Selection("fixture.tool.third", "tool", "third")


def rule(*, applicable=None, assertions=None, kind="tool", severity="error"):
    return Rule(
        "rule.fixture.cd13",
        kind,
        severity,
        lambda selection: True if applicable is None else applicable.get(selection.id),
        lambda selection: True if assertions is None else assertions.get(selection.id),
    )


class SelectionQuantifierCases(unittest.TestCase):
    def test_all_enabled_roles_receive_individual_findings(self):
        result = evaluate(
            (PRIMARY, SECONDARY, THIRD),
            rule(assertions={PRIMARY.id: True, SECONDARY.id: False, THIRD.id: None}),
        )
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertEqual(result.reason, "counterexample")
        self.assertEqual(
            [(f.selection_id, f.outcome) for f in result.findings],
            [
                (PRIMARY.id, Outcome.PASS),
                (SECONDARY.id, Outcome.FAIL),
                (THIRD.id, Outcome.UNKNOWN),
            ],
        )

    def test_quantifier_does_not_require_a_primary_role(self):
        result = evaluate((SECONDARY, THIRD), rule())
        self.assertEqual(result.outcome, Outcome.PASS)
        self.assertEqual(len(result.findings), 2)

    def test_other_kinds_and_disabled_selections_do_not_run_predicates(self):
        called = []
        checked_rule = replace(
            rule(), assertion=lambda selection: called.append(selection.id) or True
        )
        result = evaluate(
            (
                PRIMARY,
                replace(SECONDARY, enabled=False),
                Selection("fixture.mcp.primary", "mcp_server", "primary"),
            ),
            checked_rule,
        )
        self.assertEqual(called, [PRIMARY.id])
        self.assertEqual([f.selection_id for f in result.findings], [PRIMARY.id])

    def test_absent_and_all_disabled_scope_is_skipped_without_vacuous_pass(self):
        for selections in ((), (replace(PRIMARY, enabled=False),)):
            with self.subTest(selections=selections):
                result = evaluate(selections, rule())
                self.assertEqual(result.outcome, Outcome.SKIPPED)
                self.assertEqual(result.reason, "no_enabled_selections")
                self.assertEqual(result.findings, ())

    def test_applicability_and_assertion_truth_table(self):
        cases = (
            (True, True, Outcome.PASS, "assertion_true", 1),
            (True, False, Outcome.FAIL, "assertion_false", 1),
            (True, None, Outcome.UNKNOWN, "eligible_evidence_missing", 1),
            (False, True, Outcome.SKIPPED, "not_applicable", 0),
            (False, False, Outcome.SKIPPED, "not_applicable", 0),
            (False, None, Outcome.SKIPPED, "not_applicable", 0),
            (None, True, Outcome.UNKNOWN, "applicability_unknown", 0),
            (None, False, Outcome.UNKNOWN, "applicability_unknown", 0),
            (None, None, Outcome.UNKNOWN, "applicability_unknown", 0),
        )
        for applicable, assertion, outcome, reason, calls in cases:
            with self.subTest(applicable=applicable, assertion=assertion):
                called = []
                checked_rule = replace(
                    rule(applicable={PRIMARY.id: applicable}),
                    assertion=lambda selection: called.append(selection.id)
                    or assertion,
                )
                result = evaluate((PRIMARY,), checked_rule)
                self.assertEqual(result.outcome, outcome)
                self.assertEqual(result.findings[0].reason, reason)
                self.assertEqual(len(called), calls)

    def test_all_inapplicable_is_distinct_from_no_enabled_selections(self):
        result = evaluate(
            (PRIMARY, SECONDARY),
            rule(applicable={PRIMARY.id: False, SECONDARY.id: False}),
        )
        self.assertEqual(result.outcome, Outcome.SKIPPED)
        self.assertEqual(result.reason, "none_applicable")
        self.assertEqual(len(result.findings), 2)

    def test_mixed_applicability_keeps_unknown_and_skipped_rows(self):
        result = evaluate(
            (PRIMARY, SECONDARY, THIRD),
            rule(applicable={PRIMARY.id: True, SECONDARY.id: None, THIRD.id: False}),
        )
        self.assertEqual(result.outcome, Outcome.UNKNOWN)
        self.assertEqual(
            [f.outcome for f in result.findings],
            [Outcome.PASS, Outcome.UNKNOWN, Outcome.SKIPPED],
        )

    def test_pass_plus_inapplicable_is_pass_with_fixed_severity(self):
        for severity in ("error", "warning", "info"):
            with self.subTest(severity=severity):
                checked_rule = rule(
                    applicable={PRIMARY.id: True, SECONDARY.id: False},
                    severity=severity,
                )
                result = evaluate((PRIMARY, SECONDARY), checked_rule)
                self.assertEqual(result.outcome, Outcome.PASS)
                self.assertEqual(result.severity, severity)
                self.assertEqual(result.rule_id, checked_rule.id)

    def test_order_does_not_hide_counterexample_or_change_attribution(self):
        selections = (PRIMARY, SECONDARY, THIRD)
        checked_rule = rule(
            assertions={PRIMARY.id: True, SECONDARY.id: None, THIRD.id: False}
        )
        expected = evaluate(selections, checked_rule)
        for permutation in itertools.permutations(selections):
            with self.subTest(order=[s.id for s in permutation]):
                self.assertEqual(evaluate(permutation, checked_rule), expected)

    def test_duplicate_primary_rejected_even_if_one_is_disabled(self):
        for enabled in (True, False):
            with self.subTest(enabled=enabled):
                duplicate = replace(SECONDARY, role="primary", enabled=enabled)
                with self.assertRaisesRegex(
                    ValueError, "ambiguous kind/role: tool/primary"
                ):
                    evaluate((PRIMARY, duplicate), rule())

    def test_duplicate_nonprimary_role_also_fails_identity_precondition(self):
        with self.assertRaisesRegex(ValueError, "ambiguous kind/role: tool/secondary"):
            evaluate((SECONDARY, replace(THIRD, role="secondary")), rule())

    def test_duplicate_id_cannot_overwrite_different_kind_or_disabled_selection(self):
        duplicate = Selection(PRIMARY.id, "mcp_server", "secondary", enabled=False)
        with self.assertRaisesRegex(ValueError, "duplicate selection id"):
            evaluate((PRIMARY, duplicate), rule())

    def test_role_is_scoped_to_kind(self):
        selections = (
            PRIMARY,
            Selection("fixture.mcp.primary", "mcp_server", "primary"),
        )
        self.assertEqual(evaluate(selections, rule()).outcome, Outcome.PASS)
        self.assertEqual(
            evaluate(selections, rule(kind="mcp_server")).outcome, Outcome.PASS
        )

    def test_preflight_rejects_entire_build_before_any_predicate_runs(self):
        called = []
        checked_rule = replace(
            rule(),
            applies_when=lambda selection: called.append(selection.id) or True,
        )
        invalid = (
            PRIMARY,
            Selection("fixture.mcp.one", "mcp_server", "primary"),
            Selection("fixture.mcp.two", "mcp_server", "primary"),
        )
        with self.assertRaisesRegex(ValueError, "ambiguous kind/role"):
            evaluate(invalid, checked_rule)
        self.assertEqual(called, [])

    def test_predicate_values_are_not_coerced_by_truthiness(self):
        for value in ("unknown", "false", 0, 1, [], {}):
            for field in ("applies_when", "assertion"):
                with self.subTest(value=value, field=field):
                    checked_rule = replace(rule(), **{field: lambda selection: value})
                    with self.assertRaisesRegex(ValueError, "normalized bool or None"):
                        evaluate((PRIMARY,), checked_rule)

    def test_frozen_v1_duplicate_primary_can_skip_before_proposed_preflight(self):
        contract = Path(__file__).resolve().parents[1] / "contracts/v1"
        spec = importlib.util.spec_from_file_location(
            "cd13_frozen_evaluator", contract / "reference/evaluate.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        build = json.loads((contract / "examples/build.json").read_text())
        catalog = json.loads((contract / "examples/catalog.json").read_text())
        ruleset = json.loads((contract / "baseline/core-ruleset.json").read_text())
        ruleset["rules"] = [
            r for r in ruleset["rules"] if r["id"] == "rule.agent.tools.framework"
        ]
        for selection in build["selections"]:
            if selection["kind"] == "agent_framework":
                selection["enabled"] = False
        before = module.Evaluator(build, catalog, ruleset).evaluate()["findings"][0]
        self.assertEqual(before["outcome"], "fail")
        duplicate = copy.deepcopy(
            next(s for s in build["selections"] if s["kind"] == "tool")
        )
        duplicate["id"] = "fixture.duplicate.tool"
        build["selections"].append(duplicate)
        after = module.Evaluator(build, catalog, ruleset).evaluate()["findings"][0]
        self.assertEqual(after["outcome"], "skipped")
        normalized = tuple(
            Selection(s["id"], s["kind"], s["role"], s["enabled"])
            for s in build["selections"]
        )
        with self.assertRaisesRegex(ValueError, "ambiguous kind/role: tool/primary"):
            evaluate(normalized, rule())


if __name__ == "__main__":
    unittest.main()
