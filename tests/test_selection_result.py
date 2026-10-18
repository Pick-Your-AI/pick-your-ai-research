"""Synthetic structured rejection, evaluated-result and error-boundary cases."""

import copy
import itertools
import json
from dataclasses import asdict, replace
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from tests.required_presence_prototype import (
    PresenceRule,
    PresenceSelection,
    evaluate_required_presence,
)
from tests.selection_quantifier_prototype import (
    IdentityPreflightError,
    Rule,
    Selection,
    evaluate,
    validate_identities,
)
from tests.selection_result_prototype import PROPOSAL_VERSION, evaluate_structured


PRIMARY = Selection("fixture.tool.primary", "tool", "primary")
SECONDARY = Selection("fixture.tool.secondary", "tool", "secondary")


def fixture_rule(**changes):
    return replace(
        Rule("rule.fixture.cd13", "tool", "error", lambda _: True, lambda _: True),
        **changes,
    )


class SelectionResultCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name("fixtures") / "selection-result.schema.json"
        cls.schema = json.loads(path.read_text())
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)

    def checked(self, selections, rule=None):
        document = evaluate_structured(
            selections, rule or fixture_rule(), proposal_version=PROPOSAL_VERSION
        )
        self.validator.validate(document)
        self.assertEqual(json.loads(json.dumps(document)), document)
        return document

    def test_duplicate_id_has_code_and_exact_conflict_without_rule_outcome(self):
        duplicate = Selection(PRIMARY.id, "mcp_server", "secondary", False)
        document = self.checked((PRIMARY, duplicate))
        self.assertEqual(document, {
            "proposal_version": "cd13-result-0.1",
            "identity_policy": "strict_build_wide",
            "status": "rejected",
            "phase": "identity_preflight",
            "rule_id": "rule.fixture.cd13",
            "severity": "error",
            "rejection": {
                "reason_code": "duplicate_selection_id",
                "selection_id": PRIMARY.id,
            },
        })

    def test_duplicate_role_has_code_kind_and_role_without_exception_text(self):
        document = self.checked((PRIMARY, replace(SECONDARY, role="primary")))
        self.assertEqual(document["rejection"], {
            "reason_code": "ambiguous_selection_role", "kind": "tool", "role": "primary"
        })
        self.assertNotIn("message", json.dumps(document))
        self.assertNotIn("ambiguous kind/role", json.dumps(document))

    def test_all_activation_combinations_keep_strict_build_wide_rejection(self):
        for left, right in itertools.product((True, False), repeat=2):
            for mode in ("id", "role"):
                with self.subTest(left=left, right=right, mode=mode):
                    a = replace(PRIMARY, enabled=left)
                    b = replace(SECONDARY, enabled=right, **(
                        {"id": PRIMARY.id} if mode == "id" else {"role": "primary"}
                    ))
                    expected = self.checked((a, b))
                    self.assertEqual(expected["status"], "rejected")
                    self.assertEqual(self.checked((b, a)), expected)

    def test_unrelated_kind_conflict_rejects_before_any_callback(self):
        calls = []
        rule = fixture_rule(
            applies_when=lambda s: calls.append(("applies", s.id)) or True,
            assertion=lambda s: calls.append(("assertion", s.id)) or True,
        )
        inventory = (
            PRIMARY,
            Selection("fixture.mcp.a", "mcp_server", "primary"),
            Selection("fixture.mcp.b", "mcp_server", "primary", False),
        )
        for permutation in itertools.permutations(inventory):
            with self.subTest(inventory=permutation):
                document = self.checked(permutation, rule)
                self.assertEqual(document["rejection"]["kind"], "mcp_server")
                self.assertEqual(calls, [])

    def test_roles_remain_scoped_to_kind_and_include_nonprimary_ambiguity(self):
        distinct = (PRIMARY, Selection("fixture.mcp.a", "mcp_server", "primary"))
        self.assertEqual(self.checked(distinct)["status"], "evaluated")
        conflict = (SECONDARY, Selection("fixture.tool.third", "tool", "secondary"))
        self.assertEqual(self.checked(conflict)["rejection"]["role"], "secondary")

    def test_rejection_retains_fixed_severity_and_exact_rule_id(self):
        for severity in ("info", "warning", "error"):
            rule = fixture_rule(id="rule.fixture.another", severity=severity)
            with self.subTest(severity=severity):
                document = self.checked((PRIMARY, replace(SECONDARY, role="primary")), rule)
                self.assertEqual(document["severity"], severity)
                self.assertEqual(document["rule_id"], rule.id)

    def test_all_predicate_truth_pairs_retain_exact_evaluated_findings(self):
        for applicable, assertion in itertools.product((True, False, None), repeat=2):
            with self.subTest(applicable=applicable, assertion=assertion):
                rule = fixture_rule(applies_when=lambda _: applicable, assertion=lambda _: assertion)
                original = evaluate((PRIMARY,), rule)
                document = self.checked((PRIMARY,), rule)
                self.assertEqual(document["status"], "evaluated")
                self.assertNotIn("rejection", document)
                self.assertEqual(document["result"], json.loads(json.dumps(asdict(original))))

    def test_optional_empty_and_all_inapplicable_keep_distinct_skips(self):
        empty = self.checked(())
        disabled = self.checked((replace(PRIMARY, enabled=False),))
        inapplicable = self.checked((PRIMARY,), fixture_rule(applies_when=lambda _: False))
        self.assertEqual(empty["result"], disabled["result"])
        self.assertEqual(empty["result"]["reason"], "no_enabled_selections")
        self.assertEqual(inapplicable["result"]["reason"], "none_applicable")
        self.assertEqual(inapplicable["result"]["findings"][0]["outcome"], "skipped")

    def test_counterexample_keeps_other_unknown_rows_and_input_order_invariance(self):
        inventory = (PRIMARY, SECONDARY, Selection("fixture.tool.third", "tool", "third"))
        facts = {PRIMARY.id: True, SECONDARY.id: None, inventory[2].id: False}
        rule = fixture_rule(assertion=lambda s: facts[s.id])
        expected = self.checked(inventory, rule)
        self.assertEqual(expected["result"]["outcome"], "fail")
        self.assertEqual([f["outcome"] for f in expected["result"]["findings"]],
                         ["pass", "unknown", "fail"])
        for permutation in itertools.permutations(inventory):
            self.assertEqual(self.checked(permutation, rule), expected)

    def test_legacy_callers_still_receive_valueerror_with_exact_messages(self):
        cases = (
            ((PRIMARY, replace(SECONDARY, id=PRIMARY.id)),
             "duplicate selection id: " + PRIMARY.id, "duplicate_selection_id"),
            ((PRIMARY, replace(SECONDARY, role="primary")),
             "ambiguous kind/role: tool/primary", "ambiguous_selection_role"),
        )
        for inventory, message, code in cases:
            with self.subTest(code=code):
                for operation in (validate_identities, lambda rows: evaluate(rows, fixture_rule())):
                    with self.assertRaises(ValueError) as caught:
                        operation(inventory)
                    self.assertIs(type(caught.exception), IdentityPreflightError)
                    self.assertEqual(str(caught.exception), message)
                    self.assertEqual(caught.exception.reason_code, code)

    def test_required_presence_keeps_its_existing_error_boundary_and_outcomes(self):
        rule = PresenceRule("rule.fixture.required", "tool", "primary", "error")
        inventory = (PresenceSelection(PRIMARY.id, "tool", "primary", False),
                     PresenceSelection(SECONDARY.id, "tool", "primary", None))
        with self.assertRaisesRegex(ValueError, "ambiguous kind/role: tool/primary"):
            evaluate_required_presence(inventory, rule, inventory_complete=True)
        for active, outcome in ((True, "pass"), (False, "fail"), (None, "unknown")):
            result = evaluate_required_presence((replace(inventory[0], active=active),),
                                               rule, inventory_complete=True)
            self.assertEqual(result.outcome, outcome)

    def test_callback_valueerror_is_not_misreported_as_input_rejection(self):
        for position in ("applies_when", "assertion"):
            original = ValueError("synthetic callback failure")
            def fail(_):
                raise original
            with self.subTest(position=position):
                with self.assertRaises(ValueError) as caught:
                    self.checked((PRIMARY,), fixture_rule(**{position: fail}))
                self.assertIs(caught.exception, original)

    def test_callback_typed_identity_error_also_remains_an_execution_error(self):
        for position in ("applies_when", "assertion"):
            original = IdentityPreflightError("synthetic callback error", reason_code="duplicate_selection_id",
                                              selection_id="fixture.callback")
            def fail(_):
                raise original
            with self.subTest(position=position):
                with self.assertRaises(IdentityPreflightError) as caught:
                    self.checked((PRIMARY,), fixture_rule(**{position: fail}))
                self.assertIs(caught.exception, original)

    def test_invalid_predicate_values_keep_execution_errors_without_partial_result(self):
        for value in ("unknown", "false", 0, 1, [], {}):
            for position in ("applies_when", "assertion"):
                with self.subTest(value=value, position=position):
                    with self.assertRaisesRegex(ValueError, "normalized bool or None"):
                        self.checked((PRIMARY,), fixture_rule(**{position: lambda _: value}))

    def test_version_is_explicit_and_cannot_inherit_a_previous_result(self):
        calls = []
        rule = fixture_rule(assertion=lambda s: calls.append(s.id) or True)
        self.checked((PRIMARY,), rule)
        calls.clear()
        for version in (None, True, 1, "cd13-0.1", "cd13-result-0.2", "cd13-result-0.1\n"):
            with self.subTest(version=version):
                with self.assertRaisesRegex(ValueError, "unsupported CD-13 result"):
                    evaluate_structured((PRIMARY,), rule, proposal_version=version)
                self.assertEqual(calls, [])
        with self.assertRaises(TypeError):
            evaluate_structured((PRIMARY,), rule)
        self.assertEqual(calls, [])

    def test_malformed_python_records_are_not_accepted_as_normalized_facts(self):
        calls = []
        rule = fixture_rule(assertion=lambda s: calls.append(s.id) or True)
        inventories = ([PRIMARY], (object(),), (replace(PRIMARY, id=""),),
                       (replace(PRIMARY, kind=" tool"),), (replace(PRIMARY, role=None),))
        inventories += tuple((replace(PRIMARY, enabled=value),) for value in (None, 0, 1, "false"))
        for inventory in inventories:
            with self.subTest(inventory=inventory):
                with self.assertRaises(ValueError):
                    evaluate_structured(inventory, rule, proposal_version=PROPOSAL_VERSION)
        for malformed in (object(), replace(rule, id=""), replace(rule, kind=None),
                          replace(rule, severity="critical"), replace(rule, assertion=None)):
            with self.subTest(rule=malformed):
                with self.assertRaises(ValueError):
                    evaluate_structured((PRIMARY,), malformed, proposal_version=PROPOSAL_VERSION)
        self.assertEqual(calls, [])

    def test_result_schema_prevents_rejection_from_becoming_a_rule_outcome(self):
        rejected = self.checked((PRIMARY, replace(SECONDARY, role="primary")))
        evaluated = self.checked((PRIMARY,))
        candidates = []
        for status in ("pass", "fail", "unknown", "skipped", "evaluated"):
            candidates.append({**copy.deepcopy(rejected), "status": status})
        candidates += [
            {**copy.deepcopy(rejected), "result": evaluated["result"]},
            {**copy.deepcopy(rejected), "outcome": "unknown"},
            {**copy.deepcopy(rejected), "findings": []},
            {**copy.deepcopy(rejected), "phase": "evaluation"},
            {**copy.deepcopy(evaluated), "rejection": rejected["rejection"]},
            {**copy.deepcopy(evaluated), "identity_policy": "enabled_roles"},
            {**copy.deepcopy(evaluated), "proposal_version": "cd13-result-0.2"},
        ]
        for candidate in candidates:
            with self.subTest(candidate=candidate):
                self.assertFalse(self.validator.is_valid(candidate))
        for code in ("unknown", "assertion_false", "", None):
            candidate = copy.deepcopy(rejected)
            candidate["rejection"]["reason_code"] = code
            self.assertFalse(self.validator.is_valid(candidate))

    def test_original_inventory_and_repeated_result_objects_are_isolated(self):
        inventory = (PRIMARY, SECONDARY)
        before = tuple(asdict(s) for s in inventory)
        first = self.checked(inventory)
        expected = copy.deepcopy(first)
        first["result"]["findings"].clear()
        self.assertEqual(self.checked(inventory), expected)
        self.assertEqual(tuple(asdict(s) for s in inventory), before)


if __name__ == "__main__":
    unittest.main()
