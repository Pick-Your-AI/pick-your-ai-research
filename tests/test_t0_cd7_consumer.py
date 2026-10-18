"""Native CD-7 integrity handoff tests; all retained source bytes are synthetic."""

from copy import deepcopy
from contextlib import contextmanager
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import t0_cd7_consumer_prototype as consumer
from t0_cd7_consumer_prototype import (
    ConsumerError, DEFAULT_ARTIFACT_BYTES, MAX_DEPTH, MAX_ENVELOPE_BYTES,
    MAX_NODES, MAX_REVISION, SCHEMA, bounded_json, decode, digest, encoded,
    inspect, request, verify_complete_pair, wire,
)
from t0_revision_lock_prototype import SnapshotArchive
from test_t0_revision_locks import BUILD, CATALOG, PRICEBOOK, archive, sidecar

FIXTURES = ROOT / "tests/fixtures"
PINS = (FIXTURES / "t0-revision-locks.json").read_bytes()
REQUEST = (FIXTURES / "t0-cd7-consumer-request.json").read_bytes()
RESPONSE = (FIXTURES / "t0-cd7-consumer-response.json").read_bytes()
ARTIFACTS = {"catalog_snapshot": CATALOG, "pricebook": PRICEBOOK}


def result(raw):
    return decode(raw)["x_t0_cd7_consumer_result"]


@contextmanager
def without_optional_formats():
    # Exercise the supported dependency configuration even if a developer has
    # installed JSON Schema's optional date-time extras.
    with patch("validate_research.FormatChecker", lambda: FormatChecker(formats=[])), \
            patch.object(consumer, "VALIDATOR", consumer.VALIDATOR.evolve(format_checker=None)):
        yield


def forged_artifact_response(kind, raw):
    # Keep a truthful advertised date while replacing the artifact bytes/digest.
    # The consumer must check the received document before trusting this claim.
    document = decode(RESPONSE)
    descriptor = document["x_t0_cd7_consumer_result"]["bindings"][kind]["artifact"]
    descriptor["sha256"], descriptor["byte_length"] = digest(raw), len(raw)
    descriptor["retrieval_path"] = "/artifacts/sha256/" + digest(raw) + ".json"
    artifacts = {**ARTIFACTS, kind: raw}
    return encoded(document), artifacts


class CD7Consumer(unittest.TestCase):
    def assert_code(self, code, function, *args, **kwargs):
        with self.assertRaises(ConsumerError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def test_exported_wire_examples_replay_exact_unchanged_frozen_bytes(self):
        Draft202012Validator.check_schema(SCHEMA)
        self.assertEqual(REQUEST, request(BUILD, PINS))
        self.assertEqual(RESPONSE, inspect(archive(), REQUEST, BUILD, PINS))
        accepted = verify_complete_pair(RESPONSE, REQUEST, BUILD, PINS, ARTIFACTS)
        self.assertIs(accepted[0], CATALOG)
        self.assertIs(accepted[1], PRICEBOOK)
        self.assertEqual(result(RESPONSE)["pair"]["status"], "resolved")
        self.assertEqual(result(RESPONSE)["qualification"],
                         {"publication": "not_established", "source_use": "not_established"})

    def test_portable_response_mutation_matrix_rejects_complete_pair(self):
        for case in json.loads((FIXTURES / "t0-cd7-consumer-negative.json").read_text())["cases"]:
            document = decode(RESPONSE)
            target = document["x_t0_cd7_consumer_result"]
            for key in case["path"][:-1]:
                target = target[key]
            target[case["path"][-1]] = case["value"]
            with self.subTest(case=case["id"]):
                self.assert_code(case["error"], verify_complete_pair, encoded(document),
                                 REQUEST, BUILD, PINS, ARTIFACTS)

    def test_request_and_result_bind_exact_request_build_and_sidecar_bytes(self):
        self.assert_code("request_build_mismatch", inspect, archive(), REQUEST, BUILD + b"\n", PINS)
        self.assert_code("request_sidecar_mismatch", inspect, archive(), REQUEST, BUILD, PINS + b"\n")
        self.assert_code("request_sidecar_mismatch", inspect, archive(), REQUEST, BUILD, None)
        equivalent_request = json.dumps(decode(REQUEST), indent=2).encode()
        self.assert_code("response_request_mismatch", verify_complete_pair, RESPONSE,
                         equivalent_request, BUILD, PINS, ARTIFACTS)

    def test_missing_unavailable_and_digest_mismatch_stay_distinct(self):
        missing = result(inspect(archive(), request(BUILD), BUILD))
        self.assertEqual({binding["status"] for binding in missing["bindings"].values()}, {"revision_pin_missing"})
        self.assertTrue(all("revision" not in binding for binding in missing["bindings"].values()))
        for stored, expected in ((SnapshotArchive([]), "pinned_revision_unavailable"),
                                 (archive(CATALOG + b"\n", PRICEBOOK + b"\n"), "content_digest_mismatch")):
            resolved = result(inspect(stored, REQUEST, BUILD, PINS))
            self.assertEqual({binding["status"] for binding in resolved["bindings"].values()}, {expected})
            self.assertEqual({selection["status"] for selection in resolved["selections"]}, {"snapshot_unresolved"})
            self.assertEqual(resolved["pair"], {"status": "incomplete"})

    def test_newer_artifacts_do_not_replace_unavailable_requested_revisions(self):
        newer = []
        for kind, raw in ARTIFACTS.items():
            document = decode(raw)
            document["revision"] = 2
            newer.append((kind, encoded(document)))
        response = result(inspect(SnapshotArchive(newer), REQUEST, BUILD, PINS))
        self.assertEqual({b["status"] for b in response["bindings"].values()}, {"pinned_revision_unavailable"})

    def test_partial_result_is_inspectable_but_never_a_complete_pair(self):
        raw = inspect(SnapshotArchive([("catalog_snapshot", CATALOG)]), REQUEST, BUILD, PINS)
        response = result(raw)
        self.assertEqual(response["bindings"]["catalog_snapshot"]["status"], "resolved")
        self.assertEqual(response["bindings"]["pricebook"]["status"], "pinned_revision_unavailable")
        self.assertEqual({s["status"] for s in response["selections"]}, {"resolved"})
        self.assert_code("pair_unresolved", verify_complete_pair, raw, REQUEST, BUILD, PINS, ARTIFACTS)
        self.assert_code("complete_pair_required", verify_complete_pair, RESPONSE, REQUEST,
                         BUILD, PINS, {"catalog_snapshot": CATALOG})

    def test_optional_pricebook_absence_is_preserved(self):
        build = decode(BUILD)
        del build["locks"]["pricebook_id"]
        raw = encoded(build)
        pins = sidecar(raw, pricebook=None)
        req = request(raw, pins)
        response = inspect(archive(), req, raw, pins)
        self.assertIsNone(result(response)["bindings"]["pricebook"])
        self.assertEqual(result(response)["pair"], {"status": "pricebook_absent"})
        self.assert_code("pair_unresolved", verify_complete_pair, response, req, raw, pins, ARTIFACTS)
        extra = sidecar(raw)
        self.assert_code("invalid_cd7_input", inspect, archive(), request(raw, extra), raw, extra)

    def test_original_selection_outcomes_have_no_inferred_values(self):
        build = decode(BUILD)
        build["selections"][0]["enabled"] = False
        build["selections"][1]["catalog_item_version"] = "missing-version"
        build["selections"][2]["catalog_item_id"] = build["selections"][3]["catalog_item_id"]
        raw = encoded(build)
        pins = sidecar(raw)
        selections = result(inspect(archive(), request(raw, pins), raw, pins))["selections"]
        self.assertEqual([s["status"] for s in selections[:3]],
                         ["not_enabled", "selected_version_absent", "selected_kind_mismatch"])
        self.assertTrue(all("catalog_item" not in s for s in selections[:3]))
        self.assertEqual(set(selections[3]["catalog_item"]), {"id", "version", "kind"})

    def test_native_revision_range_is_explicit_without_narrowing_frozen_v1(self):
        for revision in (MAX_REVISION, MAX_REVISION + 1):
            catalog = decode(CATALOG)
            catalog["revision"] = revision
            raw = encoded(catalog)
            pins = sidecar(catalog=raw)
            stored = archive(raw)  # Frozen schema still admits either positive integer.
            response = result(inspect(stored, request(BUILD, pins), BUILD, pins))
            binding = response["bindings"]["catalog_snapshot"]
            if revision == MAX_REVISION:
                self.assertEqual(binding["status"], "resolved")
                self.assertEqual(binding["revision"], MAX_REVISION)
            else:
                self.assertEqual(binding["status"], "native_revision_unsupported")
                self.assertNotIn("revision", binding)
                self.assertNotIn("artifact", binding)
                self.assertEqual(response["pair"]["status"], "incomplete")
        build = decode(BUILD)
        build["revision"] = MAX_REVISION + 1
        raw = encoded(build)
        self.assert_code("native_revision_unsupported", inspect, archive(), request(raw), raw)

    def test_new_wire_integer_tokens_do_not_coerce_float_bool_or_string(self):
        for value in (524288.0, True, "524288"):
            self.assert_code("integer_representation_unsupported", request, BUILD, PINS, value)
        pins = decode(PINS)
        pins["x_t0_revision_locks"]["artifacts"]["catalog_snapshot"]["revision"] = 1.0
        raw = encoded(pins)
        self.assert_code("invalid_cd7_input", inspect, archive(), request(BUILD, raw), BUILD, raw)

    def test_exact_pin_dispositions_withhold_bytes_without_granting_qualification(self):
        for status in ("revoked", "temporarily_unavailable"):
            dispositions = {("catalog_snapshot", "catalog.fixture.1", 1): status}
            response = result(inspect(archive(), REQUEST, BUILD, PINS, dispositions=dispositions))
            self.assertEqual(response["bindings"]["catalog_snapshot"]["status"], status)
            self.assertNotIn("artifact", response["bindings"]["catalog_snapshot"])
            self.assertEqual(response["pair"]["status"], "incomplete")
            self.assertEqual({s["status"] for s in response["selections"]}, {"snapshot_unresolved"})
            # A disposition for a different revision cannot affect this pin.
            other = {("catalog_snapshot", "catalog.fixture.1", 2): status}
            self.assertEqual(inspect(archive(), REQUEST, BUILD, PINS, dispositions=other), RESPONSE)
            # An observed integrity failure is not masked by a publisher status.
            corrupted = result(inspect(archive(CATALOG + b"\n"), REQUEST, BUILD, PINS, dispositions=dispositions))
            self.assertEqual(corrupted["bindings"]["catalog_snapshot"]["status"], "content_digest_mismatch")
        self.assert_code("invalid_disposition", inspect, archive(), REQUEST, BUILD, PINS,
                         dispositions={("catalog_snapshot", "catalog.fixture.1", 1): "approved"})

    def test_pricebook_must_reference_exact_members_of_this_catalog(self):
        for field, value in (("catalog_item_id", "cat.missing.fixture"),
                             ("catalog_item_version", "other-snapshot-version")):
            prices = decode(PRICEBOOK)
            prices["rates"][0][field] = value
            raw = encoded(prices)
            pins = sidecar(pricebook=raw)
            req = request(BUILD, pins)
            response = inspect(archive(pricebook=raw), req, BUILD, pins)
            with self.subTest(field=field):
                self.assertEqual(result(response)["pair"], {"status": "rate_catalog_mismatch",
                                 "unmatched_rate_ids": [prices["rates"][0]["id"]]})
                self.assertEqual({b["status"] for b in result(response)["bindings"].values()}, {"resolved"})
                self.assert_code("pair_unresolved", verify_complete_pair, response, req, BUILD,
                                 pins, {"catalog_snapshot": CATALOG, "pricebook": raw})

    def test_complete_pair_identity_changes_with_either_artifacts_exact_bytes(self):
        for kind in ARTIFACTS:
            changed = dict(ARTIFACTS)
            changed[kind] += b"\n"
            pins = sidecar(catalog=changed["catalog_snapshot"], pricebook=changed["pricebook"])
            req = request(BUILD, pins)
            response = inspect(SnapshotArchive(list(changed.items())), req, BUILD, pins)
            self.assertNotEqual(result(response)["pair"]["identity"], result(RESPONSE)["pair"]["identity"])
            self.assertEqual(verify_complete_pair(response, req, BUILD, pins, changed),
                             (changed["catalog_snapshot"], changed["pricebook"]))
            self.assert_code("content_length_mismatch", verify_complete_pair, RESPONSE,
                             REQUEST, BUILD, PINS, changed)

    def test_length_digest_and_structure_limits_precede_complete_pair_use(self):
        limit = max(len(BUILD), len(PRICEBOOK))
        self.assertLess(limit, len(CATALOG))
        req = request(BUILD, PINS, limit)
        response = result(inspect(archive(), req, BUILD, PINS))
        self.assertEqual(response["bindings"]["catalog_snapshot"]["status"], "artifact_too_large")
        self.assertEqual(response["pair"]["status"], "incomplete")
        changed = dict(ARTIFACTS)
        changed["pricebook"] = PRICEBOOK.replace(b"0.80", b"9.80")
        self.assertEqual(len(changed["pricebook"]), len(PRICEBOOK))
        self.assert_code("content_digest_mismatch", verify_complete_pair, RESPONSE,
                         REQUEST, BUILD, PINS, changed)
        self.assert_code("byte_limit_exceeded", wire, b" " * (MAX_ENVELOPE_BYTES + 1), "x_t0_cd7_consumer")
        deep = b"[" * MAX_DEPTH + b"0" + b"]" * MAX_DEPTH
        self.assert_code("structure_limit_exceeded", bounded_json, deep, DEFAULT_ARTIFACT_BYTES)
        many = encoded([0] * MAX_NODES)
        self.assert_code("structure_limit_exceeded", bounded_json, many, DEFAULT_ARTIFACT_BYTES)

    def test_strict_raw_json_rejects_escaped_duplicate_keys_and_nonfinite_tokens(self):
        duplicate = RESPONSE.replace(b'"publication":', b'"publi\\u0063ation":"not_established","publication":', 1)
        self.assert_code("malformed_document", wire, duplicate, "x_t0_cd7_consumer_result")
        for raw in (b'{"revision":1,"revi\\u0073ion":2}', b'{"amount":"1","amo\\u0075nt":"2"}',
                    b'{"sha256":"a","sha\\u003256":"b"}', b'{"x":NaN}', b'{"x":1e9999}', b'"\xff"'):
            with self.subTest(raw=raw):
                self.assert_code("malformed_document", bounded_json, raw, MAX_ENVELOPE_BYTES)
        self.assert_code("ambiguous_object_keys", bounded_json,
                         '{"\u00e9":1,"e\u0301":2}'.encode(), MAX_ENVELOPE_BYTES)

    def test_forged_valid_digest_cannot_bypass_full_artifact_validation(self):
        for field, value, code in (("schema_version", "1.1.0", "unsupported_schema_version"),
                                   ("rates", [], "invalid_artifact_document")):
            document = decode(PRICEBOOK)
            document[field] = value
            raw = encoded(document)
            response = decode(RESPONSE)
            descriptor = response["x_t0_cd7_consumer_result"]["bindings"]["pricebook"]["artifact"]
            descriptor["sha256"], descriptor["byte_length"] = digest(raw), len(raw)
            descriptor["retrieval_path"] = "/artifacts/sha256/" + digest(raw) + ".json"
            with self.subTest(field=field):
                self.assert_code(code, verify_complete_pair, encoded(response), REQUEST, BUILD,
                                 PINS, {"catalog_snapshot": CATALOG, "pricebook": raw})

    def test_native_unicode_profile_rejects_isolated_surrogates_in_keys_and_values(self):
        for raw in (b'"\\ud800"', b'"\\udfff"', b'{"\\ud800":1}',
                    b'{"x":"\\udfff"}', b'"\\ud800\\ud800"'):
            with self.subTest(raw=raw):
                self.assert_code("unicode_scalar_unsupported", bounded_json, raw, MAX_ENVELOPE_BYTES)
        # A properly paired escape decodes to one valid Unicode scalar.
        self.assertEqual(bounded_json(b'"\\ud83d\\ude00"', MAX_ENVELOPE_BYTES), "\U0001f600")
        self.assertEqual(bounded_json('{"\u00e9":"\U0001f600"}'.encode(), MAX_ENVELOPE_BYTES), {"\u00e9": "\U0001f600"})
        # Reproduce the receiving review's schema-valid but non-native version.
        catalog, build = decode(CATALOG), decode(BUILD)
        catalog["items"][0]["version"] = build["selections"][0]["catalog_item_version"] = "\ud800"
        raw_catalog, raw_build = encoded(catalog), encoded(build)
        pins = sidecar(raw_build, catalog=raw_catalog)
        stored = archive(raw_catalog)  # Frozen-v1 schema semantics are unchanged.
        self.assert_code("unicode_scalar_unsupported", inspect, stored,
                         request(raw_build, pins), raw_build, pins)
        # An artifact-only invalid scalar is withheld while the other artifact remains inspectable.
        catalog = decode(CATALOG)
        catalog["items"][0]["name"] = "\ud800"
        raw_catalog = encoded(catalog)
        pins = sidecar(catalog=raw_catalog)
        response = result(inspect(archive(raw_catalog), request(BUILD, pins), BUILD, pins))
        self.assertEqual(response["bindings"]["catalog_snapshot"]["status"], "artifact_structure_unsupported")
        self.assertEqual(response["bindings"]["pricebook"]["status"], "resolved")

    def test_mutating_decoded_envelopes_never_changes_retained_or_future_results(self):
        stored = archive()
        before = inspect(stored, REQUEST, BUILD, PINS)
        document = deepcopy(result(before))
        document["bindings"]["catalog_snapshot"]["artifact"]["id"] = "changed.fixture"
        document["selections"][0]["catalog_item"]["version"] = "changed"
        self.assertEqual(inspect(stored, REQUEST, BUILD, PINS), before)
        self.assertEqual(ARTIFACTS, {"catalog_snapshot": CATALOG, "pricebook": PRICEBOOK})

    def test_invalid_capture_dates_stay_inspectable_without_optional_formats(self):
        invalid = (
            "", "not-a-date", "2026-02-30T00:00:00Z", "2025-02-29T00:00:00Z",
            "2026-00-18T00:00:00Z", "2026-13-18T00:00:00Z", "0000-01-01T00:00:00Z",
            "2026-10-18T24:00:00Z", "2026-10-18T00:60:00Z", "2026-10-18T00:00:61Z",
            "2026-10-18T00:00:00", "2026-10-18 00:00:00Z", "2026-10-18T00:00:00.Z",
            "2026-10-18T00:00:00+24:00", "2026-10-18T00:00:00+00:60",
            "2026-10-18T00:00:00+0000", "2026-10-18T00:00:00Z\n",
            " 2026-10-18T00:00:00Z", "2026-10-18T00:00:00Z ",
            # Valid RFC leap-second syntax is explicitly outside this profile.
            "1990-12-31T23:59:60Z",
        )
        with without_optional_formats():
            for kind in ARTIFACTS:
                for captured_at in invalid:
                    document = decode(ARTIFACTS[kind])
                    document["captured_at"] = captured_at
                    artifacts = {**ARTIFACTS, kind: encoded(document)}
                    pins = sidecar(catalog=artifacts["catalog_snapshot"], pricebook=artifacts["pricebook"])
                    req = request(BUILD, pins)
                    stored = SnapshotArchive(list(artifacts.items()))
                    with self.subTest(kind=kind, captured_at=captured_at):
                        raw = inspect(stored, req, BUILD, pins)
                        observed = result(raw)
                        self.assertEqual(observed["bindings"][kind]["status"],
                                         "artifact_representation_unsupported")
                        self.assertNotIn("artifact", observed["bindings"][kind])
                        other = next(name for name in ARTIFACTS if name != kind)
                        self.assertEqual(observed["bindings"][other]["status"], "resolved")
                        self.assertEqual(observed["pair"], {"status": "incomplete"})
                        self.assert_code("pair_unresolved", verify_complete_pair,
                                         raw, req, BUILD, pins, artifacts)

    def test_received_dates_are_checked_in_both_descriptors_and_original_artifacts(self):
        with without_optional_formats():
            for kind in ARTIFACTS:
                for captured_at in ("not-a-date", "2026-02-30T00:00:00Z",
                                    "2026-10-18T00:00:00+24:00", "2026-10-18T00:00:00Z\n"):
                    with self.subTest(kind=kind, captured_at=captured_at):
                        response = decode(RESPONSE)
                        response["x_t0_cd7_consumer_result"]["bindings"][kind]["artifact"]["captured_at"] = captured_at
                        self.assert_code("artifact_representation_unsupported", wire,
                                         encoded(response), "x_t0_cd7_consumer_result")
                        document = decode(ARTIFACTS[kind])
                        document["captured_at"] = captured_at
                        response, artifacts = forged_artifact_response(kind, encoded(document))
                        self.assert_code("artifact_representation_unsupported", verify_complete_pair,
                                         response, REQUEST, BUILD, PINS, artifacts)

    def test_supported_capture_dates_preserve_original_strings_bytes_and_pair_identity(self):
        supported = (
            "0001-01-01T00:00:00+23:59", "9999-12-31T23:59:59-23:59",
            "2024-02-29t12:34:56.123456789012345678900z",
            "2026-10-18T12:30:00+05:45", "2026-10-18T12:30:00-00:00",
        )
        with without_optional_formats():
            for captured_at in supported:
                artifacts = {}
                for kind, raw in ARTIFACTS.items():
                    document = decode(raw)
                    document["captured_at"] = captured_at
                    artifacts[kind] = encoded(document)
                pins = sidecar(catalog=artifacts["catalog_snapshot"], pricebook=artifacts["pricebook"])
                req = request(BUILD, pins)
                response = inspect(SnapshotArchive(list(artifacts.items())), req, BUILD, pins)
                accepted = verify_complete_pair(response, req, BUILD, pins, artifacts)
                with self.subTest(captured_at=captured_at):
                    self.assertIs(accepted[0], artifacts["catalog_snapshot"])
                    self.assertIs(accepted[1], artifacts["pricebook"])
                    for kind in ARTIFACTS:
                        self.assertEqual(result(response)["bindings"][kind]["artifact"]["captured_at"], captured_at)
                    self.assertNotEqual(result(response)["pair"]["identity"], result(RESPONSE)["pair"]["identity"])
                    self.assertEqual(result(response)["qualification"], result(RESPONSE)["qualification"])

    def test_newline_rate_id_is_withheld_before_membership_or_output_encoding(self):
        for mismatched in (False, True):
            prices = decode(PRICEBOOK)
            prices["rates"][0]["id"] += "\n"
            if mismatched:
                prices["rates"][0]["catalog_item_id"] = "cat.missing.fixture"
            raw = encoded(prices)
            pins = sidecar(pricebook=raw)
            req = request(BUILD, pins)
            with self.subTest(mismatched=mismatched):
                # Frozen validation admits this suffix; never strip retained IDs.
                response = result(inspect(archive(pricebook=raw), req, BUILD, pins))
                self.assertEqual(response["bindings"]["pricebook"]["status"],
                                 "artifact_representation_unsupported")
                self.assertEqual(response["bindings"]["catalog_snapshot"]["status"], "resolved")
                self.assertEqual(response["pair"], {"status": "incomplete"})
                forged, artifacts = forged_artifact_response("pricebook", raw)
                self.assert_code("artifact_representation_unsupported", verify_complete_pair,
                                 forged, REQUEST, BUILD, PINS, artifacts)
        # A well-formed cross-catalog rate keeps its existing distinct result.
        prices["rates"][0]["id"] = prices["rates"][0]["id"].rstrip("\n")
        raw = encoded(prices)
        pins = sidecar(pricebook=raw)
        observed = result(inspect(archive(pricebook=raw), request(BUILD, pins), BUILD, pins))
        self.assertEqual(observed["pair"], {"status": "rate_catalog_mismatch",
                         "unmatched_rate_ids": [prices["rates"][0]["id"]]})

    def test_native_id_profile_covers_artifact_members_and_reference_fields(self):
        catalog = decode(CATALOG)
        model = next(i for i, item in enumerate(catalog["items"]) if item["kind"] == "model")
        for kind, path in (
                ("catalog_snapshot", ("items", 0, "id")),
                ("catalog_snapshot", ("items", model, "spec", "provider_ref")),
                ("pricebook", ("rates", 0, "catalog_item_id"))):
            document = decode(ARTIFACTS[kind])
            target = document
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] += "\n"
            artifacts = {**ARTIFACTS, kind: encoded(document)}
            pins = sidecar(catalog=artifacts["catalog_snapshot"], pricebook=artifacts["pricebook"])
            with self.subTest(kind=kind, path=path):
                response = result(inspect(SnapshotArchive(list(artifacts.items())),
                                          request(BUILD, pins), BUILD, pins))
                self.assertEqual(response["bindings"][kind]["status"], "artifact_representation_unsupported")
                self.assertEqual(response["pair"], {"status": "incomplete"})

    def test_native_build_and_wire_selection_ids_require_the_entire_string(self):
        for path in (("id",), ("locks", "dependency_graph_id"), ("selections", 0, "id"),
                     ("selections", 0, "catalog_item_id"), ("links", 0, "id"),
                     ("links", 0, "from_selection_id"), ("links", 0, "to_selection_id")):
            build = decode(BUILD)
            target = build
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] += "\n"
            raw = encoded(build)
            pins = sidecar(raw)
            with self.subTest(path=path):
                self.assert_code("invalid_cd7_input", inspect, archive(), request(raw, pins), raw, pins)
        response = decode(RESPONSE)
        response["x_t0_cd7_consumer_result"]["selections"][0]["selection_id"] += "\n"
        self.assert_code("malformed_envelope", wire, encoded(response), "x_t0_cd7_consumer_result")

    def test_native_id_checks_preserve_frozen_schemas_and_untyped_extension_values(self):
        frozen = {path.name: json.loads(path.read_text())
                  for path in (ROOT / "contracts/v1/schemas").glob("*.schema.json")}
        self.assertEqual(consumer.SCHEMAS, frozen)
        catalog = decode(CATALOG)
        catalog["items"][0]["extensions"] = {
            "x_cd7_fixture": {"id": "external/display id\n", "captured_at": "display text, not a timestamp\n"}}
        raw = encoded(catalog)
        pins = sidecar(catalog=raw)
        req = request(BUILD, pins)
        response = inspect(archive(raw), req, BUILD, pins)
        accepted = verify_complete_pair(response, req, BUILD, pins,
                                        {"catalog_snapshot": raw, "pricebook": PRICEBOOK})
        self.assertIs(accepted[0], raw)
        self.assertEqual(consumer.SCHEMAS, frozen)

    def test_descriptor_timestamps_are_ascii_without_narrowing_frozen_v1(self):
        for captured_at in ("２０２６-10-16T09:00:00Z", "٢٠٢٦-10-16T09:00:00Z",
                            "2026-１０-16T09:00:00Z", "2026-10-16T０９:00:00Z"):
            catalog = decode(CATALOG)
            catalog["captured_at"] = captured_at
            raw = encoded(catalog)
            stored = archive(raw)  # The pinned frozen format checker admits these.
            pins = sidecar(catalog=raw)
            req = request(BUILD, pins)
            response = inspect(stored, req, BUILD, pins)
            with self.subTest(captured_at=captured_at):
                self.assertEqual(result(response)["bindings"]["catalog_snapshot"]["status"],
                                 "artifact_representation_unsupported")
                self.assertEqual(result(response)["bindings"]["pricebook"]["status"], "resolved")
                self.assertEqual(result(response)["pair"]["status"], "incomplete")
                # A producer cannot advertise an ASCII date while returning
                # otherwise digest-valid bytes with a non-ASCII date.
                forged = decode(RESPONSE)
                descriptor = forged["x_t0_cd7_consumer_result"]["bindings"]["catalog_snapshot"]["artifact"]
                descriptor["sha256"], descriptor["byte_length"] = digest(raw), len(raw)
                descriptor["retrieval_path"] = "/artifacts/sha256/" + digest(raw) + ".json"
                self.assert_code("artifact_representation_unsupported", verify_complete_pair,
                                 encoded(forged), REQUEST, BUILD, PINS,
                                 {"catalog_snapshot": raw, "pricebook": PRICEBOOK})


if __name__ == "__main__":
    unittest.main()
