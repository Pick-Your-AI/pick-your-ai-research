"""Adversarial synthetic #41 price-policy cases; no real rates or retrieval."""

import unittest
from dataclasses import replace
from datetime import date
from decimal import Decimal

from tests.price_policy_prototype import (
    Authority,
    Outcome,
    Rate,
    Scope,
    choose_current_rate,
    match_scope,
)

SCOPE = Scope(
    "synthetic.item",
    "v1",
    "synthetic.provider",
    "synthetic_meter",
    "usage_based",
    "USD",
    "region-a",
    (("plan", "standard"), ("cache", "uncached")),
)
BASE = Rate(
    "synthetic.rate.old",
    SCOPE,
    Decimal("2"),
    date(2026, 1, 1),
    date(2026, 1, 2),
    True,
    True,
    True,
)


class PricePolicyCases(unittest.TestCase):
    def test_eligibility_precedes_later_effective_and_capture_dates(self):
        unrelated = replace(
            BASE,
            rate_id="synthetic.other.region",
            amount=Decimal("0.1"),
            scope=replace(SCOPE, region="region-b"),
            effective_on=date(2026, 10, 18),
            captured_on=date(2026, 10, 18),
        )
        result = choose_current_rate(SCOPE, (BASE, unrelated))
        self.assertEqual(result.amount, Decimal("2"))
        self.assertEqual(result.selected_rate_ids, (BASE.rate_id,))
        self.assertIn(Outcome.FAIL, [item.outcome for item in result.trace])

    def test_effective_date_precedes_capture_date(self):
        recaptured_old = replace(BASE, captured_on=date(2026, 10, 18))
        new = replace(
            BASE,
            rate_id="synthetic.rate.new",
            effective_on=date(2026, 2, 1),
            captured_on=date(2026, 2, 2),
            amount=Decimal("3"),
        )
        result = choose_current_rate(SCOPE, (recaptured_old, new))
        self.assertEqual(result.amount, Decimal("3"))
        self.assertEqual(result.permitted_history, (recaptured_old, new))

    def test_recent_capture_cannot_rescue_an_expired_rate(self):
        expired = replace(BASE, valid_for_query=False, captured_on=date(2026, 10, 18))
        result = choose_current_rate(SCOPE, (expired,))
        self.assertIsNone(result.amount)
        self.assertEqual(result.permitted_history, (expired,))
        self.assertEqual(result.trace[0].reason, "validity")

    def test_elapsed_age_does_not_create_an_unadopted_ttl(self):
        old = replace(BASE, captured_on=date(2020, 1, 1))
        self.assertEqual(choose_current_rate(SCOPE, (old,)).amount, Decimal("2"))

    def test_recent_capture_is_not_a_successful_current_scope_refresh(self):
        for refreshed in (False, None):
            with self.subTest(refreshed=refreshed):
                old = replace(
                    BASE, refreshed_for_query=refreshed, captured_on=date(2026, 10, 18)
                )
                result = choose_current_rate(SCOPE, (old,))
                self.assertIsNone(result.amount)
                self.assertEqual(result.permitted_history, (old,))
                self.assertEqual(result.trace[0].outcome, Outcome.UNKNOWN)

    def test_rights_exclusion_hides_historical_and_current_values(self):
        for allowed in (False, None):
            with self.subTest(allowed=allowed):
                excluded = replace(
                    BASE, display_allowed=allowed, refreshed_for_query=False
                )
                result = choose_current_rate(SCOPE, (excluded,))
                self.assertIsNone(result.amount)
                self.assertEqual(result.permitted_history, ())
                self.assertEqual(result.trace[0].reason, "display_rights")

    def test_missing_currency_and_unconverted_currency_do_not_match(self):
        for currency in (None, "EUR"):
            with self.subTest(currency=currency):
                request = replace(SCOPE, currency=currency)
                self.assertIsNone(choose_current_rate(request, (BASE,)).amount)

    def test_missing_condition_is_not_a_wildcard(self):
        for conditions in (
            None,
            (("plan", "standard"),),
            (("plan", "standard"), ("cache", None)),
        ):
            with self.subTest(conditions=conditions):
                rate = replace(BASE, scope=replace(SCOPE, conditions=conditions))
                self.assertEqual(match_scope(SCOPE, rate), Outcome.UNKNOWN)
                self.assertIsNone(choose_current_rate(SCOPE, (rate,)).amount)

    def test_empty_condition_inventory_is_distinct_from_missing_inventory(self):
        empty = replace(SCOPE, conditions=())
        self.assertEqual(match_scope(empty, replace(BASE, scope=empty)), Outcome.PASS)
        missing = replace(SCOPE, conditions=None)
        self.assertEqual(
            match_scope(missing, replace(BASE, scope=missing)), Outcome.UNKNOWN
        )

    def test_missing_identity_or_meter_does_not_default_to_a_current_offering(self):
        for field in ("item_id", "version", "provider", "meter", "billing_class"):
            with self.subTest(field=field):
                self.assertEqual(
                    match_scope(replace(SCOPE, **{field: None}), BASE), Outcome.UNKNOWN
                )
                mismatch = replace(BASE, scope=replace(SCOPE, **{field: "other"}))
                self.assertEqual(match_scope(SCOPE, mismatch), Outcome.FAIL)

    def test_known_scope_mismatch_remains_ineligible_with_another_unknown(self):
        rate = replace(BASE, scope=replace(SCOPE, provider="other", currency=None))
        self.assertEqual(match_scope(SCOPE, rate), Outcome.FAIL)

    def test_global_scope_requires_explicit_evidence_and_a_selected_region(self):
        missing_region = replace(BASE, scope=replace(SCOPE, region=None))
        self.assertEqual(match_scope(SCOPE, missing_region), Outcome.UNKNOWN)
        global_rate = replace(missing_region, explicitly_global=True)
        self.assertEqual(match_scope(SCOPE, global_rate), Outcome.PASS)
        self.assertEqual(
            match_scope(replace(SCOPE, region=None), global_rate), Outcome.UNKNOWN
        )

    def test_specific_region_precedes_newer_global_scope(self):
        global_rate = replace(
            BASE,
            rate_id="synthetic.global",
            scope=replace(SCOPE, region=None),
            explicitly_global=True,
            effective_on=date(2026, 10, 18),
            amount=Decimal("1"),
        )
        result = choose_current_rate(SCOPE, (global_rate, BASE))
        self.assertEqual(result.selected_rate_ids, (BASE.rate_id,))

    def test_billing_beats_overview_only_after_scope_and_date(self):
        overview = replace(
            BASE,
            rate_id="synthetic.overview",
            amount=Decimal("1"),
            authority=Authority.OVERVIEW,
        )
        result = choose_current_rate(SCOPE, (overview, BASE))
        self.assertEqual(result.selected_rate_ids, (BASE.rate_id,))
        newer_overview = replace(overview, effective_on=date(2026, 2, 1))
        self.assertEqual(
            choose_current_rate(SCOPE, (BASE, newer_overview)).selected_rate_ids,
            (overview.rate_id,),
        )

    def test_equal_rank_numeric_conflict_uses_disputed_upper_bound(self):
        conflicting = replace(BASE, rate_id="synthetic.conflict", amount=Decimal("3"))
        for rates in ((BASE, conflicting), (conflicting, BASE)):
            result = choose_current_rate(SCOPE, rates)
            self.assertEqual(result.amount, Decimal("3"))
            self.assertTrue(result.disputed)
            self.assertEqual(
                result.selected_rate_ids, ("synthetic.conflict", BASE.rate_id)
            )

    def test_equal_amounts_are_not_a_numeric_dispute(self):
        same = replace(BASE, rate_id="synthetic.corroborating")
        self.assertFalse(choose_current_rate(SCOPE, (BASE, same)).disputed)

    def test_zero_is_preserved_while_missing_amount_is_unknown(self):
        self.assertEqual(
            choose_current_rate(SCOPE, (replace(BASE, amount=Decimal("0")),)).amount,
            Decimal("0"),
        )
        result = choose_current_rate(SCOPE, (replace(BASE, amount=None),))
        self.assertIsNone(result.amount)
        self.assertEqual(result.trace[0].reason, "amount")

    def test_unknown_validity_and_effective_date_do_not_produce_current_price(self):
        for rate in (
            replace(BASE, valid_for_query=None),
            replace(BASE, effective_on=None),
        ):
            with self.subTest(rate=rate):
                self.assertIsNone(choose_current_rate(SCOPE, (rate,)).amount)

    def test_duplicate_id_or_condition_and_nonfinite_amount_are_rejected(self):
        with self.assertRaises(ValueError):
            choose_current_rate(SCOPE, (BASE, BASE))
        with self.assertRaises(ValueError):
            match_scope(
                SCOPE,
                replace(
                    BASE,
                    scope=replace(
                        SCOPE, conditions=(("plan", "standard"), ("plan", "premium"))
                    ),
                ),
            )
        with self.assertRaises(ValueError):
            replace(BASE, explicitly_global=True)
        for amount in (Decimal("NaN"), Decimal("Infinity"), Decimal("-1")):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                choose_current_rate(SCOPE, (replace(BASE, amount=amount),))


if __name__ == "__main__":
    unittest.main()
