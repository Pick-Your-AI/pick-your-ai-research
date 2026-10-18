"""Executable research cases for CTX-01/02 and CD-11; all quantities are synthetic."""

import unittest
from dataclasses import replace
from typing import Final

from tests.context_budget_prototype import (
    Budget,
    Outcome,
    Semantics,
    TokenRange,
    effective_limit,
    evaluate,
)

SHARED: Final = Budget(
    Semantics.SHARED, TokenRange(7000, 7000), 2000, 4000, shared_cap=8000
)


class ContextBudgetCases(unittest.TestCase):
    def test_shared_window_rejects_sum_when_individual_limits_fit(self) -> None:
        result = evaluate(SHARED)
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertFalse(result.may_not_fit)

    def test_separate_caps_do_not_invent_a_shared_window(self) -> None:
        budget = replace(SHARED, semantics=Semantics.SEPARATE, input_cap=8000)
        result = evaluate(budget)
        self.assertEqual(result.outcome, Outcome.PASS)
        self.assertEqual(
            next(c.upper for c in result.checks if c.name == "combined"),
            Outcome.SKIPPED,
        )

    def test_bound_straddling_limit_fails_with_uncertainty_flag(self) -> None:
        budget = replace(SHARED, input_tokens=TokenRange(5500, 6500))
        result = evaluate(budget)
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertTrue(result.may_not_fit)

    def test_upper_bound_equal_to_limit_passes(self) -> None:
        result = evaluate(replace(SHARED, input_tokens=TokenRange(5000, 6000)))
        self.assertEqual(result.outcome, Outcome.PASS)

    def test_shared_straddle_keeps_uncertainty_when_output_cap_is_unknown(self) -> None:
        budget = replace(SHARED, input_tokens=TokenRange(5500, 6500), output_cap=None)
        result = evaluate(budget)
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertTrue(result.may_not_fit)

    def test_separate_straddle_keeps_uncertainty_when_output_cap_is_unknown(
        self,
    ) -> None:
        budget = replace(
            SHARED,
            semantics=Semantics.SEPARATE,
            input_tokens=TokenRange(7500, 8500),
            input_cap=8000,
            output_cap=None,
        )
        result = evaluate(budget)
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertTrue(result.may_not_fit)

    def test_definite_output_failure_prevents_uncertainty_only_label(self) -> None:
        budget = replace(SHARED, input_tokens=TokenRange(5500, 6500), output_cap=1000)
        result = evaluate(budget)
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertFalse(result.may_not_fit)

    def test_known_failure_is_not_hidden_by_missing_input(self) -> None:
        result = evaluate(replace(SHARED, input_tokens=None, reserved_output=4001))
        self.assertEqual(result.outcome, Outcome.FAIL)

    def test_known_input_failure_is_not_hidden_by_unknown_budget_semantics(self) -> None:
        budget = replace(SHARED, semantics=Semantics.UNKNOWN, input_cap=6000)
        result = evaluate(budget)
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertFalse(result.may_not_fit)

    def test_input_straddle_keeps_uncertainty_with_unknown_budget_semantics(self) -> None:
        budget = replace(
            SHARED,
            semantics=Semantics.UNKNOWN,
            input_tokens=TokenRange(5500, 6500),
            input_cap=6000,
        )
        result = evaluate(budget)
        self.assertEqual(result.outcome, Outcome.FAIL)
        self.assertTrue(result.may_not_fit)

    def test_fitting_input_cap_cannot_resolve_unknown_budget_semantics(self) -> None:
        budget = replace(SHARED, semantics=Semantics.UNKNOWN, input_cap=8000)
        result = evaluate(budget)
        self.assertEqual(result.outcome, Outcome.UNKNOWN)
        self.assertFalse(result.may_not_fit)

    def test_partial_pass_cannot_hide_unknown_required_operands(self) -> None:
        fitting = replace(SHARED, input_tokens=TokenRange(5000, 5000))
        for budget in (
            replace(fitting, input_tokens=None),
            replace(fitting, reserved_output=None),
            replace(fitting, output_cap=None),
            replace(fitting, shared_cap=None),
            replace(fitting, semantics=Semantics.UNKNOWN),
        ):
            with self.subTest(budget=budget):
                self.assertEqual(evaluate(budget).outcome, Outcome.UNKNOWN)

    def test_separate_input_and_output_fail_independently(self) -> None:
        separate = replace(SHARED, semantics=Semantics.SEPARATE, input_cap=8000)
        for budget in (
            replace(separate, input_tokens=TokenRange(8001, 8001)),
            replace(separate, reserved_output=4001),
        ):
            with self.subTest(budget=budget):
                self.assertEqual(evaluate(budget).outcome, Outcome.FAIL)

    def test_policy_ceiling_is_an_explicit_additional_predicate(self) -> None:
        budget = replace(
            SHARED,
            semantics=Semantics.SEPARATE,
            input_cap=8000,
            policy_total_cap=8500,
        )
        self.assertEqual(evaluate(budget).outcome, Outcome.FAIL)

    def test_missing_route_tuple_cannot_use_another_routes_limit(self) -> None:
        self.assertEqual(
            evaluate(replace(SHARED, tuple_matches=False)).outcome, Outcome.UNKNOWN
        )

    def test_disabled_selection_skips_without_inferred_support(self) -> None:
        self.assertEqual(
            evaluate(replace(SHARED, enabled=False)).outcome, Outcome.SKIPPED
        )

    def test_unknown_extension_uses_native_limit(self) -> None:
        limit = effective_limit(32768, extension=131072)
        budget = replace(
            SHARED,
            input_tokens=TokenRange(99000, 99000),
            reserved_output=1000,
            shared_cap=limit,
        )
        self.assertEqual(evaluate(budget).outcome, Outcome.FAIL)

    def test_evidenced_extension_obeys_lower_runtime_ceiling(self) -> None:
        limit = effective_limit(
            32768, extension=131072, extension_evidenced=True, runtime_ceiling=65536
        )
        self.assertEqual(limit, 65536)

    def test_native_limit_pass_does_not_supply_runtime_or_memory_evidence(self) -> None:
        budget = replace(
            SHARED,
            input_tokens=TokenRange(20000, 20000),
            reserved_output=8000,
            output_cap=8000,
            shared_cap=effective_limit(32768),
        )
        self.assertEqual(evaluate(budget).outcome, Outcome.PASS)

    def test_missing_native_limit_stays_unknown(self) -> None:
        self.assertIsNone(effective_limit(None, extension=131072))


if __name__ == "__main__":
    _ = unittest.main()
