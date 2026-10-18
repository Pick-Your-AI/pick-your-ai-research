"""Synthetic source identity/date admission; no source is fetched or graded."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from tests.support_evidence_admission_prototype import (
    MAX_EVIDENCE_BYTES, RESULT, SupportEvidenceRecord,
)
from tests.support_membership_binding_prototype import (
    ELIGIBILITY, SupportQueryRecord, answer_path, digest,
)


FIXTURES = Path(__file__).with_name("fixtures")
QUALIFIED = dict.fromkeys(ELIGIBILITY, True)


def encoded(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")


class SupportEvidenceAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.binding_raw = (FIXTURES / "support-membership-binding.json").read_bytes()
        self.answers_raw = (FIXTURES / "support-membership-answers.json").read_bytes()
        self.evidence_raw = (FIXTURES / "support-evidence-admission.json").read_bytes()
        self.document = json.loads(self.evidence_raw)

    def record(self, document=None, evidence_raw=None):
        raw = evidence_raw if evidence_raw is not None else (
            self.evidence_raw if document is None else encoded(document))
        return SupportEvidenceRecord(raw, self.binding_raw, self.answers_raw)

    def context(self, record, **changes):
        return {"enabled": True, "eligible_inputs": QUALIFIED,
                "qualified_evidence_sha256": digest(record.original_bytes[0]),
                "source_qualified": True, **changes}

    def evaluated(self, record=None, **changes):
        record = record or self.record()
        return record.evaluate(record.scope, **self.context(record, **changes))

    def decision(self, result):
        return result["x_t0_support_evidence_result"]["membership"]["x_t0_support_result"]["decision"]

    def change_answers(self, **changes):
        binding = json.loads(self.binding_raw)
        answers = json.loads(self.answers_raw)
        proposal = binding["x_t0_support_query"]
        for field, value in changes.items():
            answers["x_t0_answer_states"]["answers"][answer_path(proposal, field)] = value
        self.answers_raw = encoded(answers)
        proposal["answer_states_sha256"] = digest(self.answers_raw)
        self.binding_raw = encoded(binding)
        self.document["x_t0_support_evidence"]["binding_sha256"] = digest(self.binding_raw)
        self.evidence_raw = encoded(self.document)

    def test_actual_prior_binding_carries_scope_but_has_no_source_date_slot(self):
        query = SupportQueryRecord(self.binding_raw, self.answers_raw)
        result = query.evaluate(query.scope, enabled=True, eligible_inputs=QUALIFIED)
        self.assertEqual(result["x_t0_support_result"]["decision"]["outcome"], "pass")
        self.assertEqual(result["x_t0_support_result"]["scope"], self.document["x_t0_support_evidence"]["scope"])
        for field, value in (("checked_at", "2026-10-18T00:00:00Z"),
                             ("source_uri", self.document["x_t0_support_evidence"]["sources"][0]["source_uri"])):
            changed = json.loads(self.binding_raw)
            changed["x_t0_support_query"]["cohort"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                SupportQueryRecord(encoded(changed), self.answers_raw)

    def test_dated_exact_scope_source_record_and_original_bytes_are_retained(self):
        record = self.record()
        result = self.evaluated(record)
        value = result["x_t0_support_evidence_result"]
        self.assertTrue(RESULT.is_valid(result))
        expected_fixture = json.loads((FIXTURES / "support-evidence-admission-result.json").read_bytes())
        self.assertEqual(result, expected_fixture)
        self.assertEqual(value["evidence"], self.document["x_t0_support_evidence"])
        self.assertEqual(record.original_bytes, (self.evidence_raw, self.binding_raw, self.answers_raw))
        self.assertEqual(value["admission"]["reason"], "source_qualified")
        self.assertEqual(self.decision(result)["outcome"], "pass")
        self.assertIsNone(self.decision(result)["evidence_label"])
        self.assertEqual(record.verify_result(encoded(result), record.scope, **self.context(record)), result)

    def test_every_required_source_and_context_field_is_checked(self):
        for location, fields in (((), ("proposal_version", "binding_sha256", "query", "scope", "cohort", "sources")),
                                 (("sources", 0), ("id", "revision", "source_uri", "checked_at"))):
            for field in fields:
                changed = deepcopy(self.document)
                target = changed["x_t0_support_evidence"]
                for part in location:
                    target = target[part]
                del target[field]
                with self.subTest(location=location, field=field), self.assertRaisesRegex(ValueError, "shape_malformed"):
                    self.record(changed)

    def test_extra_fields_cannot_supply_authority_or_secret_reference_slots(self):
        for location in ((), ("sources", 0), ("scope",), ("cohort",)):
            for field in ("eligible", "checked_only", "secret_ref"):
                changed = deepcopy(self.document)
                target = changed["x_t0_support_evidence"]
                for part in location:
                    target = target[part]
                target[field] = True
                with self.subTest(location=location, field=field), self.assertRaisesRegex(ValueError, "shape_malformed"):
                    self.record(changed)

    def test_source_timestamps_need_real_calendar_and_explicit_offset_without_extras(self):
        for timestamp in ("not-a-date", "2026-02-30T00:00:00Z", "2025-02-29T00:00:00Z",
                          "2026-10-18", "2026-10-18T00:00:00", "2026-10-18T24:00:00Z",
                          "2026-10-18T00:00:60Z", "2026-10-18T00:00:00+24:00",
                          "2026-10-18T00:00:00+00:60", "0000-01-01T00:00:00Z",
                          "２０２６-10-18T00:00:00Z", "2026-10-18T00:00:00Z\n"):
            changed = deepcopy(self.document)
            changed["x_t0_support_evidence"]["sources"][0]["checked_at"] = timestamp
            with self.subTest(timestamp=timestamp), self.assertRaisesRegex(ValueError, "timestamp_unsupported"):
                self.record(changed)

    def test_supported_timestamp_precision_offsets_and_old_dates_are_preserved(self):
        for timestamp in ("0001-01-01T00:00:00Z", "2024-02-29t23:59:59z",
                          "2026-10-18T05:45:00.123456789123456789+05:45",
                          "9999-12-31T23:59:59.000000001-23:59"):
            changed = deepcopy(self.document)
            changed["x_t0_support_evidence"]["sources"][0]["checked_at"] = timestamp
            record = self.record(changed)
            result = self.evaluated(record)
            self.assertEqual(self.decision(result)["outcome"], "pass")
            self.assertEqual(result["x_t0_support_evidence_result"]["evidence"]["sources"][0]["checked_at"], timestamp)

    def test_public_stable_locator_shape_does_not_admit_credentials_or_queries(self):
        for uri in ("https://fixture@github.com/synthetic", "https://github.com:99999/synthetic",
                    "https://github.com/synthetic?fixture=1", "https://github.com/\nsynthetic",
                    "https://127.0.0.1/synthetic", "https://localhost/synthetic",
                    "file:///synthetic", "https://", "https://%67ithub.com/synthetic"):
            changed = deepcopy(self.document)
            changed["x_t0_support_evidence"]["sources"][0]["source_uri"] = uri
            with self.subTest(uri=uri), self.assertRaisesRegex(ValueError, "locator_unsupported"):
                self.record(changed)
        record = self.record()
        self.assertTrue(record.original_bytes[0].endswith(b"\n"))
        self.assertIn("#formats", self.evaluated(record)["x_t0_support_evidence_result"]["evidence"]["sources"][0]["source_uri"])

    def test_source_inventory_is_nonempty_bounded_and_has_unique_versioned_identities(self):
        original = self.document["x_t0_support_evidence"]["sources"][0]
        for sources in ([], [original, original], [original] * 33):
            changed = deepcopy(self.document)
            changed["x_t0_support_evidence"]["sources"] = deepcopy(sources)
            with self.subTest(count=len(sources)), self.assertRaises(ValueError):
                self.record(changed)
        changed = deepcopy(self.document)
        second = {**original, "revision": "synthetic-release-2", "checked_at": "2020-01-01T00:00:00Z"}
        changed["x_t0_support_evidence"]["sources"].append(second)
        result = self.evaluated(self.record(changed))
        self.assertEqual(result["x_t0_support_evidence_result"]["evidence"]["sources"], [original, second])

    def test_each_query_cohort_and_scope_dimension_must_match_the_bound_query(self):
        mutations = [(("binding_sha256",), "0" * 64), (("query", "version"), "other-version"),
                     (("query", "severity"), "warning"), (("cohort", "id"), "cohort.other"),
                     (("cohort", "version"), "other-version"), (("scope", "selection_id"), "sel_other"),
                     (("scope", "catalog_sha256"), "1" * 64), (("scope", "item", "id"), "other.item"),
                     (("scope", "item", "version"), "other-version"), (("scope", "item", "kind"), "model"),
                     (("scope", "property"), "/spec/other"), (("scope", "conditions_sha256"), "2" * 64)]
        for path, value in mutations:
            changed = deepcopy(self.document)
            target = changed["x_t0_support_evidence"]
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] = value
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "evidence_(binding|context)_mismatch"):
                self.record(changed)

    def test_missing_or_unmatched_qualification_never_passes_or_infers_a_grade(self):
        record = self.record()
        cases = ((None, True, "source_receipt_missing"), ("0" * 64, True, "source_receipt_mismatch"),
                 (digest(self.evidence_raw), None, "source_qualification_unresolved"),
                 (digest(self.evidence_raw), False, "source_ineligible"))
        for receipt, qualified, reason in cases:
            with self.subTest(reason=reason):
                result = self.evaluated(record, qualified_evidence_sha256=receipt,
                                        source_qualified=qualified, cohort_checked_only=True)
                self.assertEqual(result["x_t0_support_evidence_result"]["admission"]["reason"], reason)
                self.assertEqual(self.decision(result)["outcome"], "unknown")
                self.assertEqual(self.decision(result)["findings"], [])
                self.assertIsNone(self.decision(result)["evidence_label"])
        self.assertEqual(self.decision(self.evaluated(record))["outcome"], "pass")
        self.assertEqual(self.decision(self.evaluated(record, source_qualified=None))["outcome"], "unknown")

    def test_qualification_of_other_bytes_cannot_be_reused_after_metadata_or_whitespace_changes(self):
        original_receipt = digest(self.evidence_raw)
        for path, value in (("checked_at", "2026-10-17T00:00:00Z"), ("revision", "other-release"),
                            ("source_uri", "https://github.com/Pick-Your-AI/__synthetic__/other")):
            changed = deepcopy(self.document)
            changed["x_t0_support_evidence"]["sources"][0][path] = value
            record = self.record(changed)
            with self.subTest(path=path):
                self.assertEqual(self.decision(self.evaluated(record, qualified_evidence_sha256=original_receipt))["outcome"], "unknown")
        changed = self.record(evidence_raw=self.evidence_raw + b" ")
        self.assertEqual(self.decision(self.evaluated(changed, qualified_evidence_sha256=original_receipt))["outcome"], "unknown")

    def test_source_qualification_cannot_replace_independent_input_qualification(self):
        for field in ("applies_when", "requested", "cohort"):
            for value in (None, False):
                with self.subTest(field=field, value=value):
                    result = self.evaluated(eligible_inputs={**QUALIFIED, field: value}, cohort_checked_only=True)
                    self.assertEqual(self.decision(result)["outcome"], "unknown")
                    self.assertIsNone(self.decision(result)["evidence_label"])
        # A positive ANY witness does not require complete requested alternatives.
        result = self.evaluated(eligible_inputs={**QUALIFIED, "requested_complete": None})
        self.assertEqual(self.decision(result)["outcome"], "pass")

    def test_disabled_unresolved_mismatched_scope_and_nonapplicable_dispositions_survive(self):
        record = self.record()
        for enabled, expected in ((False, "skipped"), (None, "unknown")):
            result = self.evaluated(record, enabled=enabled, qualified_evidence_sha256=None)
            self.assertEqual(self.decision(result)["outcome"], expected)
        for scope in (None, {**record.scope, "selection_id": "sel_other"}):
            result = record.evaluate(scope, **self.context(record))
            self.assertEqual(self.decision(result)["outcome"], "unknown")
            self.assertIsNone(self.decision(result)["evidence_label"])
        self.change_answers(applies_when={"state": "provided", "value": False})
        self.assertEqual(self.decision(self.evaluated(qualified_evidence_sha256=None))["outcome"], "skipped")

    def test_actual_negative_and_unmarked_unknown_results_keep_their_existing_semantics(self):
        self.change_answers(requested={"state": "provided", "value": ["onnx"]},
                            supported={"state": "provided", "value": ["gguf"]},
                            unsupported={"state": "provided", "value": []})
        self.assertEqual(self.decision(self.evaluated())["outcome"], "unknown")
        self.change_answers(exhaustive={"state": "provided", "value": True})
        self.assertEqual(self.decision(self.evaluated())["outcome"], "fail")
        self.assertEqual(self.decision(self.evaluated(source_qualified=None))["outcome"], "unknown")

    def test_checked_only_label_remains_a_separate_current_invocation_fact(self):
        for checked in (None, False, True, None):
            with self.subTest(checked=checked):
                decision = self.decision(self.evaluated(cohort_checked_only=checked))
                self.assertEqual(decision["outcome"], "pass")
                self.assertEqual(decision["evidence_label"], "unverified" if checked is True else None)

    def test_malformed_qualifications_and_receipts_reject_before_disabled_shortcuts(self):
        record = self.record()
        for malformed in (0, 1, "true", [], {}):
            for changes in ({"source_qualified": malformed}, {"cohort_checked_only": malformed},
                            {"eligible_inputs": {**QUALIFIED, "cohort": malformed}}):
                with self.subTest(changes=changes), self.assertRaises(ValueError):
                    self.evaluated(record, enabled=False, **changes)
        for malformed in (0, "a" * 63, "A" * 64, "a" * 64 + "\n"):
            with self.subTest(receipt=malformed), self.assertRaisesRegex(ValueError, "digest_malformed"):
                self.evaluated(record, enabled=False, qualified_evidence_sha256=malformed)
        for malformed in ([], {"source": True}):
            with self.subTest(eligible=malformed), self.assertRaises(ValueError):
                self.evaluated(record, enabled=False, eligible_inputs=malformed)

    def test_original_json_admission_rejects_ambiguity_invalid_scalars_and_unsupported_size(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e9999}', b'{"x":"\\ud800"}', b'\xff'):
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, "json_malformed"):
                self.record(evidence_raw=raw)
        for raw in (self.evidence_raw.decode(), None):
            with self.subTest(kind=type(raw)), self.assertRaisesRegex(ValueError, "requires_bytes"):
                SupportEvidenceRecord(raw, self.binding_raw, self.answers_raw)
        with self.assertRaisesRegex(ValueError, "size_unsupported"):
            self.record(evidence_raw=self.evidence_raw + b" " * MAX_EVIDENCE_BYTES)

    def test_result_metadata_and_context_cannot_verify_themselves(self):
        record = self.record()
        result = self.evaluated(record)
        mutations = [(("evidence", "sources", 0, "checked_at"), "2026-10-17T00:00:00Z"),
                     (("evidence", "sources", 0, "revision"), "other-release"),
                     (("evidence", "sources", 0, "source_uri"), "https://github.com/__synthetic__/other"),
                     (("evidence", "cohort", "version"), "other-version"),
                     (("evidence_sha256",), "1" * 64),
                     (("admission", "source_qualified"), False),
                     (("admission", "requested_eligible_inputs", "cohort"), False)]
        for path, changed in mutations:
            forged = deepcopy(result)
            target = forged["x_t0_support_evidence_result"]
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] = changed
            with self.subTest(path=path):
                self.assertTrue(RESULT.is_valid(forged))
                with self.assertRaisesRegex(ValueError, "result_mismatch"):
                    record.verify_result(encoded(forged), record.scope, **self.context(record))
        # Even an internally consistent claimed qualified result cannot supply
        # the caller's absent qualification at verification time.
        with self.assertRaisesRegex(ValueError, "result_mismatch"):
            record.verify_result(encoded(result), record.scope, **self.context(record, source_qualified=None))

    def test_result_format_can_change_but_retained_inputs_and_returned_data_cannot(self):
        record = self.record()
        result = self.evaluated(record)
        wire = json.dumps(result, indent=4, sort_keys=True).encode()
        self.assertEqual(record.verify_result(wire, record.scope, **self.context(record)), result)
        result["x_t0_support_evidence_result"]["evidence"]["sources"].clear()
        result["x_t0_support_evidence_result"]["admission"]["requested_eligible_inputs"]["cohort"] = False
        scope = record.scope
        scope["item"]["version"] = "changed"
        self.assertEqual(record.original_bytes, (self.evidence_raw, self.binding_raw, self.answers_raw))
        fresh = self.evaluated(record)
        self.assertEqual(fresh["x_t0_support_evidence_result"]["evidence"], self.document["x_t0_support_evidence"])
        self.assertEqual(self.decision(fresh)["outcome"], "pass")

    def test_unselected_proposal_versions_and_malformed_identities_are_not_migrated(self):
        for value in ("cd3-0.3", "cd3-evidence-0.0", "cd3-evidence-0.2"):
            changed = deepcopy(self.document)
            changed["x_t0_support_evidence"]["proposal_version"] = value
            with self.subTest(version=value), self.assertRaisesRegex(ValueError, "shape_malformed"):
                self.record(changed)
        for field, value in (("id", "source.synthetic\n"), ("revision", " "), ("revision", "v1\n")):
            changed = deepcopy(self.document)
            changed["x_t0_support_evidence"]["sources"][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "shape_malformed"):
                self.record(changed)


if __name__ == "__main__":
    unittest.main()
