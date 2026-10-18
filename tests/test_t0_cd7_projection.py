"""Synthetic projection/fork controls; no private user data or source evidence."""

import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import t0_cd7_projection_prototype as projection
from t0_cd7_consumer_prototype import DOCUMENT_VALIDATORS, MAX_DEPTH, MAX_ENVELOPE_BYTES, encoded
from t0_revision_lock_prototype import digest
from test_t0_revision_locks import BUILD, archive, sidecar
from tests.t0_answer_state_prototype import (
    AnswerRule, PredicateResult, RulePolicy, State, evaluate_answer_rule,
)

VERSION = "cd7-projection-0.1"
FORK_ID = "build.synthetic-recipient"


def data(packet):
    return projection.read_projection(VERSION, packet.projection, packet.binding)


def rebind(raw, old_binding):
    binding = json.loads(old_binding)
    record = binding[projection.BINDING]
    record["projection_sha256"], record["projection_byte_length"] = digest(raw), len(raw)
    return encoded(binding)


def changed(packet, callback):
    document = json.loads(packet.projection)
    callback(document[projection.PROJECTION])
    raw = encoded(document)
    return raw, rebind(raw, packet.binding)


def private_source():
    """Known schema-defined private fields plus synthetic extension canaries."""
    build = json.loads(BUILD)
    build.update(name="synthetic-private-build-name", owner_ref="synthetic-private-owner", lifecycle="deployed")
    build["objectives"].update(region="synthetic-private-region", requests_per_day=0,
                               monthly_budget_amount="0", data_classification="restricted")
    build["policy"] = {"fail_on_unknown": False}
    build["extensions"] = {"x_organisation": {"lawful_basis": "synthetic-private-basis",
        "licence_answers": {"grant_ref": "synthetic-private-grant"}, "zero_retention_approved": True}}
    schemas = json.loads((ROOT / "contracts/v1/schemas/selection.schema.json").read_bytes())["$defs"]
    for selection in build["selections"]:
        selection["notes"] = "synthetic-private-note-" + selection["id"]
        selection["extensions"] = {"x_organisation": {"account_approved": True,
                                                       "private_key_name": "synthetic-private-attestation"}}
        fields = schemas["settings_" + selection["kind"]]["properties"]
        for name in fields:
            if name in {"credential_ref", "account_ref", "encryption_key_ref", "connector_secret_ref"}:
                selection["settings"][name] = "secret://synthetic-private/" + name
            elif name in {"api_base_url", "endpoint", "weights_uri", "artifact_uri"}:
                selection["settings"][name] = "https://synthetic-private.example.invalid/" + name
            elif name in {"index_name", "approval_ticket"}:
                selection["settings"][name] = "synthetic-private-" + name
    # Preserve a provided false configuration value, separately from private zero inputs.
    build["selections"][0]["enabled"] = False
    build["links"][0]["required"] = False
    raw = encoded(build)
    DOCUMENT_VALIDATORS["build.schema.json"].validate(json.loads(raw))
    return raw, sidecar(raw)


class CD7Projection(unittest.TestCase):
    def setUp(self):
        self.original, self.pins = private_source()
        self.packet = projection.create_projection(VERSION, self.original, self.pins)

    def assert_code(self, code, function, *args, **kwargs):
        with self.assertRaises(projection.ProjectionError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def test_schema_and_new_byte_binding_preserve_exact_configuration(self):
        Draft202012Validator.check_schema(projection.SCHEMA)
        original = json.loads(self.original)
        result = data(self.packet)
        config = result["configuration"]
        self.assertEqual(set(config), {"schema_version", "locks", "selections", "links"})
        self.assertEqual(config["locks"], original["locks"])
        self.assertEqual(config["links"], original["links"])
        for actual, source in zip(config["selections"], original["selections"], strict=True):
            self.assertEqual(actual, {key: source[key] for key in
                ("id", "kind", "catalog_item_id", "catalog_item_version", "role", "enabled")})
        binding = json.loads(self.packet.binding)[projection.BINDING]
        self.assertEqual(binding["projection_sha256"], digest(self.packet.projection))
        self.assertEqual(binding["projection_byte_length"], len(self.packet.projection))
        self.assertEqual(result["source_artifact_pins"], json.loads(self.pins)["x_t0_revision_locks"]["artifacts"])
        self.assertEqual(result["source"], {"id": original["id"], "revision": original["revision"],
            "build_sha256": digest(self.original), "sidecar_sha256": digest(self.pins)})

    def test_all_schema_secret_and_infrastructure_fields_stay_private_on_share_and_export(self):
        export = projection.export_projection(VERSION, self.original, self.pins)
        self.assertEqual(export, self.packet)
        for raw in (self.packet.projection, self.packet.binding, export.projection, export.binding):
            self.assertNotIn(b"synthetic-private", raw)
            self.assertNotIn(b"secret://", raw.lower())
            for field in (b"credential_ref", b"connector_secret_ref", b"encryption_key_ref",
                          b"account_ref", b"approval_ticket", b"api_base_url", b"weights_uri",
                          b"artifact_uri", b"index_name", b"grant_ref", b"lawful_basis", b"account_approved"):
                self.assertNotIn(field, raw)
        self.assertEqual(json.loads(self.original)["lifecycle"], "deployed")
        self.assertNotIn(b'"deployed"', self.packet.projection)

    def test_share_withheld_groups_and_fork_missing_groups_never_default_or_run_dependent_predicate(self):
        fork = projection.fork_projection(VERSION, self.packet.projection, self.packet.binding, new_build_id=FORK_ID)
        for packet, state, reason in ((self.packet, State.WITHHELD, "answer_withheld"),
                                      (fork, State.MISSING, "answer_missing")):
            answers = projection.projection_answers(VERSION, packet.projection, packet.binding)
            for pointer in ("/objectives/requests_per_day", "/policy/fail_on_unknown",
                            "/selections/2/settings/credential_ref", "/extensions/x_organisation",
                            "/owner_ref", "/selections/0/notes"):
                calls = []
                with self.subTest(kind=data(packet)["kind"], pointer=pointer):
                    answer = answers.read(pointer, {"type": "integer", "minimum": 0})
                    self.assertEqual(answer.state, state)
                    self.assertIsNone(answer.value)
                    rule = AnswerRule("synthetic.private-required", "error", RulePolicy.COMPATIBILITY,
                        lambda: PredicateResult(State.PROVIDED, True),
                        lambda: answers.predicate(pointer, {"type": "integer", "minimum": 0},
                                                   lambda value: calls.append(value) or False).negated())
                    finding = evaluate_answer_rule(rule)
                    self.assertEqual((finding.outcome.value, finding.reason, finding.severity), ("unknown", reason, "error"))
                    self.assertEqual(calls, [])
            self.assertEqual(answers.read("/selections", {"type": "array"}).state, state)

    def test_public_false_and_exact_integer_remain_provided_without_transferring_private_zero(self):
        answers = projection.projection_answers(VERSION, self.packet.projection, self.packet.binding)
        enabled = answers.read("/selections/0/enabled", {"type": "boolean"})
        self.assertEqual(enabled.state, State.PROVIDED)
        self.assertIs(enabled.value, False)
        self.assertIs(answers.read("/links/0/required", {"type": "boolean"}).value, False)
        revision = answers.read("/locks/dependency_graph_revision", {"type": "integer", "minimum": 1})
        self.assertEqual(revision.state, State.PROVIDED)
        self.assertIs(type(revision.value), int)
        rule = AnswerRule("synthetic.optional", "warning", RulePolicy.COMPATIBILITY,
                         lambda: answers.predicate("/selections/0/enabled", {"type": "boolean"}, lambda value: value),
                         lambda: self.fail("disabled configuration must not execute its assertion"))
        self.assertEqual(evaluate_answer_rule(rule).outcome.value, "skipped")

    def test_fork_is_a_new_revision_one_draft_with_explicit_lineage_and_separate_binding(self):
        fork = projection.fork_projection(VERSION, self.packet.projection, self.packet.binding, new_build_id=FORK_ID)
        shared, draft = data(self.packet), data(fork)
        self.assertEqual(draft["identity"], {"id": FORK_ID, "revision": 1})
        self.assertEqual(draft["source"], shared["source"])
        self.assertEqual(draft["parent_projection_sha256"], digest(self.packet.projection))
        self.assertEqual(draft["configuration"], shared["configuration"])
        self.assertNotEqual(fork.projection, self.packet.projection)
        self.assertNotEqual(fork.binding, self.packet.binding)
        self.assert_code("projection_length_mismatch", projection.read_projection,
                         VERSION, fork.projection, self.packet.binding)
        self.assertNotIn(b"synthetic-private", fork.projection + fork.binding)
        for record in (shared, draft):
            self.assertEqual(record["qualification"], {"source_authenticity": "not_established",
                "source_use": "not_established", "artifact_resolution": "not_established", "evaluation": "not_performed"})
            self.assertNotIn("report", record)
            self.assertNotIn("result", record)
            with self.assertRaises(ValidationError):
                DOCUMENT_VALIDATORS["build.schema.json"].validate(record)

    def test_old_binding_and_old_build_reader_cannot_claim_projection_or_fork_bytes(self):
        self.assert_code("malformed_projection_envelope", projection.read_projection,
                         VERSION, self.packet.projection, self.pins)
        for raw in (self.packet.projection, encoded(dict(json.loads(self.original), id=FORK_ID, revision=1))):
            with self.assertRaises(ValueError):
                archive().resolve(raw, self.pins)
        retained = archive().resolve(self.original, self.pins)
        self.assertIs(retained.original_bytes, self.original)
        self.assertEqual(sum(s.status == "resolved" for s in retained.selections), 28)

    def test_no_pin_stays_missing_and_never_invents_a_catalog_or_pricebook_revision(self):
        for raw, pins in ((self.original, None), (self.original, sidecar(self.original, catalog=None, pricebook=None))):
            packet = projection.create_projection(VERSION, raw, pins)
            result = data(packet)
            self.assertEqual(result["source_artifact_pins"], {})
            self.assertEqual(result["source"]["sidecar_sha256"], digest(pins) if pins else None)
        build = json.loads(self.original)
        del build["locks"]["pricebook_id"]
        raw = encoded(build)
        packet = projection.create_projection(VERSION, raw, sidecar(raw, pricebook=None))
        self.assertNotIn("pricebook_id", data(packet)["configuration"]["locks"])
        self.assertNotIn("pricebook", data(packet)["source_artifact_pins"])

    def test_original_pin_binding_and_each_source_identity_are_checked_before_redaction(self):
        self.assert_code("source_binding_invalid", projection.create_projection, VERSION, self.original + b"\n", self.pins)
        for kind in ("catalog_snapshot", "pricebook"):
            pins = json.loads(self.pins)
            pins["x_t0_revision_locks"]["artifacts"][kind]["id"] = "synthetic.wrong-source"
            self.assert_code("source_binding_invalid", projection.create_projection, VERSION, self.original, encoded(pins))
        for mutation in (lambda d: d["selections"][1].update(id=d["selections"][0]["id"]),
                         lambda d: d.update(schema_version="1.1.0"), lambda d: d.pop("owner_ref")):
            document = json.loads(self.original); mutation(document)
            raw = encoded(document)
            with self.assertRaises(projection.ProjectionError):
                projection.create_projection(VERSION, raw, sidecar(raw))

    def test_exact_projection_length_digest_and_equivalent_reencoding_remain_distinct(self):
        for field, value, expected in (("projection_byte_length", 1, "projection_length_mismatch"),
                                       ("projection_sha256", "0" * 64, "projection_digest_mismatch")):
            binding = json.loads(self.packet.binding)
            binding[projection.BINDING][field] = value
            self.assert_code(expected, projection.read_projection, VERSION, self.packet.projection, encoded(binding))
        raw = json.dumps(json.loads(self.packet.projection), indent=1).encode()
        self.assert_code("projection_length_mismatch", projection.read_projection, VERSION, raw, self.packet.binding)
        self.assertEqual(projection.read_projection(VERSION, raw, rebind(raw, self.packet.binding)), data(self.packet))
        raw = self.packet.projection.replace(b'"enabled":false', b'"enabled":true ', 1)
        self.assertEqual(len(raw), len(self.packet.projection))
        self.assert_code("projection_digest_mismatch", projection.read_projection, VERSION, raw, self.packet.binding)

    def test_recomputed_hash_cannot_override_omission_states_or_public_value_types(self):
        for callback in (
            lambda p: p["answer_states"]["x_t0_answer_states"]["answers"].update({"/owner_ref": {"state": "provided", "value": "leak"}}),
            lambda p: p["answer_states"]["x_t0_answer_states"]["answers"]["/selections/0/enabled"].update(value=0),
            lambda p: p["answer_states"]["x_t0_answer_states"]["answers"]["/objectives"].update(state="not_applicable"),
            lambda p: p["answer_states"]["x_t0_answer_states"]["answers"].pop("/selections/0/settings"),
        ):
            raw, binding = changed(self.packet, callback)
            self.assert_code("projection_answer_states_mismatch", projection.read_projection, VERSION, raw, binding)

    def test_envelope_closed_shapes_reject_private_values_reports_and_unknown_fields(self):
        for callback in (
            lambda p: p["configuration"].update(owner_ref="synthetic-private-owner"),
            lambda p: p["configuration"]["selections"][0].update(settings={"private": "value"}),
            lambda p: p.update(report={"result": "valid"}),
            lambda p: p.update(qualification={**p["qualification"], "evaluation": "passed"}),
            lambda p: p["source"].update(private_name="synthetic-private-name"),
        ):
            raw, binding = changed(self.packet, callback)
            self.assert_code("malformed_projection_envelope", projection.read_projection, VERSION, raw, binding)

    def test_secret_locators_cannot_hide_in_public_versions_or_escaped_transport_strings(self):
        for value in ("secret://synthetic/reference", "SeCrEt://synthetic/reference"):
            source = json.loads(self.original)
            source["selections"][0]["catalog_item_version"] = value
            raw = encoded(source)
            self.assert_code("secret_locator_forbidden", projection.create_projection, VERSION, raw, sidecar(raw))
        raw, binding = changed(self.packet, lambda p: p["configuration"]["selections"][0].update(
            catalog_item_version="secret://synthetic/reference"))
        raw = raw.replace(b"secret://", b"secret:\\u002f\\u002f")
        self.assert_code("secret_locator_forbidden", projection.read_projection, VERSION, raw, rebind(raw, binding))

    def test_share_fork_and_pin_identity_inconsistencies_fail_with_recomputed_digests(self):
        for callback in (
            lambda p: p["identity"].update(id="synthetic.foreign-build"),
            lambda p: p["identity"].update(revision=p["identity"]["revision"] + 1),
            lambda p: p.update(parent_projection_sha256="0" * 64),
        ):
            raw, binding = changed(self.packet, callback)
            self.assert_code("projection_identity_mismatch", projection.read_projection, VERSION, raw, binding)
        for kind in ("catalog_snapshot", "pricebook"):
            raw, binding = changed(self.packet, lambda p: p["source_artifact_pins"][kind].update(id="synthetic.foreign-pin"))
            self.assert_code("source_pin_identity_mismatch", projection.read_projection,
                             VERSION, raw, binding)
        raw, binding = changed(self.packet, lambda p: p["source"].update(sidecar_sha256=None))
        self.assert_code("source_pins_without_sidecar", projection.read_projection, VERSION, raw, binding)

    def test_source_pins_live_inside_projection_digest_and_cannot_shift_in_binding(self):
        for kind in ("catalog_snapshot", "pricebook"):
            for field, replacement in (("revision", 2), ("sha256", "0" * 64)):
                document = json.loads(self.packet.projection)
                document[projection.PROJECTION]["source_artifact_pins"][kind][field] = replacement
                raw = encoded(document)
                self.assertEqual(len(raw), len(self.packet.projection))
                self.assert_code("projection_digest_mismatch", projection.read_projection,
                                 VERSION, raw, self.packet.binding)
        binding = json.loads(self.packet.binding)
        binding[projection.BINDING]["source_artifact_pins"] = data(self.packet)["source_artifact_pins"]
        self.assert_code("malformed_projection_envelope", projection.read_projection,
                         VERSION, self.packet.projection, encoded(binding))

    def test_fork_identity_is_explicit_new_and_whole_string_with_no_implicit_refork(self):
        for value in (None, True, 1, "", "synthetic.new\n", "secret://synthetic/key"):
            self.assert_code("fork_identity_invalid", projection.fork_projection,
                             VERSION, self.packet.projection, self.packet.binding, new_build_id=value)
        self.assert_code("fork_identity_mismatch", projection.fork_projection, VERSION,
                         self.packet.projection, self.packet.binding, new_build_id=data(self.packet)["identity"]["id"])
        fork = projection.fork_projection(VERSION, self.packet.projection, self.packet.binding, new_build_id=FORK_ID)
        self.assert_code("fork_requires_share_projection", projection.fork_projection,
                         VERSION, fork.projection, fork.binding, new_build_id="build.another-recipient")
        for callback in (lambda p: p["identity"].update(revision=2), lambda p: p.update(parent_projection_sha256=None)):
            raw, binding = changed(fork, callback)
            self.assert_code("fork_identity_mismatch", projection.read_projection, VERSION, raw, binding)

    def test_explicit_protocol_selection_and_successor_versions_have_no_fallback(self):
        for version in (None, True, "", "cd7-consumer-0.1", "cd7-projection-0.2"):
            for function, args in ((projection.create_projection, (self.original, self.pins)),
                                   (projection.read_projection, (self.packet.projection, self.packet.binding))):
                self.assert_code("unsupported_projection_version", function, version, *args)
        raw, binding = changed(self.packet, lambda p: p.update(protocol_version="cd7-projection-0.2"))
        self.assert_code("unsupported_projection_version", projection.read_projection, VERSION, raw, binding)

    def test_json_integer_representation_and_bounds_are_not_coerced(self):
        for value in (True, 1.0, 0, -1, 2**63):
            for path in (("identity", "revision"), ("source", "revision"),
                         ("configuration", "locks", "dependency_graph_revision")):
                def mutate(p):
                    for key in path[:-1]:
                        p = p[key]
                    p[path[-1]] = value
                raw, binding = changed(self.packet, mutate)
                self.assert_code("integer_representation_unsupported", projection.read_projection, VERSION, raw, binding)
            binding = json.loads(self.packet.binding)
            binding[projection.BINDING]["projection_byte_length"] = value
            self.assert_code("integer_representation_unsupported", projection.read_projection,
                             VERSION, self.packet.projection, encoded(binding))
            raw, binding = changed(self.packet, lambda p: p["source_artifact_pins"]["catalog_snapshot"].update(revision=value))
            self.assert_code("integer_representation_unsupported", projection.read_projection, VERSION, raw, binding)
        for value in (1.0, 2**63):
            source = dict(json.loads(self.original), revision=value)
            raw = encoded(source)
            self.assert_code("integer_representation_unsupported", projection.create_projection, VERSION, raw, sidecar(raw))

    def test_duplicate_nonfinite_unicode_and_depth_fail_before_semantic_use(self):
        malformed = (b'{"x_t0_cd7_projection":{},"x_t0_cd7_projection":{}}',
                     b'{"x_t0_cd7_projection":{},"x_t0_cd7_projectio\\u006e":{}}',
                     b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e10000}')
        for raw in malformed:
            self.assert_code("malformed_document", projection.read_projection, VERSION, raw, self.packet.binding)
            self.assert_code("malformed_document", projection.create_projection, VERSION, raw)
        for value in ("\ud800", "\udfff"):
            raw = encoded(dict(json.loads(self.original), name=value))
            self.assert_code("unicode_scalar_unsupported", projection.create_projection, VERSION, raw)
        raw = b'{"x_t0_cd7_projection":{},"e\\u0301":0,"\\u00e9":1}'
        self.assert_code("ambiguous_object_keys", projection.read_projection, VERSION, raw, self.packet.binding)
        nested = 0
        for _ in range(MAX_DEPTH + 1):
            nested = [nested]
        self.assert_code("structure_limit_exceeded", projection.read_projection, VERSION, encoded(nested), self.packet.binding)

    def test_valid_non_ascii_and_paired_unicode_configuration_is_preserved(self):
        source = json.loads(self.original)
        source["selections"][0]["catalog_item_version"] = "synthetic-café-\U0001f680"
        source["name"] = "synthetic-private-\U0001f680"
        raw = json.dumps(source, ensure_ascii=True).encode()
        packet = projection.create_projection(VERSION, raw, sidecar(raw))
        self.assertEqual(data(packet)["configuration"]["selections"][0]["catalog_item_version"], "synthetic-café-\U0001f680")
        self.assertNotIn(b"synthetic-private", packet.projection + packet.binding)

    def test_transport_bounds_and_stable_errors_never_echo_private_values(self):
        self.assert_code("byte_limit_exceeded", projection.create_projection,
                         VERSION, b" " * (projection.DEFAULT_ARTIFACT_BYTES + 1))
        for raw in (b" " * (MAX_ENVELOPE_BYTES + 1), self.packet.projection + b" " * MAX_ENVELOPE_BYTES):
            self.assert_code("byte_limit_exceeded", projection.read_projection, VERSION, raw, self.packet.binding)
        raw = encoded(dict(json.loads(self.original), owner_ref={"synthetic-private-secret": "value"}))
        error = self.assert_code("source_build_invalid", projection.create_projection, VERSION, raw)
        self.assertNotIn("synthetic-private", str(error))
        for raw in (None, "not bytes", bytearray(self.original)):
            self.assert_code("malformed_document", projection.create_projection, VERSION, raw)

    def test_self_consistent_origin_claim_remains_unqualified_not_authenticated(self):
        raw, binding = changed(self.packet, lambda p: p["source"].update(build_sha256="0" * 64))
        unqualified = projection.read_projection(VERSION, raw, binding)
        self.assertEqual(unqualified["qualification"]["source_authenticity"], "not_established")
        self.assertEqual(unqualified["qualification"]["evaluation"], "not_performed")
        self.assertNotIn("accepted", unqualified)

    def test_repeated_reads_and_forks_leave_all_original_input_bytes_unchanged(self):
        originals = (self.original, self.pins, self.packet.projection, self.packet.binding)
        mutated = data(self.packet)
        mutated["configuration"]["selections"][0]["enabled"] = True
        mutated["qualification"]["evaluation"] = "passed"
        fork = projection.fork_projection(VERSION, self.packet.projection, self.packet.binding, new_build_id=FORK_ID)
        fork_data = data(fork); fork_data["source"]["build_sha256"] = "0" * 64
        self.assertEqual(originals, (self.original, self.pins, self.packet.projection, self.packet.binding))
        self.assertFalse(data(self.packet)["configuration"]["selections"][0]["enabled"])
        self.assertEqual(data(fork)["source"]["build_sha256"], digest(self.original))
        self.assertEqual(projection.create_projection(VERSION, self.original, self.pins), self.packet)


if __name__ == "__main__":
    unittest.main()
