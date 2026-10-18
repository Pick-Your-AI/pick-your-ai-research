"""Synthetic CD-9 proofs and counterexamples; no real location qualification."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from tests.jurisdiction_binding_prototype import (
    COLLECTIONS, JurisdictionRecord, Outcome, constraint_path,
    descriptor_digest, digest, fact_path,
)


FIXTURES = Path(__file__).with_name("fixtures")
LOCAL = "synthetic-local-query"
PROCESSING = "synthetic-processing-query"
STORAGE = "synthetic-storage-query"
A = "synthetic-country-a"
B = "synthetic-country-b"
NORTH = "synthetic-a-north"


def encode(value):
    return (json.dumps(value, indent=2, allow_nan=False) + "\n").encode("utf-8")


class JurisdictionBindingTests(unittest.TestCase):
    def setUp(self):
        self.binding = json.loads((FIXTURES / "jurisdiction-binding.json").read_text())
        self.answers = json.loads((FIXTURES / "jurisdiction-answers.json").read_text())

    @property
    def proposal(self):
        return self.binding["x_t0_jurisdiction"]

    @property
    def facts(self):
        return self.answers["x_t0_answer_states"]["answers"]

    def item(self, kind, identity):
        return next(item for item in self.proposal[COLLECTIONS[kind]] if item["id"] == identity)

    def reference(self, kind, identity):
        record_kind = "region" if kind == "provider_region" else kind
        try:
            target = self.item(record_kind, identity)
        except StopIteration:
            return {"kind": kind, "id": identity}
        return {"kind": kind, "id": identity, "descriptor_sha256": descriptor_digest(target)}

    def record(self):
        answers = encode(self.answers)
        self.proposal["answer_states_sha256"] = digest(answers)
        return JurisdictionRecord(encode(self.binding), answers)

    def qualify_fixture(self, *, repin=False):
        """Assert new invented facts for a test; never an evidence resolver."""
        if repin:
            for query in self.proposal["queries"]:
                query["location_refs"] = [self.reference(ref["kind"], ref["id"])
                                          for ref in query["location_refs"]]
            for dimension in ("processing", "storage"):
                answer = self.facts.get(constraint_path(dimension), {})
                value = answer.get("value", {})
                if isinstance(value, dict) and value.get("mode") == "restricted":
                    value["allowed"] = [self.reference(ref["kind"], ref["id"])
                                        for ref in value["allowed"]]
        for path in self.record().answer_paths:
            if not path.startswith("/workload/"):
                self.facts.setdefault(path, {"state": "provided", "value": True,
                                            "source": "synthetic:fixture-only"})

    def set_fact(self, kind, identity, *tokens, value=True, state="provided"):
        path = fact_path(kind, self.item(kind, identity), *tokens)
        self.facts[path] = {"state": state, **({"value": value} if state == "provided" else {})}
        return path

    def allow(self, dimension, *refs):
        self.facts[constraint_path(dimension)] = {
            "state": "provided", "value": {"mode": "restricted", "allowed": list(refs)}}

    def locations(self, query_id, *refs):
        self.item("query", query_id)["location_refs"] = list(refs)
        self.qualify_fixture()

    def results(self, eligibility=None):
        record = self.record()
        if eligibility is None:
            eligibility = {path: True for path in record.answer_paths}
        return {query.query_id: query for query in record.evaluate(eligibility).queries}

    def test_fixture_keeps_processing_and_storage_independent(self):
        result = self.results()
        self.assertEqual(result[LOCAL].outcome, Outcome.PASS)
        self.assertEqual(result[PROCESSING].outcome, Outcome.PASS)
        self.assertEqual(result[STORAGE].outcome, Outcome.FAIL)
        comparison = result[LOCAL].checks[-1].comparisons[0]
        self.assertEqual(comparison.witness, (NORTH, A))
        exclusion = result[STORAGE].checks[-1].comparisons[0]
        self.assertEqual(exclusion.disjoint_witnesses,
                         (("synthetic-a-b-disjoint", (B,), (A,)),))
        for row in result.values():
            self.assertEqual((row.rule_id, row.severity, row.on_unknown), ("D-R6", "error", "review"))

    def test_unconstrained_is_distinct_from_all_unresolved_answer_states(self):
        original = deepcopy(self.answers)
        for dimension, query_id in (("processing", PROCESSING), ("storage", STORAGE)):
            for state in ("unknown", "missing", "withheld", "not_applicable", "absent"):
                with self.subTest(dimension=dimension, state=state):
                    self.answers = deepcopy(original)
                    path = constraint_path(dimension)
                    if state == "absent":
                        self.facts.pop(path)
                    else:
                        self.facts[path] = {"state": state}
                    self.assertEqual(self.results()[query_id].outcome, Outcome.UNKNOWN)
            self.answers = deepcopy(original)
            self.facts[constraint_path(dimension)] = {"state": "provided", "value": {"mode": "unconstrained"}}
            self.assertEqual(self.results()[query_id].outcome, Outcome.SKIPPED)

    def test_descriptors_and_source_labels_supply_no_eligibility(self):
        record = self.record()
        result = record.evaluate()
        self.assertTrue(all(query.outcome is Outcome.UNKNOWN for query in result.queries))
        self.assertTrue(all(value is None for _, value in result.eligibility))
        self.assertTrue(any(answer.source == "synthetic:fixture-only" for _, answer in result.answers))
        eligibility = {path: True for path in record.answer_paths}
        eligibility[constraint_path("processing")] = False
        self.assertEqual(self.results(eligibility)[LOCAL].outcome, Outcome.UNKNOWN)

    def test_positive_path_does_not_need_exhaustive_ancestry(self):
        self.set_fact("jurisdiction", NORTH, "parents_complete", value=False)
        self.set_fact("jurisdiction", A, "parents_complete", state="unknown")
        self.assertEqual(self.results()[LOCAL].outcome, Outcome.PASS)
        self.set_fact("jurisdiction", NORTH, "parent", A, state="unknown")
        self.assertEqual(self.results()[LOCAL].outcome, Outcome.UNKNOWN)

    def test_complete_ancestry_alone_cannot_prove_exclusion(self):
        self.proposal["disjoint_pairs"] = []
        result = self.results()[STORAGE]
        self.assertEqual(result.outcome, Outcome.UNKNOWN)
        self.assertEqual(result.checks[-1].comparisons[0].reason, "no_disjointness_evidence")

    def test_coarse_country_scope_is_unknown_for_allowed_subdivision(self):
        self.locations(LOCAL, self.reference("jurisdiction", A))
        self.allow("processing", self.reference("jurisdiction", NORTH))
        result = self.results()[LOCAL]
        self.assertEqual(result.outcome, Outcome.UNKNOWN)
        self.assertEqual(result.checks[-1].comparisons[0].reason, "location_scope_coarser_than_constraint")

    def test_sibling_names_and_common_prefix_do_not_imply_disjointness(self):
        self.allow("processing", self.reference("jurisdiction", "synthetic-a-east"))
        self.assertEqual(self.results()[LOCAL].outcome, Outcome.UNKNOWN)
        self.proposal["jurisdictions"].append({"id": "synthetic-country-a-lookalike", "parent_ids": []})
        self.qualify_fixture()
        self.locations(LOCAL, self.reference("jurisdiction", "synthetic-country-a-lookalike"))
        self.allow("processing", self.reference("jurisdiction", A))
        self.assertEqual(self.results()[LOCAL].outcome, Outcome.UNKNOWN)

    def test_disjointness_inherits_only_along_confirmed_paths_on_both_sides(self):
        self.allow("storage", self.reference("jurisdiction", NORTH))
        self.locations(STORAGE, self.reference("jurisdiction", "synthetic-b-north"))
        self.assertEqual(self.results()[STORAGE].outcome, Outcome.FAIL)
        self.set_fact("jurisdiction", NORTH, "parent", A, state="withheld")
        self.assertEqual(self.results()[STORAGE].outcome, Outcome.UNKNOWN)

    def test_unknown_false_or_ineligible_disjointness_is_not_a_negative(self):
        path = fact_path("disjoint", self.item("disjoint", "synthetic-a-b-disjoint"), "confirmed")
        for value in (False, None):
            with self.subTest(eligibility=value):
                record = self.record()
                eligibility = {key: True for key in record.answer_paths}
                eligibility[path] = value
                self.assertEqual(self.results(eligibility)[STORAGE].outcome, Outcome.UNKNOWN)
        self.facts[path] = {"state": "provided", "value": False}
        self.assertEqual(self.results()[STORAGE].outcome, Outcome.UNKNOWN)

    def test_positive_and_disjoint_proofs_are_disputed(self):
        self.proposal["disjoint_pairs"].append({"id": "synthetic-impossible-edge",
                                                 "left_id": NORTH, "right_id": A})
        self.qualify_fixture()
        result = self.results()[LOCAL]
        self.assertEqual(result.outcome, Outcome.UNKNOWN)
        comparison = result.checks[-1].comparisons[0]
        self.assertIn("disputed", comparison.reason)
        self.assertTrue(comparison.disjoint_witnesses)

    def test_internal_ancestry_contradiction_cannot_pass_a_third_ancestor(self):
        c = "synthetic-containing-c"
        x = "synthetic-impossible-x"
        self.proposal["jurisdictions"].extend([
            {"id": c, "parent_ids": []}, {"id": x, "parent_ids": [A, B]}])
        self.item("jurisdiction", A)["parent_ids"] = [c]
        self.item("jurisdiction", B)["parent_ids"] = [c]
        self.qualify_fixture(repin=True)
        self.locations(LOCAL, self.reference("jurisdiction", x))
        self.allow("processing", self.reference("jurisdiction", c))
        result = self.results()[LOCAL]
        self.assertEqual(result.outcome, Outcome.UNKNOWN)
        self.assertEqual(result.checks[-1].comparisons[0].reason, "disputed_jurisdiction_ancestry")

    def test_group_positive_survives_unknown_other_members_and_retains_them(self):
        group = self.item("group", "synthetic-group-a")
        group["member_ids"].append("synthetic-missing-member")
        self.qualify_fixture()
        self.allow("processing", self.reference("group", group["id"]))
        self.set_fact("group", group["id"], "members_complete", value=False)
        result = self.results()[LOCAL]
        self.assertEqual(result.outcome, Outcome.PASS)
        member_rows = result.checks[-1].comparisons[0].members
        self.assertEqual({row[1] for row in member_rows}, {Outcome.PASS, Outcome.UNKNOWN})

    def test_group_negative_requires_complete_membership_and_all_exclusions(self):
        self.allow("storage", self.reference("group", "synthetic-group-a"))
        self.assertEqual(self.results()[STORAGE].outcome, Outcome.FAIL)
        self.set_fact("group", "synthetic-group-a", "members_complete", state="unknown")
        self.assertEqual(self.results()[STORAGE].outcome, Outcome.UNKNOWN)
        self.set_fact("group", "synthetic-group-a", "members_complete", value=True)
        self.set_fact("group", "synthetic-group-a", "member", A, state="unknown")
        self.assertEqual(self.results()[STORAGE].outcome, Outcome.UNKNOWN)

    def test_complete_empty_group_is_distinct_from_missing_membership(self):
        self.allow("processing", self.reference("group", "synthetic-empty-group"))
        self.assertEqual(self.results()[LOCAL].outcome, Outcome.FAIL)
        self.set_fact("group", "synthetic-empty-group", "members_complete", value=False)
        self.assertEqual(self.results()[LOCAL].outcome, Outcome.UNKNOWN)

    def test_allowed_alternatives_keep_unknown_rows_after_a_positive(self):
        self.allow("processing", self.reference("group", "synthetic-missing-group"),
                   self.reference("jurisdiction", A))
        result = self.results()[LOCAL]
        self.assertEqual(result.outcome, Outcome.PASS)
        self.assertEqual([row.outcome for row in result.checks[-1].comparisons],
                         [Outcome.UNKNOWN, Outcome.PASS])

    def test_counterexample_survives_unresolved_locations_and_coverage(self):
        self.locations(LOCAL, self.reference("jurisdiction", B),
                       self.reference("provider_region", "synthetic-no-map"))
        self.set_fact("query", LOCAL, "locations_complete", value=False)
        result = self.results()[LOCAL]
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertIn(Outcome.UNKNOWN, {check.outcome for check in result.checks})
        self.assertEqual(len(result.checks), 3)

    def test_query_and_mapping_coverage_are_separate_requirements_for_a_pass(self):
        self.set_fact("query", PROCESSING, "locations_complete", value=False)
        self.assertEqual(self.results()[PROCESSING].outcome, Outcome.UNKNOWN)
        self.set_fact("query", PROCESSING, "locations_complete", value=True)
        self.set_fact("region", "synthetic-processing-map", "locations_complete", value=False)
        self.assertEqual(self.results()[PROCESSING].outcome, Outcome.UNKNOWN)

    def test_empty_subject_or_region_location_list_does_not_pass_vacuously(self):
        self.locations(LOCAL)
        self.assertEqual(self.results()[LOCAL].outcome, Outcome.UNKNOWN)
        self.item("region", "synthetic-processing-map")["jurisdiction_ids"] = []
        self.qualify_fixture(repin=True)
        self.assertEqual(self.results()[PROCESSING].outcome, Outcome.UNKNOWN)

    def test_same_region_label_cannot_mix_providers_dimensions_or_contexts(self):
        self.locations(PROCESSING, self.reference("provider_region", "synthetic-other-provider-map"))
        self.assertEqual(self.results()[PROCESSING].outcome, Outcome.FAIL)
        self.locations(PROCESSING, self.reference("provider_region", "synthetic-storage-map"))
        self.assertEqual(self.results()[PROCESSING].outcome, Outcome.UNKNOWN)
        self.locations(PROCESSING, self.reference("provider_region", "synthetic-processing-map"))
        self.item("query", PROCESSING)["context_id"] = "synthetic-configuration-2"
        self.qualify_fixture()
        self.assertEqual(self.results()[PROCESSING].outcome, Outcome.UNKNOWN)

    def test_fresh_replacement_mapping_cannot_reuse_old_subject_association(self):
        self.locations(PROCESSING, self.reference("provider_region", "synthetic-other-provider-map"))
        self.assertEqual(self.results()[PROCESSING].outcome, Outcome.FAIL)
        mapping = self.item("region", "synthetic-other-provider-map")
        mapping["provider_id"] = "synthetic-replacement-provider"
        mapping["jurisdiction_ids"] = [A]
        self.qualify_fixture()  # Fresh invented mapping facts; old subject pin remains.
        result = self.results()[PROCESSING]
        self.assertEqual(result.outcome, Outcome.UNKNOWN)
        self.assertIn("location_reference_unbound", {check.reason for check in result.checks})
        self.qualify_fixture(repin=True)  # Explicit new association and mapping scope.
        self.assertEqual(self.results()[PROCESSING].outcome, Outcome.PASS)

    def test_fresh_expanded_group_cannot_reinterpret_old_constraint(self):
        self.allow("storage", self.reference("group", "synthetic-group-a"))
        self.assertEqual(self.results()[STORAGE].outcome, Outcome.FAIL)
        self.item("group", "synthetic-group-a")["member_ids"].append(B)
        self.qualify_fixture()
        self.assertEqual(self.results()[STORAGE].outcome, Outcome.UNKNOWN)
        self.qualify_fixture(repin=True)
        self.assertEqual(self.results()[STORAGE].outcome, Outcome.PASS)

    def test_missing_reference_pin_never_uses_the_latest_descriptor(self):
        self.locations(LOCAL, {"kind": "jurisdiction", "id": NORTH})
        self.assertEqual(self.results()[LOCAL].outcome, Outcome.UNKNOWN)
        self.qualify_fixture(repin=True)
        self.allow("processing", {"kind": "jurisdiction", "id": A})
        self.assertEqual(self.results()[LOCAL].outcome, Outcome.UNKNOWN)

    def test_editing_inventory_cannot_reuse_its_old_completeness_fact(self):
        self.item("query", LOCAL)["location_refs"].append(self.reference("jurisdiction", B))
        # All new evidence keys are eligible in this artificial caller, but no
        # new CD-1 facts were supplied. The old descriptor's true is not reused.
        result = self.results()[LOCAL]
        self.assertEqual(result.outcome, Outcome.UNKNOWN)
        self.assertTrue(all(check.outcome is Outcome.UNKNOWN for check in result.checks))

    def test_exact_input_bytes_are_retained_and_hash_mismatches_are_rejected(self):
        record = self.record()
        binding_raw, answers_raw = record.original_bytes
        self.assertEqual(record.original_bytes, (encode(self.binding), encode(self.answers)))
        with self.assertRaisesRegex(ValueError, "answer bytes"):
            JurisdictionRecord(binding_raw, answers_raw + b" ")
        with self.assertRaisesRegex(ValueError, "UTF-8 bytes"):
            JurisdictionRecord(binding_raw.decode(), answers_raw)
        result = record.evaluate()
        self.assertEqual((result.binding_sha256, result.answer_states_sha256),
                         (digest(binding_raw), digest(answers_raw)))

    def test_cycles_and_duplicate_identities_are_rejected_even_when_unconstrained(self):
        baseline = deepcopy(self.binding)
        self.facts[constraint_path("processing")] = {"state": "provided", "value": {"mode": "unconstrained"}}
        for kind in COLLECTIONS:
            with self.subTest(kind=kind):
                self.binding = deepcopy(baseline)
                values = self.proposal[COLLECTIONS[kind]]
                values.append(deepcopy(values[0]))
                with self.assertRaisesRegex(ValueError, "duplicate"):
                    self.record()
        self.binding = deepcopy(baseline)
        self.item("jurisdiction", A)["parent_ids"] = [NORTH]
        with self.assertRaisesRegex(ValueError, "cyclic"):
            self.record()

    def test_scope_aliases_and_impossible_disjoint_pairs_are_rejected(self):
        baseline = deepcopy(self.binding)
        cases = []
        mapping = deepcopy(self.proposal["regions"][0])
        mapping["id"] = "synthetic-alias"
        cases.append(("regions", mapping, "mapping scope"))
        query = deepcopy(self.proposal["queries"][0])
        query["id"] = "synthetic-alias"
        cases.append(("queries", query, "dimension query"))
        cases.append(("disjoint_pairs", {"id": "synthetic-reverse", "left_id": B, "right_id": A}, "unordered"))
        cases.append(("disjoint_pairs", {"id": "synthetic-self", "left_id": A, "right_id": A}, "itself"))
        for collection, value, message in cases:
            with self.subTest(collection=collection, message=message):
                self.binding = deepcopy(baseline)
                self.proposal[collection].append(value)
                with self.assertRaisesRegex(ValueError, message):
                    self.record()

    def test_whole_identity_and_digest_boundaries(self):
        baseline = deepcopy(self.binding)
        for invalid in (True, 1, 1.0, "", "synthetic-id\n", "synthetic-é", "synthetic/id"):
            with self.subTest(identity=invalid):
                self.binding = deepcopy(baseline)
                self.proposal["queries"][0]["subject_id"] = invalid
                with self.assertRaises(ValueError):
                    self.record()
        self.binding = deepcopy(baseline)
        self.proposal["queries"][0]["location_refs"][0]["descriptor_sha256"] += "\n"
        with self.assertRaisesRegex(ValueError, "digest"):
            self.record()

    def test_malformed_unused_provided_values_are_not_hidden_by_skip(self):
        self.facts[constraint_path("processing")] = {"state": "provided", "value": {"mode": "unconstrained"}}
        self.set_fact("group", "synthetic-empty-group", "members_complete", value="unknown")
        with self.assertRaisesRegex(ValueError, "invalid provided value"):
            self.record()

    def test_raw_json_ambiguity_and_nonfinite_values_are_rejected(self):
        record = self.record()
        binding_raw, answers_raw = record.original_bytes
        duplicate = binding_raw.replace(b'"proposal_version": "cd9-0.1",',
                                        b'"proposal_version": "cd9-0.1", "proposal_version": "cd9-0.1",', 1)
        with self.assertRaises(ValueError):
            JurisdictionRecord(duplicate, answers_raw)
        for token in (b"NaN", b"Infinity", b"1e999"):
            with self.subTest(token=token):
                corrupt = answers_raw.replace(b'"value": true', b'"value": ' + token, 1)
                self.proposal["answer_states_sha256"] = digest(corrupt)
                with self.assertRaises(ValueError):
                    JurisdictionRecord(encode(self.binding), corrupt)

    def test_exact_eligibility_types_and_stale_paths_are_rejected(self):
        record = self.record()
        for invalid in (1, 0, 1.0, "true", [], {}):
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError):
                    record.evaluate({constraint_path("processing"): invalid})
        with self.assertRaisesRegex(ValueError, "scoped answer paths"):
            record.evaluate({"/cd9/stale-descriptor": True})

    def test_repeated_evaluation_does_not_cache_eligibility_or_expose_mutable_inputs(self):
        record = self.record()
        qualified = {path: True for path in record.answer_paths}
        first = record.evaluate(qualified)
        self.assertEqual(next(q for q in first.queries if q.query_id == LOCAL).outcome, Outcome.PASS)
        self.assertTrue(all(q.outcome is Outcome.UNKNOWN for q in record.evaluate().queries))
        answer = dict(first.answers)[constraint_path("processing")]
        answer.value["allowed"].clear()
        again = record.evaluate(qualified)
        self.assertEqual(next(q for q in again.queries if q.query_id == LOCAL).outcome, Outcome.PASS)
        self.assertEqual(len(dict(again.answers)[constraint_path("processing")].value["allowed"]), 1)

    def test_dangling_jurisdiction_and_group_references_stay_unknown(self):
        self.item("jurisdiction", NORTH)["parent_ids"] = ["synthetic-unrecorded-parent"]
        self.qualify_fixture(repin=True)
        self.assertEqual(self.results()[LOCAL].outcome, Outcome.UNKNOWN)
        self.allow("processing", {"kind": "group", "id": "synthetic-unrecorded-group", "descriptor_sha256": "0" * 64})
        self.assertEqual(self.results()[LOCAL].outcome, Outcome.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
