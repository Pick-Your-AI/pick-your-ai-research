"""Synthetic CD-13 wire/CD-1 integration regressions; no vendor evidence."""

from copy import deepcopy
import itertools
import json
from pathlib import Path
import unittest

from tests.selection_binding_prototype import (
    SelectionRuleRecord, WIRE, WIRE_SCHEMA, answer_path, digest,
)
from tests.selection_quantifier_prototype import Outcome
from tests.t0_answer_state_prototype import State


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures"
BUILD_RAW = (ROOT / "contracts/v1/examples/build.json").read_bytes()
BINDING_RAW = (FIXTURES / "selection-binding.json").read_bytes()
ANSWERS_RAW = (FIXTURES / "selection-answers.json").read_bytes()


def encode(value):
    return (json.dumps(value, indent=2, allow_nan=False) + "\n").encode("utf-8")


def eligible(*ids, applies_when=True, assertion=True):
    return {identity: {"applies_when": applies_when, "assertion": assertion}
            for identity in ids or ("sel_tool",)}


class SelectionBindingTests(unittest.TestCase):
    def setUp(self):
        self.build = json.loads(BUILD_RAW)
        self.binding = json.loads(BINDING_RAW)
        self.answers = json.loads(ANSWERS_RAW)

    def fact(self, field, *, selection="sel_tool", state="provided", value=True):
        path = answer_path(selection, "rule.fixture.cd13", "0.1.0", field)
        self.answers["x_t0_answer_states"]["answers"][path] = (
            {"state": state, "value": value} if state == "provided" else {"state": state})

    def tool(self, identity="sel_tool_second", role="secondary", enabled=True):
        selection = deepcopy(next(s for s in self.build["selections"] if s["id"] == "sel_tool"))
        selection.update(id=identity, role=role, enabled=enabled)
        self.build["selections"].append(selection)
        return selection

    def raw(self):
        build, answers = encode(self.build), encode(self.answers)
        binding = deepcopy(self.binding)
        binding["x_t0_selection_rule"].update(build_sha256=digest(build),
                                             answer_states_sha256=digest(answers))
        return encode(binding), build, answers

    def record(self):
        return SelectionRuleRecord(*self.raw())

    def test_committed_binding_resolves_exact_fixture_and_retains_original_bytes(self):
        WIRE.check_schema(WIRE_SCHEMA)
        WIRE.validate(json.loads(BINDING_RAW))
        record = SelectionRuleRecord(BINDING_RAW, BUILD_RAW, ANSWERS_RAW)
        result = record.evaluate(eligible())
        self.assertEqual(record.original_bytes, (BINDING_RAW, BUILD_RAW, ANSWERS_RAW))
        self.assertEqual((result.result.outcome, result.result.rule_id, result.rule_version),
                         (Outcome.PASS, "rule.fixture.cd13", "0.1.0"))
        self.assertEqual(result.answers[0].assertion.source, "synthetic:normalized-assertion")
        self.assertEqual(result.result.findings[0].selection_id, "sel_tool")

    def test_every_enabled_role_keeps_counterexamples_and_unknowns_in_stable_order(self):
        self.tool(); self.tool("sel_tool_third", "third")
        self.fact("applies_when", selection="sel_tool_second")
        self.fact("assertion", selection="sel_tool_second", value=False)
        self.fact("applies_when", selection="sel_tool_third")
        self.fact("assertion", selection="sel_tool_third", state="withheld")
        permissions = eligible("sel_tool", "sel_tool_second", "sel_tool_third")
        first = self.record().evaluate(permissions)
        self.assertEqual(first.result.outcome, Outcome.FAIL)
        self.assertEqual([finding.outcome for finding in first.result.findings],
                         [Outcome.PASS, Outcome.FAIL, Outcome.UNKNOWN])
        self.assertEqual(first.answers[-1].assertion.state, State.WITHHELD)
        self.build["selections"].reverse()
        self.assertEqual(self.record().evaluate(permissions), first)

    def test_nonprimary_scope_is_evaluated_without_an_arbitrary_first_match(self):
        next(s for s in self.build["selections"] if s["id"] == "sel_tool")["role"] = "secondary"
        result = self.record().evaluate(eligible())
        self.assertEqual(result.result.outcome, Outcome.PASS)
        self.assertEqual(len(result.result.findings), 1)

    def test_empty_and_disabled_scope_are_skipped_without_a_vacuous_pass(self):
        self.binding["x_t0_selection_rule"]["rule"]["kind"] = "tool"
        next(s for s in self.build["selections"] if s["kind"] == "tool")["enabled"] = False
        disabled = self.record().evaluate()
        self.assertEqual((disabled.result.outcome, disabled.result.reason, disabled.result.findings),
                         (Outcome.SKIPPED, "no_enabled_selections", ()))
        self.assertEqual(len(disabled.answers), 1)
        self.build["selections"] = [s for s in self.build["selections"] if s["kind"] != "tool"]
        # These examples do not rely on links to the removed selection.
        self.build["links"] = [link for link in self.build["links"]
                               if "sel_tool" not in (link["from_selection_id"], link["to_selection_id"])]
        absent = self.record().evaluate()
        self.assertEqual((absent.result.outcome, absent.result.reason, absent.answers),
                         (Outcome.SKIPPED, "no_enabled_selections", ()))

    def test_all_unresolved_answer_states_keep_their_own_state_and_unknown_outcome(self):
        for field, state in itertools.product(("applies_when", "assertion"),
                ("unknown", "missing", "withheld", "not_applicable")):
            with self.subTest(field=field, state=state):
                self.setUp(); self.fact(field, state=state)
                result = self.record().evaluate(eligible())
                self.assertEqual(result.result.outcome, Outcome.UNKNOWN)
                self.assertEqual(getattr(result.answers[0], field).state, State(state))
                self.assertEqual(result.result.findings[0].reason,
                                 "applicability_unknown" if field == "applies_when"
                                 else "eligible_evidence_missing")

    def test_false_applicability_needs_eligible_evidence_before_it_can_skip(self):
        self.fact("applies_when", value=False)
        self.fact("assertion", state="withheld")
        for eligibility, expected in ((True, Outcome.SKIPPED), (False, Outcome.UNKNOWN),
                                       (None, Outcome.UNKNOWN)):
            with self.subTest(eligibility=eligibility):
                result = self.record().evaluate(eligible(applies_when=eligibility))
                self.assertEqual(result.result.outcome, expected)
                self.assertIs(result.answers[0].applies_when.value, False)
                self.assertEqual(result.answers[0].assertion.state, State.WITHHELD)
                self.assertIs(result.eligibility[0][1], eligibility)

    def test_assertion_ineligibility_or_omission_cannot_become_a_counterexample(self):
        self.fact("assertion", value=False)
        for eligibility, expected in ((True, Outcome.FAIL), (False, Outcome.UNKNOWN),
                                       (None, Outcome.UNKNOWN)):
            with self.subTest(eligibility=eligibility):
                self.assertEqual(self.record().evaluate(eligible(assertion=eligibility)).result.outcome,
                                 expected)
        omitted = self.record().evaluate({"sel_tool": {"applies_when": True}})
        self.assertEqual(omitted.result.outcome, Outcome.UNKNOWN)
        self.assertEqual(self.record().evaluate().result.reason, "unresolved_selection")

    def test_missing_paths_and_another_rule_version_do_not_reuse_known_facts(self):
        self.answers["x_t0_answer_states"]["answers"] = {}
        result = self.record().evaluate(eligible())
        self.assertEqual(result.answers[0].applies_when.state, State.MISSING)
        self.assertEqual(result.result.outcome, Outcome.UNKNOWN)
        self.setUp(); self.binding["x_t0_selection_rule"]["rule"]["version"] = "0.2.0"
        result = self.record().evaluate(eligible())
        self.assertEqual(result.rule_version, "0.2.0")
        self.assertEqual(result.answers[0].applies_when.state, State.MISSING)
        self.assertEqual(result.result.outcome, Outcome.UNKNOWN)

    def test_unknown_and_provided_parents_keep_cd1_state_and_source_paths(self):
        parent = "/selection_checks/sel_tool/rule.fixture.cd13/0.1.0"
        for state in ("unknown", "missing", "withheld", "not_applicable"):
            with self.subTest(state=state):
                self.answers["x_t0_answer_states"]["answers"] = {parent: {"state": state}}
                result = self.record().evaluate(eligible())
                self.assertEqual(result.result.outcome, Outcome.UNKNOWN)
                self.assertEqual(result.answers[0].assertion.state, State(state))
                self.assertEqual(result.answers[0].assertion.source_path, parent)
        self.answers["x_t0_answer_states"]["answers"] = {
            parent: {"state": "provided", "source": "synthetic:grouped",
                     "value": {"applies_when": True, "assertion": False}}}
        result = self.record().evaluate(eligible())
        self.assertEqual(result.result.outcome, Outcome.FAIL)
        self.assertEqual(result.answers[0].assertion.source_path, parent)
        self.assertEqual(result.answers[0].assertion.source, "synthetic:grouped")

    def test_malformed_provided_operands_reject_before_disable_or_applicability_shortcut(self):
        for value, shortcut in itertools.product((False, 0, 1, 1.0, "false", None, [], {}),
                                                 ("disabled", "inapplicable", "unresolved")):
            if value is False:
                continue  # False is a valid Boolean, never an unknown sentinel.
            with self.subTest(value=value, shortcut=shortcut):
                self.setUp()
                if shortcut == "disabled":
                    next(s for s in self.build["selections"] if s["id"] == "sel_tool")["enabled"] = False
                elif shortcut == "inapplicable": self.fact("applies_when", value=False)
                else: self.fact("applies_when", state="unknown")
                self.fact("assertion", value=value)
                with self.assertRaisesRegex(ValueError, "invalid provided value"):
                    self.record()
        self.setUp(); self.fact("applies_when", value="true")
        with self.assertRaisesRegex(ValueError, "invalid provided value"):
            self.record()

    def test_ambiguous_build_identity_rejects_even_in_disabled_or_unrelated_scope(self):
        for mode in ("duplicate_role", "duplicate_id", "unrelated_role"):
            with self.subTest(mode=mode):
                self.setUp()
                if mode == "duplicate_role": self.tool(role="primary", enabled=False)
                elif mode == "duplicate_id": self.tool(identity="sel_tool", enabled=False)
                else:
                    duplicate = deepcopy(next(s for s in self.build["selections"] if s["kind"] == "mcp_server"))
                    duplicate.update(id="sel_mcp_second", enabled=False)
                    self.build["selections"].append(duplicate)
                with self.assertRaisesRegex(ValueError, "duplicate selection id|ambiguous kind/role"):
                    self.record()

    def test_full_string_selection_and_role_boundaries_reject_terminal_newlines(self):
        for field in ("id", "role"):
            for maximum in (False, True):
                with self.subTest(field=field, maximum=maximum):
                    self.setUp()
                    selection = next(s for s in self.build["selections"] if s["kind"] == "mcp_server")
                    selection[field] = ("a" * (80 if field == "id" else 50)
                                        if maximum else selection[field]) + "\n"
                    with self.assertRaisesRegex(ValueError, "whole string"):
                        self.record()

    def test_exact_build_and_answer_bytes_including_unrelated_content_are_bound(self):
        for which in (1, 2):
            with self.subTest(which=which):
                raw = [BINDING_RAW, BUILD_RAW, ANSWERS_RAW]
                raw[which] += b"\n"
                with self.assertRaisesRegex(ValueError, "bytes do not match"):
                    SelectionRuleRecord(*raw)
        self.build["name"] += " unrelated edit"
        with self.assertRaisesRegex(ValueError, "build bytes do not match"):
            SelectionRuleRecord(BINDING_RAW, encode(self.build), ANSWERS_RAW)
        self.answers["x_t0_answer_states"]["answers"]["/unrelated"] = {"state": "unknown"}
        with self.assertRaisesRegex(ValueError, "answer_states bytes do not match"):
            SelectionRuleRecord(BINDING_RAW, BUILD_RAW, encode(self.answers))

    def test_wire_rejects_unknown_quantifiers_kinds_severity_and_malformed_rule_identity(self):
        for field, value in (("quantifier", "first_primary"), ("kind", "not_a_kind"),
                ("severity", "fail"), ("id", "rule.fixture.cd13\n"),
                ("id", "a" * 120 + "\n"), ("version", "0.1.0\n"),
                ("version", "0.1"), ("version", "")):
            with self.subTest(field=field, value=value):
                self.setUp(); self.binding["x_t0_selection_rule"]["rule"][field] = value
                self.assertFalse(WIRE.is_valid(self.binding))
                with self.assertRaisesRegex(ValueError, "invalid CD-13 binding"):
                    self.record()
        self.setUp(); self.build["revision"] = 1.0
        with self.assertRaisesRegex(ValueError, "JSON integer"):
            self.record()

    def test_duplicate_keys_nonfinite_values_and_wrong_byte_types_reject(self):
        def rebound(which, altered):
            raw = [BINDING_RAW, BUILD_RAW, ANSWERS_RAW]
            raw[which] = altered
            if which:
                proposal = json.loads(BINDING_RAW)
                key = "build_sha256" if which == 1 else "answer_states_sha256"
                proposal["x_t0_selection_rule"][key] = digest(altered)
                raw[0] = encode(proposal)
            return raw

        for which, old, new in (
                (0, b'"quantifier": "all_enabled"',
                 b'"quantifier": "all_enabled", "quantifier": "all_enabled"'),
                (1, b'"revision": 1', b'"revision": 1, "revision": 1'),
                (2, b'"value": true', b'"value": true, "value": true')):
            original = (BINDING_RAW, BUILD_RAW, ANSWERS_RAW)[which]
            altered = original.replace(old, new, 1)
            self.assertNotEqual(altered, original)
            with self.subTest(duplicate=which), self.assertRaisesRegex(ValueError, "duplicate"):
                SelectionRuleRecord(*rebound(which, altered))
        # These unrelated extension/answer values are otherwise schema-valid.
        # Correct hashes must not let non-finite input survive typed admission.
        for which, literal in itertools.product((1, 2), ("NaN", "Infinity", "1e999")):
            document = json.loads(BUILD_RAW if which == 1 else ANSWERS_RAW)
            if which == 1:
                document.setdefault("extensions", {})["x_nonfinite"] = "fixture_nonfinite_literal"
            else:
                document["x_t0_answer_states"]["answers"]["/unrelated"] = {
                    "state": "provided", "value": "fixture_nonfinite_literal"}
            altered = json.dumps(document).replace('"fixture_nonfinite_literal"', literal).encode()
            with self.subTest(which=which, literal=literal), self.assertRaises(ValueError):
                SelectionRuleRecord(*rebound(which, altered))
        for which in range(3):
            raw = [BINDING_RAW, BUILD_RAW, ANSWERS_RAW]
            raw[which] = raw[which].decode()
            with self.subTest(which=which), self.assertRaises(ValueError):
                SelectionRuleRecord(*raw)

    def test_invalid_parent_traversal_or_overlapping_answer_paths_are_input_errors(self):
        parent = "/selection_checks/sel_tool/rule.fixture.cd13/0.1.0"
        for value in (True, None, [], "not-an-object"):
            with self.subTest(value=value):
                self.answers["x_t0_answer_states"]["answers"] = {parent: {"state": "provided", "value": value}}
                with self.assertRaises(ValueError): self.record()
        self.setUp(); self.answers["x_t0_answer_states"]["answers"][parent] = {"state": "withheld"}
        with self.assertRaisesRegex(ValueError, "overlapping"):
            self.record()

    def test_eligibility_shape_rejects_aliases_and_unscoped_entries_before_evaluation(self):
        record = self.record()
        for values in ([], True, {"sel_nonexistent": {}}, {"sel_model": {}},
                       {"sel_tool": None}, {"sel_tool": {"unsupported": True}},
                       {"sel_tool": {"applies_when": 1}}, {"sel_tool": {"assertion": "true"}}):
            with self.subTest(values=values), self.assertRaisesRegex(ValueError, "eligibility"):
                record.evaluate(values)

    def test_repeated_evaluation_cannot_inherit_prior_eligibility_or_change_fixed_severity(self):
        for severity in ("info", "warning", "error"):
            self.binding["x_t0_selection_rule"]["rule"]["severity"] = severity
            record = self.record(); supplied = eligible()
            first = record.evaluate(supplied)
            supplied["sel_tool"]["assertion"] = False
            self.assertEqual(record.evaluate(supplied).result.outcome, Outcome.UNKNOWN)
            self.assertEqual(record.evaluate().result.outcome, Outcome.UNKNOWN)
            self.assertEqual((first.result.outcome, first.result.severity), (Outcome.PASS, severity))
            self.assertEqual(first.eligibility, (("sel_tool", True, True),))

    def test_no_framework_requirement_is_created_by_a_tool_scope(self):
        next(s for s in self.build["selections"] if s["kind"] == "agent_framework")["enabled"] = False
        self.assertEqual(self.record().evaluate(eligible()).result.outcome, Outcome.PASS)
        self.fact("applies_when", value=False)
        self.assertEqual(self.record().evaluate(eligible()).result.outcome, Outcome.SKIPPED)


if __name__ == "__main__":
    unittest.main()
