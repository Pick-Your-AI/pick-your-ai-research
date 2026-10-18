"""Synthetic CD-7/SB-2/SB-3/SB-R1 artifact binding, never real source evidence."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from t0_revision_lock_prototype import PIN_SCHEMA, PIN_VALIDATOR, SnapshotArchive, digest

EXAMPLES = ROOT / "contracts/v1/examples"
BUILD = (EXAMPLES / "build.json").read_bytes()
CATALOG = (EXAMPLES / "catalog.json").read_bytes()
PRICEBOOK = (EXAMPLES / "pricebook.json").read_bytes()


def encoded(value):
    return json.dumps(value, allow_nan=False).encode("utf-8")


def sidecar(build=BUILD, catalog=CATALOG, pricebook=PRICEBOOK):
    pins = {}
    for kind, raw in (("catalog_snapshot", catalog), ("pricebook", pricebook)):
        if raw is not None:
            document = json.loads(raw)
            pins[kind] = {"id": document["id"], "revision": document["revision"], "sha256": digest(raw)}
    return encoded({"x_t0_revision_locks": {"proposal_version": "cd7-0.1",
                    "build_sha256": digest(build), "artifacts": pins}})


def archive(catalog=CATALOG, pricebook=PRICEBOOK):
    return SnapshotArchive([("catalog_snapshot", catalog), ("pricebook", pricebook)])


class RevisionLocks(unittest.TestCase):
    def test_published_fixture_resolves_original_bytes_and_members(self):
        Draft202012Validator.check_schema(PIN_SCHEMA)
        pins = (ROOT / "tests/fixtures/t0-revision-locks.json").read_bytes()
        result = archive().resolve(BUILD, pins)
        self.assertIs(result.original_bytes, BUILD)
        self.assertEqual(result.catalog_snapshot.raw, CATALOG)
        self.assertEqual(result.pricebook.raw, PRICEBOOK)
        self.assertEqual({s.status for s in result.selections}, {"resolved"})
        self.assertEqual(len(result.selections), len(json.loads(BUILD)["selections"]))

    def test_newer_revision_never_replaces_a_pin_in_either_archive_order(self):
        newer_catalog, newer_prices = json.loads(CATALOG), json.loads(PRICEBOOK)
        newer_catalog["revision"] = newer_prices["revision"] = 2
        newer_catalog["items"][0]["name"] = "Synthetic replacement"
        newer_prices["rates"][0]["unit_price"]["amount"] = "999"
        records = [("catalog_snapshot", CATALOG), ("pricebook", PRICEBOOK),
                   ("catalog_snapshot", encoded(newer_catalog)), ("pricebook", encoded(newer_prices))]
        for ordered in (records, list(reversed(records))):
            result = SnapshotArchive(ordered).resolve(BUILD, sidecar())
            self.assertEqual((result.catalog_snapshot.raw, result.pricebook.raw), (CATALOG, PRICEBOOK))

    def test_missing_revision_is_unresolved_even_with_only_one_available_candidate(self):
        for pins in (None, sidecar(catalog=None, pricebook=None)):
            result = archive().resolve(BUILD, pins)
            self.assertEqual(result.catalog_snapshot.status, "revision_pin_missing")
            self.assertEqual(result.pricebook.status, "revision_pin_missing")
            self.assertEqual({s.status for s in result.selections}, {"snapshot_unresolved"})
            self.assertTrue(all(s.item is None for s in result.selections))
            self.assertEqual(result.original_bytes, BUILD)

    def test_unavailable_exact_revisions_do_not_fall_back(self):
        catalog, prices = json.loads(CATALOG), json.loads(PRICEBOOK)
        catalog["revision"] = prices["revision"] = 2
        result = archive(encoded(catalog), encoded(prices)).resolve(BUILD, sidecar())
        self.assertEqual(result.catalog_snapshot.status, "pinned_revision_unavailable")
        self.assertEqual(result.pricebook.status, "pinned_revision_unavailable")
        self.assertIsNone(result.catalog_snapshot.raw)
        self.assertIsNone(result.pricebook.raw)

    def test_even_equivalent_json_bytes_require_the_selected_content_digest(self):
        result = archive(CATALOG + b"\n", PRICEBOOK + b"\n").resolve(BUILD, sidecar())
        self.assertEqual(result.catalog_snapshot.status, "content_digest_mismatch")
        self.assertEqual(result.pricebook.status, "content_digest_mismatch")
        self.assertTrue(all(s.item is None for s in result.selections))

    def test_sidecar_cannot_retarget_an_edited_build_or_different_artifact_id(self):
        changed = json.loads(BUILD)
        changed["name"] += " edited"
        with self.assertRaisesRegex(ValueError, "different build bytes"):
            archive().resolve(encoded(changed), sidecar())
        for kind in ("catalog_snapshot", "pricebook"):
            pins = json.loads(sidecar())
            pins["x_t0_revision_locks"]["artifacts"][kind]["id"] = "different.fixture"
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "artifact ID"):
                archive().resolve(BUILD, encoded(pins))

    def test_optional_pricebook_is_absent_and_sidecar_cannot_add_one(self):
        build = json.loads(BUILD)
        del build["locks"]["pricebook_id"]
        raw = encoded(build)
        result = archive().resolve(raw, sidecar(raw, pricebook=None))
        self.assertIsNone(result.pricebook)
        self.assertEqual(result.catalog_snapshot.status, "resolved")
        with self.assertRaisesRegex(ValueError, "cannot add a pricebook"):
            archive().resolve(raw, sidecar(raw))

    def test_resolved_catalog_preserves_an_independent_pricebook_failure(self):
        result = SnapshotArchive([("catalog_snapshot", CATALOG)]).resolve(BUILD, sidecar())
        self.assertEqual(result.catalog_snapshot.status, "resolved")
        self.assertEqual(result.pricebook.status, "pinned_revision_unavailable")
        self.assertEqual({s.status for s in result.selections}, {"resolved"})

    def test_multiple_versions_bind_exact_selected_version_in_either_order(self):
        catalog = json.loads(CATALOG)
        original = deepcopy(catalog["items"][0])
        newer = deepcopy(original)
        newer["version"], newer["name"] = "synthetic-next", "Different synthetic version"
        for last in (False, True):
            catalog["items"] = ([original, newer] if last else [newer, original]) + json.loads(CATALOG)["items"][1:]
            raw = encoded(catalog)
            result = archive(raw).resolve(BUILD, sidecar(catalog=raw))
            item = next(s.item for s in result.selections if s.item and s.item["id"] == original["id"])
            self.assertEqual(item, original)

    def test_known_missing_version_is_distinct_from_unavailable_snapshot_or_disabled_selection(self):
        build = json.loads(BUILD)
        build["selections"][0]["catalog_item_version"] = "absent-synthetic-version"
        raw = encoded(build)
        result = archive().resolve(raw, sidecar(raw))
        self.assertEqual(result.selections[0].status, "selected_version_absent")
        self.assertIsNone(result.selections[0].item)
        self.assertEqual(archive().resolve(raw).selections[0].status, "snapshot_unresolved")
        build["selections"][0]["enabled"] = False
        raw = encoded(build)
        self.assertEqual(archive().resolve(raw, sidecar(raw)).selections[0].status, "not_enabled")

    def test_wrong_selection_kind_does_not_expose_an_unrelated_item(self):
        build = json.loads(BUILD)
        build["selections"][0]["catalog_item_id"] = build["selections"][1]["catalog_item_id"]
        build["selections"][0]["catalog_item_version"] = build["selections"][1]["catalog_item_version"]
        raw = encoded(build)
        result = archive().resolve(raw, sidecar(raw))
        self.assertEqual(result.selections[0].status, "selected_kind_mismatch")
        self.assertIsNone(result.selections[0].item)

    def test_build_identity_validation_includes_disabled_selections(self):
        for same_role in (False, True):
            build = json.loads(BUILD)
            extra = deepcopy(build["selections"][0])
            extra["enabled"] = False
            if same_role:
                extra["id"] += "_copy"
            build["selections"].append(extra)
            raw = encoded(build)
            with self.subTest(same_role=same_role), self.assertRaises(ValueError):
                archive().resolve(raw, sidecar(raw))

    def test_duplicate_archive_or_member_identities_are_rejected(self):
        for kind, original, member_key in (("catalog_snapshot", CATALOG, "items"), ("pricebook", PRICEBOOK, "rates")):
            for different in (False, True):
                changed = json.loads(original)
                if different:
                    changed["captured_at"] = "2026-10-18T00:00:00Z"
                with self.subTest(kind=kind, different=different), self.assertRaisesRegex(ValueError, "immutable"):
                    SnapshotArchive([(kind, original), (kind, encoded(changed))])
            changed = json.loads(original)
            changed[member_key].append(deepcopy(changed[member_key][0]))
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "member identity"):
                SnapshotArchive([(kind, encoded(changed))])

    def test_invalid_retained_schema_versions_types_and_kind_bindings_are_rejected(self):
        for kind, original in (("catalog_snapshot", CATALOG), ("pricebook", PRICEBOOK)):
            for key, value in (("schema_version", "1.1.0"), ("revision", True), ("revision", 1.0), ("revision", 0)):
                changed = json.loads(original)
                changed[key] = value
                with self.subTest(kind=kind, key=key, value=value), self.assertRaises(ValueError):
                    SnapshotArchive([(kind, encoded(changed))])
        with self.assertRaises(ValueError):
            SnapshotArchive([("pricebook", CATALOG)])
        with self.assertRaises(ValueError):
            SnapshotArchive([("unknown", CATALOG)])
        catalog = json.loads(CATALOG)
        catalog["items"][0]["tier"] = "T6"
        with self.assertRaises(ValueError):
            archive(encoded(catalog))

    def test_sidecar_shape_and_integer_revisions_are_strict(self):
        for field, value in (("revision", True), ("revision", 1.0), ("revision", "1"),
                             ("revision", 0), ("sha256", "f" * 64 + "\n"), ("sha256", "F" * 64)):
            pins = json.loads(sidecar())
            pins["x_t0_revision_locks"]["artifacts"]["catalog_snapshot"][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                archive().resolve(BUILD, encoded(pins))
        for change in ("unknown_version", "unknown_artifact", "missing_digest", "extra_pin_field"):
            pins = json.loads(sidecar())
            proposal = pins["x_t0_revision_locks"]
            if change == "unknown_version": proposal["proposal_version"] = "cd7-0.2"
            elif change == "unknown_artifact": proposal["artifacts"]["latest"] = {}
            elif change == "missing_digest": del proposal["artifacts"]["pricebook"]["sha256"]
            else: proposal["artifacts"]["pricebook"]["fallback"] = "latest"
            with self.subTest(change=change), self.assertRaises(ValueError):
                archive().resolve(BUILD, encoded(pins))

    def test_pin_id_schema_rejects_forbidden_characters_and_enforces_full_length(self):
        for kind in ("catalog_snapshot", "pricebook"):
            pins = json.loads(sidecar())
            pin = pins["x_t0_revision_locks"]["artifacts"][kind]
            for value in ("abc", "a" * 120, "a-b.c_d:e"):
                pin["id"] = value
                with self.subTest(kind=kind, value=value):
                    self.assertTrue(PIN_VALIDATOR.is_valid(pins))
            for value in ("ab", "a" * 121, "Abc", "abc\n", "a" * 120 + "\n",
                          "abc\r", "abc\r\n", "abc\t", "abc ", "abc\u2028", "a\nbc"):
                pin["id"] = value
                with self.subTest(kind=kind, value=value):
                    self.assertFalse(PIN_VALIDATOR.is_valid(pins))

    def test_matching_malformed_record_ids_cannot_bypass_pin_validation(self):
        for kind, original in (("catalog_snapshot", CATALOG), ("pricebook", PRICEBOOK)):
            for identity in (json.loads(original)["id"] + "\n", "a" * 120 + "\n"):
                build, artifact = json.loads(BUILD), json.loads(original)
                artifact["id"] = build["locks"][kind + "_id"] = identity
                raw_build, raw_artifact = encoded(build), encoded(artifact)
                catalog = raw_artifact if kind == "catalog_snapshot" else CATALOG
                pricebook = raw_artifact if kind == "pricebook" else PRICEBOOK
                # Frozen v1's $ anchor admits these IDs. The new sidecar must
                # reject them even when every ID and content hash agrees.
                retained = archive(catalog, pricebook)
                pins = sidecar(raw_build, catalog, pricebook)
                with self.subTest(kind=kind, identity=identity), self.assertRaisesRegex(ValueError, "invalid CD-7 pins"):
                    retained.resolve(raw_build, pins)

    def test_strict_json_applies_to_each_retained_and_sidecar_input(self):
        readers = ((BUILD, lambda raw: archive().resolve(raw, sidecar())),
                   (sidecar(), lambda raw: archive().resolve(BUILD, raw)),
                   (CATALOG, lambda raw: SnapshotArchive([("catalog_snapshot", raw)])),
                   (PRICEBOOK, lambda raw: SnapshotArchive([("pricebook", raw)])))
        for index, (original, read) in enumerate(readers):
            document = json.loads(original)
            first_key = next(iter(document))
            # Last-key-wins would produce the same schema-valid document.
            for spelling in (json.dumps(first_key), '"\\u%04x%s"' % (ord(first_key[0]), first_key[1:])):
                repeated = encoded(document)[:-1] + ("," + spelling + ":" + json.dumps(document[first_key]) + "}").encode()
                with self.subTest(reader=index, spelling=spelling), self.assertRaisesRegex(ValueError, "duplicate JSON"):
                    read(repeated)
            for number in (b"NaN", b"Infinity", b"1e999"):
                invalid = encoded(document)[:-1] + b',"nonfinite":' + number + b"}"
                with self.subTest(reader=index, number=number), self.assertRaisesRegex(ValueError, "finite"):
                    read(invalid)
            with self.subTest(reader=index), self.assertRaises(ValueError):
                read(b"\xff")

    def test_returned_items_are_detached_from_each_other_and_retained_bytes(self):
        build = json.loads(BUILD)
        other = deepcopy(build["selections"][0])
        other["id"], other["role"] = "sel_workload_secondary", "secondary"
        build["selections"].append(other)
        raw = encoded(build)
        retained = archive()
        result = retained.resolve(raw, sidecar(raw))
        original_name = result.selections[-1].item["name"]
        result.selections[0].item["name"] = "mutated output"
        self.assertEqual(result.selections[-1].item["name"], original_name)
        self.assertEqual(retained.resolve(raw, sidecar(raw)).selections[0].item["name"], original_name)
        self.assertEqual(result.catalog_snapshot.raw, CATALOG)
        self.assertEqual(result.original_bytes, raw)

    def test_frozen_historical_evaluation_is_unchanged(self):
        sys.path.insert(0, str(ROOT / "contracts/v1/reference"))
        from evaluate import Evaluator
        def evaluate(raw):
            report = Evaluator(json.loads(raw), json.loads(CATALOG),
                               json.loads((EXAMPLES / "ruleset.json").read_bytes())).evaluate()
            return report["result"], report["findings"], report["summary"]
        baseline = evaluate(BUILD)
        for pins in (None, sidecar()):
            result = archive().resolve(BUILD, pins)
            self.assertEqual(result.original_bytes, BUILD)
            self.assertEqual(evaluate(result.original_bytes), baseline)


if __name__ == "__main__":
    unittest.main()
