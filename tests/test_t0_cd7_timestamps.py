from contextlib import ExitStack
from copy import deepcopy
import unittest
from unittest.mock import patch

from jsonschema import FormatChecker

import t0_cd7_consumer_prototype as consumer
import validate_research
from test_t0_cd7_consumer import ARTIFACTS, BUILD, CATALOG, PINS, PRICEBOOK, REQUEST, RESPONSE
from test_t0_revision_locks import archive, sidecar


INVALID_TIMESTAMPS = (
    "not-a-date", "2026-10-18", "2026-10-18T12:34:56",
    "2026-10-18 12:34:56Z", "2026-10-18T12:34Z",
    "2026-02-30T12:34:56Z", "2025-02-29T12:34:56Z",
    "1900-02-29T12:34:56Z", "2026-00-18T12:34:56Z",
    "2026-13-18T12:34:56Z", "0000-01-01T00:00:00Z",
    "2026-10-18T24:00:00Z", "2026-10-18T12:60:00Z",
    "2026-10-18T12:34:60Z", "2026-10-18T12:34:56+24:00",
    "2026-10-18T12:34:56+00:60", "2026-10-18T12:34:56+0000",
    "2026-10-18T12:34:56.Z", "2026-10-18T12:34:56,1Z",
    "2026-10-18T12:34:56Z\n", " 2026-10-18T12:34:56Z",
    "2026-10-18T12:34:56Zextra", "2026-10-18T12:34:56\x00Z",
)


class CD7TimestampBoundary(unittest.TestCase):
    def without_format_providers(self):
        stack = ExitStack()
        stack.enter_context(patch.object(
            consumer, "VALIDATOR", consumer.VALIDATOR.evolve(format_checker=None)))
        stack.enter_context(patch.object(
            validate_research, "FormatChecker", return_value=FormatChecker(formats=[])))
        return stack

    def assert_unsupported(self, function, *args):
        with self.assertRaises(consumer.ConsumerError) as caught:
            function(*args)
        self.assertEqual(caught.exception.code, "artifact_representation_unsupported")

    def test_wire_rejects_malformed_ascii_dates_without_optional_format_providers(self):
        with self.without_format_providers():
            for captured_at in INVALID_TIMESTAMPS:
                for kind in ARTIFACTS:
                    response = consumer.decode(RESPONSE)
                    response["x_t0_cd7_consumer_result"]["bindings"][kind]["artifact"]["captured_at"] = captured_at
                    with self.subTest(kind=kind, captured_at=captured_at):
                        self.assert_unsupported(consumer.wire, consumer.encoded(response),
                                                "x_t0_cd7_consumer_result")

    def test_bad_retained_dates_withhold_only_that_artifact_without_rewriting_history(self):
        with self.without_format_providers():
            for kind, original in ARTIFACTS.items():
                for captured_at in INVALID_TIMESTAMPS:
                    document = consumer.decode(original)
                    document["captured_at"] = captured_at
                    raw = consumer.encoded(document)
                    artifacts = {**ARTIFACTS, kind: raw}
                    pins = sidecar(catalog=artifacts["catalog_snapshot"], pricebook=artifacts["pricebook"])
                    req = consumer.request(BUILD, pins)
                    stored = consumer.SnapshotArchive(list(artifacts.items()))
                    response = consumer.decode(consumer.inspect(stored, req, BUILD, pins))["x_t0_cd7_consumer_result"]
                    with self.subTest(kind=kind, captured_at=captured_at):
                        self.assertEqual(response["bindings"][kind]["status"], "artifact_representation_unsupported")
                        other = "pricebook" if kind == "catalog_snapshot" else "catalog_snapshot"
                        self.assertEqual(response["bindings"][other]["status"], "resolved")
                        self.assertEqual(response["pair"], {"status": "incomplete"})
                        self.assertNotIn("artifact", response["bindings"][kind])
                        retained = stored.resolve(BUILD, pins)
                        self.assertEqual(getattr(retained, kind).raw, raw)
                        self.assertEqual(consumer.decode(raw)["captured_at"], captured_at)

    def test_complete_pair_rejects_matching_bad_dates_and_retains_previous_pair(self):
        with self.without_format_providers():
            previous = consumer.verify_complete_pair(RESPONSE, REQUEST, BUILD, PINS, ARTIFACTS)
            for kind, original in ARTIFACTS.items():
                document = consumer.decode(original)
                document["captured_at"] = "2026-02-30T12:34:56Z"
                raw = consumer.encoded(document)
                artifacts = {**ARTIFACTS, kind: raw}
                pins = sidecar(catalog=artifacts["catalog_snapshot"], pricebook=artifacts["pricebook"])
                req = consumer.request(BUILD, pins)
                response = consumer.decode(RESPONSE)
                packet = response["x_t0_cd7_consumer_result"]
                packet["request_sha256"] = consumer.digest(req)
                descriptor = packet["bindings"][kind]["artifact"]
                descriptor.update(captured_at=document["captured_at"], sha256=consumer.digest(raw),
                                  byte_length=len(raw), retrieval_path="/artifacts/sha256/" + consumer.digest(raw) + ".json")
                packet["pair"]["identity"] = consumer.pair_identity(
                    packet["bindings"]["catalog_snapshot"]["artifact"], packet["bindings"]["pricebook"]["artifact"])
                with self.subTest(kind=kind):
                    self.assert_unsupported(consumer.verify_complete_pair, consumer.encoded(response),
                                            req, BUILD, pins, artifacts)
                    self.assertEqual(previous, (CATALOG, PRICEBOOK))
            self.assertEqual(consumer.verify_complete_pair(RESPONSE, REQUEST, BUILD, PINS, ARTIFACTS), previous)

    def test_supported_dates_preserve_original_spelling_and_bytes(self):
        values = (
            "0001-01-01T00:00:00Z", "9999-12-31T23:59:59Z",
            "2000-02-29T23:59:59Z", "2024-02-29t23:59:59z",
            "2026-10-18T12:34:56.12345678901234567890+23:59",
            "2026-10-18T12:34:56.0-23:59", "2026-10-18T12:34:56-00:00",
        )
        with self.without_format_providers():
            for captured_at in values:
                for kind, original in ARTIFACTS.items():
                    document = consumer.decode(original)
                    document["captured_at"] = captured_at
                    artifacts = {**ARTIFACTS, kind: consumer.encoded(document)}
                    before = deepcopy(artifacts)
                    pins = sidecar(catalog=artifacts["catalog_snapshot"], pricebook=artifacts["pricebook"])
                    req = consumer.request(BUILD, pins)
                    response = consumer.inspect(consumer.SnapshotArchive(list(artifacts.items())), req, BUILD, pins)
                    with self.subTest(kind=kind, captured_at=captured_at):
                        descriptor = consumer.decode(response)["x_t0_cd7_consumer_result"]["bindings"][kind]["artifact"]
                        self.assertEqual(descriptor["captured_at"], captured_at)
                        self.assertEqual(consumer.verify_complete_pair(response, req, BUILD, pins, artifacts),
                                         (artifacts["catalog_snapshot"], artifacts["pricebook"]))
                        self.assertEqual(artifacts, before)

    def test_digest_mismatch_still_precedes_artifact_representation(self):
        catalog = consumer.decode(CATALOG)
        catalog["captured_at"] = "not-a-date"
        with self.without_format_providers():
            stored = archive(consumer.encoded(catalog))
            response = consumer.decode(consumer.inspect(stored, REQUEST, BUILD, PINS))["x_t0_cd7_consumer_result"]
            self.assertEqual(response["bindings"]["catalog_snapshot"]["status"], "content_digest_mismatch")
            self.assertEqual(response["bindings"]["pricebook"]["status"], "resolved")


if __name__ == "__main__":
    unittest.main()
