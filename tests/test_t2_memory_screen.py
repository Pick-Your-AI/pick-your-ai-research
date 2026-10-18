"""Synthetic arithmetic boundary cases; no GPU or vendor evidence."""
import importlib.util
from decimal import Decimal, localcontext
from pathlib import Path
import unittest

PATH = (Path(__file__).resolve().parents[1] / "research" /
        "T2-infrastructure" / "compute" / "memory_screen.py")
SPEC = importlib.util.spec_from_file_location("t2_memory_screen", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MemoryScreen(unittest.TestCase):
    def screen(self, **changes):
        inputs = dict(live_upper_bytes=41_000_000_000,
                      capacity_lower_bytes=48_000_000_000,
                      headroom=Decimal("0.1"), capacity_basis="before_reserve",
                      confidence_eligible=True, same_domain=True)
        inputs.update(changes)
        return MODULE.screen_memory(**inputs)

    def test_documented_sensitivity_changes_conditional_outcome(self):
        self.assertEqual(self.screen()["outcome"], "pass")
        self.assertEqual(self.screen(headroom=Decimal("0.2"))["outcome"], "fail")

    def test_already_reduced_pool_does_not_pay_reserve_twice(self):
        full = self.screen()
        pool = self.screen(capacity_lower_bytes=43_200_000_000,
                           capacity_basis="after_reserve")
        self.assertEqual(pool, full)

    def test_exact_boundary_and_one_byte_above(self):
        self.assertEqual(self.screen(live_upper_bytes=43_200_000_000)["outcome"], "pass")
        self.assertEqual(self.screen(live_upper_bytes=43_200_000_001)["outcome"], "fail")

    def test_explicit_zero_reserve_differs_from_missing(self):
        self.assertEqual(self.screen(headroom=Decimal(0))["budget_bytes_exact"], "48000000000")
        self.assertEqual(self.screen(headroom=None)["outcome"], "unknown")

    def test_every_missing_input_remains_unknown(self):
        for field in ("live_upper_bytes", "capacity_lower_bytes", "headroom",
                      "capacity_basis", "confidence_eligible", "same_domain"):
            with self.subTest(field=field):
                result = self.screen(**{field: None})
                self.assertEqual(result["outcome"], "unknown")
                self.assertNotIn("budget_bytes_exact", result)

    def test_more_headroom_cannot_replace_confidence_or_domain(self):
        for field in ("confidence_eligible", "same_domain"):
            self.assertEqual(self.screen(headroom=Decimal("0.99"),
                                         **{field: False})["outcome"], "unknown")

    def test_invalid_values_are_rejected(self):
        cases = [("headroom", v) for v in (Decimal("NaN"), Decimal("Infinity"),
                  Decimal("-0.1"), Decimal(1), 0.1)]
        cases += [("capacity_lower_bytes", v) for v in (0, -1, True, 48.0)]
        cases += [("live_upper_bytes", -1), ("capacity_basis", "unspecified"),
                  ("confidence_eligible", 1), ("same_domain", "yes")]
        for field, value in cases:
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.screen(**{field: value})

    def test_decimal_context_cannot_round_away_a_failure(self):
        with localcontext() as ctx:
            ctx.prec = 2
            result = self.screen(live_upper_bytes=100, capacity_lower_bytes=100,
                                 headroom=Decimal("0.00000000000000000001"))
        self.assertEqual(result["outcome"], "fail")


if __name__ == "__main__":
    unittest.main()
