"""Synthetic CD-4 truth tables and exact-scope integrity; no network execution."""

from copy import deepcopy
import itertools
import json
from pathlib import Path
import unittest

from tests.isolation_binding_prototype import (
    INVENTORIES, IsolationRecord, Outcome, WIRE, WIRE_SCHEMA, answer_path,
    digest, inventory_entries, inventory_path,
)
from tests.t0_answer_state_prototype import State


FIXTURES = Path(__file__).with_name("fixtures")
RAW = tuple((FIXTURES / name).read_bytes() for name in (
    "isolation-binding.json", "isolation-build.json", "isolation-answers.json"))
ENGINE = "sel_inference_engine"
MODEL = "sel_model"
MCP = "sel_mcp_server"
BOUNDARY = "boundary.fixture.local"
LOCAL = "endpoint.fixture.local"
OUTSIDE = "endpoint.fixture.publisher"


def encode(value):
    return (json.dumps(value, indent=2, allow_nan=False) + "\n").encode()


class IsolationBindingTests(unittest.TestCase):
    def setUp(self):
        self.binding, self.build, self.answers = map(json.loads, RAW)
        self.proposal = self.binding["x_t0_isolation"]
        self.facts = self.answers["x_t0_answer_states"]["answers"]

    def component(self, sid=ENGINE):
        return next(c for c in self.proposal["components"] if c["selection_id"] == sid)

    def fact(self, path, value=None, state="provided"):
        self.facts[path] = ({"state": state, "value": value, "source": "synthetic:mutation"}
                            if state == "provided" else {"state": state})

    def connection_path(self, field, sid=ENGINE, cid="conn.fixture.telemetry"):
        return answer_path(BOUNDARY, "components", sid, "connections", cid, field)

    def complete_path(self, inventory, sid=ENGINE):
        return inventory_path(BOUNDARY, sid, inventory,
                              inventory_entries(self.component(sid), inventory))

    def readiness_path(self, sid=MODEL):
        artifact = self.component(sid)["runtime_artifacts"][0]
        return answer_path(BOUNDARY, "components", sid, "runtime_artifacts",
                           artifact["id"], artifact["sha256"], "present_inside_boundary")

    def raw(self):
        build, answers = encode(self.build), encode(self.answers)
        self.proposal.update(build_sha256=digest(build), answer_states_sha256=digest(answers))
        return encode(self.binding), build, answers

    def record(self):
        return IsolationRecord(*self.raw())

    def result(self, changes=None):
        record = self.record()
        eligible = dict.fromkeys(record.answer_paths, True)
        eligible.update(changes or {})
        return record.evaluate(eligible)

    def test_committed_fixture_passes_with_fixed_policy_and_original_bytes(self):
        WIRE.check_schema(WIRE_SCHEMA)
        record = IsolationRecord(*RAW)
        result = record.evaluate(dict.fromkeys(record.answer_paths, True))
        self.assertEqual(record.original_bytes, RAW)
        self.assertEqual((result.outcome, result.rule_id, result.rule_version,
                          result.severity, result.on_unknown),
                         (Outcome.PASS, "W-R8", "cd4-0.1", "error", "block"))
        reasons = {check.reason for check in result.checks}
        self.assertIn("connection_disabled", reasons)
        self.assertIn("provisioning_only_connection", reasons)
        self.assertIn("connection_stays_inside", reasons)
        self.assertEqual(dict(result.answers)["/workload/network"].source, "synthetic:cd4-scenario")

    def test_external_runtime_telemetry_fails_even_without_workload_data(self):
        # W-R8 has no exception based on a telemetry purpose or optionality.
        self.fact(self.connection_path("state"), "enabled")
        result = self.result()
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertIn("enabled_runtime_egress", {check.reason for check in result.checks})

    def test_connection_truth_table_preserves_logical_unknowns(self):
        for state, lifecycle, inside in itertools.product(
                ("enabled", "disabled", None), ("runtime", "provisioning", None), (True, False, None)):
            with self.subTest(state=state, lifecycle=lifecycle, inside=inside):
                self.setUp()
                self.fact(self.connection_path("state"), state,
                          "unknown" if state is None else "provided")
                self.fact(self.connection_path("lifecycle"), lifecycle,
                          "unknown" if lifecycle is None else "provided")
                self.fact(answer_path(BOUNDARY, "endpoints", OUTSIDE, "inside_boundary"), inside,
                          "unknown" if inside is None else "provided")
                if state == "disabled" or lifecycle == "provisioning" or inside is True:
                    expected = Outcome.PASS
                elif state == "enabled" and lifecycle == "runtime" and inside is False:
                    expected = Outcome.FAIL
                else:
                    expected = Outcome.UNKNOWN
                self.assertEqual(self.result().outcome, expected)

    def test_provisioning_download_does_not_prove_runtime_artifact_readiness(self):
        self.fact(self.readiness_path(), False)
        result = self.result()
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertIn("exact_runtime_artifact_not_ready", {check.reason for check in result.checks})
        self.fact(self.readiness_path(), state="unknown")
        self.assertEqual(self.result().outcome, Outcome.UNKNOWN)

    def test_known_counterexamples_survive_incomplete_or_absent_other_inventory(self):
        self.fact(self.connection_path("state"), "enabled")
        self.proposal["components"] = [c for c in self.proposal["components"] if c["selection_id"] != MODEL]
        self.fact(self.complete_path("runtime_artifacts"), False)
        result = self.result()
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertTrue(any(check.reason == "component_inventory_missing" for check in result.checks))
        self.assertTrue(any(check.reason == "inventory_coverage_unknown" for check in result.checks))

    def test_missing_empty_and_incomplete_inventories_are_distinct(self):
        for mode in ("component_missing", "answer_missing", "incomplete", "empty_complete"):
            with self.subTest(mode=mode):
                self.setUp()
                if mode == "component_missing":
                    self.proposal["components"] = [c for c in self.proposal["components"] if c["selection_id"] != MODEL]
                elif mode == "answer_missing":
                    del self.facts[self.complete_path("connections", MODEL)]
                elif mode == "incomplete":
                    self.fact(self.complete_path("connections", MODEL), False)
                self.assertEqual(self.result().outcome,
                                 Outcome.PASS if mode == "empty_complete" else Outcome.UNKNOWN)

    def test_removing_descriptors_cannot_reuse_previous_completeness(self):
        for inventory, key in (("connections", "connections"),
                               ("runtime_endpoints", "runtime_endpoint_ids"),
                               ("runtime_artifacts", "runtime_artifacts")):
            with self.subTest(inventory=inventory):
                self.setUp()
                old = self.complete_path(inventory)
                self.component()[key] = []
                new = self.complete_path(inventory)
                self.assertNotEqual(old, new)
                result = self.result()
                self.assertEqual(result.outcome, Outcome.UNKNOWN)
                self.assertEqual(dict(result.answers)[new].state, State.MISSING)
        # An explicit new reviewed completeness answer can attest an empty list;
        # it cannot be obtained by changing the inventory declaration alone.
        self.fact(new, True)
        self.assertEqual(self.result().outcome, Outcome.PASS)

    def test_artifact_presence_is_scoped_to_exact_required_digest(self):
        old = self.readiness_path()
        self.component(MODEL)["runtime_artifacts"][0]["sha256"] = "a" * 64
        self.fact(self.complete_path("runtime_artifacts", MODEL), True)
        self.assertNotEqual(self.readiness_path(), old)
        result = self.result()
        self.assertEqual(result.outcome, Outcome.UNKNOWN)
        self.assertEqual(dict(result.answers)[self.readiness_path()].state, State.MISSING)

    def test_runtime_endpoint_outside_fails_without_relying_on_an_egress_edge(self):
        self.component(MCP)["connections"] = []
        self.fact(self.complete_path("connections", MCP), True)
        self.fact(answer_path(BOUNDARY, "endpoints", LOCAL, "inside_boundary"), False)
        result = self.result()
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertTrue(any(c.selection_id == MCP and c.reason == "runtime_endpoint_outside"
                            for c in result.checks))

    def test_nonprimary_and_additional_kind_selections_cannot_disappear(self):
        next(s for s in self.build["selections"] if s["id"] == ENGINE)["role"] = "secondary"
        self.fact(self.connection_path("state"), "enabled")
        result = self.result()
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertTrue(any(c.selection_id == ENGINE and c.reason == "enabled_runtime_egress"
                            for c in result.checks))
        self.setUp()
        added = deepcopy(next(s for s in self.build["selections"] if s["id"] == MCP))
        added.update(id="sel_mcp_second", role="secondary")
        self.build["selections"].append(added)
        result = self.result()
        self.assertEqual(result.outcome, Outcome.UNKNOWN)
        self.assertTrue(any(c.selection_id == "sel_mcp_second" and c.reason == "component_inventory_missing"
                            for c in result.checks))

    def test_operator_and_legacy_build_mode_do_not_decide_isolation(self):
        for mode in ("api", "managed", "self_hosted", "hybrid"):
            with self.subTest(mode=mode):
                self.setUp()
                # These are descriptive synthetic extensions, not a schema release.
                self.build["extensions"] = {"x_synthetic_mode": mode, "x_operator": "provider"}
                self.assertEqual(self.result().outcome, Outcome.PASS)
                self.fact(self.connection_path("state"), "enabled")
                self.assertEqual(self.result().outcome, Outcome.FAIL)

    def test_eligibility_is_per_answer_and_never_inferred_from_source_labels(self):
        record = self.record()
        self.assertEqual(record.evaluate().outcome, Outcome.UNKNOWN)
        # A known negative endpoint membership becomes a counterexample only
        # when the destination, lifecycle, enabled state AND membership qualify.
        self.fact(self.connection_path("state"), "enabled")
        paths = [self.connection_path(field) for field in ("state", "lifecycle", "destination_id")]
        paths.append(answer_path(BOUNDARY, "endpoints", OUTSIDE, "inside_boundary"))
        for path, eligible in itertools.product(paths, (False, None)):
            with self.subTest(path=path, eligible=eligible):
                result = self.result({path: eligible})
                self.assertEqual(result.outcome, Outcome.UNKNOWN)
                self.assertIs(dict(result.eligibility)[path], eligible)
        self.assertEqual(self.result().outcome, Outcome.FAIL)

    def test_unresolved_answer_states_and_parent_provenance_are_retained(self):
        path = self.readiness_path()
        for state in ("unknown", "missing", "withheld", "not_applicable"):
            with self.subTest(state=state):
                self.setUp(); self.fact(path, state=state)
                result = self.result()
                self.assertEqual(result.outcome, Outcome.UNKNOWN)
                self.assertEqual(dict(result.answers)[path].state, State(state))
        parent = answer_path(BOUNDARY, "components", MODEL)
        self.facts = {key: value for key, value in self.facts.items() if not key.startswith(parent + "/")}
        self.answers["x_t0_answer_states"]["answers"] = self.facts
        self.fact(parent, state="withheld")
        result = self.result()
        self.assertEqual(result.outcome, Outcome.UNKNOWN)
        self.assertEqual(dict(result.answers)[path].source_path, parent)

    def test_network_and_boundary_answers_preserve_applicability_and_scope(self):
        for network in ("online", "private_network"):
            with self.subTest(network=network):
                self.fact("/workload/network", network)
                self.assertEqual(self.result().outcome, Outcome.SKIPPED)
                self.assertEqual(self.result({"/workload/network": False}).outcome, Outcome.UNKNOWN)
        for state in ("unknown", "missing", "withheld", "not_applicable"):
            self.fact("/workload/network", state=state)
            self.assertEqual(self.result().outcome, Outcome.UNKNOWN)
        self.fact("/workload/network", "air_gapped")
        self.fact("/workload/isolation_boundary_id", "boundary.fixture.other")
        self.assertEqual(self.result().reason, "isolation_boundary_mismatch")
        self.fact("/workload/isolation_boundary_id", state="unknown")
        self.assertEqual(self.result().reason, "isolation_boundary_unknown")

    def test_disabled_selection_skips_counterexample_but_not_input_validation(self):
        self.fact(self.connection_path("state"), "enabled")
        next(s for s in self.build["selections"] if s["id"] == ENGINE)["enabled"] = False
        result = self.result()
        self.assertEqual(result.outcome, Outcome.PASS)
        self.assertFalse(any(check.selection_id == ENGINE for check in result.checks))
        self.assertIn(self.connection_path("state"), dict(result.answers))
        self.fact(self.connection_path("state"), "false")
        with self.assertRaisesRegex(ValueError, "invalid provided value"):
            self.record()

    def test_no_enabled_selections_are_skipped_without_vacuous_success(self):
        for selection in self.build["selections"]:
            selection["enabled"] = False
        result = self.result()
        self.assertEqual((result.outcome, result.reason, result.checks),
                         (Outcome.SKIPPED, "no_enabled_selections", ()))

    def test_malformed_values_reject_before_inapplicable_or_ineligible_shortcut(self):
        cases = [(self.complete_path("connections"), value) for value in (0, 1, 1.0, "true", None, [], {})]
        cases += [(self.connection_path("lifecycle"), "unknown"),
                  (self.connection_path("state"), False),
                  ("/workload/network", "unknown"),
                  (self.connection_path("destination_id"), LOCAL + "\n")]
        for path, value in cases:
            with self.subTest(path=path, value=value):
                self.setUp(); self.fact(path, value)
                if path != "/workload/network": self.fact("/workload/network", "online")
                with self.assertRaisesRegex(ValueError, "invalid provided value"):
                    self.record()

    def test_duplicate_and_unresolved_manifest_identities_reject(self):
        for mutation in ("selection", "role", "component", "endpoint", "runtime_endpoint",
                         "connection", "artifact", "unknown_selection", "unknown_endpoint", "unknown_destination"):
            with self.subTest(mutation=mutation):
                self.setUp()
                if mutation in ("selection", "role"):
                    selection = deepcopy(self.build["selections"][0])
                    selection["enabled"] = False
                    if mutation == "role": selection["id"] = "sel_model_second"
                    self.build["selections"].append(selection)
                elif mutation == "component": self.proposal["components"].append(deepcopy(self.component()))
                elif mutation == "endpoint": self.proposal["endpoint_ids"].append(LOCAL)
                elif mutation == "runtime_endpoint": self.component()["runtime_endpoint_ids"].append(LOCAL)
                elif mutation == "connection": self.component()["connections"].append(deepcopy(self.component()["connections"][0]))
                elif mutation == "artifact": self.component()["runtime_artifacts"].append(deepcopy(self.component()["runtime_artifacts"][0]))
                elif mutation == "unknown_selection": self.component()["selection_id"] = "sel_absent"
                elif mutation == "unknown_endpoint": self.component()["runtime_endpoint_ids"] = ["endpoint.absent"]
                else: self.fact(self.connection_path("destination_id"), "endpoint.absent")
                with self.assertRaises(ValueError): self.record()

    def test_identity_tokens_and_schema_version_are_strict(self):
        for field, value in (("boundary_id", BOUNDARY + "\n"), ("boundary_id", "local/boundary"),
                             ("boundary_id", ""), ("proposal_version", "cd4-0.2")):
            with self.subTest(field=field, value=value):
                self.setUp(); self.proposal[field] = value
                with self.assertRaisesRegex(ValueError, "invalid CD-4 binding"): self.record()
        for field in ("id", "role"):
            self.setUp(); self.build["selections"][0][field] += "\n"
            with self.assertRaisesRegex(ValueError, "whole string"): self.record()
        self.setUp(); self.build["revision"] = 1.0
        with self.assertRaisesRegex(ValueError, "JSON integer"): self.record()

    def test_byte_hashes_prevent_unrelated_build_or_answer_rebinding(self):
        for which in (1, 2):
            with self.subTest(which=which):
                raw = list(RAW); raw[which] += b"\n"
                with self.assertRaisesRegex(ValueError, "bytes do not match"):
                    IsolationRecord(*raw)

    def test_raw_json_ambiguity_is_rejected_after_correct_digest_binding(self):
        def rebound(which, replacement):
            raw = list(RAW); raw[which] = replacement
            if which:
                binding = json.loads(RAW[0])
                field = "build_sha256" if which == 1 else "answer_states_sha256"
                binding["x_t0_isolation"][field] = digest(replacement)
                raw[0] = encode(binding)
            return raw
        for which, old, new in (
                (0, b'"proposal_version": "cd4-0.1"', b'"proposal_version": "cd4-0.1", "proposal_version": "cd4-0.1"'),
                (1, b'"revision": 1', b'"revision": 1, "revision": 1'),
                (2, b'"value": true', b'"value": true, "value": true')):
            altered = RAW[which].replace(old, new, 1)
            self.assertNotEqual(altered, RAW[which])
            with self.subTest(duplicate=which), self.assertRaisesRegex(ValueError, "duplicate"):
                IsolationRecord(*rebound(which, altered))
        for literal in (b"NaN", b"Infinity", b"1e999"):
            altered = RAW[2].replace(b'"value": true', b'"value": ' + literal, 1)
            with self.subTest(literal=literal), self.assertRaises(ValueError):
                IsolationRecord(*rebound(2, altered))
        for which in range(3):
            raw = list(RAW); raw[which] = raw[which].decode()
            with self.subTest(type=which), self.assertRaises(ValueError): IsolationRecord(*raw)

    def test_eligibility_map_rejects_unscoped_paths_or_truthy_non_booleans(self):
        record = self.record()
        for value in ([], True, {"/unknown": True}, {"/workload/network": 1}, {"/workload/network": "true"}):
            with self.subTest(value=value), self.assertRaises(ValueError): record.evaluate(value)

    def test_inventory_order_and_input_mutation_do_not_change_retained_results(self):
        first = self.result()
        self.build["selections"].reverse(); self.proposal["components"].reverse()
        self.proposal["endpoint_ids"].reverse()
        for component in self.proposal["components"]:
            component["connections"].reverse()
            component["runtime_artifacts"].reverse()
            component["runtime_endpoint_ids"].reverse()
        self.assertEqual(self.result(), first)
        record = self.record()
        retained = record.evaluate(dict.fromkeys(record.answer_paths, True))
        # Returned Answer values cannot modify future evaluations.
        object.__setattr__(dict(retained.answers)["/workload/network"], "value", "online")
        self.assertEqual(record.evaluate(dict.fromkeys(record.answer_paths, True)), first)


if __name__ == "__main__":
    unittest.main()
