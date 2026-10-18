"""Synthetic CD-7 diagnostics against actual retained-byte consumer inspection."""

from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
import json
import unittest
from unittest.mock import Mock, patch

import t0_cd7_consumer_prototype as consumer
import t0_cd7_diagnostics_prototype as diagnostics
import t0_historical_replay_prototype as replay
from t0_revision_lock_prototype import SnapshotArchive
from test_t0_revision_locks import BUILD, CATALOG, PRICEBOOK, archive, encoded, sidecar
from test_t0_historical_replay import SIDECAR, RECORDS, run as historical_replay

CATALOG_PIN = ("catalog_snapshot", json.loads(CATALOG)["id"], json.loads(CATALOG)["revision"])
PRICE_PIN = ("pricebook", json.loads(PRICEBOOK)["id"], json.loads(PRICEBOOK)["revision"])
CATALOG_DEPENDENCY = diagnostics.Dependency("record", "catalog_snapshot")
PRICE_DEPENDENCY = diagnostics.Dependency("record", "pricebook")
MODEL_DEPENDENCY = diagnostics.Dependency("selection", "sel_model")
PAIR_DEPENDENCY = diagnostics.Dependency("pair", "catalog_pricebook")


def rule(dependencies=(MODEL_DEPENDENCY,), *, applicable=True, assertion=True, severity="error"):
    return diagnostics.Rule("rule.synthetic.cd7", severity, dependencies,
                            Mock(return_value=applicable), Mock(return_value=assertion))


def evaluate(selected_rule, *, source=None, build=BUILD, pins=SIDECAR, **kwargs):
    return diagnostics.evaluate(
        archive() if source is None else source, consumer.request(build, pins), build, pins,
        proposal_version=diagnostics.VERSION, rule=selected_rule, **kwargs,
    )


def inspect(*, source=None, build=BUILD, pins=SIDECAR, **kwargs):
    return diagnostics.inspect(
        archive() if source is None else source, consumer.request(build, pins), build, pins,
        proposal_version=diagnostics.VERSION, **kwargs,
    )


class CD7DiagnosticsTests(unittest.TestCase):
    def assert_unresolved(self, result, selected_rule, codes):
        value = result.rule_result
        self.assertEqual((value.rule_id, value.severity, value.outcome, value.reason_code),
                         (selected_rule.id, selected_rule.severity, "unknown", "dependency_unresolved"))
        self.assertEqual({d.reason_code for d in value.diagnostics}, set(codes))
        self.assertTrue(all(d.message.startswith("cannot be reproduced: ") for d in value.diagnostics))
        selected_rule.applies_when.assert_not_called()
        selected_rule.assertion.assert_not_called()

    def test_resolved_inputs_still_execute_explicit_applicability_and_assertion(self):
        cases = [(False, True, "skipped", "not_applicable"),
                 (None, True, "unknown", "applicability_unknown"),
                 (True, None, "unknown", "eligible_evidence_missing"),
                 (True, False, "fail", "assertion_false"),
                 (True, True, "pass", "assertion_true")]
        for applicable, assertion, outcome, reason in cases:
            with self.subTest(applicable=applicable, assertion=assertion):
                selected_rule = rule(applicable=applicable, assertion=assertion, severity="warning")
                result = evaluate(selected_rule)
                self.assertEqual((result.rule_result.outcome, result.rule_result.reason_code), (outcome, reason))
                self.assertEqual(result.rule_result.severity, "warning")
                self.assertEqual(result.inspection.diagnostics, ())
                selected_rule.applies_when.assert_called_once_with()
                if applicable is True:
                    selected_rule.assertion.assert_called_once_with()
                else:
                    selected_rule.assertion.assert_not_called()
                self.assertEqual(set(result.inspection.qualification.values()), {"not_established"})

    def test_missing_pins_preserve_each_record_and_the_unchanged_consumer_response(self):
        selected_rule = rule((CATALOG_DEPENDENCY, PRICE_DEPENDENCY))
        result = evaluate(selected_rule, pins=None)
        self.assert_unresolved(result, selected_rule, {"revision_pin_missing"})
        self.assertEqual(len(result.rule_result.diagnostics), 2)
        self.assertTrue(all(d.revision is None for d in result.rule_result.diagnostics))
        self.assertEqual(result.inspection.consumer_response_bytes,
                         consumer.inspect(archive(), consumer.request(BUILD), BUILD))
        self.assertEqual(result.rule_result.diagnostics[0].message,
                         "cannot be reproduced: catalog_snapshot catalog.fixture.1")

    def test_unavailable_exact_revision_never_borrows_the_only_newer_candidate(self):
        newer = json.loads(CATALOG)
        newer["revision"] += 1
        records = [("catalog_snapshot", encoded(newer)), ("pricebook", PRICEBOOK)]
        for ordered in (records, list(reversed(records))):
            with self.subTest(order=[k for k, _ in ordered]):
                selected_rule = rule()
                result = evaluate(selected_rule, source=SnapshotArchive(ordered))
                self.assert_unresolved(result, selected_rule, {"pinned_revision_unavailable"})
                self.assertEqual(result.rule_result.diagnostics[0].revision, CATALOG_PIN[2])

    def test_digest_mismatch_keeps_precedence_over_both_withholding_dispositions(self):
        for disposition in ("revoked", "temporarily_unavailable"):
            with self.subTest(disposition=disposition):
                selected_rule = rule()
                result = evaluate(selected_rule, source=archive(CATALOG + b"\n"),
                                  dispositions={CATALOG_PIN: disposition})
                self.assert_unresolved(result, selected_rule, {"content_digest_mismatch"})
                self.assertEqual(result.rule_result.diagnostics[0].message,
                                 "cannot be reproduced: catalog_snapshot catalog.fixture.1 revision 1")

    def test_revoked_and_temporary_catalog_causes_reach_every_enabled_selection(self):
        dependencies = tuple(diagnostics.Dependency("selection", s["id"])
                             for s in json.loads(BUILD)["selections"] if s["enabled"])
        for disposition in ("revoked", "temporarily_unavailable"):
            with self.subTest(disposition=disposition):
                selected_rule = rule(dependencies)
                result = evaluate(selected_rule, dispositions={CATALOG_PIN: disposition})
                self.assert_unresolved(result, selected_rule, {disposition})
                # All selections share this cause; repeated declarations do not
                # fabricate independent failures or erase its original identity.
                self.assertEqual(len(result.rule_result.diagnostics), 1)
                packet = consumer.wire(result.inspection.consumer_response_bytes, "x_t0_cd7_consumer_result")
                self.assertEqual({s["status"] for s in packet["selections"]}, {"snapshot_unresolved"})

    def test_pricebook_withholding_does_not_demote_independent_catalog_rules(self):
        for disposition in ("revoked", "temporarily_unavailable"):
            with self.subTest(disposition=disposition):
                model_rule = rule()
                model = evaluate(model_rule, dispositions={PRICE_PIN: disposition})
                self.assertEqual(model.rule_result.outcome, "pass")
                model_rule.assertion.assert_called_once_with()
                for dependency in (PRICE_DEPENDENCY, PAIR_DEPENDENCY):
                    dependent = rule((dependency,))
                    result = evaluate(dependent, dispositions={PRICE_PIN: disposition})
                    self.assert_unresolved(result, dependent, {disposition})
                    self.assertEqual(result.rule_result.diagnostics[0].record_kind, "pricebook")

    def test_selected_version_and_kind_mismatches_are_unknown_membership_causes(self):
        for mismatch in ("selected_version_absent", "selected_kind_mismatch"):
            changed = json.loads(BUILD)
            model = next(s for s in changed["selections"] if s["id"] == "sel_model")
            if mismatch == "selected_version_absent":
                model["catalog_item_version"] = "unavailable-version"
            else:
                model["catalog_item_id"] = "cat.model_provider.fixture"
            build = encoded(changed)
            with self.subTest(mismatch=mismatch):
                selected_rule = rule()
                result = evaluate(selected_rule, build=build, pins=sidecar(build))
                self.assert_unresolved(result, selected_rule, {mismatch})
                self.assertEqual(result.rule_result.diagnostics[0].record_id, "sel_model")
                self.assertIn(result.rule_result.diagnostics[0], result.inspection.diagnostics)

    def test_unsupported_native_revision_remains_explicit_without_numeric_coercion(self):
        changed = json.loads(CATALOG)
        changed["revision"] = consumer.MAX_REVISION + 1
        catalog = encoded(changed)
        selected_rule = rule()
        result = evaluate(selected_rule, source=archive(catalog), pins=sidecar(catalog=catalog))
        self.assert_unresolved(result, selected_rule, {"native_revision_unsupported"})
        self.assertIsNone(result.rule_result.diagnostics[0].revision)
        self.assertEqual(json.loads(catalog)["revision"], 9223372036854775808)
        packet = consumer.wire(result.inspection.consumer_response_bytes, "x_t0_cd7_consumer_result")
        self.assertNotIn("revision", packet["bindings"]["catalog_snapshot"])

    def test_unsupported_artifact_representation_and_structure_keep_distinct_reasons(self):
        bad_time = json.loads(CATALOG)
        bad_time["captured_at"] = "2026-02-30T00:00:00Z"
        deep = json.loads(CATALOG)
        child = deep["items"][0].setdefault("extensions", {}).setdefault("x_synthetic_depth", {})
        for _ in range(consumer.MAX_DEPTH):
            child["nested"] = {}
            child = child["nested"]
        for changed, reason in ((bad_time, "artifact_representation_unsupported"),
                                (deep, "artifact_structure_unsupported")):
            catalog = encoded(changed)
            with self.subTest(reason=reason):
                selected_rule = rule()
                result = evaluate(selected_rule, source=archive(catalog), pins=sidecar(catalog=catalog))
                self.assert_unresolved(result, selected_rule, {reason})

    def test_artifact_byte_limit_is_a_diagnostic_without_rewriting_retained_bytes(self):
        self.assertGreater(len(CATALOG), len(BUILD))
        request = consumer.request(BUILD, SIDECAR, max_artifact_bytes=len(BUILD))
        selected_rule = rule()
        result = diagnostics.evaluate(archive(), request, BUILD, SIDECAR,
                                      proposal_version=diagnostics.VERSION, rule=selected_rule)
        self.assert_unresolved(result, selected_rule, {"artifact_too_large"})
        self.assertEqual(result.inspection.consumer_response_bytes,
                         consumer.inspect(archive(), request, BUILD, SIDECAR))

    def test_cross_catalog_rate_mismatch_only_gates_rules_that_require_the_pair(self):
        changed = json.loads(PRICEBOOK)
        changed["rates"][0]["catalog_item_version"] = "unavailable-version"
        prices = encoded(changed)
        kwargs = {"source": archive(pricebook=prices), "pins": sidecar(pricebook=prices)}
        independent = evaluate(rule(), **kwargs)
        self.assertEqual(independent.rule_result.outcome, "pass")
        dependent = rule((PAIR_DEPENDENCY,))
        result = evaluate(dependent, **kwargs)
        self.assert_unresolved(result, dependent, {"rate_catalog_mismatch"})
        self.assertEqual(result.rule_result.diagnostics[0].record_kind, "catalog_pricebook")

    def test_disabled_scope_skips_but_does_not_hide_a_separate_unknown_dependency(self):
        changed = json.loads(BUILD)
        next(s for s in changed["selections"] if s["id"] == "sel_model")["enabled"] = False
        build = encoded(changed)
        kwargs = {"build": build, "pins": sidecar(build), "source": SnapshotArchive([])}
        disabled = rule()
        result = evaluate(disabled, **kwargs)
        self.assertEqual((result.rule_result.outcome, result.rule_result.reason_code), ("skipped", "not_enabled"))
        self.assertEqual(result.rule_result.disabled_dependencies, (MODEL_DEPENDENCY,))
        disabled.applies_when.assert_not_called()
        disabled.assertion.assert_not_called()
        mixed = rule((MODEL_DEPENDENCY, CATALOG_DEPENDENCY))
        result = evaluate(mixed, **kwargs)
        self.assert_unresolved(result, mixed, {"pinned_revision_unavailable"})
        self.assertEqual(result.rule_result.disabled_dependencies, (MODEL_DEPENDENCY,))

    def test_optional_pricebook_absence_is_not_a_global_error_or_zero_price(self):
        changed = json.loads(BUILD)
        del changed["locks"]["pricebook_id"]
        build = encoded(changed)
        pins = sidecar(build, pricebook=None)
        independent = evaluate(rule(), build=build, pins=pins)
        self.assertEqual(independent.rule_result.outcome, "pass")
        self.assertEqual(independent.inspection.diagnostics, ())
        packet = consumer.wire(independent.inspection.consumer_response_bytes, "x_t0_cd7_consumer_result")
        self.assertIsNone(packet["bindings"]["pricebook"])
        self.assertEqual(packet["pair"], {"status": "pricebook_absent"})
        for dependency in (PRICE_DEPENDENCY, PAIR_DEPENDENCY):
            dependent = rule((dependency,))
            result = evaluate(dependent, build=build, pins=pins)
            self.assert_unresolved(result, dependent, {"pricebook_absent"})
            self.assertEqual(result.rule_result.diagnostics[0].message, "cannot be reproduced: pricebook")

    def test_required_pair_retains_both_missing_catalog_and_absent_pricebook_causes(self):
        changed = json.loads(BUILD)
        del changed["locks"]["pricebook_id"]
        build = encoded(changed)
        dependent = rule((PAIR_DEPENDENCY,))
        result = evaluate(dependent, build=build, pins=sidecar(build, pricebook=None),
                          source=SnapshotArchive([]))
        self.assert_unresolved(result, dependent, {"pinned_revision_unavailable", "pricebook_absent"})
        self.assertEqual({d.record_kind for d in result.rule_result.diagnostics}, set(diagnostics.RECORDS))

    def test_independent_rule_executes_without_making_the_unresolved_snapshot_valid(self):
        independent = rule((), assertion=False, severity="info")
        result = evaluate(independent, source=SnapshotArchive([]))
        self.assertEqual((result.rule_result.outcome, result.rule_result.reason_code), ("fail", "assertion_false"))
        independent.assertion.assert_called_once_with()
        self.assertEqual({d.reason_code for d in result.inspection.diagnostics}, {"pinned_revision_unavailable"})
        self.assertEqual(set(result.inspection.qualification.values()), {"not_established"})

    def test_actual_historical_report_and_bytes_remain_visible_without_implicit_replay(self):
        history = historical_replay()
        before = deepcopy(history.generated_report)
        original_build = history.original_build_bytes
        self.assertEqual(history.status, "reproduced")
        selected_rule = rule()
        with patch.object(replay, "_local_evaluator", side_effect=AssertionError("no implicit replay")):
            result = evaluate(selected_rule, dispositions={CATALOG_PIN: "revoked"}, historical_result=history)
        self.assert_unresolved(result, selected_rule, {"revoked"})
        self.assertIs(result.inspection.historical_result, history)
        self.assertEqual(history.generated_report, before)
        self.assertEqual(len(history.generated_report["findings"]), 45)
        self.assertIs(history.original_build_bytes, original_build)
        self.assertEqual(history.original_build_bytes, BUILD)
        self.assertIs(history.original_sidecar_bytes, SIDECAR)
        for binding in history.bindings:
            self.assertIs(binding.raw, RECORDS[binding.kind])

    def test_unavailable_historical_replay_is_retained_without_upgrading_its_status(self):
        records = {k: raw for k, raw in RECORDS.items() if k != "catalog_snapshot"}
        history = historical_replay(records)
        self.assertEqual(history.status, "inputs_unavailable")
        retained = next(b.raw for b in history.bindings if b.kind == "evaluation_report")
        result = inspect(source=SnapshotArchive([]), historical_result=history)
        self.assertIs(result.historical_result, history)
        self.assertIs(retained, RECORDS["evaluation_report"])
        self.assertEqual(result.historical_result.status, "inputs_unavailable")
        self.assertIsNone(result.historical_result.generated_report)

    def test_historical_binding_requires_exact_build_and_sidecar_bytes(self):
        history = historical_replay()
        for build, pins in ((BUILD + b"\n", SIDECAR), (BUILD, SIDECAR + b"\n")):
            with self.subTest(build_changed=build != BUILD):
                selected_rule = rule()
                with self.assertRaises(diagnostics.DiagnosticsError) as caught:
                    evaluate(selected_rule, build=build, pins=pins, historical_result=history)
                self.assertEqual(caught.exception.code, "historical_input_mismatch")
                selected_rule.applies_when.assert_not_called()
        with self.assertRaises(diagnostics.DiagnosticsError) as caught:
            inspect(historical_result={"status": "reproduced"})
        self.assertEqual(caught.exception.code, "invalid_historical_result")

    def test_callback_exceptions_escape_without_becoming_dependency_unknown(self):
        for phase in ("applies_when", "assertion"):
            for error in (ValueError("callback failed"), diagnostics.DiagnosticsError("callback_failed"),
                          consumer.ConsumerError("callback_failed")):
                with self.subTest(phase=phase, exception=type(error).__name__):
                    selected_rule = rule()
                    getattr(selected_rule, phase).side_effect = error
                    with self.assertRaises(type(error)) as caught:
                        evaluate(selected_rule)
                    self.assertIs(caught.exception, error)

    def test_predicates_require_exact_normalized_booleans_without_truthiness(self):
        for phase in ("applies_when", "assertion"):
            for value in (0, 1, "true", "unknown", [], {}):
                with self.subTest(phase=phase, value=value):
                    selected_rule = rule()
                    getattr(selected_rule, phase).return_value = value
                    with self.assertRaisesRegex(ValueError, "normalized bool or None"):
                        evaluate(selected_rule)

    def test_invalid_rule_and_dependency_declarations_reject_before_callbacks(self):
        good = rule()
        invalid = [replace(good, id="rule.invalid\n"), replace(good, severity="unknown"),
                   replace(good, severity=True), replace(good, dependencies="catalog_snapshot"),
                   replace(good, dependencies=[MODEL_DEPENDENCY]),
                   replace(good, dependencies=(MODEL_DEPENDENCY, MODEL_DEPENDENCY)),
                   replace(good, dependencies=(diagnostics.Dependency("catalog_snapshot", "record"),)),
                   replace(good, dependencies=(diagnostics.Dependency("record", "latest"),)),
                   replace(good, dependencies=(diagnostics.Dependency("pair", "latest"),)),
                   replace(good, dependencies=(diagnostics.Dependency("selection", "sel_model\n"),)),
                   replace(good, dependencies=(diagnostics.Dependency("selection", "sel_absent"),)),
                   replace(good, applies_when=True)]
        for selected_rule in invalid:
            with self.subTest(rule=selected_rule):
                with self.assertRaises(diagnostics.DiagnosticsError):
                    evaluate(selected_rule)
        good.applies_when.assert_not_called()
        good.assertion.assert_not_called()

    def test_version_and_malformed_requests_are_call_errors_not_rule_findings(self):
        selected_rule = rule()
        request = consumer.request(BUILD, SIDECAR)
        for version in (None, "cd7-diagnostics-0.2", True):
            with self.subTest(version=version), self.assertRaises(diagnostics.DiagnosticsError) as caught:
                diagnostics.evaluate(archive(), request, BUILD, SIDECAR, proposal_version=version, rule=selected_rule)
            self.assertEqual(caught.exception.code, "unsupported_proposal_version")
        changed = json.loads(request)
        changed["x_t0_cd7_consumer"]["protocol_version"] = "cd7-consumer-0.2"
        for bad_request, code in ((encoded(changed), "unsupported_protocol_version"),
                                  (b'{"x_t0_cd7_consumer":', "malformed_document")):
            with self.subTest(code=code), self.assertRaises(consumer.ConsumerError) as caught:
                diagnostics.evaluate(archive(), bad_request, BUILD, SIDECAR,
                                      proposal_version=diagnostics.VERSION, rule=selected_rule)
            self.assertEqual(caught.exception.code, code)
        selected_rule.applies_when.assert_not_called()
        selected_rule.assertion.assert_not_called()

    def test_diagnostics_carry_no_payload_and_returned_metadata_cannot_rewrite_later_inspection(self):
        changed = json.loads(BUILD)
        changed.setdefault("extensions", {})["x_synthetic_note"] = "synthetic retained note is not a diagnostic"
        build = encoded(changed)
        pins = sidecar(build)
        result = inspect(build=build, pins=pins, source=SnapshotArchive([]))
        self.assertNotIn("synthetic retained note", repr(result))
        self.assertNotIn(b"synthetic retained note", result.consumer_response_bytes)
        with self.assertRaises(FrozenInstanceError):
            result.diagnostics = ()
        result.qualification["source_use"] = "approved"
        again = inspect(build=build, pins=pins, source=SnapshotArchive([]))
        self.assertEqual(again.consumer_response_bytes, result.consumer_response_bytes)
        self.assertEqual(again.diagnostics, result.diagnostics)
        self.assertEqual(again.qualification["source_use"], "not_established")


if __name__ == "__main__":
    unittest.main()
