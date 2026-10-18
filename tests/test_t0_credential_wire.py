"""CD-6 wire, identity, source-choice and privacy boundary regressions.

All inputs derive from the frozen fictional examples. Opaque references below
are fictional metadata strings, never credentials or accessible secret locations.
"""

from copy import deepcopy
from dataclasses import asdict, FrozenInstanceError
import json
from pathlib import Path
import sys
import traceback
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from t0_credential_wire_prototype import Outcome, WIRE_SCHEMA, WIRE_VALIDATOR, project
from t0_revision_lock_prototype import SnapshotArchive, digest

EXAMPLES = ROOT / "contracts/v1/examples"
BUILD = (EXAMPLES / "build.json").read_bytes()
CATALOG = (EXAMPLES / "catalog.json").read_bytes()
PRICEBOOK = (EXAMPLES / "pricebook.json").read_bytes()
DIRECT = {"selection_id": "sel_tool", "source": "direct", "auth_method": "oauth2"}
INTEGRATION = {"selection_id": "sel_tool", "source": "integration",
               "auth_method": "oauth2", "target_selection_id": "sel_integration"}


def encoded(value):
    return json.dumps(value, allow_nan=False).encode("utf-8")


def wire(build, pins, bindings):
    return encoded({"x_t0_credential_bindings": {
        "proposal_version": "cd6-0.1", "build_sha256": digest(build),
        "revision_locks_sha256": digest(pins), "bindings": bindings}})


def checks(row):
    return {check.code: check.outcome for check in row.checks}


class CredentialWire(unittest.TestCase):
    def setUp(self):
        self.build, self.catalog = json.loads(BUILD), json.loads(CATALOG)
        self.selections = {s["id"]: s for s in self.build["selections"]}
        self.items = {i["id"]: i for i in self.catalog["items"]}

    def inputs(self, bindings=None):
        build, catalog = encoded(self.build), encoded(self.catalog)
        prices = json.loads(PRICEBOOK)
        pins = encoded({"x_t0_revision_locks": {"proposal_version": "cd7-0.1",
            "build_sha256": digest(build), "artifacts": {
                "catalog_snapshot": {"id": self.catalog["id"], "revision": self.catalog["revision"],
                                     "sha256": digest(catalog)},
                "pricebook": {"id": prices["id"], "revision": prices["revision"],
                              "sha256": digest(PRICEBOOK)}}}})
        archive = SnapshotArchive([("catalog_snapshot", catalog), ("pricebook", PRICEBOOK)])
        return archive, build, pins, wire(build, pins, [DIRECT] if bindings is None else bindings)

    def evaluate(self, bindings=None):
        return project(*self.inputs(bindings))

    def add_reference(self, selection_id):
        self.selections[selection_id]["settings"]["credential_ref"] = "secret://fixture/never-resolved"

    def add_link(self, target="sel_integration", identity="link.credential"):
        self.build["links"].append({"id": identity, "relation": "provided_by",
            "from_selection_id": "sel_tool", "to_selection_id": target})

    def inherited(self):
        self.add_reference("sel_integration")
        self.add_link()

    def test_published_wire_schema_and_original_fixture_reject_missing_reference(self):
        Draft202012Validator.check_schema(WIRE_SCHEMA)
        pins = (ROOT / "tests/fixtures/t0-revision-locks.json").read_bytes()
        choice = (ROOT / "tests/fixtures/t0-credential-bindings.json").read_bytes()
        archive = SnapshotArchive([("catalog_snapshot", CATALOG), ("pricebook", PRICEBOOK)])
        row = project(archive, BUILD, pins, choice).tools[0]
        self.assertEqual(row.outcome, Outcome.FAIL)
        self.assertEqual(checks(row)["direct_reference_present"], Outcome.FAIL)

    def test_direct_metadata_pass_never_establishes_authorization_or_exposes_locator(self):
        self.add_reference("sel_tool")
        result = self.evaluate()
        self.assertEqual(result.tools[0].outcome, Outcome.PASS)
        serialized_result = json.dumps(asdict(result))
        self.assertNotIn("secret://", serialized_result)
        self.assertNotIn("never-resolved", serialized_result)
        self.assertNotIn("credential_ref", serialized_result)
        self.assertEqual(result.revision_binding, "exact_pin_bytes_verified")
        self.assertEqual(result.authorization, "not_evaluated")
        self.assertEqual(result.secret_resolution, "not_performed")
        self.assertEqual(result.evidence, "synthetic_contract_experiment")

    def test_missing_sidecar_or_empty_choices_does_not_infer_a_legacy_source(self):
        self.add_reference("sel_tool")
        archive, build, pins, _ = self.inputs()
        for choice in (None, wire(build, pins, [])):
            row = project(archive, build, pins, choice).tools[0]
            self.assertEqual(row.outcome, Outcome.UNKNOWN)
            self.assertEqual(checks(row), {"binding_missing": Outcome.UNKNOWN})

    def test_integration_reads_exact_selected_connection_without_a_local_copy(self):
        self.inherited()
        row = self.evaluate([INTEGRATION]).tools[0]
        self.assertEqual(row.outcome, Outcome.PASS)
        self.assertEqual(checks(row)["one_exact_provided_by_link"], Outcome.PASS)
        self.assertNotIn("credential_ref", self.selections["sel_tool"]["settings"])

    def test_identical_or_different_local_and_inherited_references_do_not_override(self):
        self.inherited()
        for locator in ("secret://fixture/never-resolved", "secret://fixture/different"):
            self.selections["sel_tool"]["settings"]["credential_ref"] = locator
            row = self.evaluate([INTEGRATION]).tools[0]
            self.assertEqual(row.outcome, Outcome.UNKNOWN)
            self.assertEqual(checks(row), {"local_and_inherited_source_conflict": Outcome.UNKNOWN})

    def test_provider_link_reference_and_auth_cannot_invent_provider_execution_or_api_support(self):
        self.add_reference("sel_model_provider")
        self.add_link("sel_model_provider")
        self.items["cat.model_provider.fixture"]["spec"]["supported_auth"] = ["oauth2"]
        choice = {**INTEGRATION, "source": "model_provider", "target_selection_id": "sel_model_provider"}
        row = self.evaluate([choice]).tools[0]
        self.assertEqual(row.outcome, Outcome.UNKNOWN)
        self.assertEqual(checks(row)["provider_hosted_execution_evidence"], Outcome.UNKNOWN)
        self.assertEqual(checks(row)["provider_api_operation_evidence"], Outcome.UNKNOWN)
        self.assertEqual(checks(row)["target_reference_present"], Outcome.PASS)

    def test_missing_disabled_or_wrong_kind_target_fails(self):
        self.inherited()
        for target in ("sel_absent", "sel_model_provider"):
            row = self.evaluate([{**INTEGRATION, "target_selection_id": target}]).tools[0]
            self.assertEqual(row.outcome, Outcome.FAIL)
        self.selections["sel_integration"]["enabled"] = False
        self.assertEqual(self.evaluate([INTEGRATION]).tools[0].outcome, Outcome.FAIL)

    def test_known_catalog_kind_mismatch_fails_without_borrowing_other_settings(self):
        self.inherited()
        self.selections["sel_integration"]["catalog_item_id"] = "cat.model_provider.fixture"
        row = self.evaluate([INTEGRATION]).tools[0]
        self.assertEqual(checks(row)["target_catalog_binding_valid"], Outcome.FAIL)
        self.assertEqual(row.outcome, Outcome.FAIL)

    def test_missing_selected_version_remains_unknown(self):
        self.inherited()
        self.selections["sel_integration"]["catalog_item_version"] = "fixture-unavailable-version"
        row = self.evaluate([INTEGRATION]).tools[0]
        self.assertEqual(row.outcome, Outcome.UNKNOWN)
        self.assertEqual(checks(row)["target_catalog_binding_valid"], Outcome.UNKNOWN)

    def test_unavailable_or_unpinned_catalog_does_not_gain_a_latest_fallback(self):
        self.add_reference("sel_tool")
        archive, build, pins, choice = self.inputs()
        row = project(archive, build, None, choice).tools[0]
        self.assertEqual(row.outcome, Outcome.UNKNOWN)
        self.assertEqual(checks(row)["catalog_revision_pin_missing"], Outcome.UNKNOWN)
        no_catalog = SnapshotArchive([("pricebook", PRICEBOOK)])
        row = project(no_catalog, build, pins, choice).tools[0]
        self.assertEqual(row.outcome, Outcome.UNKNOWN)
        self.assertEqual(checks(row)["catalog_pinned_revision_unavailable"], Outcome.UNKNOWN)

    def test_provided_sidecar_without_pins_never_claims_the_digest_was_verified(self):
        self.add_reference("sel_tool")
        self.items["cat.tool.fixture"]["spec"]["auth_methods"] = ["oauth2", "none"]
        for binding in (DIRECT, {**DIRECT, "source": "none", "auth_method": "none"}):
            archive, build, pins, choice = self.inputs([binding])
            document = json.loads(choice)
            document["x_t0_credential_bindings"]["revision_locks_sha256"] = "0" * 64
            for retained_choice in (choice, encoded(document)):
                result = project(archive, build, None, retained_choice)
                self.assertEqual(result.revision_binding, "revision_pins_missing")
                self.assertEqual(result.tools[0].outcome, Outcome.UNKNOWN)
                self.assertEqual(checks(result.tools[0])["credential_revision_pins_bound"], Outcome.UNKNOWN)
                self.assertEqual(checks(result.tools[0])["catalog_revision_pin_missing"], Outcome.UNKNOWN)
            self.assertEqual(project(archive, build, pins, choice).revision_binding, "exact_pin_bytes_verified")

    def test_absent_revision_authority_remains_visible_when_no_tool_applies(self):
        self.selections["sel_tool"]["enabled"] = False
        archive, build, pins, choice = self.inputs()
        result = project(archive, build, None, choice)
        self.assertEqual(result.tools[0].outcome, Outcome.SKIPPED)
        self.assertEqual(result.revision_binding, "revision_pins_missing")
        self.assertEqual(project(archive, build, pins).revision_binding, "credential_sidecar_missing")

    def test_changed_retained_catalog_bytes_preserve_the_content_mismatch(self):
        self.add_reference("sel_tool")
        _, build, pins, choice = self.inputs()
        changed = encoded(self.catalog) + b"\n"
        archive = SnapshotArchive([("catalog_snapshot", changed), ("pricebook", PRICEBOOK)])
        row = project(archive, build, pins, choice).tools[0]
        self.assertEqual(row.outcome, Outcome.UNKNOWN)
        self.assertEqual(checks(row)["catalog_content_digest_mismatch"], Outcome.UNKNOWN)

    def test_unmarked_auth_lists_do_not_establish_unsupported_methods(self):
        self.add_reference("sel_tool")
        spec = self.items["cat.tool.fixture"]["spec"]
        for methods in ([], ["api_key"], None):
            if methods is None:
                spec.pop("auth_methods", None)
            else:
                spec["auth_methods"] = methods
            row = self.evaluate().tools[0]
            self.assertEqual(row.outcome, Outcome.UNKNOWN)
            self.assertEqual(checks(row)["chosen_tool_auth_supported"], Outcome.UNKNOWN)

    def test_absent_or_unmarked_operation_association_does_not_prove_a_negative(self):
        self.inherited()
        spec = self.items["cat.integration.fixture"]["spec"]
        for refs in ([], ["cat.unrelated.fixture"], None):
            if refs is None:
                spec.pop("associated_tool_refs", None)
            else:
                spec["associated_tool_refs"] = refs
            row = self.evaluate([INTEGRATION]).tools[0]
            self.assertEqual(row.outcome, Outcome.UNKNOWN)
            self.assertEqual(checks(row)["connection_serves_operation"], Outcome.UNKNOWN)

    def test_none_requires_an_explicit_choice_and_positive_metadata(self):
        self.items["cat.tool.fixture"]["spec"]["auth_methods"] = ["none", "oauth2"]
        choice = {**DIRECT, "source": "none", "auth_method": "none"}
        self.assertEqual(self.evaluate([choice]).tools[0].outcome, Outcome.PASS)
        self.assertEqual(self.evaluate([]).tools[0].outcome, Outcome.UNKNOWN)
        self.items["cat.tool.fixture"]["spec"]["auth_methods"] = ["oauth2"]
        self.assertEqual(self.evaluate([choice]).tools[0].outcome, Outcome.UNKNOWN)

    def test_association_or_an_exposes_link_cannot_replace_exact_provided_by(self):
        self.add_reference("sel_integration")
        row = self.evaluate([INTEGRATION]).tools[0]
        self.assertEqual(row.outcome, Outcome.FAIL)
        self.assertEqual(checks(row)["connection_serves_operation"], Outcome.PASS)
        self.assertEqual(checks(row)["one_exact_provided_by_link"], Outcome.FAIL)

    def test_duplicate_exact_links_remain_ambiguous_even_with_different_link_ids(self):
        self.inherited()
        self.add_link(identity="link.credential-two")
        row = self.evaluate([INTEGRATION]).tools[0]
        self.assertEqual(row.outcome, Outcome.UNKNOWN)
        self.assertEqual(checks(row)["one_exact_provided_by_link"], Outcome.UNKNOWN)

    def test_an_explicit_target_disambiguates_other_available_connections(self):
        self.inherited()
        other = deepcopy(self.selections["sel_integration"])
        other.update(id="sel_other_integration", role="secondary")
        self.build["selections"].append(other)
        self.add_link(other["id"], identity="link.other-credential")
        self.assertEqual(self.evaluate([INTEGRATION]).tools[0].outcome, Outcome.PASS)

    def test_competing_bindings_are_not_deduplicated_or_selected_by_array_order(self):
        self.inherited()
        for choices in ([INTEGRATION, INTEGRATION], [INTEGRATION, DIRECT], [DIRECT, INTEGRATION]):
            row = self.evaluate(choices).tools[0]
            self.assertEqual(row.outcome, Outcome.UNKNOWN)
            self.assertEqual(checks(row), {"competing_bindings": Outcome.UNKNOWN})

    def test_every_selected_tool_retains_its_own_outcome_and_fixed_severity(self):
        self.add_reference("sel_tool")
        other = deepcopy(self.selections["sel_tool"])
        other.update(id="sel_other_tool", role="secondary")
        self.build["selections"].append(other)
        results = self.evaluate().tools
        self.assertEqual([r.outcome for r in results], [Outcome.PASS, Outcome.UNKNOWN])
        self.assertTrue(all(r.severity == "error" and r.on_unknown == "review" for r in results))
        self.selections["sel_tool"]["enabled"] = False
        self.assertEqual(self.evaluate().tools[0].outcome, Outcome.SKIPPED)

    def test_known_failure_does_not_discard_unknown_requirements(self):
        self.add_link()
        self.items["cat.integration.fixture"]["spec"].pop("auth_methods")
        row = self.evaluate([INTEGRATION]).tools[0]
        self.assertEqual(row.outcome, Outcome.FAIL)
        self.assertEqual(checks(row)["target_reference_present"], Outcome.FAIL)
        self.assertEqual(checks(row)["chosen_target_auth_supported"], Outcome.UNKNOWN)

    def test_sidecar_is_bound_to_exact_build_and_revision_pin_bytes(self):
        archive, build, pins, choice = self.inputs()
        for changed_build, changed_pins in ((build + b"\n", pins), (build, pins + b"\n")):
            with self.assertRaisesRegex(ValueError, "invalid retained credential-binding input"):
                project(archive, changed_build, changed_pins, choice)

    def test_closed_sidecar_rejects_new_versions_bad_types_and_secret_fields(self):
        archive, build, pins, choice = self.inputs()
        for path, value in (("proposal_version", "cd6-0.2"), ("build_sha256", True),
                            ("revision_locks_sha256", "a" * 64 + "\n"), ("bindings", {})):
            document = json.loads(choice)
            document["x_t0_credential_bindings"][path] = value
            with self.subTest(path=path), self.assertRaises(ValueError):
                project(archive, build, pins, encoded(document))
        for key, value in (("credential_ref", "secret://fixture/hidden"),
                           ("target_selection_id", "sel_integration"),
                           ("auth_method", "none"), ("source", "automatic")):
            document = json.loads(choice)
            document["x_t0_credential_bindings"]["bindings"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                project(archive, build, pins, encoded(document))

    def test_binding_ids_reject_terminal_lf_and_enforce_complete_length(self):
        archive, build, pins, _ = self.inputs()
        for value in ("sel_tool\n", "sel_tool\t", " sel_tool", "x" * 81, "ab"):
            document = json.loads(wire(build, pins, [{**DIRECT, "selection_id": value}]))
            self.assertFalse(WIRE_VALIDATOR.is_valid(document))
            with self.assertRaises(ValueError):
                project(archive, build, pins, encoded(document))
        maximum = "s" * 80
        self.selections["sel_tool"]["id"] = maximum
        for link in self.build["links"]:
            for key in ("from_selection_id", "to_selection_id"):
                if link[key] == "sel_tool": link[key] = maximum
        self.add_reference("sel_tool")
        self.assertEqual(self.evaluate([{**DIRECT, "selection_id": maximum}]).tools[0].outcome, Outcome.PASS)

    def test_binding_cannot_name_absent_or_non_tool_selection(self):
        for identity in ("sel_absent", "sel_model_provider"):
            with self.assertRaisesRegex(ValueError, "retained tool selection"):
                self.evaluate([{**DIRECT, "selection_id": identity}])

    def test_duplicate_disabled_selection_id_or_role_fails_before_binding(self):
        for same_role in (False, True):
            self.setUp()
            extra = deepcopy(self.selections["sel_integration"])
            extra["enabled"] = False
            if same_role: extra["id"] = "sel_duplicate_role"
            self.build["selections"].append(extra)
            with self.subTest(same_role=same_role), self.assertRaises(ValueError):
                self.evaluate([])

    def test_duplicate_link_ids_or_dangling_endpoints_are_rejected(self):
        self.build["links"].append(deepcopy(self.build["links"][0]))
        with self.assertRaises(ValueError): self.evaluate()
        self.build["links"].pop()
        self.build["links"][0]["to_selection_id"] = "sel_missing"
        with self.assertRaises(ValueError): self.evaluate()

    def test_raw_duplicate_keys_nonfinite_and_malformed_secret_diagnostics_are_sanitized(self):
        archive, build, pins, _ = self.inputs()
        bad_inputs = (b'{"x_t0_credential_bindings":{},"x_t0_credential_bindings":{}}',
                      b'{"x_t0_credential_bindings":NaN}', b'"private-submitted-text"')
        for raw in bad_inputs:
            with self.assertRaisesRegex(ValueError, "invalid retained credential-binding input"):
                project(archive, build, pins, raw)
        marker = "private-fixture-locator"
        self.selections["sel_tool"]["settings"]["credential_ref"] = "secret://" + marker + "\n"
        archive, build, pins, choice = self.inputs()
        try:
            project(archive, build, pins, choice)
        except ValueError as error:
            self.assertNotIn(marker, "".join(traceback.format_exception(error)))
            self.assertNotIn("secret://", str(error))
        else:
            self.fail("malformed secret locator was admitted")

    def test_input_bytes_and_immutable_output_do_not_mutate_retained_history(self):
        self.add_reference("sel_tool")
        inputs = self.inputs()
        before = inputs[1:]
        result = project(*inputs)
        with self.assertRaises(FrozenInstanceError): result.tools[0].outcome = Outcome.FAIL
        self.assertEqual(project(*inputs), result)
        self.assertEqual(inputs[1:], before)
        self.assertEqual((EXAMPLES / "build.json").read_bytes(), BUILD)
        self.assertEqual((EXAMPLES / "catalog.json").read_bytes(), CATALOG)


if __name__ == "__main__":
    unittest.main()
