"""Synthetic regressions for standard API estimates and pricing provenance."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pricing_compiler", ROOT / "scripts/compile_ai_logs.py")
assert SPEC and SPEC.loader
compiler = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compiler)


class PricingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pricing = json.loads((ROOT / "templates/pricing.json").read_text(encoding="utf-8"))

    def price(self, model="gpt-6.1-sol", tool="codex", **tokens):
        return compiler.price_event(dict(model=model, tool=tool, **tokens), self.pricing)

    def test_exact_models_use_verified_standard_rates_without_fallback(self):
        # Mixed request below the long-context threshold, covering every token class.
        examples = (
            ("gpt-6-astra", "codex", 0.3495, 0.35),
            ("gpt-6.1-sol", "codex", 0.0697, 0.07),
            ("gpt-6-sol", "codex", 0.0699, 0.07),
            ("gpt-6-luna", "codex", 0.003495, 0.0035),
            ("claude-opus-5-5", "claude-code", 0.1514, 0.14),
            ("claude-sonnet-5-5", "claude-code", 0.0757, 0.07),
        )
        for model, tool, expected_cost, expected_nocache in examples:
            with self.subTest(model=model):
                cost, nocache, priced_as, assumed = self.price(
                    model, tool, input_uncached=1000, cache_read=2000,
                    cache_write_5m=3000, cache_write_1h=4000, output=5000,
                )
                self.assertAlmostEqual(cost, expected_cost)
                self.assertAlmostEqual(nocache, expected_nocache)
                self.assertEqual(priced_as, model)
                self.assertIsNone(assumed)
                row = self.pricing["models"][model]
                self.assertEqual(row["service_tier"], "standard")
                verified_at = "2026-10-11" if tool == "claude-code" else "2026-10-03"
                self.assertEqual(row["verified_at"], verified_at)
                source = ("https://platform.claude.com/docs/en/about-claude/pricing"
                          if tool == "claude-code" else "https://developers.openai.com/api/docs/pricing")
                self.assertEqual(row["source"], source)

    def test_provider_prefix_resolves_exact_model(self):
        cost, nocache, priced_as, assumed = self.price("openai/gpt-6.1-sol", cache_read=100000)
        self.assertAlmostEqual(cost, 0.01)
        self.assertAlmostEqual(nocache, 0.2)
        self.assertEqual(priced_as, "gpt-6.1-sol")
        self.assertIsNone(assumed)

    def test_claude_55_cache_heavy_calls_use_exact_model_rates(self):
        for model, expected_cost, expected_nocache in (
            ("claude-opus-5-5", 0.2, 4.0),
            ("claude-sonnet-5-5", 0.1, 2.0),
        ):
            for identity in (model, "anthropic/" + model):
                with self.subTest(model=identity):
                    cost, nocache, priced_as, assumed = self.price(
                        identity, "claude-code", cache_read=1000000,
                    )
                    self.assertAlmostEqual(cost, expected_cost)
                    self.assertAlmostEqual(nocache, expected_nocache)
                    self.assertEqual(priced_as, model)
                    self.assertIsNone(assumed)

    def test_gpt_cache_writes_use_api_rates_for_both_duration_fields(self):
        for field in ("cache_write_5m", "cache_write_1h", "cache_write"):
            with self.subTest(field=field):
                cost, nocache, _, _ = self.price(**{field: 100000})
                self.assertAlmostEqual(cost, 0.25)
                self.assertAlmostEqual(nocache, 0.2)

    def test_long_context_rates_for_each_gpt_model(self):
        for model, expected in (
            ("gpt-6-astra", 5.51502), ("gpt-6.1-sol", 1.103004),
            ("gpt-6-sol", 1.103004), ("gpt-6-luna", 0.0551502),
        ):
            with self.subTest(model=model):
                cost, nocache, priced_as, assumed = self.price(model, input_uncached=272001, output=1000)
                self.assertAlmostEqual(cost, expected)
                self.assertAlmostEqual(nocache, expected)
                self.assertEqual(priced_as, model)
                self.assertIsNone(assumed)

    def test_long_context_boundary_counts_all_input_categories(self):
        tokens = dict(input_uncached=1000, cache_read=260000, cache_write_5m=6000,
                      cache_write_1h=5000, output=10000)
        cost, nocache, _, _ = self.price(**tokens)
        self.assertAlmostEqual(cost, 0.1555)
        self.assertAlmostEqual(nocache, 0.644)
        tokens["cache_read"] += 1
        cost, nocache, _, _ = self.price(**tokens)
        self.assertAlmostEqual(cost, 0.2610002)
        self.assertAlmostEqual(nocache, 1.238004)

    def test_each_input_category_can_cross_long_context_boundary(self):
        for field, expected in (
            ("input_uncached", 1.088004), ("cache_read", 1.0880002),
            ("cache_write_5m", 1.088005), ("cache_write_1h", 1.088005),
            ("cache_write", 1.088005),
        ):
            with self.subTest(field=field):
                tokens = {"input_uncached": 272000}
                tokens[field] = tokens.get(field, 0) + 1
                cost, nocache, _, _ = self.price(**tokens)
                self.assertAlmostEqual(cost, expected)
                self.assertAlmostEqual(nocache, 1.088004)

    def test_output_tokens_do_not_trigger_long_context(self):
        cost, nocache, _, _ = self.price(input_uncached=272000, output=1000000)
        self.assertAlmostEqual(cost, 10.544)
        self.assertAlmostEqual(nocache, 10.544)

    def test_explicit_cache_write_breakdown_does_not_double_count_aggregate(self):
        cost, nocache, _, _ = self.price(
            input_uncached=272000, cache_write=50000, cache_write_5m=0, cache_write_1h=0,
        )
        self.assertAlmostEqual(cost, 0.544)
        self.assertAlmostEqual(nocache, 0.544)

    def test_sonnet_full_context_keeps_standard_rates(self):
        cost, nocache, _, assumed = self.price(
            "claude-sonnet-5-5", "claude-code", input_uncached=900000, output=1000,
        )
        self.assertAlmostEqual(cost, 1.81)
        self.assertAlmostEqual(nocache, 1.81)
        self.assertIsNone(assumed)

    def test_unknown_model_fallback_identifies_unpriced_model(self):
        cost, nocache, priced_as, assumed = self.price("unpublished-model", input_uncached=100000)
        self.assertAlmostEqual(cost, 0.4)
        self.assertAlmostEqual(nocache, 0.4)
        self.assertEqual(priced_as, "gpt-5.6-sol")
        self.assertTrue(assumed.startswith("No price for unpublished-model; using gpt-5.6-sol."))
        self.assertIn(self.pricing["fallback_by_tool"]["codex"]["note"], assumed)

    def test_missing_model_fallback_distinguishes_missing_identity(self):
        for model in (None, "", "?"):
            with self.subTest(model=model):
                cost, nocache, priced_as, assumed = self.price(model, input_uncached=100000)
                self.assertAlmostEqual(cost, 0.4)
                self.assertAlmostEqual(nocache, 0.4)
                self.assertEqual(priced_as, "gpt-5.6-sol")
                self.assertTrue(assumed.startswith("No model recorded; using gpt-5.6-sol."))

    def test_unknown_model_without_fallback_stays_explicitly_unpriced(self):
        self.assertEqual(
            self.price("unpublished-model", "unknown-tool", input_uncached=100000),
            (0.0, 0.0, None, "no price for unpublished-model"),
        )

    def test_legacy_flat_price_rows_keep_rates_and_assumptions(self):
        cost, nocache, priced_as, assumed = self.price(
            "gpt-5.3-codex-spark", input_uncached=500000, cache_read=100000, output=1000,
        )
        self.assertAlmostEqual(cost, 0.9065)
        self.assertAlmostEqual(nocache, 1.064)
        self.assertEqual(priced_as, "gpt-5.3-codex-spark")
        self.assertEqual(assumed, "no public API price; priced as gpt-5.3-codex")
        self.assertNotIn("verified_at", self.pricing["models"]["gpt-5.3-codex-spark"])

    def test_legacy_fallback_and_aggregate_cache_write_remain_supported(self):
        legacy = {"models": {"sibling": {
            "input": 3, "cache_read": 0.3, "cache_write_5m": 3.75,
            "cache_write_1h": 6, "output": 15,
        }}, "fallback_by_tool": {"synthetic": {"model": "sibling", "note": "legacy rule"}}}
        event = dict(tool="synthetic", model="unknown", input_uncached=100000,
                     cache_read=100000, cache_write=100000, output=10000)
        cost, nocache, priced_as, assumed = compiler.price_event(event, legacy)
        self.assertAlmostEqual(cost, 0.855)
        self.assertAlmostEqual(nocache, 1.05)
        self.assertEqual(priced_as, "sibling")
        self.assertIn("legacy rule", assumed)

    def test_pricing_does_not_mutate_snapshot_when_selecting_context_tier(self):
        original = copy.deepcopy(self.pricing)
        self.price(input_uncached=500000)
        self.price(input_uncached=1000)
        self.assertEqual(self.pricing, original)

    def test_logged_cost_bypasses_token_rate_estimation(self):
        result = self.price("openrouter/z-ai/glm-5.3-flash", "openclaw", cost_usd=1.23, input_uncached=900000)
        self.assertEqual(result, (1.23, 1.23, "openrouter/z-ai/glm-5.3-flash", None))


if __name__ == "__main__":
    unittest.main()
